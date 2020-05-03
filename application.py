import os

from flask import Flask,  session , render_template , redirect , url_for , escape , request , abort
from flask_session import Session
from sqlalchemy import create_engine
from datetime import datetime

app = Flask(__name__)
# Configure session to use filesystem
app.secret_key = 'This is A Sample Secret Key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# DATABASE_URL=postgres://athncldfkluzpq:5dab398fc5ec4f2daf8f2c9b96062478b4cfce8bd2f398312da69fd998ace3db@ec2-34-204-22-76.compute-1.amazonaws.com:5432/d3hv5j2det4su0

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    RuntimeError("DATABASE_URL is not set")
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
        session.pop('CurBookID', None)
        
    return redirect(url_for('signin'))



#--------------------------------------------------------------------------
# show the book search page...
#
@app.route('/booksearch/', methods = ["GET", "POST"])
def booksearch():
    # Do the Book Search
    if ( not IsUserLoggedIn()) :
        return redirect(url_for('signin'))

    #remove the current book selection    
    session.pop('CurBookID', None)

    if request.method == "POST":
        InSearchString = request.form.get("inputSearchData")
        InSearchColumn = request.form.get("inputSearchColumn")
        if ((None == InSearchColumn) or (not(InSearchColumn in { "isbn" , "author" , "title" } ))):
            InSearchColumn ="isbn"

        if ((None == InSearchString) or (not(InSearchString and InSearchString.strip()))):
            return render_template("booksearch.html", ErrorMsg="Search string is empty", SearchColumn=InSearchColumn)


        if ( 'isbn' == InSearchColumn ) :
            SearchCriteria = "ISBN"
        elif ( 'author' == InSearchColumn ) :
            SearchCriteria = "Author"
        elif ( 'title' == InSearchColumn ) :
            SearchCriteria = "Title"
        else :
            SearchCriteria = "ISBN"

        FinalSearchString = "%" + InSearchString + "%"
        # SearchQuery = "SELECT * FROM BooksData WHERE " + SearchCriteria + " iLike %(isbn)s"

        SearchQuery = "SELECT BooksData.*, BookReview.Review , BookReview.Rating FROM BooksData \
        LEFT JOIN BookReview \
        ON BooksData.Book_ID=BookReview.Book_ID and BookReview.User_ID = " + str(session['LoggedUserID']) + " \
        WHERE " + SearchCriteria + " iLike %(isbn)s"


        BooksData = connection.execute(SearchQuery, { 'isbn': FinalSearchString } ).fetchall()
        if ( None == BooksData or len(BooksData) < 1 ) :
            return render_template("booksearch.html", ErrorMsg="No books data found...." , SearchData=InSearchString, SearchColumn=InSearchColumn)

        return render_template("booksearch.html", BooksData=BooksData, SearchData=InSearchString , SearchColumn=InSearchColumn)

    return render_template("booksearch.html")





#--------------------------------------------------------------------------
# show the book details page...
#
@app.route('/bookpage/<int:Book_ID>')
def bookpage(Book_ID):
    # Do the Book Search
    if ( not IsUserLoggedIn()) :
        return redirect(url_for('signin'))

    session['CurBookID'] = Book_ID
    if ((None == Book_ID) or ( Book_ID < 1 ) ):
        abort(404 , description="Book data not found (Invalid ID)" )

    # Now lets find the details for the book...
    SearchQuery = f"SELECT * FROM BooksData WHERE Book_ID = {Book_ID}"
    BookData = connection.execute(SearchQuery).fetchone()

    if ( None == BookData ) :
        abort(404 , description="Book data not found" )

    # Now lets fetch the book review by the current user..
    SearchQuery = f"SELECT * FROM BookReview WHERE Book_ID = {Book_ID} AND User_ID = {session['LoggedUserID']}"
    BookReview = connection.execute(SearchQuery).fetchone()

    return render_template("bookpage.html", BookData=BookData, BookReview=BookReview)





#--------------------------------------------------------------------------
# show the book search page...
#
@app.route('/submitreview', methods = ["POST"])
def submitreview():
    # Do the Book Search
    if ( not IsUserLoggedIn()) :
        return redirect(url_for('signin'))

    if not 'CurBookID' in session:
        return redirect(url_for('booksearch'))

    Book_ID = int(session['CurBookID'])
    # Now lets fetch the book review by the current user..
    SearchQuery = f"SELECT * FROM BookReview WHERE Book_ID = {Book_ID} AND User_ID = {session['LoggedUserID']}"
    BookReview = connection.execute(SearchQuery).fetchone()

    buttonaction = request.form.get ('btnaction')

    if ( 'CancelReview' == buttonaction ):
        return redirect(url_for('bookpage',Book_ID=Book_ID))
    elif ( 'DeleteReview' == buttonaction ):
        # set the review for this book
        finalquery = f"Delete From BookReview WHERE Review_ID = {BookReview[0]}" 
        connection.execute(finalquery)
        return redirect(url_for('bookpage',Book_ID=Book_ID))
    

    # Now lets find the details for the book...
    SearchQuery = f"SELECT * FROM BooksData WHERE Book_ID = {Book_ID}"
    BookData = connection.execute(SearchQuery).fetchone()

    InRating = request.form.get("inputRating")
    InReview = request.form.get("inputReview")

    if ((None == InRating) or (not(InRating and InRating.strip()))):
        return render_template("bookpage.html", ErrorMsg="Book Rating is not valid", BookData=BookData , BookReview=BookReview , InRating=InRating , InReview=InReview)
    if ((None == InReview) or (not(InReview and InReview.strip()))):
        return render_template("bookpage.html", ErrorMsg="Book review cannot be left blank", BookData=BookData, BookReview=BookReview , InRating=InRating , InReview=InReview)

    if ( 'SetReview' == buttonaction ):
        # set the review for this book
        finalquery = "INSERT INTO BookReview (Book_ID, User_ID , Review , Rating ) VALUES ({bookid}, {userid}, '{review}' , {rating})" \
                    .format(bookid=Book_ID , userid = session['LoggedUserID'] , review = InReview , rating = int(InRating)) 
        connection.execute(finalquery)
    elif ( 'UpdateReview' == buttonaction ):
        # set the review for this book
        finalquery = "Update BookReview SET Book_ID = {bookid} , User_ID = {userid} , Review = '{review}' , Rating = {rating} , ReviewDate = '{reviewdate}' WHERE Review_ID = {reviewid}" \
                    .format(bookid=Book_ID , userid = session['LoggedUserID'] , review = InReview , rating = int(InRating) , reviewid = BookReview[0] , reviewdate = datetime.utcnow()) 
        connection.execute(finalquery)
        
        
    return redirect(url_for('bookpage',Book_ID=Book_ID))




@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = str(error)), 404