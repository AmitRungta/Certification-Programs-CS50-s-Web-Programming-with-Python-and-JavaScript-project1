# Project 1

Web Programming with Python and JavaScript


Requirements :

--> Login : This feature is implemented using the sign.html page. In this page user can specify their user ID and password to login into the site if already registered with the same credentials. If user is not registered of if some data is empty we show that message in the page as error. From this page user also has a option to go back to index page for Signup to the website. The login event is being handeled in the '/login' route written the application.py file.

--> Signup : Index.html page is being used to register a new user to the site. If the user is already registered then he can direclty go to the signin page through a link on this page. In this page user can specify his userName diaplay name and password ( we ask him to type password 2 times to verify it for correctness ). Signup request is being handled in the route '/createaccount' in application.py file. If there is any error in ceating a account ( like user already present or password mismatch ) we show it in this page and ask him to feed the new data.     


--> Logout : Once the user is logged in we store his credentials inside the session. All the pages once the user is logged in contains a link on the navigation bar for logout which is handeled in the route '/logout' in application.py. Once the user is logged out we redirect him to the signin page.   


--> Import: This featue is being implemented in the import.py file. In here we first create the 3 tables for BooksData, UserData and UserReview. Once all the tables are created we fetch the data from the books.csv file and insert them into the BooksData table one by one.


--> Search Page : once a usr is logged in he is directed to this page. In this page user can search for books on its ISBN / Aurthor or title. If no record is found then its error is shown otherwise list of the books is shown. In this page i am also showing the review of the current user for the books by using the Left Join query while fetching the data. 


--> Book Page: In this page user seeis the  books detail with any review if he has already given. If the user has already given a review then he can delete it or modify it. If no review is specified then he can set a new review for it. 


--> Goodreads Review Data: On your book page, you should also display (if available) the
average rating and number of ratings the work has received from Goodreads.
**************************************************************************



--> API Access: If users make a GET request to your website’s /api/<isbn> route, where
<isbn> is an ISBN number, your website should return a JSON response containing the
book’s title, author, publication date, ISBN number, review count, and average score. The
resulting JSON should follow the format:
**************************************************************************











