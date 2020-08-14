import json
import os
import flask
import google_auth
from flask import render_template, redirect, session

app = flask.Flask(__name__)
app.debug = True
app.secret_key = "b']\xa0\x02\x94Rl\x15\x10z\x19\xdaEE\xbf\x08!'"
app.register_blueprint(google_auth.app)
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "daily_tasks.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

from views import create_task, get_task, get_all_tasks, update_task, delete_task, get_all_projects, create_project, \
    delete_project, create_user,generate_report, get_task_info ,user_status


def login_required(func):
    def wrapper(*args, **kwargs):
        if google_auth.is_logged_in():
            return func(*args, **kwargs)
        return redirect("/")

    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def index():
    if google_auth.is_logged_in():
        response = create_user()
        if 'user' in session:
            user = session['user']['user_id']
        else:
            user = 'Anonymous'
        context = {
            'user_id': user,
        }
        response = json.loads(response.get_data())
        if response['status']:
            return render_template('tables.html', context=context)
        else:
            return str(response)
    return render_template('login.html')


@app.route('/tasks/', methods=['GET'])
@login_required
def get_tasks():
    return get_all_tasks()


@app.route('/task/<int:user_id>/', methods=['GET'])
@login_required
def get_task_main(user_id):
    return get_task(user_id)


@app.route('/taskinfo/<int:task_id>/', methods=['GET'])
@login_required
def get_info_task(task_id):
    return get_task_info(task_id)


@app.route('/task/', methods=["POST"])
@login_required
def create_task_main():
    return create_task()


@app.route('/task/<int:task_id>/', methods=['PUT'])
@login_required
def update_task_main(task_id):
    return update_task(task_id)


@app.route("/task/<int:task_id>/", methods=["DELETE"])
@login_required
def delete_task_main(task_id):
    return delete_task(task_id)


@app.route("/project/", methods=["GET"])
@login_required
def get_projects():
    return get_all_projects()


@app.route('/project/', methods=["POST"])
@login_required
def create_project_main():
    return create_project()


@app.route("/project/<int:project_id>/", methods=["DELETE"])
@login_required
def delete_project_main(project_id):
    return delete_project(project_id)


@app.route("/report/", methods=["GET"])
@login_required
def generate_report_main():
    return generate_report()


@app.route("/table/")
@login_required
def render_table():
    context = {
        'user_id': session['user']['user_id'],
    }
    return render_template('tables.html', context=context)


@app.route("/admin/")
@login_required
def render_admin():
    user_stat = user_status()
    return render_template('admin.html',context=user_stat)


@app.route("/select/")
@login_required
def render_select():
    response = get_all_projects()
    response = json.loads(response.get_data())
    # last_task = json.loads(get_task(session['user']['user_id']).get_data())
    # print(last_task)
    context = {
        'user': session['user']
    }
    if 'data' in response:
        context.update({'projects':response['data']})
    return render_template('select.html', context=context)


@app.route("/edit/<int:task_id>")
@login_required
def render_edit(task_id):
    response_project = json.loads(get_all_projects().get_data())
    response_task = json.loads(get_task_info(task_id).get_data())
    context = {
        'projects': response_project['data'],
        'task': response_task['data'],
    }
    return render_template('edit.html', context=context)
