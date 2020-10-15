# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os
import re
import json
import codecs
import locale
import requests
import datetime

import tabula
from tabula import read_pdf

import pandas as pd


# %%
#----------------------------------------------------------------
# Configurations section
#----------------------------------------------------------------

# Url of the pdf file to download:
url_region_pdf = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/schede-riepilogative/regioni/dpc-covid19-ita-scheda-regioni-latest.pdf"
                  
#----------------------------------------------------------------
#
#----------------------------------------------------------------
now = datetime.datetime.now()
sample_date = now.strftime("%d/%m/%Y")

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
ok_statuses = [200, 201, 202]
data_file_path = os.path.join("..","data")
#data_file_path = os.path.join(os.sep,"tmp")

pdf_file_name = os.path.join(os.sep, "tmp", "temp_data_file.pdf")
it_data_file = os.path.join(data_file_path, "virus-it.csv")
it_tmp_data_file = os.path.join(data_file_path, "virus-it-{dt}.csv".format(dt=now.strftime("%Y%m%d")))

lomb_data_file = os.path.join(data_file_path, "virus-lombardia.csv")
lomb_tmp_data_file = os.path.join(data_file_path, "virus-lombardia-{dt}.csv".format(dt=now.strftime("%Y%m%d")))


# %%
#result = requests.get(url_province_latest)
#if result.status_code not in ok_statuses:
#    assert "Get data failed. Received error code: {er}".format(er=str(result.status_code))
    
#with codecs.open(prov_data_file, "w", "utf-8") as fh:
#    fh.write(result.text)


# %%
#----------------------------------------------------------------
#
#----------------------------------------------------------------

def get_web_file(url):
    """
    
    :param url: 
    :return (rv, content):
    """
    rv = False
    result = None
    try:
        result = requests.get(url_region_pdf)
        if result.status_code not in ok_statuses:
            print("Get data failed. Received error code: {er}".format(er=str(result.status_code)))
        else:
            result = result.content
    except Exception as ex:
        print("get_web_file failed - {ex}".format(ex=ex))
    else:
        rv = True
    return (rv, result)    
        
def save_content_to_file(file_name, content):
    """
    
    :param file_name: 
    :return rv:
    """
    rv = False
    try:
        with open(file_name, "wb") as fh:
            fh.write(content)
    except Exception as ex:
        print("save_content_to_file failed - {ex}".format(ex=ex))
    else:
        rv = True
    return rv
   
def pdf_to_dataframe(pdf_file_name):
    """
    
    :param version: valid values v1 or v2; 
    :param pdf_file_name: 
    :return rv:
    """
    rv = False
    df = None
    try:
        df = tabula.read_pdf(pdf_file_name, pages='all')
        #print("Df list len: {l}".format(l=len(df)))
        
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
        #print("{lst}".format(lst=list_reg))
        df = pd.DataFrame([line.split(",") for line in list_reg])
        rv = True

    except Exception as ex:
        print("pdf_to_dataframe failed - {ex}".format(ex=ex))
    return (rv, df)

def get_row_from_Italy_df(df):
    """
    :param df: 
    :return (rv, content):
    """
    rv = False
    csv_row = []
    try:
        pass
#        csv_row.append(sample_date)
#        
#        infected_label = df.columns.values[0]
#        infected_num = locale.atoi(df.columns.values[1])
#        csv_row.append(str(infected_num))
#        
#        df.set_index(["ATTUALMENTE POSITIVI"], inplace=True)
#        df["Totals"] = df[df.columns[0]].apply(lambda row: int(row) if row.is_integer() else int(row * 1000) )
#        
#        tot_deads = df.loc["TOTALE DECEDUTI", ['Totals']]
#        tot_deads = str(int(tot_deads.values[0]))
#        csv_row.append(tot_deads)
#        
#        tot_recovered = df.loc["TOTALE GUARITI", ['Totals']]
#        tot_recovered = str(int(tot_recovered.values[0]))
#        csv_row.append(tot_recovered)
#        
#        tot_infected = df.loc["CASI TOTALI", ['Totals']]
#        tot_infected = str(int(tot_infected.values[0]))
#        csv_row.append(tot_infected)
#        
#        csv_row = ",".join(csv_row)
        
    except Exception as ex:
        print("get_row_from_Italy_df failed - {ex}".format(ex=ex))
    else:
        rv = True
    return (rv, csv_row)

