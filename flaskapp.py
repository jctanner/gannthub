#!/usr/bin/env python

import copy

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SubmitField

from ganttapi import GanttApi


from pprint import pprint


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '011111'
api = GanttApi()


@app.template_filter()
def split_ymd(ds, ix=None):
    ds = ds.split('-')
    if ix is None:
        return ds
    return ds[ix]


@app.route('/')
def index():
    return render_template('index.html', api=api, tasks=api.get_projects())


class AddProjectForm(FlaskForm):
    projectid = StringField(label='project id')
    projectname = StringField(label='project name')
    trackerurl = StringField(label='tracker url')
    startdate = StringField(label='start date')
    enddate = StringField(label='end date')
    duration = IntegerField(label='duration')
    dependencies = StringField(label='dependencies')
    submit = SubmitField(label='save')


class AddTaskForm(FlaskForm):
    projectid = StringField(label='project id')
    taskid = StringField(label='task id')
    taskname = StringField(label='task name')
    trackerurl = StringField(label='tracker url')
    startdate = StringField(label='start date')
    enddate = StringField(label='end date')
    duration = IntegerField(label='duration')
    dependencies = StringField(label='dependencies')
    submit = SubmitField(label='save')


@app.route('/addproject', methods=['GET', 'POST'])
def add_project():
    form = AddProjectForm()

    if request.method == 'POST':
        kwargs = copy.deepcopy(form.data)
        kwargs.pop('csrf_token', None)
        kwargs.pop('submit', None)
        api.add_project(**kwargs)
        return redirect('/')

    return render_template('addproject.html', api=api, form=form)


@app.route('/deleteproject/<string:projectid>', methods=['GET', 'POST'])
def delete_project(projectid):
    api.delete_project(projectid=projectid)
    return redirect('/')


@app.route('/editproject/<string:projectid>', methods=['GET', 'POST'])
def edit_project(projectid):
    project = api.get_project(projectid=projectid)
    form = AddProjectForm(
        projectid=projectid,
        projectname=project['task_name'],
        trackerurl=project.get('tracker_url', ''),
        startdate=project['start_date'],
        enddate=project['end_date'],
        duration=project['duration'],
        dependencies=project['dependencies']
    )

    if request.method == 'POST':
        kwargs = copy.deepcopy(form.data)
        kwargs.pop('csrf_token', None)
        kwargs.pop('submit', None)
        api.add_project(**kwargs)
        return redirect('/')

    return render_template('addproject.html', api=api, form=form)


@app.route('/projects/<string:projectid>')
def project_view(projectid):
    project = api.get_project(projectid=projectid)
    tasks = api.get_tasks(projectid=projectid)
    pprint(tasks)
    return render_template('project.html', api=api, project=project, projectid=projectid, tasks=tasks)


@app.route('/addtask', methods=['GET', 'POST'])
@app.route('/addtask/<string:projectid>', methods=['GET', 'POST'])
def add_task(projectid=None):
    if projectid:
        form = AddTaskForm(projectid=projectid)
    else:
        form = AddTaskForm()

    if request.method == 'POST':
        kwargs = copy.deepcopy(form.data)
        kwargs.pop('csrf_token', None)
        kwargs.pop('submit', None)
        api.add_task(**kwargs)
        return redirect('/')

    return render_template('addtask.html', api=api, form=form)


@app.route('/tasks/<string:taskid>', methods=['GET', 'POST'])
def task_view(taskid):
    task = api.get_task(taskid=taskid)
    form = AddTaskForm(
        projectid=task['projectid'],
        taskid=taskid,
        taskname=task['task_name'],
        trackerurl=task.get('tracker_url', ''),
        startdate=task['start_date'],
        enddate=task['end_date'],
        duration=task['duration'],
        dependencies=task['dependencies']
    )
    return render_template('task.html', api=api, task=task, form=form)


####################################################
#   API FUNCTIONS
####################################################

@app.route('/api')
def api_root():
    return jsonify(['/api/tasks'])


@app.route('/api/projects')
def api_projects_root():
    return jsonify(api.get_projects())


@app.route('/api/projects/<string:projectid>')
def api_project(projectid):
    return jsonify(api.get_project(projectid=projectid))


@app.route('/api/projects/<string:projectid>/tasks')
def api_project_tasks(projectid):
    return jsonify(api.get_tasks(projectid=projectid))


@app.route('/api/tasks')
def api_tasks_root():
    return jsonify(api.get_tasks())


@app.route('/api/tasks/<string:taskid>')
def api_task(taskid):
    return jsonify(api.get_tasks(taskid=taskid))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)