#!/usr/bin/env python

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

from flask_wtf.csrf import CSRFProtect

from ganttapi import GanttApi


app = Flask(__name__)
csrf = CSRFProtect(app)
api = GanttApi()


@app.template_filter()
def split_ymd(ds, ix=None):
    ds = ds.split('-')
    if ix is None:
        return ds
    return ds[ix]


@app.route('/')
def index():
    return render_template('index.html', tasks=api.get_tasks())


@app.route('/api')
def api_root():
    return jsonify(['/api/tasks'])


@app.route('/api/tasks')
def api_tasks_root():
    return jsonify(api.get_tasks())


@app.route('/api/tasks/<string:taskid>')
def api_task(taskid):
    return jsonify(api.get_tasks(taskid=taskid))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)