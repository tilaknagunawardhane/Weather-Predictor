import streamlit as st
import requests
from typing import Optional, Dict
from config import Config

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"

    @st.cache_data(ttl=Config.CACHE_DURATION)
    def get_current_weather(_self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch current weather data for given latitude and longitude."""
        try:
            url = f"{_self.base_url}/weather?lat={lat}&lon={lon}&appid={_self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") != 200:
                st.error(f"Error fetching weather data: {data.get('message', 'Unknown error')}")
                return None
            return data
        except Exception as e:
            st.error(f"Error fetching current weather: {str(e)}")
            return None
        
    @st.cache_data(ttl=Config.CACHE_DURATION)
    def get_forecast(_self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch 5-day weather forecast using coordinates."""
        try:
            url = f"{_self.base_url}/forecast?lat={lat}&lon={lon}&appid={_self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") != "200":
                st.error(f"Error fetching forecast data: {data.get('message', 'Unknown error')}")
                return None
            return data
        except Exception as e:
            st.error(f"Error fetching weather forecast: {str(e)}")
            return None