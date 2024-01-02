import diskcache as dc
import json
import requests

cache = dc.Cache('./wo_cache')


def _get_weather_data(lat, lon, date, api_key):
    # Create a unique cache key
    cache_key = f"{lat}_{lon}_{date}"

    # Check cache first
    if cache_key in cache:
        return json.loads(cache[cache_key])

    # API call if data not in cache
    response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date}&appid={api_key}")
    if response.status_code == 200:
        cache[cache_key] = json.dumps(response.json())
        return response.json()

    return None  # or handle error appropriately


def get_cached_weather_data(city, country, date, api_key, cities_df):
    city_data = cities_df[cities_df['city'] == city].iloc[0]
    lat, lon = city_data['lat'], city_data['lng']
    return _get_weather_data(lat, lon, date, api_key)
