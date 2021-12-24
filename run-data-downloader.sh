#!/bin/bash

usage="Usage: run-data-downloader.sh [data|vac|vacd|etl]"

VIRTUALENV=/Users/ERIZZAG5J/venv/bin/activate
source ${VIRTUALENV}

DATA_SCRIPT_PATH=./src/DataDownloader.py
VAC_SCRIPT_PATH=./src/VacciniDownload.py
ETL_SCRIPT_PATH=./src/ETL.py

case $1 in
data)
  echo "Download regional COVID19 data."
  python ${DATA_SCRIPT_PATH} --date_range $2 $3 $4 $5
  ;;
etl)
  echo "Run etl."
  python ${ETL_SCRIPT_PATH}
  ;;
vac)
  echo "Download vaccination dataset."
  python ${VAC_SCRIPT_PATH} --download_vaccinazioni
  ;;
vacd)
  echo "Download delivered vaccins dataset."
  python ${VAC_SCRIPT_PATH} --download_consegne
  ;;
help|h)
  echo $usage
  ;;
*)
  echo "Get actual data range."
  python ${DATA_SCRIPT_PATH} --get_date_range
  ;;
esac

