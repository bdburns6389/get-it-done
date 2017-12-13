from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:root@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'root' #should be a better key for security purposes, but oh well, right?


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Links Task table to User table to allow one to many relationship

    def __init__(self,name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120), unique=True)
    tasks = db.relationship('Task', backref='owner') #Lets SQL know that this is linked to Task table/class

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request  #this gets checked before any request is pushed through, to check for whatever function wants.
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged In') #Allows message on screen that will be cleared after reload (I think)
            return redirect('/')
        else:
            flash('User Password Incorrect, or User Does Not Exist', 'error')
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
            session['email'] = email
            return redirect('/')
        else:
            #TODO message that says already exists in database
            return '<h1>Duplicate User</h1>'

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():
    
    owner = User.query.filter_by(email=session['email']).first() #pulls session email from above as a way to link user with Task.


    if request.method == 'POST': #if data is received from html template
        task_name = request.form['task']
        new_task = Task(task_name, owner) #uses Task object to create entry in db
        db.session.add(new_task) #SQLAlchemy adds new_task to database
        db.session.commit() #necessary to actually add to assigned database


    tasks= Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()
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
