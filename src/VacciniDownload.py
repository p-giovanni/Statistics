import os
import sys
import locale
import logging
import requests
import datetime as dt
import argparse

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

colors = ["#9aff33","#34ff33","#33ff98","#33fffe","#339aff","#3371ff","#5b33ff","#c133ff","#ff33d7"]

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

def create_delivered_dataframe(data_file:str)-> ResultValue:
    log = logging.getLogger('create_delivered_dataframe')
    log.info(" >>")
    try:
        df = pd.read_csv(data_file, sep=','
                        ,parse_dates=["data_consegna"])

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
        ln_one_color = "#9992e9"
        ln_two_color = "#92b7e9"
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
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
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

def plot_delivered_vaccines_quantity(df_delivered:pd.DataFrame, ax:mp.axes.Axes)-> ResultValue :
    log = logging.getLogger('plot_vaccinations_by_time')
    log.info(" >>")
    width = 1.2
    bar_space = width/3
    try:
        df_delivered.sort_values(by="data_consegna", inplace=True)
        by_date = df_delivered.groupby(["data_consegna"]).sum()
        by_date.reset_index(level=0, inplace=True)
              
        x_del = by_date["data_consegna"]
        y_del = by_date["numero_dosi"]
        
        remove_tick_lines('x', ax)
        remove_tick_lines('y', ax)
        set_axes_common_properties(ax, no_grid=True)

        ax.bar(x_del, y_del, color=colors[4], width=width, label='2020')
        ax.set_xticklabels(x_del, rotation=80)

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

def company_distribution(df:pd.DataFrame, ax:mp.axes.Axes)-> ResultValue :
    log = logging.getLogger('company_distribution')
    log.info(" >>")
    try:
        def autopct_format(values):
            def my_format(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                str_val = f'{val:n}'
                return '{v:d}'.format(v=val)
            return my_format

        colors = ["#9aff33","#34ff33","#33ff98","#33fffe","#339aff","#3371ff","#5b33ff","#c133ff","#ff33d7"]
        by_company = df.groupby(["fornitore"]).sum()
        by_company.reset_index(level=0, inplace=True)
        values = by_company["numero_dosi"]
        labels = by_company["fornitore"]
        ax.pie(values, labels=labels, colors=colors, autopct = autopct_format(values))
        ax.set_title("Vaccini consegnati", fontsize=18)

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
        today = dt.datetime.now().strftime("%Y%m%d")
            
        if args.download_vaccinazioni == True:
            file_name = "{dt}_vaccinazioni.csv".format(dt=today)
            url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv"
        if args.download_consegne == True:
            file_name = "{dt}_vaccini_consegnati.csv".format(dt=today)
            url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv"

        if args.download_vaccinazioni == True or args.download_consegne == True:
            data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                    ,".."
                                                    ,"data", file_name)
            rv = download_csv_file(url=url, data_file=data_file)
            if rv.is_in_error():
                msg = "Data download error: {e}".format(e=rv.value)
                log.error(msg)
            else:
                msg = "Data downloaded."
                log.info(msg)

        if args.chart == True:
            data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                    ,".."
                                                    ,"data", "vaccinazioni.csv")
            rv = create_dataframe(data_file=data_file)
            if rv.is_in_error():
                log.error(rv.value())
                return ResultKo(rv())
            df = rv.value()

            data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                    ,".."
                                                    ,"data", "vaccini_consegnati.csv")
            rv = create_delivered_dataframe(data_file=data_file)
            if rv.is_in_error():
                log.error(rv.value())
                return ResultKo(rv())
            df_delivered = rv()

            region_name = "Lombardia"
            mask_region = (df["nome_area"] == region_name)
            df_region = df.loc[mask_region, ["data_somministrazione", "totali", 'fascia_anagrafica', "sesso_maschile","sesso_femminile", "fornitore", "prima_dose", "seconda_dose"]]

            mask_region = (df_delivered["nome_area"] == region_name)
            df_delivered_region = df_delivered.loc[mask_region, ["fornitore","numero_dosi","data_consegna"]]


            fig = plt.figure(figsize=(20, 10))
            gs1 = gridspec.GridSpec(1, 1
                       ,hspace=0.2
                       ,wspace=0.1 
                       ,figure=fig)
            ax = []
            ax.append(fig.add_subplot(gs1[0,0]))
            idx = 0
                  
            result = plot_delivered_vaccines_quantity(df_delivered_region, ax=ax[idx])
               
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
    parser.add_argument("--download_vaccinazioni", "-dv", action='store_true', help="Download performed vaccinations file.")
    parser.add_argument("--download_consegne", "-dc", action='store_true', help="Download vaccines delivery.")
    parser.add_argument("--chart",    "-c", action='store_true', help="Chart.")
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv.is_ok() == True else os.EX_USAGE
    sys.exit(ret_val)

