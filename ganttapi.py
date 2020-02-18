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
    project: <bool>             # is this a project or not?
}
"""

import glob
import json
import os


class GanttApi:

    tasks = None
    datadir = 'data'

    def __init__(self, datadir=None):
        if datadir:
            self.datadir = datadir
        self.load_data()
    
    def load_data(self):
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)
        self.tasks = []
        dfs = glob.glob('%s/*.json' % self.datadir)
        for df in dfs:
            print('read %s' % df)
            with open(df, 'r') as f:
                self.tasks.append(json.loads(f.read()))
        print(self.tasks)

    def get_projects(self):
        if not isinstance(self.tasks, list):
            return []
        projects = [x for x in self.tasks if x.get('project') == True]
        return projects

    def get_tasks(self, projectid=None, taskid=None):
        if not isinstance(self.tasks, list):
            return []

        if projectid and taskid:
            for task in self.tasks:
                if task.get('project_id') == projectid and task.get('task_id') == taskid:
                    return task
        
        if projectid:
            return [x for x in self.tasks if x.get('projectid') == projectid]

        if taskid:
            for task in self.tasks:
                if task['task_id'] == taskid:
                    return task

        if isinstance(self.tasks, list):
            return self.tasks[:]

        return []
    
    def get_task(self, taskid=None):
        for task in self.tasks:
            if task['task_id'] == taskid:
                return task
        return None

    def get_project(self, projectid=None):
        for task in self.tasks:
            if task.get('project') and task['task_id'] == projectid:
                return task

    def add_project(self, projectid=None, projectname=None, trackerurl=None, startdate=None, enddate=None, duration=None, dependencies=None):
        fn = os.path.join(self.datadir, 'project_%s.json' % projectid)
        with open(fn, 'w') as f:
            f.write(json.dumps({
                'project': True,
                'task_id': projectid,
                'task_name': projectname,
                'tracker_url': trackerurl,
                'start_date': startdate,
                'end_date': enddate,
                'duration': duration,
                'percent_complete': 0,
                'dependencies': dependencies,
            }))
        self.load_data()
    
    def delete_project(self, projectid=None):
        pfiles = glob.glob('%s/project_%s*' % (self.datadir, projectid))
        for pfile in pfiles:
            print('deleting %s' % pfile)
            os.remove(pfile)
        self.load_data()

    def add_task(self, projectid=None, taskid=None, taskname=None, trackerurl=None, startdate=None, enddate=None, duration=None, dependencies=None):
        fn = os.path.join(self.datadir, 'project_%s_task_%s.json' % (projectid, taskid))
        with open(fn, 'w') as f:
            f.write(json.dumps({
                'project': False,
                'projectid': projectid,
                'task_id': taskid,
                'task_name': taskname,
                'tracker_url': trackerurl,
                'start_date': startdate,
                'end_date': enddate,
                'duration': duration,
                'percent_complete': 0,
                'dependencies': dependencies,
            }))
        self.load_data()