import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
from datetime import datetime
import time
from collections import defaultdict

# Store your OpenSky credentials here
OPENSKY_USERNAME = "GripenNG"
OPENSKY_PASSWORD = "@en@yWKMpYkrY5B"

# Checking credentials
if not OPENSKY_USERNAME or not OPENSKY_PASSWORD:
    raise ValueError("OpenSky credentials are not set!")

# Store flight paths
flight_paths = defaultdict(lambda: {'lats': [], 'lons': [], 'times': []})
tracked_callsigns = set()

def get_initial_callsigns():
    """Get first three valid callsigns from the API"""
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, auth=(OPENSKY_USERNAME, OPENSKY_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            callsigns = []
            for state in data['states']:
                if state[1] and state[1].strip():  # Check for valid callsign
                    callsigns.append(state[1].strip())
                if len(callsigns) == 3:
                    break
            return callsigns
        return []
    except Exception as e:
        print(f"Error getting initial callsigns: {e}")
        return []

def get_flight_data(callsigns):
    """Get flight data for specific callsigns"""
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, auth=(OPENSKY_USERNAME, OPENSKY_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            flight_data = []
            
            for state in data['states']:
                if state[1] and state[1].strip() in callsigns:
                    flight_data.append({
                        'callsign': state[1].strip(),
                        'latitude': state[6],
                        'longitude': state[5],
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
            return flight_data
        return None
    except Exception as e:
        print(f"Error getting flight data: {e}")
        return None

# Initialize Dash app
app = Dash(__name__)

# Get initial callsigns to track
initial_callsigns = get_initial_callsigns()
print(f"Tracking callsigns: {initial_callsigns}")
tracked_callsigns.update(initial_callsigns)

# Create the layout
app.layout = html.Div([
    html.H1('Flight Tracker 2.0'),
        dcc.Dropdown(
        id='callsign-dropdown',
        options=[],
        multi=True,
        placeholder='Select callsigns to track',
    ),
    html.Div(id='tracking-info', children=f'Tracking: {", ".join(tracked_callsigns)}'),
    html.Div(id='last-update'),
    dcc.Graph(id='live-map'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    [Output('live-map', 'figure'),
     Output('last-update', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_map(n):
    # Get new flight data
    flight_data = get_flight_data(tracked_callsigns)
    current_time = datetime.now().strftime('%H:%M:%S')
    
    if flight_data:
        # Update flight paths
        for flight in flight_data:
            callsign = flight['callsign']
            flight_paths[callsign]['lats'].append(flight['latitude'])
            flight_paths[callsign]['lons'].append(flight['longitude'])
            flight_paths[callsign]['times'].append(flight['time'])
    
    # Create base map
    fig = go.Figure()
    
    # Add path and current position for each tracked flight
    colors = ['red', 'blue', 'green']  # Different color for each aircraft
    for i, callsign in enumerate(tracked_callsigns):
        if flight_paths[callsign]['lats']:
            # Add flight path
            fig.add_trace(go.Scattergeo(
                lon=flight_paths[callsign]['lons'],
                lat=flight_paths[callsign]['lats'],
                mode='lines',
                line=dict(width=2, color=colors[i%3]),
                name=f'{callsign} path'
            ))
            
            # Add current position
            fig.add_trace(go.Scattergeo(
                lon=[flight_paths[callsign]['lons'][-1]],
                lat=[flight_paths[callsign]['lats'][-1]],
                mode='markers+text',
                marker=dict(size=10, color=colors[i%3]),
                text=[callsign],
                textposition="top center",
                name=f'{callsign} current position'
            ))
    
    # Update map layout
    fig.update_layout(
        title='Live Aircraft Tracking',
        showlegend=True,
        geo=dict(
            projection_type='equirectangular',
            showland=True,
            showcountries=True,
            showocean=True,
            countrywidth=0.5,
            landcolor='rgb(243, 243, 243)',
            oceancolor='rgb(204, 229, 255)',
            projection_scale=1.4
        ),
        height=800
    )
    
    return fig, f'Last updated: {current_time}'

def main():
    print(f"Starting flight tracker...")
    print(f"Tracking aircraft: {', '.join(tracked_callsigns)}")
    app.run_server(debug=True)

if __name__ == '__main__':
    main()