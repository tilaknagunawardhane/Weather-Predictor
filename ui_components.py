import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from typing import Optional, Dict, List
from city_search import CitySearchEngine

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
                                st.balloons()  # Fun animation when city is selected
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