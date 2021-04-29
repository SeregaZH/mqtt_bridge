#!/usr/bin/env bash
set -e

python -m pip install -U -r requirements.txt
sudo apt-get install -y python-shapely mosquitto mosquitto-clients