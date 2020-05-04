import os

from flask import Flask,  session , render_template , redirect , url_for , escape , request , abort , jsonify
from flask_session import Session
from sqlalchemy import create_engine
from datetime import datetime
import requests


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


class BookDetails:
    def __init__(self, BookData, BookReview , GoodReadReviews ):
        self.BookData = BookData
        self.BookReview = BookReview
        self.GoodReadReviews = GoodReadReviews




# General method to convert string for Query format.
def IsValidUserName( UserName , CanContainBlank = False):
    """Checks if teh entry is a valid or not."""
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
    """Check if a user is logged in or not using session data."""
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
    """Checks and creates a new account for the user."""
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
    """LOgin the user after validating his credentials.."""
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
    """logout a user."""
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
    """DO a book search."""
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
# Gives the details for the book with given book ID like Book Data and Book Review...
#
def fnGetBookDetails(Book_ID ):
    """Gives the details for the book with given book ID like Book Data and Book Review."""
    if ((None == Book_ID) or ( Book_ID < 1 ) ):
        return None

    SearchQuery = f"SELECT * FROM BooksData WHERE Book_ID = {Book_ID}"
    BookData = connection.execute(SearchQuery).fetchone()
    
    if ( None == BookData ) :
        return None

    # Now lets fetch the book review by the current user..
    SearchQuery = f"SELECT * FROM BookReview WHERE Book_ID = {Book_ID} AND User_ID = {session['LoggedUserID']}"
    BookReview = connection.execute(SearchQuery).fetchone()

    # Now lets try to fetch the good books review...
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "vgmf6zfC5WkH9Ef0XyaNg", "isbns": BookData[1]})

    GoodReadReviews = None    
    if ( res.status_code == 200 ):
        data = res.json()
        if 'books' in data :
            booksdata = data.get('books')
            if ( booksdata and 1 == len ( booksdata ) ):
                curbook = booksdata[0]
                work_ratings_count = curbook.get('work_ratings_count',0)
                average_rating = curbook.get('average_rating',1.)
                GoodReadReviews = {"ratings_count" : work_ratings_count , "average_rating" : average_rating }

    return BookDetails( BookData=BookData , BookReview=BookReview , GoodReadReviews= GoodReadReviews)



#--------------------------------------------------------------------------
# show the book details page...
#
@app.route('/bookpage/<int:Book_ID>')
def bookpage(Book_ID):
    """Return details of a book with given database book_ID."""

    # Do the Book Search
    if ( not IsUserLoggedIn()) :
        return redirect(url_for('signin'))

    session['CurBookID'] = Book_ID
    if ((None == Book_ID) or ( Book_ID < 1 ) ):
        abort(404 , description="Book data not found (Invalid ID)" )

    # Now lets find the details for the book...
    BookDetails = fnGetBookDetails ( Book_ID )
    if ( None == BookDetails or None == BookDetails.BookData ) :
        abort(404 , description="Book data not found" )

    return render_template("bookpage.html", BookDetails=BookDetails)





#--------------------------------------------------------------------------
# show the book search page...
#
@app.route('/submitreview', methods = ["POST"])
def submitreview():
    """Submits a review for the given book."""

    # Do the Book Search
    if ( not IsUserLoggedIn()) :
        return redirect(url_for('signin'))

    if not 'CurBookID' in session:
        return redirect(url_for('booksearch'))
    Book_ID = int(session['CurBookID'])

    # Get the button action to perform
    buttonaction = request.form.get ('btnaction')
    if ( 'CancelReview' == buttonaction ):
        return redirect(url_for('bookpage',Book_ID=Book_ID))


    # Now lets find the details for the book...
    BookDetails = fnGetBookDetails ( Book_ID )
    if ( None == BookDetails or None == BookDetails.BookData ) :
        abort(404 , description="Book data not found" )


    if ( 'DeleteReview' == buttonaction ):
        # set the review for this book
        if ( BookDetails.BookReview ):
            finalquery = f"Delete From BookReview WHERE Review_ID = {BookDetails.BookReview[0]}" 
            connection.execute(finalquery)
        return redirect(url_for('bookpage',Book_ID=Book_ID))
    

    InRating = request.form.get("inputRating")
    InReview = request.form.get("inputReview")

    if ((None == InRating) or (not(InRating and InRating.strip()))):
        return render_template("bookpage.html", ErrorMsg="Book Rating is not valid", BookDetails=BookDetails , InRating=InRating , InReview=InReview)
    if ((None == InReview) or (not(InReview and InReview.strip()))):
        return render_template("bookpage.html", ErrorMsg="Book review cannot be left blank", BookDetails=BookDetails, InRating=InRating , InReview=InReview)

    if ( 'SetReview' == buttonaction ):
        # set the review for this book
        finalquery = "INSERT INTO BookReview (Book_ID, User_ID , Review , Rating ) VALUES ({bookid}, {userid}, '{review}' , {rating})" \
                    .format(bookid=Book_ID , userid = session['LoggedUserID'] , review = InReview , rating = int(InRating)) 
        connection.execute(finalquery)
    elif ( 'UpdateReview' == buttonaction ):
        # set the review for this book
        finalquery = "Update BookReview SET Book_ID = {bookid} , User_ID = {userid} , Review = '{review}' , Rating = {rating} , ReviewDate = '{reviewdate}' WHERE Review_ID = {reviewid}" \
                    .format(bookid=Book_ID , userid = session['LoggedUserID'] , review = InReview , rating = int(InRating) , reviewid = BookDetails.BookReview[0] , reviewdate = datetime.utcnow()) 
        connection.execute(finalquery)
        
        
    return redirect(url_for('bookpage',Book_ID=Book_ID))




@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = str(error)), 404




@app.route("/api/<Book_Isbn>")
def BookIsbnApi(Book_Isbn):
    """Return details for the given book."""

    if ((None == Book_Isbn) or (not(Book_Isbn and Book_Isbn.strip()))):
        return jsonify({"error": "Invalid book isbn number in request"}), 422

    # convert the desired string to stripped format for proper checking
    Book_Isbn = Book_Isbn.strip() 

    # Lets first get the book details for this book with given ISBN number.
    BookData = connection.execute("SELECT * FROM BooksData WHERE LOWER(ISBN) = %(isbn)s" , { 'isbn': Book_Isbn.lower() } ).fetchone()

    if BookData is None:
        return jsonify({"error": f"Book data with isbn number '{Book_Isbn}' not found"}), 404

    # AmitTempCode Do the average review data here....
    ReviewCount = 0 
    AverageScore = 1.0
    RatingData = connection.execute( f"SELECT COUNT(Rating), AVG(Rating) FROM BookReview WHERE Book_ID = {BookData[0]}" , ).fetchone()
    if ( RatingData ):
        ReviewCount = RatingData[0] 
        AverageScore = float(RatingData[1])

    return jsonify({
            "title": BookData[2],
            "author": BookData[3],
            "year": BookData[4],
            "isbn": BookData[1],
            "review_count": ReviewCount,
            "average_score": round ( AverageScore , 2 )
        })
