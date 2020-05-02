import os

from flask import Flask,  session , render_template , redirect , url_for , escape , request
from flask_session import Session
from sqlalchemy import create_engine 

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
connection = engine.connect()



class UserRegistrationData:
    def __init__(self, DisplayName, UserName):
        self.DisplayName = DisplayName
        self.UserName = UserName




# General method to convert string for Query format.
def IsValidUserName( UserName , CanContainBlank = False):
    if ( ( None == UserName ) or (not(UserName and UserName.strip())) ) :
        return "cannot be empty."

    if ( CanContainBlank == False and -1 != UserName.rfind (" ") ):
        return "cannot contain blank spaces."

    if ( -1 != UserName.rfind ("'") or \
        -1 != UserName.rfind ('"') or \
        -1 != UserName.rfind ("=") or \
        -1 != UserName.rfind (";") or \
        -1 != UserName.rfind ("=") or \
        -1 != UserName.rfind ("*") or \
        -1 != UserName.rfind ("%") or \
        -1 != UserName.rfind ("/") or \
        -1 != UserName.rfind ("\\") \
        ):
        return "cannot contain special character."
    return ""


def IsUserLoggedIn():
    LoggedUserID = session.get('LoggedUserID')
    if (None == LoggedUserID or LoggedUserID < 1):
        return False
    else:
        return True



#--------------------------------------------------------------------------
# show the signup page...
#
@app.route("/")
def index():
    if ( IsUserLoggedIn()) :
        return redirect(url_for('booksearch'))

    return render_template("index.html")


#--------------------------------------------------------------------------
# will be called from response for createaccount button state. We should come here only from the post command.
#
@app.route('/createaccount', methods = ['GET', 'POST'])
def createaccount():
    if ( IsUserLoggedIn()) :
        return redirect(url_for('booksearch'))

    if request.method == 'GET':
        # if the user have come here directly then move back to index page.
        return redirect(url_for('index'))

    UserRegistrationData.UserName = request.form.get("inputUserName")
    UserRegistrationData.DisplayName = request.form.get("inputDisplayName")

    UserPassword = request.form.get("inputPassword")
    UserRePassword = request.form.get("inputRePassword")

    NameErrror = IsValidUserName(UserRegistrationData.DisplayName , True)
    if ( None != NameErrror ) and (len(NameErrror) > 0 ) :
        return  render_template("index.html", ErrorMsg=f"Display name {NameErrror}" , RegistrationData = UserRegistrationData)

    NameErrror = IsValidUserName(UserRegistrationData.UserName)
    if ( None != NameErrror ) and (len(NameErrror) > 0 ) :
        return  render_template("index.html", ErrorMsg=f"User name {NameErrror}" , RegistrationData = UserRegistrationData)

    NameErrror = IsValidUserName(UserPassword)
    if ( None != NameErrror ) and (len(NameErrror) > 0 ) :
        return  render_template("index.html", ErrorMsg=f"Password {NameErrror}" , RegistrationData = UserRegistrationData)

    if ( ( None == UserRePassword ) or ( UserPassword != UserRePassword ) ) :
        return  render_template("index.html", ErrorMsg="Retyped Password is not same as the original", RegistrationData = UserRegistrationData)


    # now lets check if the user name is already present or not.
    #  
    SelectQuery = f"SELECT *FROM UserData WHERE UserName = '{UserRegistrationData.UserName}'"
    RowCount = connection.execute(SelectQuery).rowcount
    if ( RowCount > 0):
        return  render_template("index.html", ErrorMsg="User with the given name already exist. Please select a different name.", RegistrationData = UserRegistrationData)

    # we are here this menas we can add this new user.
    InsertQuery = f"INSERT INTO UserData (UserName, Password , DisplayName ) VALUES ('{UserRegistrationData.UserName}', '{UserPassword}', '{UserRegistrationData.DisplayName}' )"
    connection.execute(InsertQuery)

    return redirect(url_for('signin'))





#--------------------------------------------------------------------------
# show the signin page...
#
@app.route('/signin')
def signin():
    if ( IsUserLoggedIn()) :
        return redirect(url_for('booksearch'))

    return render_template("signin.html")



#--------------------------------------------------------------------------
# will be called from response for createaccount button state. We should come here only from the post command.
#
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if ( IsUserLoggedIn()) :
        return redirect(url_for('booksearch'))


    if request.method == 'GET':
        # if the user have come here directly then move back to signin page.
        return redirect(url_for('signin'))

    UserName = request.form.get("inputUserName")
    UserPassword = request.form.get("inputPassword")

    NameErrror = IsValidUserName(UserName)
    if ( None != NameErrror ) and (len(NameErrror) > 0 ) :
        return  render_template("signin.html", ErrorMsg=f"User name {NameErrror}" , UserName = UserName)

    NameErrror = IsValidUserName(UserPassword)
    if ( None != NameErrror ) and (len(NameErrror) > 0 ) :
        return  render_template("signin.html", ErrorMsg=f"Password {NameErrror}" , UserName = UserName)

    # now lets check if the user with giben name and password esit or not.
    SelectData = None
    try:
        SelectData = connection.execute("SELECT User_ID, DisplayName , UserName , JoinDate FROM UserData WHERE UserName = %(username)s AND Password = %(password)s", {'username': UserName , 'password' : UserPassword}).fetchone()
        if ( None == SelectData ) :
            return  render_template("signin.html", ErrorMsg="User details for given name or password could not be fetched" , UserName = UserName)

    except :
        return  render_template("signin.html", ErrorMsg="Error in processing query" , UserName = UserName)

    finally:
        if ( None != SelectData ):
            session['LoggedUserDisplayName'] = SelectData[1]
            session['LoggedUserID'] = SelectData[0]
            session['LoggedUserName'] = SelectData[2]
            session['LoggedUserJoiningDate'] = SelectData[3]
            return  redirect(url_for('booksearch'))

    return redirect(url_for('signin'))



#--------------------------------------------------------------------------
# Logout from the current session...
#
@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    if (IsUserLoggedIn()):
        session.pop('LoggedUserDisplayName', None)
        session.pop('LoggedUserID', None)
        session.pop('LoggedUserName', None)
        session.pop('LoggedUserJoiningDate', None)
    return redirect(url_for('signin'))



#--------------------------------------------------------------------------
# show the book search page...
#
@app.route('/booksearch', methods = ["GET", "POST"])
def booksearch():
    # Do the Book Search
    if ( not IsUserLoggedIn()) :
        return redirect(url_for('signin'))

    if request.method == "POST":
        InSearchString = request.form.get("inputSearchData")
        if ((None == InSearchString) or (not(InSearchString and InSearchString.strip()))):
            return render_template("booksearch.html", ErrorMsg="Search string is empty")
            

    return render_template("booksearch.html")

