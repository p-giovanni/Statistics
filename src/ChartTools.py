import os
import re
import json
import codecs
import locale
import requests
import datetime
import logging

from typing import Union, Optional, Tuple, List, cast

import matplotlib as mp                 # type: ignore
from matplotlib import pyplot as plt    # type: ignore
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator) # type: ignore
import matplotlib.dates as mdates       # type: ignore
import matplotlib.gridspec as gridspec  # type: ignore

import numpy as np # type: ignore
import pandas as pd# type: ignore 

from typing import Any, Tuple, Dict, Union

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

def text_box(ax:mp.axes.Axes
            ,text:str
            ,colors:List[str]=["#FFFFFF", "#000000"]
            ,fontsize:int=14
            ,x:int=0
            ,y:int=0)-> bool:
    log = logging.getLogger('text_box')
    log.info(" >>")
    rv = False
    try:
        edgecolor = "none"
        boxstyle = "square"
        if len(colors) >= 3 and colors[2] is not None:
            edgecolor = colors[2]
            boxstyle = "round,pad=1"
        ax.text(x, y
               ,text
               ,ha="left", va="center" 
               ,bbox=dict(boxstyle = boxstyle, facecolor = colors[0], edgecolor = edgecolor)
               ,color=colors[1]
               ,fontsize=fontsize)
        set_axes_common_properties(ax, no_grid=True)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        
    except Exception as ex:
        print("text_box failed - {ex}".format(ex=ex))
    else:
        rv = True    
    log.info(" <<")
    return rv    

def remove_tick_lines(which:str, ax:mp.axes.Axes)-> None :
    if which == 'y':
        for line in ax.yaxis.get_majorticklines():
            line.set_visible(False)
    elif which == 'x':
        for line in ax.xaxis.get_majorticklines():
            line.set_visible(False)
    else:
        assert False, "Wrong axis parameter."

def every_nth_tick(ax:mp.axes.Axes, every_nth:int = 2)-> None :
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

def autolabel(rects, ax:mp.axes.Axes, dec_no:int = 0, fontsize:int = 8)-> None :
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., height + (height * 0.01),
                '%s' % round(height, dec_no),
                ha='center', va='bottom'
               ,fontsize=fontsize)
        
def set_axes_common_properties(axe:mp.axes.Axes, no_grid:bool = False, border:bool = False)-> bool :
    rv = False
    try:
        axe.spines['top'].set_visible(border)
        axe.spines['left'].set_visible(border)
        axe.spines['right'].set_visible(border)
        axe.spines['bottom'].set_visible(border)
        if no_grid == False:
            axe.grid(color='#636262', linestyle='-.', linewidth=0.2)
        rv = True
    except Exception as ex:
        print("Errore - {e}".format(e=str(ex)))
        
    return rv



