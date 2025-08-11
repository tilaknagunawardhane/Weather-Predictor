import plotly.graph_objects as go
from typing import List, Dict

class WeatherMap:
    @staticmethod
    def create_world_map(cities_data: List[Dict]) -> go.Figure:
        """Create a world map with markers for given cities."""
        if not cities_data:
            return go.Figure()
        
        fig = go.Figure()

        lats = [city['coordinates']['lat'] for city in cities_data]
        lons = [city['coordinates']['lon'] for city in cities_data]
        names = [f"{city['city']}, {city['country']}" for city in cities_data]
        temps = [city['temperature'] for city in cities_data]

        fig.add_trace(go.Scatttermapbox(
            lat = lats,
            lon = lons,
            mode = 'markers',
            marker = dict(
                size=[max(10, min(30, temp + 20)) for temp in temps],  # Size based on temperature
                color=temps,
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Temperature (°C)")
            ),
            text = names,
            hovertemplate = "<b>%{text}</b><br>Temperature: %{marker.color}°C<extra></extra>",
            showlegend = False
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