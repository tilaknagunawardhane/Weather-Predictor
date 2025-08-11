import pandas as pd
from datetime import datetime
from typing import Dict

class WeatherProcessor:
    @staticmethod
    def process_current_weather(data: Dict) -> Dict:
        """Process current weather data into a standardized format."""
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind'].get('deg', 0),
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'].title(),
            'weather_icon': data['weather'][0]['icon'],
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']),
            'coordinates': {
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon']
            }
        }
    
    @staticmethod
    def process_forecast_data(data: Dict) -> pd.DataFrame:
        """Process forecast data into a pandas format."""
        forecast_list = []

        for item in data['list']:
            forecast_list.append({
                'datetime': datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S'),
                'temperature': round(item['main']['temp'], 1),
                'feels_like': round(item['main']['feels_like'], 1),
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'wind_speed': item['wind']['speed'],
                'weather_main': item['weather'][0]['main'],
                'weather_description': item['weather'][0]['description'].title(),
                'weather_icon': item['weather'][0]['icon'],
                'pop': item.get('pop', 0) * 100  # Probability of precipitation
            })

        return pd.DataFrame(forecast_list)