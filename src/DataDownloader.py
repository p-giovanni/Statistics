import os
import re
import sys
import csv
import json
import codecs
import locale
import requests
import argparse
import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
#from datetime import timedelta, date

from typing import Any, Tuple, Dict
from typing import Union, Optional, Tuple, List, cast

import tabula               # type: ignore
from tabula import read_pdf # type: ignore
import pandas as pd         # type: ignore
import numpy as np          # type: ignore

from result_value import ResultKo, ResultOk, ResultValue

from logger_init import init_logger

# ----------------------------------------
ok_statuses = [200, 201, 202]
# ----------------------------------------

def get_web_file(url:str) -> ResultValue :
    log = logging.getLogger('get_web_file')
    log.info(" >>")
    log.info("Url: {u}".format(u=url))
    rv:ResultValue = ResultKo(Exception("Error"))
    result_content:bytes = bytearray()
    try:
        result = requests.get(url)
        if result.status_code not in ok_statuses:
            log.info("Get data failed. Received error code: {er}".format(er=str(result.status_code)))
        else:
            result_content = result.content
            rv = ResultOk(result_content)
    except Exception as ex:
        log.error(" failed - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info("get_web_file ({rv}) <<".format(rv=rv))
    return rv
        
def save_content_to_file(file_name:str, content:bytes) -> ResultValue :
    log = logging.getLogger('save_content_to_file')
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        with open(file_name, "wb") as fh:
            fh.write(content)
    except Exception as ex:
        log.error("save_content_to_file failed - {ex}".format(ex=ex))
        rv = ResultKo(ex)
    else:
        rv = ResultOk(True)
    return rv
   
def pdf_to_dataframe(pdf_file_name:str) -> ResultValue :
    log = logging.getLogger('pdf_to_dataframe')
    log.info(" ({fn}) >>".format(fn=pdf_file_name))
    df = None
    report_date:dt.datetime = dt.datetime(1964,8,3,0,0)
    try:
        df = tabula.read_pdf(pdf_file_name, pages='all')
        #log.info("Df list len: {l}".format(l=len(df)))
        
        csv_file = os.path.splitext(pdf_file_name)[0] + ".csv"
        tabula.convert_into(pdf_file_name, csv_file, output_format="csv", pages='all')
        list_reg = [] 
        with open(csv_file, "r") as fh:
            start = False
            end = False
            reg = re.compile("(\d{1,3}) (\d)")
            for line in fh:
                if line.startswith("Lombardia") == True:
                    start = True
                if line.startswith("TOTALE") == True:
                    end = True
                    start = False
                if start == True:
                    line = line.replace(".", "")
                    line = line.replace("+ ", "")
                    #line = line.replace(" ", ",")
                    line = reg.sub("\\1,\\2", line)
                    line = line.replace("\n", "")
                    list_reg.append(line)
                if 'Aggiornamento casi Covid-19' in line:
                    parts = line.split(" - ")
                    if len(parts) > 1:
                        report_date_s = parts[0]
                        if parts[0][0] == "\"":
                            report_date_s = parts[0][1:]
                        log.debug(report_date)
                        report_date_rv = translate_to_date(report_date_s.split(" "))
                        if report_date_rv.is_in_error():
                            msg = "Error in date translation."
                            log.error(msg)
                            return ResultKo(Exception(msg))
                        else:
                            report_date = report_date_rv()
                elif 'AGGIORNAMENTO ' in line:
                    parts = line.split(" ")
                    if len(parts) > 1:
                        report_date = dt.datetime.strptime(parts[1], '%d/%m/%Y')
                        log.info("RDate: {rd}".format(rd=report_date))
        
        df = pd.DataFrame([line.split(",") for line in list_reg])
        
    except Exception as ex:
        log.info("pdf_to_dataframe failed - {ex}".format(ex=ex))
        return ResultKo(ex)
    log.info(" (report_date={rd}) <<".format(rd=report_date))
    return ResultOk((df, report_date))

def translate_to_date(report_date:List[str])-> ResultValue :
    #log.info("translate_to_date {p} >>".format(p=str(dt)))
    log = logging.getLogger('data_downloader')
    date = None
    months_names = {
        "gennaio":    1
        ,"febbraio":  2
        ,"marzo":     3
        ,"aprile":    4
        ,"maggio":    5
        ,"giugno":    6
        ,"luglio":    7
        ,"agosto":    8
        ,"settembre": 9
        ,"ottobre":  10
        ,"novembre": 11
        ,"dicembre": 12
    }
    if len(report_date) >= 3 :
        try:
            day = report_date[0]
            year = report_date[2]
            month = months_names.get(report_date[1].lower())
            if month is not None:
                #log.info("Dt: {d}/{m}/{y}".format(d=day,m=month,y=year))
                date = dt.datetime(year=int(year), month=int(month), day=int(day))
            else:
                ex = Exception("Unknown month: {m}".format(m=report_date[1]))
                log.error("Error in date translation - {e}".format(e=ex))
                return ResultKo(ex)
        except Exception as ex:
            log.error("Exception - {e}".format(e=ex))
            return ResultKo(ex)
    else:
        exc = Exception("Wrong format: {dt}".format(dt=str(dt)))
        log.error("Error in date translation - {e}".format(e=exc))
        return ResultKo(exc)
    return ResultOk(date)
    
def refactor_region_df(df:pd.DataFrame, report_date:dt.datetime, pdf_version:str="v1") -> ResultValue :
    log = logging.getLogger('refactor_region_df')
    log.info(" ({ver} - {dt}) >>".format(dt=report_date,ver=pdf_version))
    log.debug("\n{d}".format(d=str(df)))
    df_res = None
    try:
        df_res = df
        if pdf_version == "v1":
            df_res.rename(columns={df_res.columns[ 0]: "Regione"
                                  ,df_res.columns[ 1]: "Ricoverati con sintomi"
                                  ,df_res.columns[ 2]: "Terapia intensiva"
                                  ,df_res.columns[ 3]: "Isolamento domiciliare"
                                  ,df_res.columns[ 4]: "Totale attualmente positivi"
                                  ,df_res.columns[ 5]: "DIMESSI/GUARITI"
                                  ,df_res.columns[ 6]: "DECEDUTI"
                                  ,df_res.columns[ 7]: "CASI TOTALI - A"
                                  ,df_res.columns[ 8]: "INCREMENTO CASI TOTALI (rispetto al giorno precedente)"
                                  ,df_res.columns[ 9]: "Casi identificatidal sospettodiagnostico"
                                  ,df_res.columns[10]: "Casi identificatida attività discreening"
                                  ,df_res.columns[11]: "CASI TOTALI - B"
                                  ,df_res.columns[12]: "Totale casi testati"
                                  ,df_res.columns[13]: "Totale tamponi effettuati"
                                  ,df_res.columns[14]: "INCREMENTO TAMPONI" 
                          },
                      inplace = True)
        elif pdf_version in ["v6"]:
            df_res.rename(columns={df_res.columns[ 0]: "Regione"
                                  ,df_res.columns[ 1]: "Ricoverati con sintomi"
                                  ,df_res.columns[ 2]: "Terapia intensiva"
                                  ,df_res.columns[ 3]: "Terapia intensiva / Ingressi delgiorno"
                                  ,df_res.columns[ 4]: "Isolamento domiciliare"
                                  ,df_res.columns[ 5]: "Totale attualmente positivi"
                                  ,df_res.columns[ 6]: "DIMESSI/GUARITI"
                                  ,df_res.columns[ 7]: "DECEDUTI"
                                  ,df_res.columns[ 8]: "CASI TOTALI - A"
                                  ,df_res.columns[ 9]: "INCREMENTO CASI TOTALI (rispetto al giorno precedente)"
                                  ,df_res.columns[10]: "Totale persone testate"
                                  ,df_res.columns[11]: "Totale tamponi effettuati"
                                  ,df_res.columns[12]: "INCREMENTO TAMPONI" 
                          },
                      inplace = True)         

        elif pdf_version in ["v5"]:
            df_res.rename(columns={df_res.columns[ 0]: "Regione"
                                  ,df_res.columns[ 1]: "Ricoverati con sintomi"
                                  ,df_res.columns[ 2]: "Terapia intensiva"
                                  ,df_res.columns[ 3]: "Isolamento domiciliare"
                                  ,df_res.columns[ 4]: "Totale attualmente positivi"
                                  ,df_res.columns[ 5]: "DIMESSI/GUARITI"
                                  ,df_res.columns[ 6]: "DECEDUTI"
                                  ,df_res.columns[ 7]: "CASI TOTALI - A"
                                  ,df_res.columns[ 8]: "INCREMENTO CASI TOTALI (rispetto al giorno precedente)"
                                  ,df_res.columns[ 9]: "Totale tamponi effettuati"
                                  ,df_res.columns[10]: "Casi testati"
              },
            inplace = True)         
        else:
            ex = Exception("Unknown pdf version: {pv}".format(pv=pdf_version))
            log.error("Error - {ex}".format(ex=ex))
            return ResultKo(ex)
        
        df_res["REPORT DATE"] = report_date #pd.to_datetime(report_date, format="%d/%m/%Y")
        df_res["SCHEMA VERSION"] = pdf_version
        log.debug("\n{d}".format(d=str(df_res)))
        
    except Exception as ex:
        log.error(" failed - {ex}".format(ex=ex))
        return ResultKo(ex)

    log.info(" <<")
    return ResultOk(df_res)

def create_dataframe(pdf_url:str
                    ,local_file_path:str
                    ,pdf_version:str) -> ResultValue :
    log = logging.getLogger('create_dataframe')
    log.info(" >>")
    ret_data_frame:ResultValue = ResultKo(Exception("Error"))
    try:
        file_downloaded_rv = get_web_file(pdf_url)
        if file_downloaded_rv.is_ok:
            if save_content_to_file(local_file_path, cast(bytes, file_downloaded_rv())) == True:
                to_df_rv  = pdf_to_dataframe(local_file_path)
                if to_df_rv.is_ok():
                    df, report_date = to_df_rv()
                    ret_data_frame = refactor_region_df(df, report_date, pdf_version)

    except Exception as ex:
        log.error(" failed - {ex}".format(ex=ex))
        return ResultKo(ex)
        
    log.info(" ({rv}) <<".format(rv=rv))
    return ret_data_frame

def save_df_to_csv(df:pd.DataFrame
                  ,csv_file_name:str
                  ,column_list:List[str]
                  ,sorting_col:str) -> ResultValue :
    log = logging.getLogger('save_df_to_csv')
    log.info(" >>")
    try:
        mode = 'w'
        header = True
        df = df.loc[:,column_list]
        df.sort_values(by=[sorting_col], inplace=True)    
        if os.path.isfile(csv_file_name) == True:
            header = False
            mode = 'a'
            with open(csv_file_name) as fh:
                csv_reader = csv.reader(fh)
                csv_headings = next(csv_reader)
                if csv_headings != column_list:
                    ex = Exception("Columns differnt from file header\n {l1}\n {l2}\n".format(l1=column_list, l2=csv_headings))
                    log.error("Error in date translation - {e}".format(e=ex))
                    return ResultKo(ex)
        log.info("Save to: {f} headers: {h}".format(f=csv_file_name, h=header))
        df.to_csv(csv_file_name, mode=mode, header = header, index=False)
    
    except Exception as ex:
        log.error(" failed - {ex}".format(ex=ex))
        return ResultKo(ex)
        
    log.info(" <<")
    return ResultOk(True)

def get_version_from_date(date:dt.datetime)-> ResultValue :
    log = logging.getLogger('get_version_from_date')
    log.info(" >>")
    version = ""
    if date >= dt.datetime.strptime("03/12/2020", '%d/%m/%Y'):
        version = "v6"
    elif date >= dt.datetime.strptime("25/06/2020", '%d/%m/%Y'):
        version = "v1"
    elif date >= dt.datetime.strptime("01/05/2020", '%d/%m/%Y'):
        version = "v5"
    else:
        ex = Exception("Unable to find a valid version for {d}".format(d=date))
        log.error("Error {e}".format(e=ex))
        return ResultKo(ex)
    log.info(" <<")
    return ResultOk(version)

def append_new_data(report_date:str, context:dict) -> ResultValue :
    log = logging.getLogger('append_new_data')
    log.info(" >>")
    try:
        date = dt.datetime.strptime(report_date, '%d/%m/%Y')
        
        version = get_version_from_date(date)
        if version.is_in_error():
            return ResultKo(version())
        pdf_file_name = "dpc-covid19-ita-scheda-regioni-{y}{m}{d}.pdf".format(y=date.year
                                                                             ,m=str(date.month).rjust(2, '0')
                                                                             ,d=str(date.day).rjust(2, '0'))
        pdf_url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/schede-riepilogative/regioni/{fn}".format(fn=pdf_file_name)
        log.info("Url: {u}".format(u=pdf_url))
        
        content = get_web_file(pdf_url)
        if content.is_in_error():
            return ResultKo(content())

        file_name = os.path.join(context["temp_dir"], pdf_file_name)
        if save_content_to_file(file_name, cast(bytes, content())).is_in_error():
            return ResultKo(Exception("Error in save_content_to_file."))

        rv = pdf_to_dataframe(file_name)
        if rv.is_in_error():
            return ResultKo(Exception("Error in pdf_to_dataframe."))

        df, report_read_date = rv()
        df_regions = refactor_region_df(df, report_read_date, version())
        if df_regions.is_in_error():
            return ResultKo(df_regions())

        if context["save"] == True:
            rv = save_df_to_csv(df_regions(), context["data file"], context["columns"], context["sort column"])
            if rv.is_in_error():
                return ResultKo(rv())
    except Exception as ex:
        log.error("append_new_data failed - {ex}".format(ex=ex))
        return ResultKo(ex)
        
    log.info(" <<")
    return ResultOk(df_regions)

def daterange(start_date:dt.datetime, end_date:dt.datetime):
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)

