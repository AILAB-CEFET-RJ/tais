#!/bin/bash
export DB_HOSTNAME=db
export DB_USERNAME=root
export DB_PASSWORD=root
export DB_PORT=5432
export DB_NAME=ais
export FLASK_APP=app # api filename
mv init.sql /docker-entrypoint-initdb.d/ # Init migration sql file
python3 -m debugpy --listen "0.0.0.0:5678" -m flask run -h 0.0.0.0 -p 5000