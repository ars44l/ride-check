import requests
import os

EIA_API_KEY = os.environ.get("EIA_API_KEY")

def get_gas_price(state_code="NY"):
    url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[duoarea][]": f"S{state_code}",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data["response"]["data"]:
        raise ValueError(f"No gas price data available for state '{state_code}'")

    latest = data["response"]["data"][0]
    return float(latest["value"])

if __name__ == "__main__":
    price = get_gas_price("NY")
    print(f"Latest NY gas price: ${price}/gallon")