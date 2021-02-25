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
from matplotlib import colors           # type: ignore
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
        if result.status_code in [200]:
            with open(data_file, "w") as text_file:
                text_file.write(result.text)
            rv = ResultOk(True)
        else:
            msg = "Error downloading the data file: {e}.".format(e=result.reason)
            log.error(msg)
            rv = ResultKo(Exception(msg))

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

        df["totali"] = df["sesso_maschile"] + df["sesso_femminile"]

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
        ax.set_title("Distribuzione per genere", fontsize=18)

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def plot_vaccinations_by_time(df:pd.DataFrame, ax:mp.axes.Axes, wich:str="first")-> ResultValue :
    log = logging.getLogger('plot_vaccinations_by_time')
    log.info(" >>")
    try:
        ln_one_color = "#92b7e9"
        ln_two_color = "#9992e9"
        ln_one_label = "Cumulata numero vaccinazioni"
        ln_two_label = "Distribuzione giornaliera"

        grp_by_time = df.groupby("data_somministrazione").sum()
        x = grp_by_time.index.values
        y = grp_by_time["prima_dose"]
        y_cum_sum = grp_by_time["prima_dose"].cumsum()

        set_axes_common_properties(ax, no_grid=False)

        ax.get_yaxis().set_major_formatter(mp.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

        remove_tick_lines('x', ax)
        remove_tick_lines('y', ax)

        ax.set_xticks(x)
        ax.set_xticklabels(x, rotation=80)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d/%m"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax.set_ylabel(ln_one_label, fontsize=14)
        ax.set_xlabel("Data", fontsize=14)
        ax.set_title("Vaccinazioni nel tempo - prima dose", fontsize=18)
        ax.tick_params(axis='y', colors=ln_one_color)
        ax.yaxis.label.set_color(ln_one_color)

        ax.scatter(x, y_cum_sum, color=ln_one_color, s=30, marker='.')
        ln_one = ax.plot(x, y_cum_sum, 'b-', linewidth=2, color=ln_one_color, label="Dosi - somma")

        ax_dec = ax.twinx()
        
        remove_tick_lines('y', ax_dec)
        remove_tick_lines('x', ax_dec)

        set_axes_common_properties(ax_dec, no_grid=True)
        
        ax_dec.scatter(x, y, color=ln_two_color, s=30, marker='.')
        ln_two = ax_dec.plot(x, y, 'b-', linewidth=2, color=ln_two_color, label=ln_two_label)
        
        ax_dec.set_ylabel(ln_two_label, fontsize=14)
        ax_dec.yaxis.label.set_color(ln_two_color)
        ax_dec.tick_params(axis='y', colors=ln_two_color)

        lns = ln_one+ln_two
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc='upper left')

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def chart_vaccinations_fornitore(df:pd.DataFrame, ax:mp.axes.Axes)-> ResultValue :
    log = logging.getLogger('chart_vaccinations_fornitore')
    log.info(" >>")
    try:
        by_company = df.groupby(["fornitore"]).sum()
        by_company["totals"] = by_company["sesso_maschile"] + by_company["sesso_femminile"]
        by_company.reset_index(level=0, inplace=True)

        values = by_company["totals"]
        labels = by_company["fornitore"]
        ax.pie(values, labels=labels, colors=["#dfeef4", "#c2e7f6", "#7fd2f3"], autopct='%1.1f%%')
        ax.set_title("Distribuzione per fornitore", fontsize=18)
        
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
        ax.set_title("Distribuzione per eta'", fontsize=18)
    
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def main( args:argparse.Namespace ) -> ResultValue :
    log = logging.getLogger('Main')
    log.info(" >>")
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        if args.download == True:
            today = dt.datetime.now().strftime("%Y%m%d")
            data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                    ,".."
                                                    ,"data", "{dt}_vaccinazioni.csv".format(dt=today))
            url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv"
            rv = download_csv_file(url=url, data_file=data_file)
            if rv.is_in_error():
                msg = "Data download error: {e}".format(e=rv.value)
                log.error(msg)
                print(msg)
            else:
                msg = "Data downloaded."
                log.info(msg)
                print(msg)

        if args.chart == True:
            data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                    ,".."
                                                    ,"data", "vaccinazioni.csv")
            rv = create_dataframe(data_file=data_file)
            if rv.is_in_error():
                log.error(rv.value())
            else:
                df = rv.value()
                region_name = "Lombardia"
                mask_region = (df["nome_area"] == region_name)
                df_region = df.loc[mask_region, ["data_somministrazione", "totali", 'fascia_anagrafica', "sesso_maschile","sesso_femminile", "fornitore", "prima_dose", "seconda_dose"]]

                fig = plt.figure(figsize=(20, 10))
                gs1 = gridspec.GridSpec(1, 1
                           ,hspace=0.2
                           ,wspace=0.1 
                           ,figure=fig)
                ax = []
                ax.append(fig.add_subplot(gs1[0,0]))
                idx = 0

                rv = plot_vaccinations_by_time(df_region, ax=ax[idx])

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
    parser.add_argument("--download", "-d", action='store_true', help="Data download.")
    parser.add_argument("--chart",    "-c", action='store_true', help="Chart.")
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv.is_ok() == True else os.EX_USAGE
    sys.exit(ret_val)

