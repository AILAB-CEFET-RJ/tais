import csv
from datetime import datetime, timedelta
import math

# Constantrs
R = 6371  # RAIO DA TERRA em km
INTERVAL_MINUTES = 15

def great_circle_intermediate(start_lat, start_lon, end_lat, end_lon, fraction):
    start_lat, start_lon, end_lat, end_lon = map(math.radians, [start_lat, start_lon, end_lat, end_lon])
    
    delta_lat = end_lat - start_lat
    delta_lon = end_lon - start_lon
    
    a = math.sin(delta_lat / 2)**2 + math.cos(start_lat) * math.cos(end_lat) * math.sin(delta_lon / 2)**2
    distance = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    A = math.sin((1 - fraction) * distance) / math.sin(distance)
    B = math.sin(fraction * distance) / math.sin(distance)
    
    x = A * math.cos(start_lat) * math.cos(start_lon) + B * math.cos(end_lat) * math.cos(end_lon)
    y = A * math.cos(start_lat) * math.sin(start_lon) + B * math.cos(end_lat) * math.sin(end_lon)
    z = A * math.sin(start_lat) + B * math.sin(end_lat)
    
    intermediate_lat = math.atan2(z, math.sqrt(x**2 + y**2))
    intermediate_lon = math.atan2(y, x)
    
    return math.degrees(intermediate_lat), math.degrees(intermediate_lon)

# Function to calculate speed based on time fraction
def calculate_speed(fraction, min_speed=5, max_speed=15):
    if fraction < 0.5:
        # Accelerating phase
        speed = min_speed + (max_speed - min_speed) * (2 * fraction)
    else:
        # Decelerating phase
        speed = max_speed - (max_speed - min_speed) * (2 * (fraction - 0.5))
    
    return round(speed, 1)

# Function to generate the trajectory
def generate_trajectory(boat_id, start_lat, start_lon, end_lat, end_lon, start_date, end_date, output_file):
    
    start_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    
    total_duration = (end_time - start_time).total_seconds()
    interval_seconds = INTERVAL_MINUTES * 60
    
    trajectory_data = []
    current_time = start_time
    
    while current_time <= end_time:
        fraction = (current_time - start_time).total_seconds() / total_duration
        fraction = min(fraction, 1.0)
        
        lat, lon = great_circle_intermediate(start_lat, start_lon, end_lat, end_lon, fraction)
        speed = calculate_speed(fraction)  # Use the new speed calculation
        
        trajectory_data.append([
            boat_id,
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
            180,
            speed,
            lat,
            lon
        ])
        
        current_time += timedelta(seconds=interval_seconds)
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(trajectory_data)
    
    print(f"Trajectory generated and saved to {output_file}")

# MUDAR PARA CRIAR NOVOS DADOS:
boat_id = "IHS-AIS-TESTE"
start_lat, start_lon = -21.849659, -40.993800  # Rio de Janeiro
end_lat, end_lon = -22.673284, 14.519859  # Namibia
start_date = "2024-06-24 23:49:02"
end_date = "2024-08-24 23:49:02"  # 2 months later
output_file = "ship_trajectory.csv"

generate_trajectory(boat_id, start_lat, start_lon, end_lat, end_lon, start_date, end_date, output_file)
