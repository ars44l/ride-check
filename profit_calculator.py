def calculate_gas_cost(miles, mpg, price_per_gallon):
    gallons_used = miles / mpg
    return gallons_used * price_per_gallon

def calculate_wear_and_tear(miles, irs_rate=0.70):
    return miles * irs_rate

def calculate_profit(fare, miles, mpg, price_per_gallon):
    gas_cost = calculate_gas_cost(miles, mpg, price_per_gallon)
    wear_cost = calculate_wear_and_tear(miles)
    profit = fare - gas_cost - wear_cost
    return {
        "profit": round(profit, 2),
        "gas_cost": round(gas_cost, 2),
        "wear_cost": round(wear_cost, 2),
    }

def calculate_profit_per_hour(profit, duration_minutes):
    hours = duration_minutes / 60
    return round(profit / hours, 2)

def should_take_ride(profit_per_hour, target_hourly_rate):
    difference = round(profit_per_hour - target_hourly_rate, 2)
    worth_it = profit_per_hour >= target_hourly_rate
    return {
        "worth_it": worth_it,
        "difference": difference,
    }
