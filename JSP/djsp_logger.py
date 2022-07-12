import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta 
from pprint import pprint
import os

class DJSP_Logger(object):
    def __init__(self):
        self.history = []
        self.jobs_to_schedule = []
        self.order = 0
        self.NOOP_JOB_ID = 1 << 20
        self.NOOP_OP_ID = 1 << 20

        self.google_chart_front_text = '''
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
        dataTable.addColumn({ type: 'string', role: 'style' });
        dataTable.addColumn({ type: 'string', role: 'tooltip' });
        // dataTable.addColumn({ type: 'date', id: 'Start' });
        // dataTable.addColumn({ type: 'date', id: 'End' });
        dataTable.addColumn({ type: 'number', id: 'Start' });
        dataTable.addColumn({ type: 'number', id: 'End' });
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
    
    def add_op(self, op):
        # add op information to history
        op_info = {
            'Order':        self.order,
            'job_id':       op.job_id,
            'op_id':        op.op_id,
            'machine_id':   op.selected_machine_id,
            'start_time':   op.start_time, 
            'process_time': op.process_times,
            'finish_time':  op.finish_time,
        }
        self.order += 1
        self.history.append(op_info)

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
        dataTable.addColumn({ type: 'number', id: 'Start' });
        dataTable.addColumn({ type: 'number', id: 'End' });
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
    ### run all
    ortools_result_dir = '../ortools_result_6000'
    out_dir = '../ortools_result_6000_noop'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for i, file_name in enumerate(os.listdir(ortools_result_dir)): 
        json_in_file = os.path.join(ortools_result_dir, file_name)
        logger = DJSP_Logger()
        logger.load(json_in_file)
        logger.find_noop()
        fn, _ = os.path.splitext(file_name)
        out_file = os.path.join(out_dir, fn+'.json')
        print(out_file)
        logger.save(out_file)


