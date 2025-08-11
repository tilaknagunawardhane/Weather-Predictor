import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Always fetch API key from environment
    API_KEY = os.getenv("WEATHER_API_KEY")
    CACHE_DURATION = 300 # 5 mins
    GEOCODING_CACHE_DURATION = 3600  # 1 hour for city suggestions

    @staticmethod
    def test_api_key():
        """Test if the API key is valid."""
        try:
            test_url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={Config.API_KEY}&units=metric"
            response = requests.get(test_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False