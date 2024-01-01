from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd
import requests

api_key = 'X'

app = Flask(__name__)
cities_df = pd.read_csv('data/worldcities.csv')


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
    date = request.form.get('date')

    # Find the coordinates of the city
    city_data = cities_df[cities_df['city'] == city].iloc[0]
    lat = city_data['lat']
    lon = city_data['lng']

    weather_data = []
    for i in range(1, 4):  # Last 3 years
        year = int(date.split('-')[0]) - i
        new_date = f"{year}-{date.split('-')[1]}-{date.split('-')[2]}"
        unix_time = int(datetime.strptime(new_date, '%Y-%m-%d').timestamp())
        response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={unix_time}&appid={api_key}")
        if response.status_code == 200:
            year_data = response.json()
            year_data['year'] = year  # Add the year to the data
            for data in year_data['data']:
                # Convert Unix timestamp to a formatted date string
                data['formatted_date'] = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d')
                if 'temp' in data:
                    data['temp'] = K2C(data['temp'])
                if 'feels_like' in data:
                    data['feels_like'] = K2C(data['feels_like'])
            weather_data.append(year_data)
        else:
            weather_data.append({'error': 'No data', 'year': year})

    return render_template('weather_results.html', weather_data=weather_data, city=city, date=date)

if __name__ == '__main__':
    app.run(debug=True)
