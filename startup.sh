#!/bin/bash

# cd /train
host=`cat /etc/hosts | awk 'END {print}' | cut -f 1`
sed -i "s/127.0.0.1/${host}/g" nginx.conf
nginx -c /train/nginx.conf
python run.py

# docker run -d -p 80:80 trainsystem:1206 ./startup.sh
# set ff=unix
# chmod +x ./startup.sh