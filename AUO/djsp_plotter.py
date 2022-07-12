import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
from pprint import pprint
from datetime import datetime
import argparse
from colorhash import ColorHash

from djsp_logger import DJSP_Logger

class DJSP_Plotter(object):
    def __init__(self, logger):
        self.logger = logger
    def _get_tooltip(self, wip_info):
        return str(wip_info)
    def _get_machine(self, wip_info):
        assert 'selected_eqp_id' in wip_info, 'There is no key named selected_eqp_id in wip_info'
        return '%s' %(wip_info['selected_eqp_id'])
    def _get_model_abbr(self, wip_info):
        assert 'model_abbr' in wip_info, 'There is no key named model_abbr in wip_info'
        return str(wip_info['model_abbr'])
    def _get_color(self, wip_info):
        # if wip_info['other'] == 'extend_xaxis':
        #     return '#FFFFFF'
        idle_color = {
            'IDLE': '#FFFF8F',
            'DOWN': '#FF0000',
            'PM': '#00FFFF',
            'DMQC': '#FF00FF',
            'TEST': '#98FB98',
        }
        idle_type = wip_info.get('other', None)
        if wip_info['sheet_status'] == 'RUN':
            return '#808080'
        elif idle_type in idle_color:
            return idle_color[idle_type]
        else:
            color = ColorHash(wip_info['model_abbr'])
            return color.hex
    def _get_gc_row(self, wip_info):
        assert 'start_time' in wip_info, 'There is no key named start_time in wip_info'
        assert 'finish_time' in wip_info, 'There is no key named finish_time in wip_info'
        start_str = wip_info['start_time']
        finish_str = wip_info['finish_time']
        row = [
            self._get_machine(wip_info),
            self._get_model_abbr(wip_info),
            self._get_color(wip_info),
            self._get_tooltip(wip_info),
        ]
        start_dt = datetime.strptime(start_str, '%Y/%m/%d %H:%M')
        finish_dt = datetime.strptime(finish_str, '%Y/%m/%d %H:%M')
        start_gcstr = 'new Date(%d,%d,%d,%d,%d,0)' %(start_dt.year, start_dt.month-1, start_dt.day, start_dt.hour, start_dt.minute)
        finish_gcstr = 'new Date(%d,%d,%d,%d,%d,0)' %(finish_dt.year, finish_dt.month-1, finish_dt.day, finish_dt.hour, finish_dt.minute)
        date_str = ',%s, %s' %(start_gcstr, finish_gcstr)
        row = str(row)[:-1] + date_str + ']'
        return row
    def plot_googlechart_timeline(self, html_out_file):
        history = self.logger.history
        # history = sorted(history, key=lambda wip_info : wip_info['machine_id'])
        history = sorted(history, key=lambda wip_info : wip_info['selected_eqp_id'])
        html_text = ''
        html_text += self.logger.google_chart_front_text
        
        for i, wip_info in enumerate(history):
            gc_row = self._get_gc_row(wip_info)
            gc_row = gc_row + ',\n'
            html_text += gc_row
        html_text += self.logger.google_chart_back_text
        with open(html_out_file, 'w') as f:
            f.write(html_text)

    def plot_plotly_timeline(self, html_name, color_by='job_id'):
        ### timeline
        ### x-axis: date
        if isinstance(color_by, str):
            data = self.logger.get_plotly_timeline_input(color_by)
            df = pd.DataFrame(data)
            fig = px.timeline(
                df, x_start='StartDateTime', x_end='FinishDateTime', y='machine_id', color='job_id', 
                hover_name='job_id', hover_data=['job_id', 'op_id', 'process_time', 'Start', 'Finish']
            )
            fig.update_layout(xaxis_type='date')    # ['-', 'linear', 'log', 'date', 'category', 'multicategory']
            fig.write_html(html_name)
        if isinstance(color_by, tuple):
            # colors = [ 'red', 'green', 'blue', 'orange', 'purple' ]
            color_maps = [ 
                px.colors.sequential.Reds[1:],      px.colors.sequential.Greens[1:],    px.colors.sequential.Blues[1:], 
                px.colors.sequential.Greys[1:],   px.colors.sequential.Purples[1:],   px.colors.sequential.Oranges[1:],
                px.colors.sequential.PuRd[1:]]
            color_discrete_map = {}
            for i in range(5):
                for j in range(10):
                    size = len(color_maps[i])
                    color_discrete_map[(i, j)] = color_maps[i][j%size]
            data = self.logger.get_plotly_timeline_input(color_by)
            print(data)
            df = pd.DataFrame(data)
            fig = px.timeline(
                df, x_start='StartDateTime', x_end='FinishDateTime', y='machine_id', color='color', 
                hover_name='job_id', hover_data=['job_id', 'op_id', 'process_time', 'Start', 'Finish'],
                color_discrete_map = color_discrete_map
            )
            fig.update_layout(xaxis_type='date')    # ['-', 'linear', 'log', 'date', 'category', 'multicategory']
            fig.write_html(html_name)




if __name__ == '__main__':
    # logger = DJSP_Logger()
    # logger.load('./debug.json')
    # # print(logger)
    # plotter = DJSP_Plotter(logger)
    # plotter.plot_googlechart_timeline('timeline/debug.html')

    ### run all
    # ortools_result_dir = '../ortools_result_6000'
    # ortools_result_dir = '../ortools_result_ban_noop_60'
    # result_dir = './agent/result'
    result_dir = './result/or-tools'
    
    # html_out_dir = 'timeline/6000'
    # html_out_dir = 'timeline/6000_noop'
    # html_out_dir = 'timeline/60_ban_noop'
    html_out_dir = './timeline/or-tools'
    if not os.path.exists(html_out_dir):
        os.makedirs(html_out_dir)
    for i, file_name in enumerate(os.listdir(result_dir)): 
        json_in_file = os.path.join(result_dir, file_name)
        logger = DJSP_Logger()
        logger.load(json_in_file)
        # logger.find_noop()
        plotter = DJSP_Plotter(logger)
        fn, _ = os.path.splitext(file_name)
        html_out_file = os.path.join(html_out_dir, fn+'.html')
        print(html_out_file)
        plotter.plot_googlechart_timeline(html_out_file)
