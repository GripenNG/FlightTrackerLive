import requests
import pandas as pd
import plotly.graph_objects as go
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
    html.H1('Flight Tracker 5.0'),
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
        interval=5*1000,  # Fetch data every 5 seconds
        n_intervals=0
    )
])

def fetch_callsigns():
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
    return fetch_callsigns()

@app.callback(
    [Output('live-map', 'figure'),
     Output('tracking-info', 'children'),
     Output('last-update', 'children')],
    [Input('interval-fetch', 'n_intervals'),
     Input('callsign-dropdown', 'value')]
)
def update_map(n, selected_callsigns):
    if not selected_callsigns:
        # Return empty figure but maintain zoom with uirevision
        empty_fig = go.Figure()
        empty_fig.update_layout(
            uirevision='constant',
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
        return empty_fig, "No flights selected", f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, auth=(OPENSKY_USERNAME, OPENSKY_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            flight_data = []

            for state in data['states']:
                if state[1] and state[1].strip() in selected_callsigns:
                    callsign = state[1].strip()
                    flight_data.append({
                        'callsign': callsign,
                        'latitude': state[6],
                        'longitude': state[5],
                        'time': datetime.now().strftime('%H:%M:%S')
                    })

                    flight_paths[callsign]['lats'].append(state[6])
                    flight_paths[callsign]['lons'].append(state[5])
                    flight_paths[callsign]['times'].append(datetime.now().strftime('%H:%M:%S'))

            fig = go.Figure()
            colors = ['red', 'blue', 'green', 'orange', 'purple']
            
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

            # Update layout with uirevision to maintain zoom
            fig.update_layout(
                uirevision='constant',  # This is the key to maintaining zoom
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

    # Return empty figure but maintain zoom
    error_fig = go.Figure()
    error_fig.update_layout(
        uirevision='constant',
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
    return error_fig, "Error retrieving flight data", f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

def main():
    print(f"Starting flight tracker...")
    app.run_server(debug=True)

if __name__ == '__main__':
    main()