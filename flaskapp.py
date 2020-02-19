#!/usr/bin/env python

import copy
import os

from flask import abort
from flask import Flask
from flask import jsonify
from flask import Response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import send_from_directory

from flask_login import LoginManager
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user 

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import IntegerField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField

from ganttapi import GanttApi

from pprint import pprint


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '011111'
login_manager = LoginManager(app)
login_manager.login_view = "login"
api = GanttApi()

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        print('id: %s' % self.id)
        print('name: %s' % self.name)
        print('password: %s' % self.password)
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


class LoginForm(FlaskForm):
    username = StringField(label='username')
    password = PasswordField(label='password')
    submit = SubmitField(label='login')


class AddProjectForm(FlaskForm):
    projectid = StringField(label='project id')
    projectname = StringField(label='project name')
    resource = StringField(label='resource group')
    trackerurl = StringField(label='tracker url')
    startdate = StringField(label='start date')
    enddate = StringField(label='end date')
    duration = IntegerField(label='duration')
    percentcomplete = IntegerField(label='percent complete')
    dependencies = StringField(label='dependencies')
    submit = SubmitField(label='save')


class AddTaskForm(FlaskForm):
    projectid = StringField(label='project id')
    taskid = StringField(label='task id')
    taskname = StringField(label='task name')
    resource = StringField(label='resource group')
    trackerurl = StringField(label='tracker url')
    startdate = StringField(label='start date')
    enddate = StringField(label='end date')
    duration = IntegerField(label='duration')
    percentcomplete = IntegerField(label='percent complete')
    dependencies = StringField(label='dependencies')
    submit = SubmitField(label='save')


@app.template_filter()
def split_ymd(ds, ix=None):
    ds = ds.split('-')
    if ix is None:
        return ds
    try:
        return ds[ix]
    except IndexError:
        return 0


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect('/')
        else:
            return abort(401)
    else:
        return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html', api=api, tasks=api.get_projects())


@app.route('/addproject', methods=['GET', 'POST'])
@login_required
def add_project():
    form = AddProjectForm()

    if request.method == 'POST':
        kwargs = copy.deepcopy(form.data)
        kwargs.pop('csrf_token', None)
        kwargs.pop('submit', None)
        api.add_project(**kwargs)
        return redirect('/')

    return render_template('project_add.html', api=api, form=form)


@app.route('/deleteproject/<string:projectid>', methods=['GET', 'POST'])
@login_required
def delete_project(projectid):
    api.delete_project(projectid=projectid)
    return redirect('/')


@app.route('/editproject/<string:projectid>', methods=['GET', 'POST'])
@login_required
def edit_project(projectid):
    project = api.get_project(projectid=projectid)
    form = AddProjectForm(
        projectid=projectid,
        projectname=project['task_name'],
        resource=project.get('resource_group', ''),
        trackerurl=project.get('tracker_url', ''),
        startdate=project['start_date'],
        enddate=project['end_date'],
        duration=project['duration'],
        percentcomplete=project.get('percent_complete', 0),
        dependencies=project['dependencies']
    )

    if request.method == 'POST':
        kwargs = copy.deepcopy(form.data)
        kwargs.pop('csrf_token', None)
        kwargs.pop('submit', None)
        kwargs['current_projectid'] = projectid
        pprint(kwargs)
        api.add_project(**kwargs)
        return redirect('/')

    return render_template('project_edit.html', api=api, form=form, projectid=projectid)


@app.route('/projects/<string:projectid>')
def project_view(projectid):
    project = api.get_project(projectid=projectid)
    tasks = api.get_tasks(projectid=projectid)
    pprint(tasks)
    return render_template('project_view.html', api=api, project=project, projectid=projectid, tasks=tasks)


@app.route('/addtask', methods=['GET', 'POST'])
@app.route('/addtask/<string:projectid>', methods=['GET', 'POST'])
@login_required
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
        if projectid:
            return redirect('/projects/%s' % projectid)
        else:
            return redirect('/')

    return render_template('task_add.html', api=api, form=form)


@app.route('/edittask/<string:taskid>', methods=['GET', 'POST'])
@login_required
def edit_task(taskid):
    task = api.get_task(taskid=taskid)
    form = AddTaskForm(
        projectid=task['projectid'],
        taskid=task['task_id'],
        projectname=task['task_name'],
        resource=task.get('resource_group', ''),
        trackerurl=task.get('tracker_url', ''),
        startdate=task['start_date'],
        enddate=task['end_date'],
        duration=task['duration'],
        percentcomplete=task.get('percent_complete', 0),
        dependencies=task['dependencies']
    )

    if request.method == 'POST':
        kwargs = copy.deepcopy(form.data)
        kwargs.pop('csrf_token', None)
        kwargs.pop('submit', None)
        kwargs['current_taskid'] = taskid
        api.add_task(**kwargs)
        return redirect('/projects/%s' % task['projectid'])

    return render_template('task_view.html', api=api, form=form)

@app.route('/tasks/<string:taskid>', methods=['GET', 'POST'])
def task_view(taskid):
    task = api.get_task(taskid=taskid)
    form = AddTaskForm(
        projectid=task['projectid'],
        taskid=taskid,
        taskname=task['task_name'],
        resource=task.get('resource_group', ''),
        trackerurl=task.get('tracker_url', ''),
        startdate=task['start_date'],
        enddate=task['end_date'],
        duration=task['duration'],
        percentcomplete=task.get('percent_complete', 0),
        dependencies=task['dependencies']
    )
    return render_template('task_view.html', api=api, task=task, form=form)


####################################################
#   API FUNCTIONS
####################################################

@app.route('/api')
def api_root():
    return jsonify(['/api/tasks'])


@app.route('/api/backup')
def api_backup():
    tf = api.get_backup()
    print(tf)
    return send_file(tf, as_attachment=True)
    #return send_from_directory(
    #    os.path.dirname(tf),
    #    os.path.basename(tf)
    #)


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