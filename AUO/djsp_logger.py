from cmd import IDENTCHARS
import json
from textwrap import indent
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta 
from pprint import pprint

class DJSP_Logger(object):
    def __init__(self, num_job=50, num_machine=5, num_job_type=5):
        self.history = []
        self.jobs_to_schedule = []
        self.num_machine = num_machine
        self.num_job_type = num_job_type
        self.num_job = num_job
        self.order = 0

        self.google_chart_front_text = '''
<html>
<head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <!-- <style>div.google-visualization-tooltip { transform: rotate(30deg); }</style> -->
    <script type="text/javascript">
    google.charts.load('current', {'packages':['timeline']});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        // var container = document.getElementById('example5.1');
        var container = document.getElementById('timeline-tooltip');
        // var container = document.getElementById('example7.1');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn({ type: 'string', id: 'Machine' });
        dataTable.addColumn({ type: 'string', id: 'Name' });
        dataTable.addColumn({ type: 'string', role: 'style' });
        dataTable.addColumn({ type: 'string', role: 'tooltip' });
        dataTable.addColumn({ type: 'date', id: 'Start' });
        dataTable.addColumn({ type: 'date', id: 'End' });
        // dataTable.addColumn({ type: 'number', id: 'Start' });
        // dataTable.addColumn({ type: 'number', id: 'End' });
        var scale = 10;
        dataTable.addRows([
    '''

        self.google_chart_back_text = '''
        ]);
        var options = {
          // timeline: {showRowLabels: true}, 
          // avoidOverlappingGridLines: false
          tooltip: { textStyle: { fontName: 'verdana', fontSize: 30 } }, 
        }
        chart.draw(dataTable, options);
      }
    </script>
  </head>
  <body>
    <!-- <div id="timeline" style="height: 300px;"></div> -->
    <div id="timeline-tooltip" style="height: 800px;"></div>
  </body>
</html>
    '''
    
    def add_op(self, op, machine_id, job_type):
        # add op information to history
        op_info = {
            'order':        self.order,
            'job_id':       op.job_id,
            'op_id':        op.op_id,
            'machine_id':   machine_id,
            'start_time':   op.startTime, 
            'process_time': op.RPT,
            'finish_time':  op.startTime+op.RPT,
            'job_type':     job_type,
        }
        self.order += 1
        self.history.append(op_info)
        # print(op_info)
        # self.cursor.execute(
        #         "INSERT INTO LOGGER (TIMESTAMP, MACHINE_ID, JOB_TYPE, JOB_ID, OP_ID, START_TIME, FINISH_TIME, RPT) \
        #         VALUES (%d, %d, %d, %d, %d, %f, %f, %f)" %(
        #             op_info['timestamp'], op_info['machine_id'], op_info['job_type'], op_info['job_id'], op_info['op_id'], 
        #             op_info['start_time'], op_info['finish_time'], op_info['process_time']))
    
    def save(self, json_out_file):
        with open(json_out_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def load(self, json_in_file):
        with open(json_in_file, 'r') as f:
            self.history = list(json.load(f))
    
    def get_plotly_timeline_input(self, color_by):        
        unix_epoch = datetime.strptime('1970-01-01', '%Y-%m-%d')
        data = []
        import plotly.express as px
        for t, op_info in enumerate(self.history):
            d = dict(
                Task =              'Machine '+str(op_info['machine_id']), 
                machine_id =        str(op_info['machine_id']),
                Start =             op_info['start_time'],
                Finish =            op_info['finish_time'],
                StartDateTime =     unix_epoch + timedelta(days=op_info['start_time']),
                FinishDateTime =    unix_epoch + timedelta(days=op_info['finish_time']),
                process_time =      op_info['process_time'],
                # job_type =          str(op_info['job_type']),
                job_type =          t % 5,
                job_id =            str(op_info['job_id']),
                op_id =             op_info['op_id'],
            )
            if isinstance(color_by, tuple):
                d['color'] = (d['job_type'], op_info[color_by[1]])
            data.append(d)
        return data
    def radiantQ_json(self):
        unix_epoch = datetime.strptime('2020-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        data = []
        for t, op_info in enumerate(self.history):
            # if t >= 3:
            #     break
            start_time = unix_epoch + timedelta(hours=op_info['start_time'])
            d = {
                # "Name":         "Task " + str(t),
                "Name":         "Job%d, Op%d, Machine%d, Start time:%f, RPT:%f" %(
                    op_info['job_id'], op_info['op_id'], op_info['machine_id'], op_info['start_time'], op_info['process_time']),
                "ID":           t,
                "SortOrder":    t,
                "StartTime":    str(start_time.strftime('%Y-%m-%dT%H:%M:%SZ')),
                "Effort":       str(int(op_info['process_time'])) + ":00:00",
            }
            data.append(d)
        with open('sample.json', 'w') as f:
            json.dump(data, f, indent=4)
    
google_chart_front_text = '''
<html>
<head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <!-- <style>div.google-visualization-tooltip { transform: rotate(30deg); }</style> -->
    <script type="text/javascript">
    google.charts.load('current', {'packages':['timeline']});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        // var container = document.getElementById('timeline');
        var container = document.getElementById('timeline-tooltip');
        // var container = document.getElementById('example7.1');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn({ type: 'string', id: 'Machine' });
        dataTable.addColumn({ type: 'string', id: 'Name' });
        dataTable.addColumn({ type: 'string', role: 'tooltip' });
        // dataTable.addColumn({ type: 'date', id: 'Start' });
        // dataTable.addColumn({ type: 'date', id: 'End' });
        dataTable.addColumn({ type: number, id: 'Start' });
        dataTable.addColumn({ type: number, id: 'End' });
        var scale = 10;
        dataTable.addRows([
    '''

google_chart_back_text = '''
        ]);
        var options = {
          // timeline: {showRowLabels: true}, 
          // avoidOverlappingGridLines: false
          tooltip: { textStyle: { fontName: 'verdana', fontSize: 30 } }, 
        }
        chart.draw(dataTable, options);
      }
    </script>
  </head>
  <body>
    <!-- <div id="timeline" style="height: 300px;"></div> -->
    <div id="timeline-tooltip" style="height: 800px;"></div>
  </body>
</html>
    '''

if __name__ == '__main__':
    logger = DJSP_Logger()
    logger.load('debug.json')
    # print(logger)


