from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os

from car_lookup import get_years, get_makes, get_models, get_vehicle_ids, get_mpg
from gas_prices import get_gas_price
from profit_calculator import calculate_profit, calculate_profit_per_hour, should_take_ride

app = Flask(__name__)
database_url = os.environ.get("DATABASE_URL", "sqlite:///uber_tracker.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-later")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def serve_index():
    return open(os.path.join(os.path.dirname(__file__), "static", "index.html")).read()

# ---------- Models ----------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    car_year = db.Column(db.String(10))
    car_make = db.Column(db.String(50))
    car_model = db.Column(db.String(50))
    mpg = db.Column(db.Integer)
    target_hourly_rate = db.Column(db.Float, default=30.0)
    state_code = db.Column(db.String(2), default="NY")

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, default=date.today)
    fare = db.Column(db.Float)
    miles = db.Column(db.Float)
    duration_minutes = db.Column(db.Float)
    profit = db.Column(db.Float)
    profit_per_hour = db.Column(db.Float)

with app.app_context():
    db.create_all()

# ---------- Auth routes ----------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not password or (not username and not email):
        return jsonify({"error": "Username or email, plus a password, are required"}), 400

    existing = None
    if username:
        existing = User.query.filter_by(username=username).first()
    if not existing and email:
        existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "An account with that username or email already exists"}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({"logged_in": True, "user_id": user.id})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    identifier = data.get("username") or data.get("email")
    password = data.get("password")

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username/email or password"}), 401

    login_user(user)
    return jsonify({"logged_in": True, "user_id": user.id})

@app.route("/api/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"logged_out": True})

@app.route("/api/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "username": current_user.username, "email": current_user.email})
    return jsonify({"logged_in": False})

# ---------- Car setup routes ----------

@app.route("/api/years", methods=["GET"])
def api_years():
    return jsonify(get_years())

@app.route("/api/makes", methods=["GET"])
def api_makes():
    year = request.args.get("year")
    return jsonify(get_makes(year))

@app.route("/api/models", methods=["GET"])
def api_models():
    year = request.args.get("year")
    make = request.args.get("make")
    return jsonify(get_models(year, make))

@app.route("/api/save-car", methods=["POST"])
@login_required
def save_car():
    data = request.json
    year = data.get("year")
    make = data.get("make")
    model = data.get("model")
    target_hourly_rate = data.get("target_hourly_rate", 30.0)
    state_code = data.get("state_code", "NY")

    vehicle_ids = get_vehicle_ids(year, make, model)
    if not vehicle_ids:
        return jsonify({"error": "No vehicle data found for that car"}), 400

    mpg = get_mpg(vehicle_ids[0])

    settings = Settings.query.filter_by(user_id=current_user.id).first()
    if settings is None:
        settings = Settings(user_id=current_user.id)
        db.session.add(settings)

    settings.car_year = year
    settings.car_make = make
    settings.car_model = model
    settings.mpg = mpg
    settings.target_hourly_rate = target_hourly_rate
    settings.state_code = state_code
    db.session.commit()

    return jsonify({
        "year": year, "make": make, "model": model,
        "mpg": mpg, "target_hourly_rate": target_hourly_rate,
        "state_code": state_code,
    })

@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    if settings is None:
        return jsonify({"configured": False})

    return jsonify({
        "configured": True,
        "year": settings.car_year,
        "make": settings.car_make,
        "model": settings.car_model,
        "mpg": settings.mpg,
        "target_hourly_rate": settings.target_hourly_rate,
        "state_code": settings.state_code,
    })

# ---------- Guest-mode routes (no login required) ----------

@app.route("/api/guest-mpg", methods=["GET"])
def guest_mpg():
    year = request.args.get("year")
    make = request.args.get("make")
    model = request.args.get("model")

    vehicle_ids = get_vehicle_ids(year, make, model)
    if not vehicle_ids:
        return jsonify({"error": "No vehicle data found for that car"}), 400

    mpg = get_mpg(vehicle_ids[0])
    return jsonify({"mpg": mpg})

@app.route("/api/guest-gas-price", methods=["GET"])
def guest_gas_price():
    state = request.args.get("state", "NY")
    price = get_gas_price(state)
    return jsonify({"price": price})

# ---------- Ride decision route ----------

@app.route("/api/check-ride", methods=["POST"])
@login_required
def check_ride():
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    if settings is None:
        return jsonify({"error": "Car not set up yet"}), 400

    data = request.json
    fare = float(data.get("fare"))
    miles = float(data.get("miles"))
    duration_minutes = float(data.get("duration_minutes"))

    gas_price = get_gas_price(settings.state_code)
    profit_data = calculate_profit(fare, miles, settings.mpg, gas_price)
    profit_per_hour = calculate_profit_per_hour(profit_data["profit"], duration_minutes)
    decision = should_take_ride(profit_per_hour, settings.target_hourly_rate)

    return jsonify({
        "profit": profit_data["profit"],
        "gas_cost": profit_data["gas_cost"],
        "wear_cost": profit_data["wear_cost"],
        "profit_per_hour": profit_per_hour,
        "gas_price_used": gas_price,
        "worth_it": decision["worth_it"],
        "difference": decision["difference"],
        "target_hourly_rate": settings.target_hourly_rate,
    })

# ---------- Ride history routes ----------

@app.route("/api/save-ride", methods=["POST"])
@login_required
def save_ride():
    data = request.json
    ride = Ride(
        user_id=current_user.id,
        fare=data.get("fare"),
        miles=data.get("miles"),
        duration_minutes=data.get("duration_minutes"),
        profit=data.get("profit"),
        profit_per_hour=data.get("profit_per_hour"),
    )
    db.session.add(ride)
    db.session.commit()
    return jsonify({"saved": True, "id": ride.id})

@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    rides = Ride.query.filter_by(user_id=current_user.id).order_by(Ride.date.desc(), Ride.id.desc()).all()

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    all_time_total = sum(r.profit for r in rides)
    today_total = sum(r.profit for r in rides if r.date == today)
    week_total = sum(r.profit for r in rides if r.date >= week_start)

    ride_list = [{
        "id": r.id,
        "date": r.date.isoformat(),
        "fare": r.fare,
        "miles": r.miles,
        "duration_minutes": r.duration_minutes,
        "profit": r.profit,
        "profit_per_hour": r.profit_per_hour,
    } for r in rides]

    return jsonify({
        "rides": ride_list,
        "totals": {
            "today": round(today_total, 2),
            "this_week": round(week_total, 2),
            "all_time": round(all_time_total, 2),
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)