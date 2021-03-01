#!/bin/bash

VIRTUALENV=/home/giovanni/add-on/venv/bin/activate
SCRIPT_PATH=./src/DataDownloader.py
source ${VIRTUALENV}


python ${SCRIPT_PATH} $1 $2 $3 $4
