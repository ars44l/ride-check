import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://www.fueleconomy.gov/ws/rest/vehicle"

def get_years():
    url = f"{BASE_URL}/menu/year"
    response = requests.get(url)
    root = ET.fromstring(response.text)
    return [item.find("text").text for item in root]

def get_makes(year):
    url = f"{BASE_URL}/menu/make?year={year}"
    response = requests.get(url)
    root = ET.fromstring(response.text)
    return [item.find("text").text for item in root]

def get_models(year, make):
    url = f"{BASE_URL}/menu/model?year={year}&make={make}"
    response = requests.get(url)
    root = ET.fromstring(response.text)
    return [item.find("text").text for item in root]

def get_vehicle_ids(year, make, model):
    # A single year/make/model can have multiple trims/engines,
    # each with its own vehicle ID -- this returns all of them.
    url = f"{BASE_URL}/menu/options?year={year}&make={make}&model={model}"
    response = requests.get(url)
    root = ET.fromstring(response.text)
    return [item.find("value").text for item in root]

def get_mpg(vehicle_id):
    url = f"{BASE_URL}/{vehicle_id}"
    response = requests.get(url)
    root = ET.fromstring(response.text)
    combined_mpg = root.find("comb08").text
    return int(combined_mpg)

if __name__ == "__main__":
    years = get_years()
    print("Sample years:", years[:5])

    makes = get_makes("2020")
    print("2020 makes sample:", makes[:5])

    models = get_models("2020", "Toyota")
    print("2020 Toyota models:", models[:8])

    vehicle_ids = get_vehicle_ids("2020", "Toyota", "Camry")
    print("Vehicle IDs for 2020 Toyota Camry:", vehicle_ids)

    if vehicle_ids:
        mpg = get_mpg(vehicle_ids[0])
        print(f"Combined MPG for first trim: {mpg}")
