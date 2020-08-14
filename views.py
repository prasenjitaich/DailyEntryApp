from flask import request, render_template, make_response, session
from models import db
from models import Tasks, Project, User, TaskSchema, ProjectSchema, UserSchema
from response_utils import send_error_response, send_success_response
import google_auth
import datetime
import html2text
from sqlalchemy import desc
import pytz

def generate_report():
    try:
        data_dict = {}
        datenow = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()
        tasks = Tasks.query.filter_by(date=datenow).all()
        for task in tasks:
            project_task = []
            if task.project not in data_dict:
                project_task.append(task)
                data_dict[task.project] = {task.user.user_name: project_task}
            else:
                if task.user.user_name not in data_dict[task.project].keys():
                    project_task.append(task)
                    data_dict[task.project].update({task.user.user_name: project_task})
                else:
                    project_task = data_dict[task.project][task.user.user_name]
                    project_task.append(task)
                    data_dict[task.project].update({task.user.user_name: project_task})
        context = {
            'date': datenow,
            'pro_details': data_dict,
        }
        rendered = render_template("report.html", context=context)
        text = html2text.html2text(rendered)
        file_name = str(datetime.datetime.now().date()) + '_Task_Report'
        response = make_response(text)
        response.headers['Content_Type'] = 'text/plain'
        response.headers['Content-Disposition'] = 'attachment; filename={}.txt'.format(file_name)
        return response
    except Exception as e:
        print(e)
        message = "Error in generating tasks"
        return send_error_response(message)


def get_all_tasks():
    try:
        task = Tasks.query.order_by(desc(Tasks.date)).all()
        if not task:
            message = "There is no task"
            return send_success_response(message)
        task_schema = TaskSchema(many=True)
        data = task_schema.dump(task).data
        message = "Successfully retrieved tasks"
        return send_success_response(message, data)
    except Exception as e:
        print(e)
        message = "Error in retrieving tasks"
        return send_error_response(message)


def get_task(user_id):
    try:
        user = User.query.get(user_id)
        task = Tasks.query.filter_by(user=user).order_by(desc(Tasks.date)).all()
        if not task:
            message = "There is no task of user" + user.user_name
            return send_success_response(message)
        task_schema = TaskSchema(many=True)
        message = "Successfully retrieved task of " + user.user_name
        data = task_schema.dump(task).data
        return send_success_response(message, data)
    except Exception as e:
        print(e)
        message = "Error in retrieving task of " + str(user_id)
        return send_error_response(message)


def get_task_info(task_id):
    try:
        task = Tasks.query.get(task_id)
        if not task:
            message = "There is no task with that id"
            return send_success_response(message)
        task_schema = TaskSchema()
        message = "Successfully retrieved task of " + task.task_title
        data = task_schema.dump(task).data
        return send_success_response(message, data)
    except Exception as e:
        print(e)
        message = "Error in retrieving task of " + str(task_id)
        return send_error_response(message)


def create_task():
    try:
        project_name = request.json.get('project_name')
        title = request.json.get('task_title')
        status = request.json.get('status')
        reason = request.json.get('reason')
        user_name = session['user']['user_name']
        user_obj = User.query.filter_by(user_name=user_name).first()
        project_obj = Project.query.filter_by(project_name=project_name).first()
        user_obj.projects.append(project_obj)
        task = Tasks(task_title=title, status=status, reason=reason, project=project_obj, user=user_obj)
        db.session.add(task)
        db.session.commit()
        message = "Successfully saved task"
        return send_success_response(message)
    except KeyError as e:
        print(e)
        return send_error_response()
    except Exception as e:
        print(e)
        message = "Error in storing task"
        return send_error_response(message)


def update_task(task_id):
    try:
        task = Tasks.query.get(task_id)
        project_name = request.json.get('project_name')
        task.task_title = request.json.get('task_title', task.task_title)
        task.status = request.json.get('status', task.status)
        task.reason = request.json.get('reason', task.reason)
        task.project = Project.query.filter_by(project_name=project_name).first()
        db.session.commit()
        task_schema = TaskSchema()
        data = task_schema.dump(task).data
        message = "Successfully updated tasks"
        return send_success_response(message, data)
    except Exception as e:
        print(e)
        message = "Error in updating task"
        return send_error_response(message)


def delete_task(task_id):
    try:
        task = Tasks.query.get(task_id)
        db.session.delete(task)
        db.session.commit()
        message = "Deleted task successfully"
        return send_success_response(message)
    except Exception as e:
        print(e)
        message = "Error in deleting task"
        return send_error_response(message)


def create_project():
    try:
        project_name = request.json.get('project_name')
        in_report = request.json.get('in_report')
        project = Project(project_name=project_name, in_report = in_report)
        db.session.add(project)
        db.session.commit()
        message = "Successfully created project"
        return send_success_response(message)
    except Exception as e:
        print(e)
        message = "Error in creating projects"
        return send_error_response(message)


def get_all_projects():
    try:
        project = Project.query.all()
        if not project:
            message = "There is no project available"
            return send_success_response(message)
        project_schema = ProjectSchema(many=True)
        data = project_schema.dump(project).data
        message = "Successfully retrieved projects"
        return send_success_response(message, data)
    except Exception as e:
        print(e)
        message = "Error in retrieving projects"
        return send_error_response(message)


def delete_project(project_id):
    try:
        project = Project.query.get(project_id)
        db.session.delete(project)
        db.session.commit()
        message = "Deleted project successfully"
        return send_success_response(message)
    except Exception as e:
        print(e)
        message = "Error in deleting project"
        return send_error_response(message)


def create_user():
    try:
        user_info = google_auth.get_user_info()
        user = User.query.filter_by(user_name=user_info['name']).first()
        if user:
            message = "User already exists"
            user_schema = UserSchema()
            data = user_schema.dump(user).data
            session['user'] = data
            return send_success_response(message)
        if user_info['email'] == "tapan.inexture@gmail.com":
            user = User(user_name=user_info['name'], user_email=user_info['email'], is_admin=True)
        else:
            user = User(user_name=user_info['name'], user_email=user_info['email'])
        db.session.add(user)
        db.session.commit()
        user_schema = UserSchema()
        data = user_schema.dump(user).data
        session['user'] = data
        message = "User created successfully"
        return send_success_response(message)
    except Exception as e:
        message = "Error in creating user"
        return send_error_response(str(e))


def user_status():
    try:
        user_dict = {}
        user_status = set()
        datenow = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()
        tasks = Tasks.query.filter_by(date=datenow).all()
        users = User.query.all()
        for task in tasks:
            user_status.add(task.user.user_name)
        for user in users:
            if user.user_name in user_status:
                user_dict.update({user.user_name: True})
            else:
                user_dict.update({user.user_name: False})
        return user_dict
    except Exception as e:
        print(e)
        message = "Error in user status"
        return send_error_response(message)

