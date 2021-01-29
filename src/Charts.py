
import os
import sys
import locale
import logging
import argparse
import datetime as dt

import pandas as pd                     # type: ignore 
import matplotlib as mp                 # type: ignore        

from matplotlib import pyplot as plt    # type: ignore     
import matplotlib.dates as mdates       # type: ignore 
import matplotlib.gridspec as gridspec  # type: ignore      
import matplotlib.ticker as mticker     # type: ignore   

from logger_init import init_logger
from result_value import ResultKo, ResultOk, ResultValue
from ETL import load_data_file
from ChartTools import set_axes_common_properties
from ChartTools import remove_tick_lines

# ----------------------------------------
# 
# ----------------------------------------
def chart_single_line(x:pd.Series, y:pd.Series, context:dict)-> ResultValue :
    log = logging.getLogger('chart_composite')
    log.info(" >>")
    try:
        if context.get('region name') is None:
            msg = "Error: region name field is mandatory."
            log.error(msg)
            return ResultKo(Exception(msg))
        else:
            region_name = context["region name"]
        if context.get('title') is None:
            msg = "Error: title field is mandatory."
            log.error(msg)
            return ResultKo(Exception(msg))
        else:
            title = context["title"]
        fig = plt.figure(figsize=(20, 10))
        gs1 = gridspec.GridSpec(1, 1
                               ,hspace=0.2
                               ,wspace=0.1 
                               ,figure=fig)

        ax = []
        ax.append(fig.add_subplot(gs1[0,0]))
        idx = 0
        set_axes_common_properties(ax[0], no_grid=False)

        remove_tick_lines('x', ax[idx])
        remove_tick_lines('y', ax[idx])
        ax[idx].set_xticks(x)
        ax[idx].set_xticklabels(x, rotation=80)

        ax[idx].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))
        ax[idx].xaxis.set_minor_formatter(mdates.DateFormatter("%d/%m"))
        ax[idx].xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax[idx].set_ylabel("Numero", fontsize=14)
        ax[idx].set_xlabel("Data", fontsize=14)
        ax[idx].set_title("{reg} - {title} ".format(title=title, reg=region_name), fontsize=18)

        ax[idx].scatter(x, y, color="#b9290a", s=30, marker='.', label=title)
        ax[idx].plot(x, y, 'b-', linewidth=2, color="#f09352")
        if context.get('dad begin date') is not None:
            ax[idx].axvline(context.get('dad begin date'), color="#048f9e")     
            ax[idx].text(0.65, 0.25, 'Inizio dad scuole superiori'
                         ,horizontalalignment='center', verticalalignment='center'
                         ,transform=ax[idx].transAxes
                         ,rotation=90
                         ,color="#048f9e", fontsize=12)

        ax[idx].legend(fontsize=12, loc='upper left')
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def chart_composite(x:pd.Series, y_one:pd.Series, y_two:pd.Series, region_name:str)-> ResultValue :
    log = logging.getLogger('chart_composite')
    log.info(" >>")
    try:
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
        
        fig = plt.figure(figsize=(20, 10))
        gs1 = gridspec.GridSpec(1, 1
                               ,hspace=0.2
                               ,wspace=0.1 
                               ,figure=fig)

        ax = []
        ax.append(fig.add_subplot(gs1[0,0]))
        idx = 0
        set_axes_common_properties(ax[0], no_grid=False)

        ax[idx].get_yaxis().set_major_formatter(mp.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

        remove_tick_lines('x', ax[idx])
        remove_tick_lines('y', ax[idx])

        ax[idx].set_xticks(x)
        ax[idx].set_xticklabels(x, rotation=80)

        ax[idx].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))
        ax[idx].xaxis.set_minor_formatter(mdates.DateFormatter("%d/%m"))
        ax[idx].xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax[idx].set_ylabel("Numero", fontsize=14)
        ax[idx].set_xlabel("Data", fontsize=14)
        ax[idx].set_title("{reg} - {title} ".format(title="Deceduti/Ammalati - totale", reg=region_name), fontsize=18)

        ax[idx].scatter(x, y_one, color="#b9290a", s=30, marker='.')
        ln_one = ax[idx].plot(x, y_one, 'b-', linewidth=2, color="#f09352", label="Totale ammalati")

        dec_color = "#8f0013"
        ax_dec = ax[idx].twinx()

        remove_tick_lines('y', ax_dec)
        set_axes_common_properties(ax_dec, no_grid=True)
        ax_dec.scatter(x, y_two, color=dec_color, s=30, marker='.')
        
        ln_two = ax_dec.plot(x, y_two, 'b-', linewidth=2, color=dec_color, label="Totale deceduti")
        
        ax_dec.set_ylabel("Totale deceduti", fontsize=14)
        ax_dec.yaxis.label.set_color(dec_color)
        ax_dec.tick_params(axis='y', colors=dec_color)

        lns = ln_one+ln_two
        labs = [l.get_label() for l in lns]
        ax[idx].legend(lns, labs, loc='upper left')

       #ax_dec.axhline(c='#f0b4a7', lw=1)

        #ax[idx].legend(fontsize=12, loc='upper left')

    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(True)

def main( args:argparse.Namespace ) -> ResultValue :
    log = logging.getLogger('Main')
    log.info(" >>")
    data_file = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                            ,".."
                                            ,"data", "report_data.csv")
    result = load_data_file(data_file=data_file)
    if result.is_in_error():
        return ResultKo(Exception("load data failed."))
    df = result()
    
    region_name = 'Lombardia'
    mask = df['Regione'] == region_name
    region_df = df.loc[mask,:]
    region_df = region_df.sort_values(["REPORT DATE"])
    x = region_df["REPORT DATE"] 
    y = region_df["DECEDUTI"]
    y_tot = region_df["CASI TOTALI - A"]

    chart_composite(x, y, y_tot, region_name)
    log.info(" <<")
    return ResultOk(True)

if __name__ == "__main__":
    init_logger('/tmp', "etl.log",log_level=logging.DEBUG, std_out_log_level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv.is_ok() == True else os.EX_USAGE
    sys.exit(ret_val)
