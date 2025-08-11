import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Optional, Tuple, Dict, List

# Page config
st.set_page_config(
    page_title="Weather Forecast & Predictor",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced custom CSS with modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: transparent;
    }
    
    .weather-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .weather-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.2em;
        font-weight: 700;
        margin: 5px 0;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        font-weight: 500;
    }
    
    .city-suggestion {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 8px 16px;
        margin: 4px;
        border-radius: 25px;
        border: none;
        font-size: 0.9em;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        width: 100%;
        text-align: left;
    }
    
    .city-suggestion:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
    }
    
    .weather-icon-large {
        font-size: 4em;
        text-align: center;
        margin: 10px 0;
    }
    
    .search-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .suggestion-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 8px;
        margin-top: 15px;
    }
    
    .map-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input {
        background-color: #000;
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        font-weight: 500;
        font-size: 16px;
        padding: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
class Config:
    API_KEY = "d79af068"  # Replace with your actual API key
    CACHE_DURATION = 300  # 5 minutes
    GEOCODING_CACHE_DURATION = 3600  # 1 hour for city suggestions
    
    @staticmethod
    def test_api_key():
        """Test if the API key is working."""
        try:
            test_url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={Config.API_KEY}&units=metric"
            response = requests.get(test_url, timeout=5)
            return response.status_code == 200
        except:
            return False

# City search and suggestions
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

# Weather API handler
class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    @st.cache_data(ttl=Config.CACHE_DURATION)
    def get_current_weather(_self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch current weather data using coordinates."""
        try:
            url = f"{_self.base_url}/weather?lat={lat}&lon={lon}&appid={_self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('cod') != 200:
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
            
            if data.get('cod') != '200':
                return None
                
            return data
        except Exception as e:
            st.error(f"Error fetching forecast: {str(e)}")
            return None

# Weather data processor
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
        """Process forecast data into a pandas DataFrame."""
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

# Prediction model
class WeatherPredictor:
    @staticmethod
    def predict_temperature_trend(temperatures: List[float], hours_ahead: int = 24) -> Tuple[List[float], float]:
        """Predict temperature trend using linear regression."""
        if len(temperatures) < 3:
            return [], 0.0
        
        try:
            X = np.arange(len(temperatures)).reshape(-1, 1)
            y = np.array(temperatures)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future temperatures
            future_X = np.arange(len(temperatures), len(temperatures) + hours_ahead).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # Calculate confidence score based on R²
            confidence = model.score(X, y)
            
            return predictions.tolist(), confidence
        except Exception:
            return [], 0.0
    
    @staticmethod
    def analyze_weather_patterns(df: pd.DataFrame) -> Dict:
        """Analyze weather patterns from forecast data."""
        analysis = {}
        
        # Temperature analysis
        analysis['temp_trend'] = 'stable'
        temp_diff = df['temperature'].iloc[-1] - df['temperature'].iloc[0]
        if temp_diff > 2:
            analysis['temp_trend'] = 'warming'
        elif temp_diff < -2:
            analysis['temp_trend'] = 'cooling'
        
        # Rain probability
        analysis['rain_likelihood'] = df['pop'].mean()
        analysis['max_rain_prob'] = df['pop'].max()
        
        # Weather diversity
        analysis['weather_types'] = df['weather_main'].nunique()
        analysis['dominant_weather'] = df['weather_main'].mode().iloc[0]
        
        return analysis

# Interactive map component
class WeatherMap:
    @staticmethod
    def create_world_map(cities_data: List[Dict]) -> go.Figure:
        """Create an interactive world map with weather data."""
        if not cities_data:
            return go.Figure()
        
        fig = go.Figure()
        
        # Add city markers
        lats = [city['coordinates']['lat'] for city in cities_data]
        lons = [city['coordinates']['lon'] for city in cities_data]
        names = [f"{city['city']}, {city['country']}" for city in cities_data]
        temps = [city['temperature'] for city in cities_data]
        
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=dict(
                size=[max(10, min(30, temp + 20)) for temp in temps],  # Size based on temperature
                color=temps,
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Temperature (°C)")
            ),
            text=names,
            hovertemplate="<b>%{text}</b><br>Temperature: %{marker.color}°C<extra></extra>",
            showlegend=False
        ))
        
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=20, lon=0),
                zoom=1.5
            ),
            height=500,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        return fig

# UI Components
class WeatherUI:
    @staticmethod
    def display_city_search(search_engine: CitySearchEngine, key_suffix: str = "") -> Optional[Dict]:
        """Display city search interface with suggestions."""
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Search input
        col1, col2 = st.columns([4, 1])
        with col1:
            search_query = st.text_input(
                "🔍 Search for any city worldwide:",
                placeholder="Type city name (e.g., Colombo, New York, Tokyo...)",
                key=f"city_search_{key_suffix}",
                help="Search for any city in the world - start typing to see suggestions"
            )
        
        selected_city = None
        
        # Show search results
        if search_query and len(search_query) >= 2:
            try:
                with st.spinner("Searching cities..."):
                    cities = search_engine.search_cities(search_query, 8)
                
                if cities:
                    st.markdown("**🌍 Found Cities:**")
                    st.write(f"Found {len(cities)} cities matching '{search_query}'")
                    
                    # Display suggestions in a grid
                    cols = st.columns(2)
                    for i, city in enumerate(cities):
                        with cols[i % 2]:
                            # Create a unique button key
                            button_key = f"city_btn_{key_suffix}_{i}_{city['name']}_{city['country']}"
                            
                            if st.button(
                                f"📍 {city['display_name']}", 
                                key=button_key,
                                help=f"Coordinates: {city['lat']:.2f}, {city['lon']:.2f}",
                                use_container_width=True
                            ):
                                selected_city = city
                                # st.balloons()  # Fun animation when city is selected
                                return selected_city  # Return immediately when clicked
                else:
                    st.warning("🚫 No cities found. Try a different search term.")
                    st.info("💡 **Tips:** Try searching with just the city name (e.g., 'Colombo' instead of 'Colombo, Sri Lanka')")
            
            except Exception as e:
                st.error(f"❌ Error searching cities: {str(e)}")
                st.info("This might be due to API connectivity issues. Please try again.")
        
        # Show popular cities when no search
        elif not search_query:
            with st.expander("🌟 Popular Cities Worldwide", expanded=False):
                st.write("Click on any city below to get started:")
                try:
                    popular_cities = search_engine.get_popular_cities()
                    if popular_cities:
                        cols = st.columns(3)
                        for i, city in enumerate(popular_cities[:15]):  # Show first 15
                            with cols[i % 3]:
                                button_key = f"popular_city_{key_suffix}_{i}_{city['name']}"
                                if st.button(
                                    f"🏙️ {city['display_name']}", 
                                    key=button_key,
                                    use_container_width=True
                                ):
                                    selected_city = city
                                    st.balloons()
                                    return selected_city
                    else:
                        st.info("Popular cities list is loading... Please try searching for a specific city.")
                except Exception as e:
                    st.warning("Unable to load popular cities. Please search for a specific city.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return selected_city
    
    @staticmethod
    def display_current_weather(weather_data: Dict):
        """Display current weather information."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        
        # Header with city name and weather icon
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"## 🌍 {weather_data['city']}, {weather_data['country']}")
            st.markdown(f"**{weather_data['weather_description']}**")
        
        with col2:
            st.markdown(f'<div class="weather-icon-large">🌤️</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"### {weather_data['temperature']}°C")
            st.markdown(f"Feels like **{weather_data['feels_like']}°C**")
        
        # Metrics grid
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("💧", "Humidity", f"{weather_data['humidity']}%"),
            ("💨", "Wind Speed", f"{weather_data['wind_speed']} m/s"),
            ("🔽", "Pressure", f"{weather_data['pressure']} hPa"),
            ("👁️", "Visibility", f"{weather_data['visibility']:.1f} km")
        ]
        
        for i, (icon, label, value) in enumerate(metrics):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div class="metric-container">
                    <div style="font-size: 2em;">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Sun times
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"🌅 **Sunrise:** {weather_data['sunrise'].strftime('%H:%M')}")
        with col2:
            st.markdown(f"🌇 **Sunset:** {weather_data['sunset'].strftime('%H:%M')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def display_forecast_chart(df: pd.DataFrame, city: str):
        """Display interactive forecast chart."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader(f"📈 5-Day Forecast for {city}")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["🌡️ Temperature", "💧 Humidity & Rain", "💨 Wind"])
        
        with tab1:
            fig = go.Figure()
            
            # Temperature line
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['temperature'],
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#667eea', width=3),
                marker=dict(size=6)
            ))
            
            # Feels like line
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['feels_like'],
                mode='lines',
                name='Feels Like',
                line=dict(color='#764ba2', width=2, dash='dash'),
                opacity=0.7
            ))
            
            fig.update_layout(
                title="Temperature Forecast",
                xaxis_title="Date & Time",
                yaxis_title="Temperature (°C)",
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = go.Figure()
            
            # Humidity
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['humidity'],
                mode='lines+markers',
                name='Humidity (%)',
                yaxis='y',
                line=dict(color='#36A2EB', width=2)
            ))
            
            # Rain probability
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['pop'],
                mode='lines+markers',
                name='Rain Probability (%)',
                yaxis='y2',
                line=dict(color='#FF6384', width=2)
            ))
            
            fig.update_layout(
                title="Humidity & Rain Probability",
                xaxis_title="Date & Time",
                yaxis=dict(title="Humidity (%)", side='left'),
                yaxis2=dict(title="Rain Probability (%)", side='right', overlaying='y'),
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = px.line(df, x='datetime', y='wind_speed',
                         title='Wind Speed Forecast',
                         labels={'datetime': 'Date & Time', 'wind_speed': 'Wind Speed (m/s)'},
                         color_discrete_sequence=['#4BC0C0'])
            
            fig.update_layout(
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def display_weather_insights(analysis: Dict, city: str):
        """Display weather insights and patterns."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader(f"🔍 Weather Insights for {city}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trend_emoji = {"warming": "🔥", "cooling": "❄️", "stable": "➡️"}[analysis['temp_trend']]
            st.metric("Temperature Trend", analysis['temp_trend'].title(), delta=trend_emoji)
        
        with col2:
            st.metric("Average Rain Chance", f"{analysis['rain_likelihood']:.1f}%", 
                     delta=f"Max: {analysis['max_rain_prob']:.1f}%")
        
        with col3:
            st.metric("Dominant Weather", analysis['dominant_weather'], 
                     delta=f"{analysis['weather_types']} types")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main application class
class WeatherApp:
    def __init__(self):
        self.search_engine = CitySearchEngine(Config.API_KEY)
        self.weather_api = WeatherAPI(Config.API_KEY)
        self.processor = WeatherProcessor()
        self.predictor = WeatherPredictor()
        self.ui = WeatherUI()
        self.weather_map = WeatherMap()
        
        # Initialize session state
        if 'main_city_data' not in st.session_state:
            st.session_state.main_city_data = None
        if 'comparison_cities_data' not in st.session_state:
            st.session_state.comparison_cities_data = []
    
    def run(self):
        """Main application runner."""
        st.markdown("# 🌦️ Advanced Weather Forecast & Predictor")
        st.markdown("🌍 **Search for any city worldwide and get comprehensive weather information with AI-powered predictions**")
        
        # Test API key first
        if not Config.test_api_key():
            st.error("🔑 **API Key Issue:** Cannot connect to OpenWeatherMap API")
            st.warning("Please check if your API key is valid and active.")
            st.info("**Get your free API key:** https://openweathermap.org/api")
            st.info("**Note:** New API keys can take up to 2 hours to activate")
            return
        else:
            st.success("✅ API connection successful")
        
        # Main city selection
        st.markdown("## 📍 Select Main Location")
        selected_main_city = self.ui.display_city_search(self.search_engine, "main")
        
        if selected_main_city:
            st.session_state.main_city_data = selected_main_city
            st.success(f"🎯 Selected: {selected_main_city['display_name']}")
            st.rerun()
        
        # Display main weather if city is selected
        if st.session_state.main_city_data:
            self.display_main_weather()
        else:
            st.info("👆 Please search and select a city above to see weather information")
        
        # Comparison section
        st.markdown("---")
        st.markdown("## ⚖️ Compare Multiple Cities")
        
        selected_comparison_city = self.ui.display_city_search(self.search_engine, "comparison")
        
        if selected_comparison_city:
            # Check if city is already in comparison list
            city_exists = any(
                city['name'] == selected_comparison_city['name'] and 
                city['country'] == selected_comparison_city['country']
                for city in st.session_state.comparison_cities_data
            )
            
            if not city_exists:
                st.session_state.comparison_cities_data.append(selected_comparison_city)
                st.success(f"✅ Added {selected_comparison_city['display_name']} to comparison!")
                time.sleep(1)  # Brief pause to show success message
                st.rerun()
            else:
                st.warning("⚠️ This city is already in your comparison list!")
        
        # Display comparison
        if st.session_state.comparison_cities_data:
            self.display_comparison_section()
        
        # Clear all button
        if st.session_state.main_city_data or st.session_state.comparison_cities_data:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear All Data", type="secondary"):
                    st.session_state.main_city_data = None
                    st.session_state.comparison_cities_data = []
                    st.success("🧹 All data cleared!")
                    st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("**🌐 Data provided by OpenWeatherMap** | Built with ❤️ using Streamlit")
    
    def display_main_weather(self):
        """Display main city weather information."""
        city_data = st.session_state.main_city_data
        
        # Debug information
        st.write(f"🔍 **Debug:** Selected city data: {city_data}")
        
        try:
            # Fetch weather data
            with st.spinner(f"🌤️ Fetching weather data for {city_data['display_name']}..."):
                current_data = self.weather_api.get_current_weather(city_data['lat'], city_data['lon'])
                forecast_data = self.weather_api.get_forecast(city_data['lat'], city_data['lon'])
            
            # Debug API responses
            if current_data:
                st.success("✅ Current weather data received")
            else:
                st.error("❌ Failed to get current weather data")
                st.write("This might be due to:")
                st.write("- Invalid API key")
                st.write("- API rate limit exceeded")
                st.write("- Network connectivity issues")
                return
            
            if forecast_data:
                st.success("✅ Forecast data received")
            else:
                st.error("❌ Failed to get forecast data")
                return
            
            # Process data
            current_weather = self.processor.process_current_weather(current_data)
            forecast_df = self.processor.process_forecast_data(forecast_data)
            weather_analysis = self.predictor.analyze_weather_patterns(forecast_df)
            
            # Display components
            self.ui.display_current_weather(current_weather)
            self.ui.display_forecast_chart(forecast_df, current_weather['city'])
            self.ui.display_weather_insights(weather_analysis, current_weather['city'])
            
            # Temperature prediction
            self.display_temperature_prediction(forecast_df, current_weather['city'])
            
        except Exception as e:
            st.error(f"❌ Error displaying weather data: {str(e)}")
            st.write("**Error details:**")
            st.write(f"- City: {city_data.get('display_name', 'Unknown')}")
            st.write(f"- Coordinates: {city_data.get('lat', 'Unknown')}, {city_data.get('lon', 'Unknown')}")
            st.write(f"- Error: {str(e)}")
            
            # Fallback: Try with city name instead of coordinates
            st.write("🔄 **Trying alternative method...**")
            try:
                current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_data['name']}&appid={Config.API_KEY}&units=metric"
                response = requests.get(current_url, timeout=10)
                if response.status_code == 200:
                    st.success("✅ Alternative method worked!")
                    current_data = response.json()
                    current_weather = self.processor.process_current_weather(current_data)
                    self.ui.display_current_weather(current_weather)
                else:
                    st.error(f"❌ Alternative method failed with status code: {response.status_code}")
                    if response.status_code == 401:
                        st.error("🔑 **API Key Issue:** Please check if your OpenWeatherMap API key is valid")
                        st.write("Get your free API key at: https://openweathermap.org/api")
                    elif response.status_code == 429:
                        st.error("⚠️ **Rate Limit:** Too many API requests. Please wait a moment.")
            except Exception as fallback_error:
                st.error(f"❌ Fallback method also failed: {str(fallback_error)}")
                
                # Show API key status
                st.write("**🔧 Troubleshooting Steps:**")
                st.write("1. **Check API Key:** Make sure your OpenWeatherMap API key is valid")
                st.write("2. **Wait for Activation:** New API keys can take up to 2 hours to activate")
                st.write("3. **Check Internet:** Ensure you have a stable internet connection")
                st.write("4. **Try Later:** If rate limited, wait a few minutes and try again")
    
    def display_temperature_prediction(self, df: pd.DataFrame, city: str):
        """Display temperature prediction."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader(f"🔮 AI Temperature Prediction for {city}")
        
        temperatures = df['temperature'].head(12).tolist()  # Use first 12 hours
        predictions, confidence = self.predictor.predict_temperature_trend(temperatures, 8)
        
        if predictions:
            # Create prediction chart
            last_datetime = df['datetime'].iloc[11]
            prediction_times = [last_datetime + timedelta(hours=i+3) for i in range(8)]
            
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=df['datetime'].head(12),
                y=temperatures,
                mode='lines+markers',
                name='Actual Temperature',
                line=dict(color='#667eea', width=3)
            ))
            
            # Predictions
            fig.add_trace(go.Scatter(
                x=prediction_times,
                y=predictions,
                mode='lines+markers',
                name='Predicted Temperature',
                line=dict(color='#FF6384', width=3, dash='dash'),
                marker=dict(symbol='star', size=8)
            ))
            
            fig.update_layout(
                title=f"Temperature Prediction (Confidence: {confidence:.1%})",
                xaxis_title="Date & Time",
                yaxis_title="Temperature (°C)",
                template='plotly_white',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Confidence indicator
            if confidence > 0.8:
                st.success(f"🎯 High confidence prediction ({confidence:.1%})")
            elif confidence > 0.6:
                st.warning(f"⚠️ Moderate confidence prediction ({confidence:.1%})")
            else:
                st.info(f"ℹ️ Low confidence prediction ({confidence:.1%}) - Weather patterns may be unpredictable")
        else:
            st.error("Unable to generate temperature predictions")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_comparison_section(self):
        """Display city comparison section."""
        st.markdown("### 📊 Weather Comparison")
        
        # Current comparison cities
        if st.session_state.comparison_cities_data:
            st.markdown(f"**Comparing {len(st.session_state.comparison_cities_data)} cities:**")
            
            # Display city chips with remove buttons
            cols = st.columns(min(4, len(st.session_state.comparison_cities_data)))
            for i, city in enumerate(st.session_state.comparison_cities_data):
                with cols[i % len(cols)]:
                    st.markdown(f"**🏙️ {city['display_name']}**")
                    if st.button(f"❌ Remove", key=f"remove_comp_{i}"):
                        st.session_state.comparison_cities_data.pop(i)
                        st.rerun()
            
            # Fetch weather data for all comparison cities
            comparison_weather_data = []
            
            with st.spinner("🌍 Fetching weather data for comparison cities..."):
                for city in st.session_state.comparison_cities_data:
                    current_data = self.weather_api.get_current_weather(city['lat'], city['lon'])
                    if current_data:
                        weather_data = self.processor.process_current_weather(current_data)
                        comparison_weather_data.append(weather_data)
            
            if comparison_weather_data:
                # Include main city in comparison if available
                all_weather_data = comparison_weather_data.copy()
                if st.session_state.main_city_data:
                    main_current = self.weather_api.get_current_weather(
                        st.session_state.main_city_data['lat'], 
                        st.session_state.main_city_data['lon']
                    )
                    if main_current:
                        main_weather = self.processor.process_current_weather(main_current)
                        main_weather['city'] += " (Main)"  # Mark as main city
                        all_weather_data.insert(0, main_weather)
                
                # Display comparison table
                self.display_comparison_table(all_weather_data)
                
                # Display comparison charts
                self.display_comparison_charts(all_weather_data)
                
                # Display interactive map
                self.display_comparison_map(all_weather_data)
    
    def display_comparison_table(self, weather_data_list: List[Dict]):
        """Display comparison table."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader("📋 Detailed Comparison")
        
        # Create comparison DataFrame
        comparison_data = []
        for data in weather_data_list:
            comparison_data.append({
                'City': data['city'],
                'Country': data['country'],
                'Temperature (°C)': data['temperature'],
                'Feels Like (°C)': data['feels_like'],
                'Humidity (%)': data['humidity'],
                'Wind Speed (m/s)': data['wind_speed'],
                'Pressure (hPa)': data['pressure'],
                'Visibility (km)': data['visibility'],
                'Weather': data['weather_description']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Style the dataframe
        styled_df = comparison_df.style.background_gradient(
            cmap='RdYlBu_r', 
            subset=['Temperature (°C)', 'Feels Like (°C)']
        ).background_gradient(
            cmap='Blues', 
            subset=['Humidity (%)']
        ).background_gradient(
            cmap='Greens', 
            subset=['Wind Speed (m/s)']
        ).format({
            'Temperature (°C)': '{:.1f}',
            'Feels Like (°C)': '{:.1f}',
            'Wind Speed (m/s)': '{:.1f}',
            'Pressure (hPa)': '{:.0f}',
            'Visibility (km)': '{:.1f}'
        })
        
        st.dataframe(styled_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_comparison_charts(self, weather_data_list: List[Dict]):
        """Display comparison charts."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader("📈 Comparison Charts")
        
        # Create DataFrame for charts
        chart_data = []
        for data in weather_data_list:
            chart_data.append({
                'City': data['city'],
                'Temperature': data['temperature'],
                'Humidity': data['humidity'],
                'Wind Speed': data['wind_speed'],
                'Pressure': data['pressure']
            })
        
        chart_df = pd.DataFrame(chart_data)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature", "💧 Humidity", "💨 Wind Speed", "🔽 Pressure"])
        
        with tab1:
            fig = px.bar(chart_df, x='City', y='Temperature',
                        color='Temperature',
                        color_continuous_scale='RdYlBu_r',
                        title='Temperature Comparison (°C)')
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.bar(chart_df, x='City', y='Humidity',
                        color='Humidity',
                        color_continuous_scale='Blues',
                        title='Humidity Comparison (%)')
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = px.bar(chart_df, x='City', y='Wind Speed',
                        color='Wind Speed',
                        color_continuous_scale='Greens',
                        title='Wind Speed Comparison (m/s)')
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            fig = px.bar(chart_df, x='City', y='Pressure',
                        color='Pressure',
                        color_continuous_scale='Viridis',
                        title='Pressure Comparison (hPa)')
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_comparison_map(self, weather_data_list: List[Dict]):
        """Display interactive comparison map."""
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.subheader("🗺️ Interactive Weather Map")
        
        # Create and display the map
        map_fig = self.weather_map.create_world_map(weather_data_list)
        st.plotly_chart(map_fig, use_container_width=True)
        
        st.markdown("**Map Legend:** Marker size and color represent temperature. Hover over markers for details.")
        st.markdown('</div>', unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    app = WeatherApp()
    app.run()