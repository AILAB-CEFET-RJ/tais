from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

db_username = 'postgres'
db_password = 'postgres'
db_hostname = 'localhost'
db_port = '5432'
db_name = 'pcs'

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

@app.route('/api/data', methods=['GET'])
def get_data():
    # Parse query parameters
    latitude = float(request.args.get('latitude', default=-23.968076666666665))
    longitude = float(request.args.get('longitude', default=-46.297839999999994))
    start_time_str = request.args.get('start_time', default='2023-01-01 00:00:00')
    end_time_str = request.args.get('end_time', default='2023-12-31 23:59:59')

    # Convert start_time and end_time to datetime objects
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    # Create a session
    session = Session()

    # Query latitude, longitude, and ship_id based on the circular range and time range
    query = (session.query(AISData.latitude, AISData.longitude, AISData.ship_id, AISData.ship_name)
         .filter(AISData.latitude == latitude)
         .filter(AISData.longitude == longitude)
         .filter(AISData.time_utc >= start_time)
         .filter(AISData.time_utc <= end_time)
         .distinct())

    result = query.all()

    # Close the session
    session.close()

    # Convert result to a list of dictionaries
    data = [{'latitude': row.latitude, 'longitude': row.longitude, 'ship_id': row.ship_id, "ship_name": row.ship_name} for row in result]

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
