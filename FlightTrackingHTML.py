import requests
import pandas as pd
from tabulate import tabulate
import time
from datetime import datetime
from dash import Dash, html, dcc
import plotly.express as px

# Creating html app

app = Dash(__name__)

app.layout = html.Div([html.H1('Flight Tracker 1.0'), html.Div(id = "lat-long-text")])

if __name__ == "__main__":
    app.run_server(debug = True)

# Creating blank map

fig = px.line_geo()
fig.update_geos(projection_type="natural earth")
fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})

app.layout = html.Div([
    html.H1('Flight Tracker 1.0'),
    html.Div(id='lat-long-text'),
    dcc.Graph(id='map', figure=fig)
])

# Planning to write code: Using latitude and longitude, show position of multiple planes on the map

# Store your OpenSky credentials here
OPENSKY_USERNAME = "GripenNG"
OPENSKY_PASSWORD = "@en@yWKMpYkrY5B"

def get_flight_data(username, password):
    url = "https://opensky-network.org/api/states/all"
    
    try:
        # Using authentication
        response = requests.get(
            url,
            auth=(username, password)
        )
        
        if response.status_code == 200:
            data = response.json()
            flight_data = []

            for state in data['states'][:20]:
                flight_data.append({
                    'callsign': state[1].strip() if state[1] else 'N/A',
                    'latitude': f"{state[6]}°",
                    'longitude': f"{state[5]}°",
                    'altitude': f"{state[7]} m",
                    'velocity': f"{state[9]} m/s ({round(state[9] * 3.6, 1)} km/h)"
                })
                
            df = pd.DataFrame(flight_data)
            return df

        else:
            print(f"Error: Status code {response.status_code}")
            print(f"Response content: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to OpenSky: {e}")
        return None

def main():
    print("\nStarting flight tracker with authenticated access...")
    print("Testing connection...")
    
    # Test authentication first
    test_data = get_flight_data(OPENSKY_USERNAME, OPENSKY_PASSWORD)
    if test_data is None:
        print("Failed to authenticate. Please check your credentials.")
        return
        
    print("Authentication successful!")
    
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        print('\033[H\033[J')  # Clear screen
        print(f"Time: {current_time}")
        print(f"Logged in as: {OPENSKY_USERNAME}")
        
        df = get_flight_data(OPENSKY_USERNAME, OPENSKY_PASSWORD)
        if df is not None:
            print(tabulate(df, headers='keys', tablefmt='grid'))
        
        time.sleep(5)  # Wait 5 seconds before next update

if __name__ == "__main__":
    main()



