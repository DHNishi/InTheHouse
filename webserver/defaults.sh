#!/bin/sh
python app.py \
--hostname 0.0.0.0 \
--database \
ec2-54-191-243-15.us-west-2.compute.amazonaws.com \
--username server \
--password inthehouseauthpassword \
--secret secret --debug
