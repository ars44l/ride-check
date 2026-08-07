# RideCheck

A profit-tracking tool for DoorDash, Uber Eats, and rideshare drivers that estimates real take-home profit per ride or delivery before you accept it, accounting for gas and vehicle wear-and-tear costs, not just the fare.

Live at: https://uber-ridecheck.onrender.com/

## How it works

Instead of just showing the fare, RideCheck estimates the driver's actual take-home profit:

Profit = Fare - Gas Cost - Wear-and-Tear Cost

Gas cost is calculated using the vehicle's real EPA-rated MPG (looked up automatically from fueleconomy.gov based on year, make, and model) and live regional gas prices pulled from the EIA (U.S. Energy Information Administration) API. Wear-and-tear uses the IRS standard mileage rate. The resulting profit-per-hour is compared against a driver-set target rate to give a clear take-it or skip-it call, fast enough to use in the few seconds before a ride or delivery offer expires.

Account mode saves persistent car settings and ride history to a database, accessible from any device. Guest mode requires no login; car settings and ride history live only in the browser's session storage and clear automatically when the tab closes.

## Tech stack

Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login
APIs: fueleconomy.gov for vehicle MPG lookup, EIA for live gas prices
Auth: Session-based login with hashed passwords via Werkzeug
Frontend: Vanilla HTML, CSS, and JavaScript, mobile-first, dark terminal-style UI with scroll-snap sections and animated data readouts
Database: PostgreSQL in production, SQLite for local development
Deployment: Render

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

Track and surface real profit improvement over time from actual driver use
Add Google OAuth as an alternative login method
OCR-based ride offer capture to auto-fill fare, distance, and duration from a screenshot