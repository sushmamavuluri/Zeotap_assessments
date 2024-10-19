import requests
import time
from datetime import datetime
from collections import defaultdict

# OpenWeatherMap API settings
API_KEY = '3279f22e33807f7f70b8dd2c71ea1ed3'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
API_URL = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

# Data structure for storing daily weather data
daily_weather_data = defaultdict(list)
daily_summary = {}

# Configurable user alert thresholds
ALERT_THRESHOLD_TEMP = 35  # Celsius
ALERT_THRESHOLD_COUNT = 2   # Consecutive alerts threshold

# Function to convert temperature from Kelvin to Celsius
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

# Function to get weather data from OpenWeatherMap API
def fetch_weather_data(city):
    url = API_URL.format(city, API_KEY)
    response = requests.get(url)
    data = response.json()
    
    # Extract necessary fields
    weather_main = data['weather'][0]['main']
    temp = kelvin_to_celsius(data['main']['temp'])
    feels_like = kelvin_to_celsius(data['main']['feels_like'])
    timestamp = data['dt']
    
    return {
        'city': city,
        'main': weather_main,
        'temp': temp,
        'feels_like': feels_like,
        'timestamp': timestamp
    }

# Function to roll up daily weather summary
def generate_daily_summary(city, weather_data):
    temps = [entry['temp'] for entry in weather_data]
    main_conditions = [entry['main'] for entry in weather_data]
    
    average_temp = sum(temps) / len(temps)
    max_temp = max(temps)
    min_temp = min(temps)
    
    # Dominant weather condition
    dominant_condition = max(set(main_conditions), key=main_conditions.count)
    
    daily_summary[city] = {
        'average_temp': average_temp,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'dominant_condition': dominant_condition
    }

# Function to check alert threshold
def check_alert(weather_data, city, consecutive_alerts):
    current_temp = weather_data['temp']
    
    # Check if temperature exceeds threshold
    if current_temp > ALERT_THRESHOLD_TEMP:
        consecutive_alerts[city] += 1
        if consecutive_alerts[city] >= ALERT_THRESHOLD_COUNT:
            print(f"ALERT: {city} has exceeded {ALERT_THRESHOLD_TEMP}C for {consecutive_alerts[city]} consecutive readings!")
            # Reset the alert counter
            consecutive_alerts[city] = 0
    else:
        consecutive_alerts[city] = 0

# Main loop to continuously fetch data and process it
def main():
    consecutive_alerts = defaultdict(int)
    
    while True:
        for city in CITIES:
            weather_data = fetch_weather_data(city)
            
            # Append weather data for daily rollup
            date_str = datetime.utcfromtimestamp(weather_data['timestamp']).strftime('%Y-%m-%d')
            daily_weather_data[city].append(weather_data)
            
            # Check and generate daily summary if the day has changed
            if date_str not in daily_summary:
                generate_daily_summary(city, daily_weather_data[city])
                print(f"Daily Summary for {city}: {daily_summary[city]}")
            
            # Check alert thresholds
            check_alert(weather_data, city, consecutive_alerts)
        
        # Wait for the next update (e.g., every 5 minutes)
        time.sleep(5 * 60)

if __name__ == "__main__":
    main()
