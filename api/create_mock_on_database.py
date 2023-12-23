import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# Defina o modelo de dados
Base = declarative_base()

class AISData(Base):
    __tablename__ = 'ais_data'
    id = Column(Integer, primary_key=True)
    ship_id = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    ship_name = Column(String(255))
    time_utc = Column(DateTime(timezone=True))

# Configuração do banco de dados
db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_port = os.environ.get('DB_PORT')
db_name = os.environ.get('DB_NAME')

DATABASE_URL = f'postgresql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Criação de uma sessão
Session = sessionmaker(bind=engine)
session = Session()

# Inserção de dados
data_to_insert = [
    {'ship_id': 1, 'latitude': 40.7128, 'longitude': -74.0060, 'ship_name': 'Ship A', 'time_utc': '2023-08-30 04:05:12.049325798'},
    {'ship_id': 2, 'latitude': 34.0522, 'longitude': -118.2437, 'ship_name': 'Ship B', 'time_utc': '2023-08-30 05:15:30.123456789'}
]

for data in data_to_insert:
    data['time_utc'] = datetime.strptime(data['time_utc'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
    new_record = AISData(**data)
    session.add(new_record)

# Commit das alterações
session.commit()

# Consulta para verificar se os dados foram inseridos corretamente
query_result = session.query(AISData).all()
for row in query_result:
    print(f"ID: {row.id}, Ship ID: {row.ship_id}, Latitude: {row.latitude}, Longitude: {row.longitude}, Ship Name: {row.ship_name}, Time UTC: {row.time_utc}")