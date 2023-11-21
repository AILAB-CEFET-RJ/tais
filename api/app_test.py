from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pandas as pd
from geopy.distance import geodesic
from datetime import datetime

db_username = 'postgres'
db_password = 'postgres'
db_hostname = 'localhost'
db_port = '5432'
db_name = 'postgres'

# Create a connection string using variables
db_url = f'postgresql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}'

# Create an SQLAlchemy engine
engine = create_engine(db_url)

# Define the SQLAlchemy base model
Base = declarative_base()

# Define the AISData model
class AISData(Base):
    __tablename__ = 'ais_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    ship_name = Column(String)
    time_utc = Column(DateTime)

# Create an SQLAlchemy session
Session = sessionmaker(bind=engine)

app = Flask(__name__)
CORS(app)

@app.route('/api/data', methods=['GET'])
def get_data():
    # Parse query parameters
    start_time_str = request.args.get('start_time', default='2023-01-01 00:00:00')
    end_time_str = request.args.get('end_time', default='2023-12-31 23:59:59')

    # Convert start_time and end_time to datetime objects
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    # Create a session
    session = Session()

    # Query latitude, longitude, and ship_id based on the circular range and time range
    query = (session.query(AISData.latitude, AISData.longitude, AISData.ship_id, AISData.ship_name)
         .filter(AISData.time_utc >= start_time)
         .filter(AISData.time_utc <= end_time)
         .distinct())

    result = query.all()

    # Close the session
    session.close()

    # Convert result to a list of dictionaries
    data = [{'latitude': row.latitude, 'longitude': row.longitude, 'ship_id': row.ship_id, "ship_name": row.ship_name} for row in result]

    return jsonify(data)



@app.route('/api/heatmap', methods=['GET'])
def get_heatmap_data():
    # Parse query parameters
    start_datetime_str = request.args.get('start_datetime', default='2023-01-01T00:00:00.000Z')
    end_datetime_str = request.args.get('end_datetime', default='2024-12-31T23:59:59.000Z')
    grid_size_str = request.args.get('grid_size', default=1.0)

    # Convert start_time and end_time to datetime objects
    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    grid_size = float(grid_size_str)

    return calculate_heatmap_data(start_datetime, end_datetime, grid_size)


def km_to_degrees(latitude, kilometers):
    lat_degrees = geodesic((latitude, 0), (latitude + 1, 0)).kilometers
    degrees = kilometers / lat_degrees
    return degrees



def calculate_heatmap_data(start_datetime, end_datetime, grid_size):
    # Get data from 'ais_data' table and filter by start_datetime and end_datetime
    session = Session()
    query = (session.query(AISData.latitude, AISData.longitude, AISData.ship_id, AISData.ship_name, AISData.time_utc)
        .filter(AISData.time_utc >= start_datetime)
        .filter(AISData.time_utc <= end_datetime)
        .distinct())

    result = query.all()
    session.close()

    # Read data from database and convert to DataFrame
    df = pd.DataFrame(result, columns=['latitude', 'longitude', 'ship_id', 'ship_name', 'time_utc'])

    # Set grid size in degrees - measure for flat map
    mean_lat = df['latitude'].mean() 
    grid_size = km_to_degrees(mean_lat, grid_size)

    # Calculates the average latitude and longitude between points
    center_lat, center_lon = df['latitude'].mean(), df['longitude'].mean()

    # Create grids based on latitudes and longitudes
    df['grid_lat'] = (df['latitude'] // grid_size) * grid_size
    df['grid_lon'] = (df['longitude'] // grid_size) * grid_size

    # Group data by grids and calculate vessel density
    density_data = df.groupby(['grid_lat', 'grid_lon']).size().reset_index(name='density')

    # Converts data into a list of coordinates along with density for HeatMap
    heat_data = [[row['grid_lat'], row['grid_lon'], row['density']] for _, row in density_data.iterrows()]

    return { "center_latitude": center_lat, "center_longitude": center_lon, "heatmap_data": heat_data}



if __name__ == '__main__':
    app.run(debug=True)
