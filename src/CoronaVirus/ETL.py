import os
import re
import sys
import csv
import json
import codecs
import locale
import requests
import datetime
import argparse

import logging

from typing import Union, Optional, Tuple, List, cast

import numpy as np # type: ignore
import pandas as pd# type: ignore 

from typing import Any, Tuple, Dict, Union

from logger_init import init_logger
from result_value import ResultKo, ResultOk, ResultValue

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

# ----------------------------------------
# 
# ----------------------------------------
def load_data_file(data_file:str)-> ResultValue :
    log = logging.getLogger('load_data_file')
    log.info(" >>")
    try:
        df = pd.read_csv(data_file, sep=','
                        ,parse_dates=["REPORT DATE"]
                        ,dtype={
                            "Ricoverati con sintomi": np.int64
                           ,"CASI TOTALI - A": np.int64
                        })
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(df)

def save_data_file(df:pd.DataFrame
                  ,data_file_out:str
                  ,sorting_col:str = "REPORT DATE"
                  ,owerwrite:bool = False)-> ResultValue :
    log = logging.getLogger('save_data_file')
    log.info(" >>")
    try:
        mode = 'w'
        header = True
        column_list = df.columns.values
        df.sort_values(by=[sorting_col], inplace=True)    
        if os.path.isfile(data_file_out) == True:
            if not owerwrite:
                mode = 'a'
                header = False
            else:
                header = True
            with open(data_file_out) as fh:
                csv_reader = csv.reader(fh)
                csv_headings = next(csv_reader)
                if csv_headings != list(column_list):
                    ex = Exception("Columns differnt from file header\n {l1}\n {l2}\n".format(l1=column_list, l2=csv_headings))
                    log.error("Error in date translation - {e}".format(e=ex))
                    return ResultKo(ex)
        log.info("Save to: {f} headers: {h}".format(f=data_file_out, h=header))
        df.to_csv(data_file_out, mode=mode, header = header, index=False)

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(df)

def calculate_daily_diffs(df:pd.DataFrame, in_col:str, out_col:str)-> ResultValue :
    log = logging.getLogger('calculate_daily_diffs')
    log.info("({oc}) >>".format(oc=out_col))
    try:
        regions_list = df["Regione"].unique()
        for region in regions_list:
            mask = df["Regione"] == region
            df.loc[mask, out_col] = df.loc[mask, in_col].diff(periods = 1)    

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(df)

def main( args:argparse.Namespace ) -> ResultValue :
    log = logging.getLogger('Main')
    log.info(" >>")
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                ,".."
                                                ,"data", "reduced_report_data.csv")
        result = load_data_file(data_file=data_file)
        delta_cols = ["CASI TOTALI - A", "DECEDUTI"]
        for col in delta_cols:
            if result.is_ok: 
                result = calculate_daily_diffs(cast(pd.DataFrame, result())
                                              ,in_col=col, out_col="D - {c}".format(c=col))
            else:
                break
        if result.is_ok():
            result = save_data_file(cast(pd.DataFrame, result())
                                   ,os.path.join(os.path.dirname(os.path.realpath(__file__)),".." ,"data", "report_data.csv")
                                   ,owerwrite=True)
        if result.is_ok():
            rv = ResultOk(None)
        
        data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                ,".."
                                                ,"data", "report_data.csv")
        result = load_data_file(data_file=data_file)

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        rv = ResultKo(ex)
    log.info(" ({rv}) <<".format(rv=rv))
    return rv

if __name__ == "__main__":
    init_logger('/Users/ERIZZAG5J/Work/tmp', "etl.log",log_level=logging.DEBUG, std_out_log_level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv.is_ok() == True else os.EX_USAGE
    sys.exit(ret_val)

