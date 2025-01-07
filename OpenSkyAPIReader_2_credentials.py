import requests
import pandas as pd
from tabulate import tabulate
import time
from datetime import datetime
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
    paused = False
    status = "RUNNING"
    last_update = 0
    
    print("\nStarting flight tracker with authenticated access...")
    print("Testing connection...")
    
    # Test authentication first
    test_data = get_flight_data(OPENSKY_USERNAME, OPENSKY_PASSWORD)
    if test_data is None:
        print("Failed to authenticate. Please check your credentials.")
        return
        
    print("Authentication successful!")
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            current_timestamp = time.time()
            
            # Check if it's time to update (every 5 seconds)
            if not paused and current_timestamp - last_update >= 5:
                print('\033[H\033[J')
                print(f"Status: {status} at {current_time}")
                print(f"Logged in as: {OPENSKY_USERNAME}")
                print("Enter 'p' to pause/resume, 'q' to quit")
                
                df = get_flight_data(OPENSKY_USERNAME, OPENSKY_PASSWORD)
                if df is not None:
                    print(tabulate(df, headers='keys', tablefmt='grid'))
                last_update = current_timestamp
            
            # Check for commands without blocking
            if input:  # Check if there's input available
                command = input().lower()
                if command == 'q':
                    raise KeyboardInterrupt
                elif command == 'p':
                    paused = not paused
                    status = "PAUSED" if paused else "RUNNING"
            
            time.sleep(5)  # Small delay to prevent CPU overuse
                
    except KeyboardInterrupt:
        print('\033[H\033[J')
        print(f"Status: QUIT at {current_time}")

if __name__ == "__main__":
    main()