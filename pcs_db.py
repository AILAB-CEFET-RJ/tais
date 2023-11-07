import asyncio
import websockets
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from websockets.exceptions import ConnectionClosedError

# Define the SQLAlchemy database connection URL
db_url = ''

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


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create an SQLAlchemy session
Session = sessionmaker(bind=engine)
session = Session()

api_key = ''


async def connect_ais_stream():

    # Connect to the AIS WebSocket stream
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": api_key,
                             "BoundingBoxes": [[[-56.0, -79.0], [12.0, -35.0]]]}

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        # Start receiving and processing AIS messages
        try:
            async for message_json in websocket:
                message = json.loads(message_json)
                message_type = message["MessageType"]

                if message_type == "PositionReport":
                    ais_message = message['Message']['PositionReport']
                    ship_id = ais_message['UserID']
                    latitude = ais_message['Latitude']
                    longitude = ais_message['Longitude']
                    ship_name = message['MetaData']['ShipName']
                    ship_name = ship_name.replace(" ", "")

                    # Original timestamp string
                    timestamp_string = message['MetaData']['time_utc']

                    # Format the time to database
                    formatted_time_utc = timestamp_string.split('.')[0].strip()

                    # Create an instance of AISData and add it to the session
                    ais_data = AISData(
                        ship_id=ship_id, latitude=latitude, longitude=longitude, ship_name=ship_name, time_utc=formatted_time_utc)
                    session.add(ais_data)

                    print(
                        f"ship_id={ship_id}, latitude={latitude}, longitude={longitude}, ship_name={ship_name}, time_utc={formatted_time_utc}")

                    # Commit the changes to the database
                    session.commit()

                    await websocket.ping()
        except ConnectionClosedError as e:
            print(f"Connection closed: {e}")


async def main():
    await connect_ais_stream()

if __name__ == "__main__":
    asyncio.run(main())
