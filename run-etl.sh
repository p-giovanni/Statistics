#!/bin/bash

VIRTUALENV=/home/giovanni/add-on/venv/bin/activate
SCRIPT_PATH=./src/ETL.py
source ${VIRTUALENV}


python ${SCRIPT_PATH}
