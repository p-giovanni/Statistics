import os
import re
import sys
import json
import codecs
import locale
import requests
import datetime
import argparse

import logging
from logging.handlers import RotatingFileHandler

from typing import Union, Optional, Tuple, List, cast

import numpy as np # type: ignore
import pandas as pd# type: ignore 

from typing import Any, Tuple, Dict, Union

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

# ----------------------------------------
# init_logger
# ----------------------------------------
def init_logger(log_dir:str, file_name:str, log_level, std_out_log_level=logging.ERROR) -> None :
    """
    Logger initializzation for file logging and stdout logging with
    different level.

    :param log_dir: path for the logfile;
    :param log_level: logging level for the file logger;
    :param std_out_log_level: logging level for the stdout logger;
    :return:
    """
    root = logging.getLogger()
    dap_format = '%(asctime)s %(name)s %(levelname)s %(message)s'
    formatter = logging.Formatter(dap_format)
    # File logger.
    root.setLevel(logging.DEBUG)
    fh = RotatingFileHandler(os.path.join(log_dir, file_name), maxBytes=1000000, backupCount=5)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Stdout logger.
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(std_out_log_level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    for _ in ("urllib3"):
        logging.getLogger(_).setLevel(logging.CRITICAL)

def load_data_file(data_file:str)-> Union[Exception, pd.DataFrame] :
    log = logging.getLogger('load_data_file')
    log.info(" >>")
    try:
        df = pd.read_csv(data_file, sep=','
                        ,dtype={
                            "Ricoverati con sintomi": np.int64
                           ,"CASI TOTALI - A": np.int64
                        })
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return False
    log.info(" <<")
    return df

def calculate_daily_diffs(df:pd.DataFrame)-> Union[Exception, pd.DataFrame] :
    log = logging.getLogger('calculate_daily_diffs')
    log.info(" >>")
    try:
        regions_list = df["Regione"].unique()
        mask = df['Regione'] == 'Lombardia'
        df.loc[mask,'delta 2'] = df_lombardia['CASI TOTALI - A'].diff(periods = 1)
    
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return False
    log.info(" <<")
    return df

def main( args:argparse.Namespace ) -> bool:
    log = logging.getLogger('Main')
    log.info(" >>")
    rv = False
    try:
        data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                ,".."
                                                ,"data", "reduced_repord_data.csv")
        result = load_data_file(data_file=data_file)
        if type(result) == pd.DataFrame:
            pass

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        rv = False
    log.info(" ({rv}) <<".format(rv=rv))
    return rv

if __name__ == "__main__":
    init_logger('/tmp', "etl.log",log_level=logging.DEBUG, std_out_log_level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = 0 if rv == True else 1
    sys.exit(ret_val)

