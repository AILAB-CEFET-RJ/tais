#!/bin/sh
export FLASK_APP=app # api filename
python3 -m debugpy --listen "0.0.0.0:5678" -m flask run -h 0.0.0.0 -p 5000