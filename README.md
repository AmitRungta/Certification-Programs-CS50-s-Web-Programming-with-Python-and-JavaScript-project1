# Project 1

Web Programming with Python and JavaScript


Requirements :

--> Login : This feature is implemented using the sign.html page. In this page user can specify their user ID and password to login into the site if already registered with the same credentials. If user is not registered of if some data is empty we show that message in the page as error. From this page user also has a option to go back to index page for Signup to the website. The login event is being handeled in the '/login' route written the application.py file.

--> Signup : Index.html page is being used to register a new user to the site. If the user is already registered then he can direclty go to the signin page through a link on this page. In this page user can specify his userName diaplay name and password ( we ask him to type password 2 times to verify it for correctness ). Signup request is being handled in the route '/createaccount' in application.py file. If there is any error in ceating a account ( like user already present or password mismatch ) we show it in this page and ask him to feed the new data.     


--> Logout : Once the user is logged in we store his credentials inside the session. All the pages once the user is logged in contains a link on the navigation bar for logout which is handeled in the route '/logout' in application.py. Once the user is logged out we redirect him to the signin page.   



--> Import: This featue is being implemented in the import.py file. In here we first create the 3 tables for BooksData, UserData and UserReview. Once all the tables are created we fetch the data from the books.csv file and insert them into the BooksData table one by one.



--> Search Page : Once a user has logged in, they should be taken to a page where they can search for
a book. Users should be able to type in the ISBN number of a book, the title of a book, or
the author of a book. After performing the search, your website should display a list of
possible matching results, or some sort of message if there were no matches. If the user
typed in only part of a title, ISBN, or author name, your search page should find matches for
those as well!
**************************************************************************


--> Book Page: When users click on a book from the results of the search page, they should be
taken to a book page, with details about the book: its title, author, publication year, ISBN
number, and any reviews that users have left for the book on your website.
Review Submission: On the book page, users should be able to submit a review: consisting
of a rating on a scale of 1 to 5, as well as a text component to the review where the user can
write their opinion about a book. Users should not be able to submit multiple reviews for
the same book.
**************************************************************************



--> Goodreads Review Data: On your book page, you should also display (if available) the
average rating and number of ratings the work has received from Goodreads.
**************************************************************************



--> API Access: If users make a GET request to your website’s /api/<isbn> route, where
<isbn> is an ISBN number, your website should return a JSON response containing the
book’s title, author, publication date, ISBN number, review count, and average score. The
resulting JSON should follow the format:
**************************************************************************











