#!/usr/bin/env python

"""
# DATAFILE FORMAT
{
    task_id: <str>              # unique ID for the task
    task_name: <str>            # what will display in the UX
    start_date: <str>           # YYYY-MM-DD      
    end_date: <str>             # YYYY-MM-DD
    duration: <int>             # number of days to complete
    percent_complete: <int>     # whole number 0-100
    dependencies: <str>         # a csv of taskids
}
"""

import glob
import json


class GanttApi:

    tasks = None
    datadir = 'data'

    def __init__(self, datadir=None):
        if datadir:
            self.datadir = datadir
        self.load_data()
    
    def load_data(self):
        self.tasks = []
        dfs = glob.glob('%s/*.json' % self.datadir)
        for df in dfs:
            print(df)
            with open(df, 'r') as f:
                self.tasks.append(json.loads(f.read()))
        print(self.tasks)
    
    def get_tasks(self, taskid=None):
        if taskid:
            if not isinstance(self.tasks, list):
                raise Exception
            else:
                for task in self.tasks:
                    if task['task_id'] == taskid:
                        return task
        if isinstance(self.tasks, list):
            return self.tasks[:]
        return []