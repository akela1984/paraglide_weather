from flask import Flask, render_template, jsonify
from datetime import datetime  # Import the datetime module
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sites')
def sites():
    # Fetch weather data from the API
    api_url = "https://api.openweathermap.org/data/2.5/forecast?lat=55.59194&lon=-3.66288&units=metric&appid=69129460125ea343f55bb51da80ec507"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        
        # Process the data and create the forecast
        forecast_data = data['list'][:4 * 8]
        forecast = []
        
        for item in forecast_data:
            date = item['dt']
            time_str = datetime.utcfromtimestamp(date).strftime('%H:%M')
            
            # Check if the time is between 09:00 and 21:00
            if '09:00' <= time_str <= '21:00':
                day_of_week = datetime.utcfromtimestamp(date).strftime('%a')
                date_str = datetime.utcfromtimestamp(date).strftime('%d/%m/%Y')
                temperature = round(item['main']['temp'])
                description = item['weather'][0]['description'].capitalize()
                wind_direction = get_wind_direction(item['wind']['deg'])
                wind_speed = round(item['wind']['speed'], 1)
                rain = 'rain' in item and item['rain']
                
                # Determine fly condition based on JavaScript conditions
                fly_condition_tinto_south, fly_condition_class = get_fly_condition_tinto_south(wind_direction, description, wind_speed)
                fly_condition_tinto_north, fly_condition_class = get_fly_condition_tinto_north(wind_direction, description, wind_speed)
                fly_condition_abington, fly_condition_class = get_fly_condition_abington(wind_direction, description, wind_speed)

                
                forecast.append({
                    'dayOfWeek': day_of_week,
                    'date': date_str,
                    'time': time_str,
                    'temperature': temperature,
                    'description': description,
                    'windDirection': wind_direction,
                    'windSpeed': wind_speed,
                    'rain': rain,
                    'flyConditionTintoSouth': fly_condition_tinto_south,
                    'flyConditionTintoNorth': fly_condition_tinto_north,
                    'flyConditionAbington': fly_condition_abington,

                    'flyConditionClass': fly_condition_class  # Add fly condition CSS class
                })

        # Render the HTML template with the forecast data
        return render_template('sites.html', forecast=forecast)
    else:
        return "Error fetching weather data"

# Helper function to get wind direction
def get_wind_direction(degree):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return directions[round((degree % 360) / 22.5)]

# Helper function to determine fly condition for Tinto South
def get_fly_condition_tinto_south(wind_direction, description, wind_speed):
    if (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and "rain" in description.lower()
    ):
        return "Not flyable due to the rainy conditions.", "rain"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 0 <= wind_speed <= 3
    ):
        return "Ideal conditions for beginners and thermal flying", "ideal"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 3 < wind_speed <= 5
    ):
        return "Good conditions for most pilots", "good"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 5 < wind_speed <= 8
    ):
        return "Challenging conditions for intermediate pilots", "challenging"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 8 < wind_speed <= 11
    ):
        return "Difficult conditions for experienced pilots only", "difficult"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 11 < wind_speed <= 15
    ):
        return "Dangerous conditions for all pilots", "dangerous"
    elif wind_direction in ["S", "SSW", "SSE", "SW", "SE"] and wind_speed > 15:
        return "Extreme conditions, not suitable for flying", "extreme"
    else:
        return "The wind direction is not suitable for this site.", "unsuitable"
    

# Helper function to determine fly condition for Tinto North
def get_fly_condition_tinto_north(wind_direction, description, wind_speed):
    if (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and "rain" in description.lower()
    ):
        return "Not flyable due to the rainy conditions.", "rain"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 0 <= wind_speed <= 3
    ):
        return "Ideal conditions for beginners and thermal flying", "ideal"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 3 < wind_speed <= 5
    ):
        return "Good conditions for most pilots", "good"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 5 < wind_speed <= 8
    ):
        return "Challenging conditions for intermediate pilots", "challenging"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 8 < wind_speed <= 11
    ):
        return "Difficult conditions for experienced pilots only", "difficult"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 11 < wind_speed <= 15
    ):
        return "Dangerous conditions for all pilots", "dangerous"
    elif wind_direction in ["N", "NNW", "NNE", "NW", "NE"] and wind_speed > 15:
        return "Extreme conditions, not suitable for flying", "extreme"
    else:
        return "The wind direction is not suitable for this site.", "unsuitable"
    
    # Helper function to determine fly condition for Abington
def get_fly_condition_abington(wind_direction, description, wind_speed):
    if (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and "rain" in description.lower()
    ):
        return "Not flyable due to the rainy conditions.", "rain"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 0 <= wind_speed <= 3
    ):
        return "Ideal conditions for beginners and thermal flying", "ideal"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 3 < wind_speed <= 5
    ):
        return "Good conditions for most pilots", "good"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 5 < wind_speed <= 8
    ):
        return "Challenging conditions for intermediate pilots", "challenging"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 8 < wind_speed <= 11
    ):
        return "Difficult conditions for experienced pilots only", "difficult"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 11 < wind_speed <= 15
    ):
        return "Dangerous conditions for all pilots", "dangerous"
    elif wind_direction in ["W", "WSW", "WNW", "Sw", "Nw"] and wind_speed > 15:
        return "Extreme conditions, not suitable for flying", "extreme"
    else:
        return "The wind direction is not suitable for this site.", "unsuitable"

if __name__ == '__main__':
    app.run()
