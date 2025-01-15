import requests
import pandas as pd
import plotly.graph_objects as go
import time
from dash import Dash, html, dcc, Input, Output
from datetime import datetime
from collections import defaultdict

# Store your OpenSky credentials here
OPENSKY_USERNAME = "GripenNG"
OPENSKY_PASSWORD = "@en@yWKMpYkrY5B"

# Store flight paths
flight_paths = defaultdict(lambda: {'lats': [], 'lons': [], 'times': []})

# Initialize Dash app
app = Dash(__name__)

# Create the layout
app.layout = html.Div([
    html.H1('Flight Tracker 4.0'),
    dcc.Dropdown(
        id='callsign-dropdown',
        options=[],  # Will be dynamically updated
        placeholder="Select flights to track",
        multi=True  # Allow multiple selections
    ),
    html.Div(id='tracking-info'),
    html.Div(id='last-update'),
    dcc.Graph(id='live-map'),
    dcc.Interval(
        id='interval-fetch',
        interval=5*1000,  # Fetch data every 10 seconds
        n_intervals=0
    )
])

def fetch_callsigns():
    """Fetch available callsigns from OpenSky API."""
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, auth=(OPENSKY_USERNAME, OPENSKY_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"Total flights available at {current_time}: {len(data['states'])}")
            return [
                {'label': state[1].strip(), 'value': state[1].strip()}
                for state in data['states'] if state[1]
            ]
    except Exception as e:
        print(f"Error fetching callsigns: {e}")
        return []

@app.callback(
    Output('callsign-dropdown', 'options'),
    Input('interval-fetch', 'n_intervals')
)
def update_dropdown_options(n):
    """Update the dropdown with available callsigns."""
    return fetch_callsigns()

@app.callback(
    [Output('live-map', 'figure'),
     Output('tracking-info', 'children'),
     Output('last-update', 'children')],
    [Input('interval-fetch', 'n_intervals'),
     Input('callsign-dropdown', 'value')]
)
def update_map(n, selected_callsigns):
    """Update the map and tracking information."""
    if not selected_callsigns:
        return go.Figure(), "No flights selected", f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

    # Fetch flight data for selected callsigns
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, auth=(OPENSKY_USERNAME, OPENSKY_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            flight_data = []

            # Filter the data for the selected callsigns
            for state in data['states']:
                if state[1] and state[1].strip() in selected_callsigns:
                    callsign = state[1].strip()
                    flight_data.append({
                        'callsign': callsign,
                        'latitude': state[6],
                        'longitude': state[5],
                        'time': datetime.now().strftime('%H:%M:%S')
                    })

                    # Update flight paths
                    flight_paths[callsign]['lats'].append(state[6])
                    flight_paths[callsign]['lons'].append(state[5])
                    flight_paths[callsign]['times'].append(datetime.now().strftime('%H:%M:%S'))

            # Create the map
            fig = go.Figure()
            colors = ['red', 'blue', 'green', 'orange', 'purple']  # Assign colors to paths
            for i, flight in enumerate(flight_data):
                callsign = flight['callsign']
                if flight_paths[callsign]['lats']:
                    # Add flight path
                    fig.add_trace(go.Scattergeo(
                        lon=flight_paths[callsign]['lons'],
                        lat=flight_paths[callsign]['lats'],
                        mode='lines',
                        line=dict(width=2, color=colors[i % len(colors)]),
                        name=f'{callsign} path'
                    ))

                    # Add current position
                    fig.add_trace(go.Scattergeo(
                        lon=[flight_paths[callsign]['lons'][-1]],
                        lat=[flight_paths[callsign]['lats'][-1]],
                        mode='markers+text',
                        marker=dict(size=10, color=colors[i % len(colors)]),
                        text=[callsign],
                        textposition="top center",
                        name=f'{callsign} current position'
                    ))

            # Update map layout
            fig.update_layout(
                title='Live Aircraft Tracking',
                geo=dict(
                    projection_type='equirectangular',
                    showland=True,
                    showcountries=True,
                    showocean=True,
                    countrywidth=0.5,
                    landcolor='rgb(243, 243, 243)',
                    oceancolor='rgb(204, 229, 255)',
                ),
                height=800
            )
            return fig, f"Tracking: {', '.join(selected_callsigns)}", f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

    except Exception as e:
        print(f"Error updating map: {e}")

    return go.Figure(), "Error retrieving flight data", f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

def main():
    print(f"Starting flight tracker...")
    app.run_server(debug=True)

if __name__ == '__main__':
    main()
