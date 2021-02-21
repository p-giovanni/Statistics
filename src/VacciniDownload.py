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

import matplotlib as mp                 # type: ignore        
from matplotlib import pyplot as plt    # type: ignore     
import matplotlib.dates as mdates       # type: ignore 
import matplotlib.gridspec as gridspec  # type: ignore      
import matplotlib.ticker as mticker     # type: ignore   

from typing import Any, Tuple, Dict, Union

from logger_init import init_logger
from result_value import ResultKo, ResultOk, ResultValue

from ChartTools import remove_tick_lines
from ChartTools import every_nth_tick
from ChartTools import autolabel
from ChartTools import set_axes_common_properties
from ChartTools import text_box


locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

def download_csv_file(url:str, data_file:str) -> ResultValue:
    log = logging.getLogger('download_csv_file')
    log.info(" >>")
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        result = requests.get(url)
        with open(data_file, "w") as text_file:
            text_file.write(result.text)

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        rv = ResultKo(ex)
    log.info(" <<")
    return rv

def create_dataframe(data_file:str)-> ResultValue:
    log = logging.getLogger('create_dataframe')
    log.info(" >>")
    try:
        df = pd.read_csv(data_file, sep=','
                        ,parse_dates=["data_somministrazione"])

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(df)

def chart_vaccinations_male_female(df:pd.DataFrame, ax:mp.axes.Axes)-> ResultValue :
    log = logging.getLogger('chart_vaccinations_male_female')
    log.info(" >>")
    try:
        num_male = df["sesso_maschile"].sum()
        num_female = df["sesso_femminile"].sum()
        parts = [num_female, num_male]
        labels = ["Donne", "Uomini"]

        female_color = "#f1a29b"
        male_color = "#9bd7f1"
        ax.pie(parts, labels=labels, colors=[female_color, male_color], autopct='%1.1f%%')

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def age_distribution(df:pd.DataFrame, ax:mp.axes.Axes, gender:str="F")-> ResultValue :
    log = logging.getLogger('age_distribution')
    log.info(" >>")
    try:
        if gender.upper() not in ["M","F","B"]:
            msg = "Geneder {v} value not known".format(v=gender)
            log.error(msg)
            return ResultKo(Exception(msg))

        by_age = df.groupby(["fascia_anagrafica"]).sum()
        by_age.reset_index(level=0, inplace=True)
        by_age["totals"] = by_age["sesso_femminile"] + by_age["sesso_maschile"]

        colors = ["#9aff33","#34ff33","#33ff98","#33fffe","#339aff","#3371ff","#5b33ff","#c133ff","#ff33d7"]
        values = by_age["sesso_femminile" if gender == "F" else ("sesso_maschile" if gender == "M" else "totals")]
        labels = by_age["fascia_anagrafica"]
        ax.pie(values, labels=labels,  autopct='%1.1f%%', colors=colors)
    
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def main( args:argparse.Namespace ) -> ResultValue :
    log = logging.getLogger('Main')
    log.info(" >>")
    #rv:ResultValue = ResultKo(Exception("Error"))
    try:
    #    today = dt.datetime.now().strftime("%Y%m%d")
    #    data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
    #                                            ,".."
    #                                            ,"data", "{dt}_vaccinazioni.csv".format(dt=today))
    #    url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv"
    #    rv = download_csv_file(url=url, data_file=data_file)
        
        data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                ,".."
                                                ,"data", "vaccinazioni.csv")
        rv = create_dataframe(data_file=data_file)
        if rv.is_in_error():
            log.error(rv.value())
        else:
            df = rv.value()
            mask_region = df["nome_area"] == "Lombardia"
            df_region = df.loc[mask_region,["data_somministrazione","nome_area","fornitore","sesso_maschile","sesso_femminile","fascia_anagrafica"]]
            
            fig = plt.figure(figsize=(20, 10))
            gs1 = gridspec.GridSpec(1, 1
                       ,hspace=0.2
                       ,wspace=0.1 
                       ,figure=fig)
            ax = []
            ax.append(fig.add_subplot(gs1[0,0]))
            idx = 0

            age_distribution(df_region, ax=ax[idx])

            plt.savefig(os.path.join(os.sep, "tmp", "vaccini_fig.png")
                                    ,bbox_inches = 'tight'
                                    ,pad_inches = 0.2)

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        rv = ResultKo(ex)
    log.info(" ({rv}) <<".format(rv=rv))
    return rv

if __name__ == "__main__":
    init_logger('/tmp', "vaccini.log",log_level=logging.DEBUG, std_out_log_level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", type=str,help="Data download.")
    parser.add_argument("--chart", type=str,help="Chart.")
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv.is_ok() == True else os.EX_USAGE
    sys.exit(ret_val)

