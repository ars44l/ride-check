# Ride Check

A full-stack rideshare profitability calculator that helps drivers decide whether a ride is worth accepting before they take it, accounting for gas and vehicle wear-and-tear costs, not just the fare.

Built for a real driver to use in the field, comparing live profit-per-hour against a personal target rate to give an instant take-it/skip-it recommendation.

## How it works

Instead of just showing the fare, Ride Check estimates the driver's actual take-home profit per ride:

Profit = Fare - Gas Cost - Wear-and-Tear Cost

Gas cost is calculated using the vehicle's real EPA-rated MPG (looked up automatically from fueleconomy.gov based on year, make, and model) and live regional gas prices pulled from the EIA (U.S. Energy Information Administration) API. Wear-and-tear uses the IRS standard mileage rate. The resulting profit-per-hour is compared against a driver-set target rate to give a clear take-it or skip-it call.

Account mode saves persistent car settings and ride history to a database, accessible from any device. Guest mode requires no login; car settings and ride history live only in the browser's session storage and clear automatically when the tab closes.

## Tech stack

Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login
APIs: fueleconomy.gov for vehicle MPG lookup, EIA for live gas prices
Auth: Session-based login with hashed passwords via Werkzeug
Frontend: Vanilla HTML, CSS, and JavaScript, mobile-first design
Database: SQLite locally, PostgreSQL in production

## Running locally

git clone https://github.com/ars44l/ride-check.git
cd ride-check
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

You'll need a free EIA API key (register at eia.gov/opendata/register.php), set as an environment variable:

export EIA_API_KEY="your_key_here"

Then run:

python app.py

Open http://127.0.0.1:5001 in your browser.

## Project structure

app.py - Flask server: auth, car setup, ride decision engine, ride history
car_lookup.py - Vehicle year, make, model, and MPG lookup via fueleconomy.gov
gas_prices.py - Live gas price lookup via the EIA API
profit_calculator.py - Core profit, profit-per-hour, and take-it/skip-it logic
static/index.html - Frontend: auth screens, car setup, ride check, and history

## Possible next steps

Deploy to a live URL (Render config already in place: requirements.txt, Procfile, PostgreSQL support)
Track and surface real profit improvement over time once used by an actual driver
Add Google OAuth as an alternative login method