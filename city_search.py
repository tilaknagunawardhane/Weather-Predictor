import streamlit as st
import requests
from typing import List, Dict
from config import Config

class CitySearchEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/geo/1.0"
    
    @st.cache_data(ttl=Config.GEOCODING_CACHE_DURATION)
    def search_cities(_self, query: str, limit: int = 10) -> List[Dict]:
        """Search for cities using OpenWeatherMap Geocoding API."""
        if not query or len(query) < 2:
            return []
        
        try:
            url = f"{_self.base_url}/direct?q={query}&limit={limit}&appid={_self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            cities = response.json()
            
            # Process and format city data
            formatted_cities = []
            for city in cities:
                city_info = {
                    'name': city['name'],
                    'country': city['country'],
                    'state': city.get('state', ''),
                    'lat': city['lat'],
                    'lon': city['lon'],
                    'display_name': _self._format_city_name(city)
                }
                formatted_cities.append(city_info)
            
            return formatted_cities
        except Exception as e:
            st.error(f"Error searching cities: {str(e)}")
            return []
    
    def _format_city_name(self, city: Dict) -> str:
        """Format city name for display."""
        name = city['name']
        country = city['country']
        state = city.get('state', '')
        
        if state and state != name:
            return f"{name}, {state}, {country}"
        else:
            return f"{name}, {country}"
    
    @st.cache_data(ttl=Config.GEOCODING_CACHE_DURATION)
    def get_popular_cities(_self) -> List[Dict]:
        """Get a list of popular cities worldwide."""
        popular_cities = [
            "London", "New York", "Tokyo", "Paris", "Sydney", "Dubai", 
            "Singapore", "Mumbai", "São Paulo", "Cairo", "Moscow", "Beijing",
            "Los Angeles", "Chicago", "Toronto", "Berlin", "Rome", "Madrid",
            "Amsterdam", "Bangkok", "Seoul", "Mexico City", "Buenos Aires",
            "Johannesburg", "Istanbul", "Hong Kong", "Colombo", "Delhi",
            "Shanghai", "Kuala Lumpur", "Manila", "Jakarta", "Ho Chi Minh City"
        ]
        
        all_cities = []
        for city in popular_cities:
            cities = _self.search_cities(city, 1)
            if cities:
                all_cities.extend(cities)
        
        return all_cities