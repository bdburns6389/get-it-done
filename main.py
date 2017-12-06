from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:root@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)

    def __init__(self,name):
        self.name = name
        self.completed = False

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120), unique=True)

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            #TODO-->
            return redirect('/')
        else:
            #TODO-->
            pass
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO Validate Data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            #TODO --> 'remember' the user
            return redirect('/')
        else:
            #TODO message that says already exists in database
            return '<h1>Duplicate User</h1>'

    return render_template('register.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    
    if request.method == 'POST': #if data is received from html template
        task_name = request.form['task']
        new_task = Task(task_name) #uses Task object to create entry in db
        db.session.add(new_task) #SQLAlchemy adds new_task to database
        db.session.commit() #necessary to actually add to assigned database


    tasks= Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.filter_by(completed=True).all()
    return render_template('todos.html', title="Get it Done!", tasks=tasks, 
        completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    # db.session.delete(task)
    # db.session.commit()
    task.completed = True
    db.session.add(task)
    db.session.commit()


    return redirect('/')

if __name__ == "__main__":
    app.run()
