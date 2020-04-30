import os

from flask import Flask,  session , render_template , redirect , url_for , escape , request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
# Configure session to use filesystem
app.secret_key = 'This is A Sample Secret Key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# DATABASE_URL=postgres://athncldfkluzpq:5dab398fc5ec4f2daf8f2c9b96062478b4cfce8bd2f398312da69fd998ace3db@ec2-34-204-22-76.compute-1.amazonaws.com:5432/d3hv5j2det4su0

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    # raise RuntimeError("DATABASE_URL is not set")
    DatabaseUrl = "postgres://athncldfkluzpq:5dab398fc5ec4f2daf8f2c9b96062478b4cfce8bd2f398312da69fd998ace3db@ec2-34-204-22-76.compute-1.amazonaws.com:5432/d3hv5j2det4su0"
else: 
    DatabaseUrl = os.getenv("DATABASE_URL")


 # Set up database
engine = create_engine(DatabaseUrl)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
     return render_template("index.html")
   # if 'username' in session:
    #     username = session['username']
    #     return 'Logged in as ' + username + '<br>' + \
    #         "<b><a href = '/logout'>click here to log out</a></b>"
    # return "You are not logged in <br><a href = '/login'></b>" + \
    #     "click here to log in</b></a>"


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
	
   <form action = "" method = "post">
        <input type="text" name="username" placeholder="Name..">
        <input type="submit" value="Login">
   </form>
	
   '''

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))
