import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
import pytz
from app import app
from flask_marshmallow import Marshmallow
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

db = SQLAlchemy(app)
migrate = Migrate(app, db,compare_type=True)
manager = Manager(app)
ma = Marshmallow(app)
manager.add_command('db', MigrateCommand)

projects = db.Table('projects',
                    db.Column('project_id', db.Integer, db.ForeignKey('project.project_id'), primary_key=True),
                    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
                    )


class Project(db.Model):
    project_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(50), unique=True, nullable=False)
    in_report = db.Column(db.Boolean, unique=False, default=True)
    tasks = db.relationship('Tasks', backref="project")

    def __str__(self):
        return self.project_name


class User(db.Model):
    user_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_email = db.Column(db.String(50), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, unique=False, default=False)
    tasks = db.relationship('Tasks', backref="user")
    projects = db.relationship('Project', secondary=projects, lazy='subquery',
                               backref=db.backref('projects', lazy=True), passive_deletes='all')

    def __str__(self):
        return self.user_name


class Tasks(db.Model):

    def get_current_ist_time():
        return datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()

    task_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    task_title = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, default=get_current_ist_time(),
                     onupdate=get_current_ist_time())
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __str__(self):
        return self.task_title


class ProjectSchema(ma.ModelSchema):
    class Meta:
        model = Project
        sqla_session = db.session
        fields = ('project_id', 'project_name','in_report')


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        sqla_session = db.session
        fields = ('user_id', 'user_name', 'is_admin')


class TaskSchema(ma.ModelSchema):
    class Meta:
        model = Tasks
        sqla_session = db.session

    project = fields.Nested(ProjectSchema)
    user = fields.Nested(UserSchema)

if __name__=="__main__":
    manager.run()