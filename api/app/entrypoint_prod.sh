#!/usr/bin/env bash
export DB_HOSTNAME=hostname_here
export DB_USERNAME=username_here
export DB_PASSWORD=password_here
export DB_PORT=port_here
export DB_NAME=database_name_here

python3 -m debugpy --listen "0.0.0.0:5678" -m flask run -h 0.0.0.0 -p 5000