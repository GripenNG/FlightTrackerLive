import requests
import pandas as pd
from tabulate import tabulate
import time
import keyboard
from datetime import datetime

def get_flight_data():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        flight_data = []
        
        for state in data['states'][:10]:
            flight_data.append({
                'callsign': state[1].strip() if state[1] else 'N/A',
                'latitude': f"{state[6]}°",
                'longitude': f"{state[5]}°",
                'altitude': f"{state[7]} m",
                'velocity': f"{state[9]} m/s ({round(state[9] * 3.6, 1)} km/h)"
            })
        
        df = pd.DataFrame(flight_data)
        return df
    return None

def main():
    paused = False
    status = "RUNNING"
    
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        if keyboard.is_pressed('q'):
            print('\033[H\033[J')
            print(f"Status: QUIT at {current_time}")
            break
        if keyboard.is_pressed('p'):
            paused = not paused
            status = "PAUSED" if paused else "RUNNING"
            time.sleep(0.5)
            
        print('\033[H\033[J')
        print(f"Status: {status} at {current_time}")
        print("Controls: 'p' to pause/resume, 'q' to quit")
        
        if not paused:
            df = get_flight_data()
            if df is not None:
                print(tabulate(df, headers='keys', tablefmt='grid'))
            
        time.sleep(10)

if __name__ == "__main__":
    main()