def append_row(file_name, row):
    """
    
    :param file_name:
    :param row:
    """
    rv = False
    try:
        with open(file_name, 'a') as fh:
            row = row + "\n"
            fh.write(row)
    except Exception as ex:
        print("append_row failed - {ex}".format(ex=ex))
    else:
        rv = True
    return rv

def refactor_region_df(df, report_date:str):
    """
    
    :param df: a list vor v2 or a dataframe for v1
    :return (rv, df_region):
    """
    rv = False
    df_res = None
    try:
        df_res = df
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
                              ,df_res.columns[14]: "INCREMENTOTAMPONI" 
                          },
                      inplace = True)
        rv = True  
        df_res["REPORT DATE"] = report_date
        df_res.set_index("Regione", inplace=True)

    except Exception as ex:
        print("refactor_region_df failed - {ex}".format(ex=ex))
    print("rv -> {rv}".format(rv=rv))
    return (rv, df_res)

def get_region_row(df, region_name):
    """
    
    :param df: 
    :param region_name: 
    :return (rv, row):
    """
    rv = False
    row = None
    try:
        csv_row = []
        csv_row.append(sample_date)
        
        value = df.loc[region_name]['Ricoverati con sintomi']
        csv_row.append(value)
        
        value = df.loc[region_name]['Terapia intensiva']
        csv_row.append(value)

        value = df.loc[region_name]['Isolamento domiciliare']
        csv_row.append(value)

        value = df.loc[region_name]['Totale attualmente positivi']
        csv_row.append(value)

        value = df.loc[region_name]['DIMESSI/GUARITI']
        csv_row.append(value)
        
        value = df.loc[region_name]['DECEDUTI']
        csv_row.append(value)
        
        value = df.loc[region_name]['CASI TOTALI']
        csv_row.append(value)

        value = df.loc[region_name]['TAMPONI']
        csv_row.append(value)        
        
        row = ",".join(csv_row)
        
    except Exception as ex:
        print("get_region_row failed - {ex}".format(ex=ex))
    else:
        rv = True  
    return (rv, row)


# %%
#----------------------------------------------------------------
# Download the new dataset and append the new data in the csv
# files.
#
# Pay attention to the date: it is calculated as "now" so if the
# data aren't of today you shoud change the value by hand.
#----------------------------------------------------------------

df_regions = None
df_Italy = None

rv = False
result = get_web_file(url_region_pdf)
if result[0] == True:
    rv = save_content_to_file(pdf_file_name, result[1])
else:
    assert False, "File download failure."
    
if rv == True:
    df_list = pdf_to_dataframe(pdf_file_name)
if df_list[0] == True:
    df_regions = df_list[1][0]
else:
    assert False, "Unable to download or save the data file."


row_lomb = None
df_regions = refactor_region_df(df_regions, version="v2")
if df_regions[0] == True:
    df_regions = df_regions[1]
    row_lomb = get_region_row(df_regions, "Lombardia")
    if row_lomb[0] == False:
        assert False, "Region dataframe refactoring failed."
else:
    assert False, "Cannot create regions dataframe."
    
with open(lomb_data_file, 'r') as src, open(lomb_tmp_data_file, 'w') as dst: 
    dst.write(src.read())
    dst.close()
    src.close()
    rv = append_row(lomb_tmp_data_file, row_lomb[1])
    
print("Done")    


# %%
df_regions


# %%



