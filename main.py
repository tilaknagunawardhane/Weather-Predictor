import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict
from streamlit_folium import folium_static

# Import custom modules
from config import Config
from styles import load_css
from city_search import CitySearchEngine
from weather_api import WeatherAPI
from data_processor import WeatherProcessor
from predictor import WeatherPredictor
from weather_map import WeatherMap
from ui_components import WeatherUI

# Page config
st.set_page_config(
    page_title="Weather Forecast & Predictor",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        # Load CSS styles
        load_css()
        
        st.markdown("# Advanced Weather Forecast & Predictor")
        st.markdown(" **Search for any city worldwide and get comprehensive weather information with AI-powered predictions**")
        
        # Test API key first
        if not Config.test_api_key():
            st.error("🔑 **API Key Issue:** Cannot connect to OpenWeatherMap API")
            st.warning("Please check if your API key is valid and active.")
            st.info("**Get your free API key:** https://openweathermap.org/api")
            st.info("**Note:** New API keys can take up to 2 hours to activate")
            return
        # else:
        #     st.success("✅ API connection successful")
        
        # Main city selection
        st.markdown("## 📍 Select Main Location")
        selected_main_city = self.ui.display_city_search(self.search_engine, "main")
        
        if selected_main_city:
            st.session_state.main_city_data = selected_main_city
            st.success(f"🎯 Selected: {selected_main_city['display_name']}")
            st.rerun()
        
        # Display main weather if city is selected
        if st.session_state.main_city_data:
            # Display city location map at the top
            self.display_city_location_map()
            # Display weather information
            self.display_main_weather()
        else:
            st.info(" Please search and select a city above to see weather information")
        
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
    
    def display_city_location_map(self):
        """Display a map showing the selected city location at the top."""
        city_data = st.session_state.main_city_data
        
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader(f"📍 Location Map - {city_data['display_name']}")
        
        # Create and display the city location map
        city_map = self.weather_map.create_city_location_map(city_data)
        folium_static(city_map, width=800, height=400)
        
        st.markdown("**Map Features:** Zoom in/out, pan around, and explore the area around your selected city.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_main_weather(self):
        """Display main city weather information."""
        city_data = st.session_state.main_city_data
        
        # Debug information
        # st.write(f"🔍 **Debug:** Selected city data: {city_data}")
        
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
                
                # Display interactive maps
                self.display_comparison_maps(all_weather_data)
    
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
        
        # Create and display the enhanced Folium map
        world_map = self.weather_map.create_world_map(weather_data_list)
        folium_static(world_map, width=800, height=600)
        
        st.markdown("**Map Features:** Multiple tile themes, zoom in/out, pan, fullscreen, minimap, and measurement tools.")
        st.markdown("**Legend:** Marker colors represent temperature ranges (Blue: Cold, Yellow: Mild, Red: Hot)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_comparison_maps(self, weather_data_list: List[Dict]):
        """Display multiple types of comparison maps."""
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader("🗺️ Interactive Weather Maps")
        
        # Create tabs for different map types
        map_tab1, map_tab2 = st.tabs(["🌡️ Temperature Map", "☁️ Weather Summary Map"])
        
        with map_tab1:
            st.markdown("**Temperature-based weather map with interactive features:**")
            # Create and display the enhanced Folium temperature map
            world_map = self.weather_map.create_world_map(weather_data_list)
            folium_static(world_map, width=800, height=600)
            st.markdown("**Features:** Multiple tile themes, zoom in/out, pan, fullscreen, minimap, and measurement tools.")
            st.markdown("**Legend:** Marker colors represent temperature ranges (Blue: Cold, Yellow: Mild, Red: Hot)")
        
        with map_tab2:
            st.markdown("**Weather condition summary map:**")
            # Create and display the weather summary map
            summary_map = self.weather_map.create_weather_summary_map(weather_data_list)
            folium_static(summary_map, width=800, height=500)
            st.markdown("**Features:** Weather condition clustering, color-coded markers, and interactive popups.")
            st.markdown("**Legend:** Different colors represent different weather conditions across cities.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    app = WeatherApp()
    app.run()