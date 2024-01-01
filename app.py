from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

import pandas as pd
import requests

api_key = ''

app = Flask(__name__)
cities_df = pd.read_csv('data/worldcities.csv')
NUM_YEARS = 3
NUM_DAYS = 3


def K2C(kelvin_temp, decimal_places=2):
    celsius_temp = kelvin_temp - 273.15
    return round(celsius_temp, decimal_places)

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
def get_weather():
    city = request.form.get('city')
    selected_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

    city_data = cities_df[cities_df['city'] == city].iloc[0]
    lat = city_data['lat']
    lon = city_data['lng']

    weather_data = []
    for i in range(NUM_YEARS):
        year = selected_date.year - i
        yearly_data = []
        for j in range(NUM_DAYS):
            date_to_fetch = datetime(year, selected_date.month, selected_date.day) + timedelta(days=j)
            unix_time = int(date_to_fetch.timestamp())
            response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={unix_time}&appid={api_key}")
            if response.status_code == 200:
                daily_data = response.json()['data'][0]
                daily_data['formatted_date'] = date_to_fetch.strftime('%Y-%m-%d')
                if 'temp' in daily_data:
                    daily_data['temp'] = K2C(daily_data['temp'])
                if 'feels_like' in daily_data:
                    daily_data['feels_like'] = K2C(daily_data['feels_like'])
                yearly_data.append(daily_data)
            else:
                yearly_data.append({'error': 'No data', 'date': date_to_fetch.strftime('%Y-%m-%d')})
        weather_data.append({'year': year, 'data': yearly_data})

    return render_template('weather_results.html', weather_data=weather_data, city=city)


if __name__ == '__main__':
    app.run(debug=True)
