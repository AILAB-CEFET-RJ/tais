import asyncio
import websockets
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


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
                             "BoundingBoxes": [[[-11, 178], [30, 74]]]}

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        # Start receiving and processing AIS messages
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

                # Convert the input string to a datetime object
                # Remove the fractional seconds and ' UTC' from the input string
                formatted_input = timestamp_string.split('.')[0].strip()

                # Convert the modified input string to a datetime object
                input_datetime = datetime.strptime(
                    formatted_input, '%Y-%m-%d %H:%M:%S')

                # Format it as SQL datetime
                sql_datetime = input_datetime.strftime('%Y-%m-%d %H:%M:%S')

                # Create an instance of AISData and add it to the session
                ais_data = AISData(
                    ship_id=ship_id, latitude=latitude, longitude=longitude, ship_name=ship_name, time_utc=sql_datetime)
                session.add(ais_data)

                print("Creating new object")

                # Commit the changes to the database
                session.commit()


async def main():
    await connect_ais_stream()

if __name__ == "__main__":
    asyncio.run(main())
