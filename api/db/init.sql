-- Criação da tabela AISData se ela não existir
CREATE TABLE IF NOT EXISTS ais_data (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER,
    latitude FLOAT,
    longitude FLOAT,
    ship_name VARCHAR(255),
    time_utc TIMESTAMP WITH TIME ZONE
);

-- Inserção de dados apenas se a tabela estiver vazia
INSERT INTO ais_data (ship_id, latitude, longitude, ship_name, time_utc)
SELECT 1, 40.7128, -74.0060, 'Ship A', '2023-08-30 04:05:12.049325798 +0000'
WHERE NOT EXISTS (SELECT 1 FROM ais_data LIMIT 1);

INSERT INTO ais_data (ship_id, latitude, longitude, ship_name, time_utc)
SELECT 2, 34.0522, -118.2437, 'Ship B', '2023-08-30 05:15:30.123456789 +0000'
WHERE NOT EXISTS (SELECT 1 FROM ais_data LIMIT 1);