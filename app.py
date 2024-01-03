from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
from weather_api import get_cached_weather_data

#  usage url: https://home.openweathermap.org/statistics/onecall_30
# icon set: https://www.iconpacks.net/free-icon-pack/free-weather-forecast-icon-pack-201.html

api_key = 'e3ab35232ec5dc39d6b5224071a00a84'

app = Flask(__name__)
cities_df = pd.read_csv('data/worldcities.csv')
NUM_YEARS = 4
NUM_DAYS = 7


def get_weather_icon(cloud_cover, precipitation):
    if precipitation > 7.6:
        return "heavy_rain.png"
    elif precipitation > 2.5:
        return "moderate_rain.png"
    elif precipitation > 0:
        if cloud_cover < 3/8:
            return "clear_light_rain.png"
        else:
            return "light_rain.png"
    elif cloud_cover > 5/8:
        return "cloudy.png"
    elif cloud_cover > 3/8:
        return "mostly_cloudy.png"
    elif cloud_cover > 1/8:
        return "partly_cloudy.png"
    else:
        return "clear_sunny.png"


def K2C(kelvin_temp):
    celsius_temp = kelvin_temp - 273.15
    return round(celsius_temp)


def mps_to_kph(speed_mps):
    speed_kph = speed_mps * 3.6  # 1 m/s is approximately 3.6 kph
    return round(speed_kph)


def get_sky_condition(cloud_cover):
    if cloud_cover <= 1/8:
        return "Clear"
    elif 1/8 < cloud_cover <= 3/8:
        return "Mostly Clear"
    elif 3/8 < cloud_cover <= 5/8:
        return "Partly Cloudy"
    elif 5/8 < cloud_cover <= 7/8:
        return "Mostly Cloudy"
    else:  # cloud_cover > 7/8
        return "Cloudy"


def format_precipitation(precipitation):
    if precipitation == 0:
        return "-"
    elif precipitation < 1:
        return "<1 mm"
    else:
        return f"{round(precipitation)} mm"


@app.route('/')
def index():
    countries = sorted(cities_df['country'].unique())
    default_country = 'Portugal'
    cities = sorted(cities_df[cities_df['country'] == default_country]['city'].unique())
    return render_template('index.html', countries=countries, default_country=default_country, cities=cities)

@app.route('/cities', methods=['POST'])
def cities():
    country = request.form.get('country')
    cities = sorted(cities_df[cities_df['country'] == country]['city'].unique().tolist())
    return jsonify(cities)

@app.route('/get_weather', methods=['POST'])
@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form.get('city')
    country = request.form.get('country')
    selected_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

    weather_data = []
    for i in range(NUM_YEARS):
        year = selected_date.year - i
        yearly_data = []
        for j in range(NUM_DAYS):
            date_to_fetch = (datetime(year, selected_date.month, selected_date.day) + timedelta(days=j)).strftime(
                '%Y-%m-%d')

            daily_data_response = get_cached_weather_data(city, country, date_to_fetch, api_key, cities_df)

            if daily_data_response:
                # Extracting required data from response
                temperature_info = daily_data_response.get('temperature', {})
                min_temp = K2C(temperature_info.get('min', 0))
                max_temp = K2C(temperature_info.get('max', 0))
                wind_speed = mps_to_kph(daily_data_response.get('wind', {}).get('max', {}).get('speed', 0))
                humidity = daily_data_response.get('humidity', {}).get('afternoon', 0)
                precipitation = daily_data_response.get('precipitation', {}).get('total', 0)
                cloud_cover = daily_data_response.get('cloud_cover', {}).get('afternoon', 0)
                icon_filename = get_weather_icon(cloud_cover/100, precipitation)

                daily_data = {
                    'date': date_to_fetch,
                    'min_temp': min_temp,
                    'max_temp': max_temp,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'precipitation': format_precipitation(precipitation),
                    'cloud_cover': cloud_cover,
                    'clouds': get_sky_condition(cloud_cover/100),
                    'icon': icon_filename
                }
                yearly_data.append(daily_data)
            else:
                yearly_data.append({'error': 'No data', 'date': date_to_fetch})
        weather_data.append({'year': year, 'data': yearly_data})

    date_headers = [(selected_date + timedelta(days=j)).strftime('%b %-d') for j in range(NUM_DAYS)]
    return render_template('weather_results.html', weather_data=weather_data, city=city, date_headers=date_headers,
                           NUM_DAYS=NUM_DAYS)

if __name__ == '__main__':
    app.run(debug=True)
