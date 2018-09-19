#!/bin/bash

# Wait for Cassandra cluster to be up and running
bash ./wait-for-it.sh cassandra:9042

# Run DB setup
python3 db_setup.py

# Run API service
python3 -m api
