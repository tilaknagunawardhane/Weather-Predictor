import folium
import streamlit as st
from streamlit_folium import folium_static
from typing import List, Dict
import branca.colormap as cm
import xyzservices.providers as xyz

class WeatherMap:
    def __init__(self):
        """Initialize the WeatherMap class."""
        # Weather icon mapping
        self.weather_icons = {
            'clear': '☀️',
            'clouds': '☁️',
            'rain': '🌧️',
            'drizzle': '🌦️',
            'thunderstorm': '⛈️',
            'snow': '❄️',
            'mist': '🌫️',
            'fog': '🌫️',
            'haze': '🌫️',
            'smoke': '🌫️',
            'dust': '🌫️',
            'sand': '🌫️',
            'ash': '🌫️',
            'squall': '💨',
            'tornado': '🌪️'
        }
    
    def get_weather_icon(self, weather_main: str) -> str:
        """Get weather icon based on weather condition."""
        weather_lower = weather_main.lower()
        for key, icon in self.weather_icons.items():
            if key in weather_lower:
                return icon
        return '🌤️'  # Default icon
    
    def create_city_location_map(self, city_data: Dict) -> folium.Map:
        """Create a map showing the selected city location at the top."""
        # Handle both data structures (from search and from weather API)
        if not city_data:
            # Create a default world map
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=400
            )
        
        # Extract coordinates from either structure
        if 'coordinates' in city_data:
            lat = city_data['coordinates']['lat']
            lon = city_data['coordinates']['lon']
        elif 'lat' in city_data and 'lon' in city_data:
            lat = city_data['lat']
            lon = city_data['lon']
        else:
            # Create a default world map if no coordinates
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=400
            )
        
        city_name = city_data.get('display_name', city_data.get('city', 'Unknown City'))
        
        # Create a centered map on the selected city
        city_map = folium.Map(
            location=[lat, lon],
            zoom_start=10,
            tiles=xyz.OpenStreetMap.Mapnik,
            width=800,
            height=400,
            prefer_canvas=True
        )
        
        # Add a marker for the selected city with weather icon if available
        weather_icon = "📍"
        if 'weather_main' in city_data:
            weather_icon = self.get_weather_icon(city_data['weather_main'])
        
        # Create custom popup with weather info
        popup_content = f"""
        <div style="width: 250px; text-align: center;">
            <h3 style="margin: 0; color: #2c3e50; font-family: Arial, sans-serif;">{city_name}</h3>
            <div style="font-size: 48px; margin: 10px 0;">{weather_icon}</div>
            <p style="margin: 5px 0; color: #7f8c8d; font-family: Arial, sans-serif;">
                <b>📍 Selected Location</b>
            </p>
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color='red', icon='info-sign'),
            tooltip=f"{city_name} - Selected Location"
        ).add_to(city_map)
        
        # Add a circle around the city to show the area
        folium.Circle(
            location=[lat, lon],
            radius=5000,  # 5km radius
            color='#d7191c',
            fill=True,
            fill_color='#d7191c',
            fill_opacity=0.2,
            weight=2
        ).add_to(city_map)
        
        # Add tile layer options for better map experience (using xyzservices providers)
        folium.TileLayer(
            tiles=xyz.CartoDB.Positron,
            name='Light Theme',
            overlay=False,
            control=True
        ).add_to(city_map)
        
        folium.TileLayer(
            tiles=xyz.Esri.WorldTopoMap,
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(city_map)
        
        # Add layer control
        folium.LayerControl().add_to(city_map)
        
        return city_map
    
    def create_world_map(self, cities_data: List[Dict]) -> folium.Map:
        """Create an interactive world map with weather data using Folium."""
        if not cities_data:
            # Create a default world map
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=600
            )
        
        try:
            # Calculate center of all cities
            lats = []
            lons = []
            valid_cities = []
            
            for city in cities_data:
                # Handle both data structures
                lat = None
                lon = None
                
                if 'coordinates' in city:
                    lat = city['coordinates']['lat']
                    lon = city['coordinates']['lon']
                elif 'lat' in city and 'lon' in city:
                    lat = city['lat']
                    lon = city['lon']
                
                if lat is not None and lon is not None and 'temperature' in city:
                    lats.append(lat)
                    lons.append(lon)
                    valid_cities.append(city)
            
            if not valid_cities:
                return folium.Map(
                    location=[20, 0],
                    zoom_start=2,
                    tiles=xyz.OpenStreetMap.Mapnik,
                    width=800,
                    height=600
                )
            
            # Calculate center and zoom level
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            # Determine zoom level based on number of cities
            if len(valid_cities) == 1:
                zoom_start = 8
            elif len(valid_cities) <= 3:
                zoom_start = 4
            else:
                zoom_start = 2
            
            # Create the base map with multiple tile options
            world_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_start,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=600,
                prefer_canvas=True
            )
            
            # Add tile layer options (xyzservices providers handle attribution)
            folium.TileLayer(
                tiles=xyz.CartoDB.Positron,
                name='Light Theme',
                overlay=False,
                control=True
            ).add_to(world_map)
            
            folium.TileLayer(
                tiles=xyz.CartoDB.DarkMatter,
                name='Dark Theme',
                overlay=False,
                control=True
            ).add_to(world_map)
            
            folium.TileLayer(
                tiles=xyz.Esri.WorldTopoMap,
                name='Terrain',
                overlay=False,
                control=True
            ).add_to(world_map)
            
            # Create temperature color map
            temps = [city['temperature'] for city in valid_cities]
            min_temp = min(temps)
            max_temp = max(temps)
            
            # Create a colormap for temperature
            if min_temp != max_temp:
                temp_colormap = cm.LinearColormap(
                    colors=['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c'],
                    vmin=min_temp,
                    vmax=max_temp,
                    caption='Temperature (°C)'
                )
            else:
                temp_colormap = cm.LinearColormap(
                    colors=['#2c7bb6', '#d7191c'],
                    vmin=min_temp - 5,
                    vmax=max_temp + 5,
                    caption='Temperature (°C)'
                )
            
            # Add temperature legend
            temp_colormap.add_to(world_map)
            
            # Add markers for each city
            for city in valid_cities:
                # Extract coordinates from either structure
                if 'coordinates' in city:
                    lat = city['coordinates']['lat']
                    lon = city['coordinates']['lon']
                else:
                    lat = city['lat']
                    lon = city['lon']
                
                city_name = city.get('display_name', city.get('city', 'Unknown City'))
                country = city.get('country', 'Unknown Country')
                temp = city['temperature']
                humidity = city.get('humidity', 'N/A')
                wind_speed = city.get('wind_speed', 'N/A')
                weather_desc = city.get('weather_description', 'N/A')
                
                # Determine marker color based on temperature (hex colors for reliability)
                if temp <= 0:
                    marker_color = '#2c7bb6'
                elif temp <= 10:
                    marker_color = '#abd9e9'
                elif temp <= 20:
                    marker_color = '#ffffbf'
                elif temp <= 30:
                    marker_color = '#fdae61'
                else:
                    marker_color = '#d7191c'
                
                # Determine marker size based on temperature (larger for more extreme temps)
                marker_size = max(8, min(20, int(abs(temp)) + 8))
                
                # Get weather icon
                weather_icon = self.get_weather_icon(weather_desc)
                
                # Create enhanced popup content
                popup_content = f"""
                <div style="width: 220px; text-align: center;">
                    <div style="font-size: 36px; margin: 5px 0;">{weather_icon}</div>
                    <h4 style="margin: 0; color: #2c3e50; font-family: Arial, sans-serif;">{city_name}</h4>
                    <p style="margin: 5px 0; color: #7f8c8d; font-family: Arial, sans-serif;">{country}</p>
                    <hr style="margin: 10px 0;">
                    <p style="margin: 5px 0;"><b>🌡️ Temperature:</b> {temp}°C</p>
                    <p style="margin: 5px 0;"><b>💧 Humidity:</b> {humidity}%</p>
                    <p style="margin: 5px 0;"><b>💨 Wind:</b> {wind_speed} m/s</p>
                    <p style="margin: 5px 0;"><b>☁️ Weather:</b> {weather_desc}</p>
                </div>
                """
                
                # Add marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=marker_size,
                    popup=folium.Popup(popup_content, max_width=250),
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.8,
                    weight=2,
                    tooltip=f"{city_name}: {temp}°C"
                ).add_to(world_map)
            
            # Add layer control
            folium.LayerControl().add_to(world_map)
            
            # Add fullscreen option
            folium.plugins.Fullscreen(
                position='topright',
                title='Expand me',
                title_cancel='Exit me',
                force_separate_button=True
            ).add_to(world_map)
            
            # Add minimap (use plain OpenStreetMap string to avoid provider issues)
            minimap = folium.plugins.MiniMap(
                tile_layer='OpenStreetMap',
                position='bottomright',
                width=150,
                height=150,
                collapsed_width=25,
                collapsed_height=25
            )
            world_map.add_child(minimap)
            
            # Add measure tool
            folium.plugins.MeasureControl(
                position='topleft',
                primary_length_unit='kilometers',
                secondary_length_unit='miles',
                primary_area_unit='sqkilometers',
                secondary_area_unit='acres'
            ).add_to(world_map)
            
            return world_map
            
        except Exception as e:
            st.error(f"Error creating enhanced map: {str(e)}")
            # Return a basic fallback map
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=600
            )
    
    def create_weather_summary_map(self, cities_data: List[Dict]) -> folium.Map:
        """Create a summary map showing weather conditions across cities."""
        if not cities_data:
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=500
            )
        
        try:
            # Calculate center
            lats = []
            lons = []
            valid_cities = []
            
            for city in cities_data:
                if 'coordinates' in city:
                    lats.append(city['coordinates']['lat'])
                    lons.append(city['coordinates']['lon'])
                    valid_cities.append(city)
                elif 'lat' in city and 'lon' in city:
                    lats.append(city['lat'])
                    lons.append(city['lon'])
                    valid_cities.append(city)
            
            if not valid_cities:
                return folium.Map(
                    location=[20, 0],
                    zoom_start=2,
                    tiles=xyz.OpenStreetMap.Mapnik,
                    width=800,
                    height=500
                )
            
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            # Create summary map
            summary_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=3,
                tiles=xyz.CartoDB.Positron,
                width=800,
                height=500
            )
            
            # Add weather condition clusters
            weather_conditions = {}
            for city in valid_cities:
                weather = city.get('weather_main', 'Unknown')
                if weather not in weather_conditions:
                    weather_conditions[weather] = []
                weather_conditions[weather].append(city)
            
            # Add markers for each weather condition
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple']
            color_index = 0
            
            for weather, cities in weather_conditions.items():
                if color_index >= len(colors):
                    color_index = 0
                
                for city in cities:
                    if 'coordinates' in city:
                        lat = city['coordinates']['lat']
                        lon = city['coordinates']['lon']
                    else:
                        lat = city['lat']
                        lon = city['lon']
                    
                    city_name = city.get('display_name', city.get('city', 'Unknown City'))
                    temp = city.get('temperature', 'N/A')
                    icon = self.get_weather_icon(weather)
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"<b>{city_name}</b><br>{icon} {weather}<br>🌡️ {temp}°C",
                        icon=folium.Icon(color=colors[color_index], icon='cloud'),
                        tooltip=f"{city_name}: {weather}"
                    ).add_to(summary_map)
                
                color_index += 1
            
            return summary_map
            
        except Exception as e:
            st.error(f"Error creating summary map: {str(e)}")
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=800,
                height=500
            )
    
    def create_simple_location_map(self, lat: float, lon: float, city_name: str) -> folium.Map:
        """Create a simple map showing just one city location."""
        try:
            city_map = folium.Map(
                location=[lat, lon],
                zoom_start=12,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=600,
                height=300
            )
            
            # Add marker
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{city_name}</b>",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(city_map)
            
            return city_map
            
        except Exception as e:
            st.error(f"Error creating location map: {str(e)}")
            return folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles=xyz.OpenStreetMap.Mapnik,
                width=600,
                height=300
            )