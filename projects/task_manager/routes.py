from flask import Blueprint, render_template, request, redirect, url_for
from models import db, User, Task
from forms import RegistrationForm, LoginForm, CreateTaskForm

auth = Blueprint('auth', __name__)

db.init_app(auth)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@auth.route('/dashboard')
def dashboard():
    tasks = Task.query.all()
    return render_template('dashboard.html', tasks=tasks)

@auth.route('/create_task', methods=['GET', 'POST'])
def create_task():
    form = CreateTaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, description=form.description.data, completion_status=False, user_id=1)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_task.html', form=form)

@auth.route('/complete_task/<int:task_id>', methods=['GET'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completion_status = True
    db.session.commit()
    return redirect(url_for('dashboard'))

@auth.route('/delete_task/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))