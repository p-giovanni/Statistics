import os
import re
import sys
import csv
import json
import codecs
import locale
import requests
import datetime as dt
import argparse

import logging

from typing import Union, Optional, Tuple, List, cast

import numpy as np # type: ignore
import pandas as pd# type: ignore 

from typing import Any, Tuple, Dict, Union

from logger_init import init_logger
from result_value import ResultKo, ResultOk, ResultValue

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

def download_csv_file(url:str, data_file:str) -> ResultValue:
    log = logging.getLogger('download_csv_file')
    log.info(" >>")
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        result = requests.get(url)
        with open(data_file, "w") as text_file:
            text_file.write(result.text)
        pass

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        rv = ResultKo(ex)
    log.info(" <<")
    return rv

def main( args:argparse.Namespace ) -> ResultValue :
    log = logging.getLogger('Main')
    log.info(" >>")
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        today = dt.datetime.now().strftime("%Y%m%d")

        data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                ,".."
                                                ,"data", "{dt}_vaccinazioni.csv".format(dt=today))
        url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv"
        rv = download_csv_file(url=url, data_file=data_file)
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        rv = ResultKo(ex)
    log.info(" ({rv}) <<".format(rv=rv))
    return rv

if __name__ == "__main__":
    init_logger('/tmp', "vaccini.log",log_level=logging.DEBUG, std_out_log_level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv.is_ok() == True else os.EX_USAGE
    sys.exit(ret_val)

