from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import json
import requests

def get_data():
    r = requests.get("https://www.museumkaart.nl/museumkaartgeldig")
    soup = BeautifulSoup(r.text, "html.parser")
    script = soup.find_all("script")[7].string.replace('var ViewModelProvincies =', '')
    data = json.loads(script)
    return data

def write_csv(data):
    with open("museumkaart.csv", "w", encoding="utf-8") as f:
        f.write("Province,City,Museum,url,address,hours,lat,long\n")
        for province in data.keys():
            print(province)
            for city in data[province].keys():
                print(" " + city)
                for museum in data[province][city]:
                    name = museum["displayName"].replace('"', '""')
                    url = museum["link"]
                    address, hours = get_address_hours(url)
                    lat, long = get_lat_long(f"{address}, {city}, {province}, Netherlands")
                    f.write(f'"{province}","{city}","{name}","{url}","{address}","{hours}",{lat},{long}\n')
                    print("  " + name)

def get_address_hours(url):
    full_url = "https://www.museumkaart.nl" + url
    r = requests.get(full_url)
    soup = BeautifulSoup(r.text, "html.parser")
    address = str(soup.find("p", {"class": "museum-details__address"})).split("<br/>")[0].split("\r\n")[1].strip()
    try:
        hours = soup.find("p", {"class": "museum-details__openinghours"}).text.replace('"', '""')
    except:
        print("ERROR with hours: " + url)
        hours = ""
    return (address, hours)

def get_lat_long(address):
    geolocator = Nominatim()
    location = geolocator.geocode(address)
    if location is not None:
        return (location.latitude, location.longitude)
    print("ERROR with lat/long: " + address)
    return (None, None)

def main():
    data = get_data()
    write_csv(data)

if __name__ == "__main__":
    main()