import sys, os
import math
import json
import time
import random
from datetime import datetime
from .api import *

def generate_data(chart_type: str):
    """
    Generates dynamic mock data according to the specified chart type.

    Parameters
    ----------
    chart_type : str
        The type of chart requiring data (e.g., 'line', 'sequences', 'surface').

    Returns
    -------
    Any
        A data structure suitable for the given chart type.
    """
    if chart_type in ['sequence', 'line', 'bar']:
        return round(random.uniform(50, 150), 2)
    elif chart_type in ['sequences', 'lines', 'bars']:
        return [["A", "B"], [round(random.uniform(50, 150), 2), round(random.uniform(30, 130), 2)]]
    elif chart_type == 'scatter':
        return [round(random.uniform(50, 150), 2), round(random.uniform(30, 130), 2)]
    elif chart_type == 'area':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        return [dimension, value]
    elif chart_type == 'areas':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        valueA = [round(random.uniform(50, 150), 2) for _ in dimension]
        valueB = [round(random.uniform(50, 150), 2) for _ in dimension]
        series = ["A", "B"]
        value = [valueA, valueB]
        return [dimension, series, value]
    elif chart_type == 'pie':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        return [dimension, value]
    elif chart_type == 'radar':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        valueMax = [150 for _ in dimension]
        return [dimension, valueMax, value]
    elif chart_type == 'surface':
        start, stop, step = -10, 10, 1
        xRange = [start + i * step for i in range(int(math.ceil((stop - start) / step)))]
        yRange = [start + i * step for i in range(int(math.ceil((stop - start) / step)))]
        zValues = [[x,y,3*x*x+y+random.uniform(0,1)*50] for x in xRange for y in yRange]
        axis = ["moneyness", "dte", "vega"]
        shape = [len(xRange), len(yRange)]
        return [axis, shape, zValues]
    elif chart_type == 'text':
        return f'You have a text:\n {random.uniform(0,1)*50}'
    elif chart_type == 'gauge':
        return ['Delta', [-1.0, 1.0], random.uniform(-1,1)]
    else:
        return None

def simulate(chart, chart_type, num=20000, freq=0.1):
    """
    Simulates a continuous data stream by generating data and pushing it 
    to the chart object with a time delay.

    Parameters
    ----------
    chart : DataStream
        The chart object instance (e.g., Line, Scatter) to which data is pushed.
    chart_type : str
        The type of data to generate, matching the chart.
    num : int, optional
        The total number of data points to generate. Defaults to 20000.
    freq : float, optional
        The time interval (in seconds) between data pushes. Defaults to 0.1s.
    """
    for i in range(num):
        data = generate_data(chart_type)
        chart.fresh(data)
        time.sleep(freq)

def simulate_all():
    """
    Initializes one instance of every available chart type with the keyword 
    'test' and starts a data simulation thread for each.

    Note: The API Server must be initialized and running before calling this function.
    """
    chart_obj_list = [Sequence, Line, Bar, Sequences, Lines, Bars, Scatter, Area, Areas, Pie, Radar, Surface, Text, Gauge]
    key_word_list = ['test' for _ in chart_obj_list]
    chart_type_list = ['sequence', 'line', 'bar', 'sequences', 'lines', 'bars', 'scatter', 'area', 'areas', 'pie', 'radar', 'surface', 'text', 'gauge']

    for chart_obj, key_word, chart_type in zip(chart_obj_list, key_word_list, chart_type_list):
        obj = chart_obj(key_word)
        obj.execute(simulate, chart_type)