def load_date_range_reports(begin:dt.datetime, to:dt.datetime, context:dict)-> ResultValue :
    log = logging.getLogger('load_date_range_reports')
    log.info(" >>")
    try:
        for single_date in daterange(begin, to):
            df = append_new_data(single_date.strftime("%d/%m/%Y"), context)
            if df.is_in_error():
                return ResultKo(Exception("Failure in append_new_data."))

    except Exception as ex:
        log.error(" failed - {ex}".format(ex=ex))
        return ResultKo(ex)
        
    log.info(" <<")
    return ResultOk(df)

# ----------------------------------------
# Notebook content - END.
# ----------------------------------------

def main( args:argparse.Namespace ) -> bool:
    log = logging.getLogger('Main')
    log.info(" >>")
    rv:ResultValue = ResultKo(Exception("Error"))
    try:
        date_format = '%d/%m/%Y'
        data_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__))
                                     ,".."
                                     ,"data", "reduced_report_data.csv")
        if args.date_range is not None:
            begin_dt = dt.datetime.strptime(args.date_range[0], date_format)
            end_dt   = dt.datetime.strptime(args.date_range[1], date_format)
            if end_dt < begin_dt:
                log.error("Wrong date range: {b} < {e}".format(b=begin_dt, e=end_dt))
                return False

            columns_report_charts = ["REPORT DATE","Regione"
                                    ,"Ricoverati con sintomi","Terapia intensiva","Totale attualmente positivi"
                                    ,"DECEDUTI"
                                    ,"Isolamento domiciliare"
                                    ,"CASI TOTALI - A"
                                    ,"Totale tamponi effettuati"
                                    ,"SCHEMA VERSION"]
            temp_content_dir = os.path.join(os.sep, 'tmp') 
            rv = load_date_range_reports(begin=begin_dt
                                            ,to=end_dt
                                            ,context={
                                                "temp_dir": temp_content_dir
                                               ,"data file": data_file_name
                                               ,"columns":columns_report_charts
                                               ,"save": True
                                               ,"sort column": "REPORT DATE"
                                            })
            rv = ResultOk(True)

        elif args.get_date_range is not None and args.get_date_range == True:
            df = pd.read_csv(data_file_name, sep=',')
            msg = "Data minima: {dmin} - data massima: {dmax} - numero righe: {nr}".format(nr=df.shape
                                                                                          ,dmin=df["REPORT DATE"].min()
                                                                                          ,dmax=df["REPORT DATE"].max())
            print(msg)
            log.info(msg)                                                                                          
            rv = ResultOk(True)
        else:
            msg = "Nothing to do!"
            rv = ResultOk(True)
 
    except Exception as ex:
        log.error("Exception caught - {ex}".format(ex=ex))
        return False
    log.info(" (Is ok: {rv}) <<".format(rv=rv.is_ok()))
    return rv.is_ok()

if __name__ == "__main__":
    init_logger('/tmp', "virus.log",log_level=logging.DEBUG, std_out_log_level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--date_range", "-dr", nargs=2, help="Date range of reports to download (dd/mm/yyyy).")
    parser.add_argument("--get_date_range", "-gdr", action='store_true', help="Returns the first and last date in the data file.")
    args = parser.parse_args()
    
    rv = main(args)

    ret_val = os.EX_OK if rv == True else os.EX_USAGE
    sys.exit(ret_val)

