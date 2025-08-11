import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from typing import List, Dict

class WeatherMap:
    @staticmethod
    def create_world_map(cities_data: List[Dict]) -> go.Figure:
        """Create an interactive world map with weather data."""
        if not cities_data:
            fig = go.Figure()
            fig.update_layout(
                title="No cities to display",
                height=400
            )
            return fig
        
        try:
            # Extract data
            lats = []
            lons = []
            names = []
            temps = []
            weather_icons = []
            
            for city in cities_data:
                if 'coordinates' in city and 'temperature' in city:
                    lats.append(city['coordinates']['lat'])
                    lons.append(city['coordinates']['lon'])
                    names.append(f"{city['city']}, {city['country']}")
                    temps.append(city['temperature'])
                    weather_icons.append(city.get('weather_icon', '01d'))  # Default clear sky icon
            
            if not lats:
                st.error("No valid coordinate data found for cities")
                return go.Figure()
            
            # Create the map
            fig = go.Figure()
            
            # Add scatter mapbox trace with enhanced styling
            fig.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers',
                marker=dict(
                    size=[max(10, min(30, temp + 20)) for temp in temps],  # More prominent markers
                    color=temps,
                    colorscale='RdYlBu_r',
                    showscale=True,
                    colorbar=dict(
                        title="Temperature (°C)",
                        title_side="right",
                        thickness=15,
                        len=0.5,
                        yanchor="middle",
                        y=0.5
                    ),
                    opacity=0.9,
                    sizemode='diameter',
                    sizemin=8
                ),
                text=names,
                customdata=temps,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "<b>Temperature:</b> %{customdata}°C<br>"
                    "<extra></extra>"
                ),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=14,
                    font_family="Inter"
                ),
                showlegend=False
            ))
            
            # Enhanced layout with modern styling
            fig.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(
                        lat=sum(lats) / len(lats) if lats else 20,
                        lon=sum(lons) / len(lons) if lons else 0
                    ),
                    zoom=1.5 if len(lats) > 3 else 3,
                    bearing=0,
                    pitch=0
                ),
                height=600,  # Taller for better visibility
                margin=dict(l=0, r=0, t=40, b=0),
                title=dict(
                    text=f"<b>Weather Map - {len(cities_data)} Cities</b>",
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(
                        family="Inter",
                        size=20,
                        color="#2c3e50"
                    )
                ),
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",
                hovermode="closest",
                autosize=True
            )
            
            # Add weather icons as annotations if available
            if weather_icons:
                for i, (lat, lon, icon) in enumerate(zip(lats, lons, weather_icons)):
                    fig.add_annotation(
                        x=lon,
                        y=lat,
                        text=f"☀️",  # Placeholder - could use actual weather icons
                        showarrow=False,
                        font=dict(size=12),
                        xshift=0,
                        yshift=0
                    )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            return WeatherMap.create_fallback_map(cities_data)

    @staticmethod
    def create_fallback_map(cities_data: List[Dict]) -> go.Figure:
        """Create a fallback scatter plot if mapbox fails."""
        try:
            map_data = []
            for city in cities_data:
                if 'coordinates' in city and 'temperature' in city:
                    map_data.append({
                        'lat': city['coordinates']['lat'],
                        'lon': city['coordinates']['lon'],
                        'city': f"{city['city']}, {city['country']}",
                        'temperature': city['temperature'],
                        'size': max(10, city['temperature'] + 20),
                        'weather': city.get('weather_description', 'N/A')
                    })
            
            if not map_data:
                return go.Figure()
            
            # Create enhanced fallback map with plotly express
            fig = px.scatter_mapbox(
                map_data,
                lat='lat',
                lon='lon',
                hover_name='city',
                hover_data={
                    'temperature': ':.1f°C',
                    'weather': True,
                    'lat': False,
                    'lon': False,
                    'size': False
                },
                color='temperature',
                size='size',
                color_continuous_scale='RdYlBu_r',
                mapbox_style='open-street-map',
                zoom=1.5,
                height=600,
                title="<b>Weather Map - Fallback View</b>"
            )
            
            fig.update_layout(
                margin=dict(l=0, r=0, t=60, b=0),
                title_x=0.5,
                title_font=dict(size=18, family="Inter"),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=14,
                    font_family="Inter"
                ),
                coloraxis_colorbar=dict(
                    title="Temp (°C)",
                    thickness=15,
                    len=0.5
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Fallback map also failed: {str(e)}")
            return go.Figure()

# Alternative implementation using plotly express (modernized)
class AlternativeWeatherMap:
    @staticmethod
    def create_simple_map(cities_data: List[Dict]) -> go.Figure:
        """Create a simple map using plotly express with modern styling."""
        if not cities_data:
            return go.Figure()
        
        # Prepare enhanced data structure
        map_data = []
        for city in cities_data:
            if 'coordinates' in city and 'temperature' in city:
                map_data.append({
                    'lat': city['coordinates']['lat'],
                    'lon': city['coordinates']['lon'],
                    'city': f"{city['city']}, {city['country']}",
                    'temperature': city['temperature'],
                    'size': max(12, city['temperature'] + 22),  # Slightly larger markers
                    'weather': city.get('weather_description', 'N/A'),
                    'humidity': city.get('humidity', 0),
                    'wind_speed': city.get('wind_speed', 0)
                })
        
        if not map_data:
            return go.Figure()
        
        # Create map with enhanced styling
        fig = px.scatter_mapbox(
            map_data,
            lat='lat',
            lon='lon',
            hover_name='city',
            hover_data={
                'temperature': ':.1f°C',
                'weather': True,
                'humidity': ':.0f%',
                'wind_speed': ':.1f m/s',
                'lat': False,
                'lon': False,
                'size': False
            },
            color='temperature',
            size='size',
            color_continuous_scale='RdYlBu_r',
            size_max=30,
            mapbox_style='open-street-map',
            zoom=1.5,
            height=600,
            title="<b>Interactive Weather Map</b>"
        )
        
        # Enhanced layout configuration
        fig.update_layout(
            margin=dict(l=0, r=0, t=60, b=0),
            title_x=0.5,
            title_font=dict(size=20, family="Inter", color="#2c3e50"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter"
            ),
            coloraxis_colorbar=dict(
                title="Temp (°C)",
                title_side="right",
                thickness=15,
                len=0.6,
                yanchor="middle",
                y=0.5
            )
        )
        
        return fig