import csv
import os


# DATABASE_URL=postgres://athncldfkluzpq:5dab398fc5ec4f2daf8f2c9b96062478b4cfce8bd2f398312da69fd998ace3db@ec2-34-204-22-76.compute-1.amazonaws.com:5432/d3hv5j2det4su0

# from sqlalchemy import Table, MetaData, create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import Table, MetaData , engine , create_engine 

def main():
    # Create the engine for database connection...
    engine = create_engine(os.getenv("DATABASE_URL"))
    if engine == None:
        return print("Unable to create the engine")     # We are unable to create the engine hence return.

    # Now lets try to connect to this engine.
    connection = engine.connect()
    if connection == None:
        return print("Unable to connect to the engine")     # We are unable to connect to the engine hence return.

    
    bTablesCreated = True

    if False == bTablesCreated:
        # Now lets try to create the Database table for the Books. In this we will will have following columns.
        # Book_ID : this is the prmary ket autogenerated key for keeping the book ID.
        # ISBN : ISBN number of the book. This is a string with maximum of 16 characters and should not be null.
        # Title : Title of the book. This filed is a string which cannot be null.
        # Author : Author of the book. This filed is a string which cannot be null.
        # PubYear : Publication year of the book. This field is of Date type and shold not be null.
        #
        #    
        connection.execute ( "CREATE TABLE BooksData ( \
                                Book_ID SERIAL PRIMARY KEY, \
                                ISBN VARCHAR(16) NOT NULL, \
                                Title VARCHAR NOT NULL, \
                                Author VARCHAR NOT NULL , \
                                PubYear INTEGER NOT NULL); ") 

        # Now lets try to create the Database table for the USers. In this we will will have following columns.
        # User_ID : this is the primary ket autogenerated key for keeping the User ID.
        # UserName : this is the user name for login. This filed is a string which cannot be null.
        # Password : this is the password for login. This filed is a string which cannot be null.
        # DisplayName : Display name for the user. This filed is a string which can be null.
        # JoinDate : Joining date time of the user. This field is of Datetime type and shold not be null.
        #
        #    
        connection.execute ( "CREATE TABLE UserData ( \
                                User_ID SERIAL PRIMARY KEY, \
                                UserName VARCHAR(64) NOT NULL, \
                                Password VARCHAR(64) NOT NULL , \
                                DisplayName VARCHAR(64) NOT NULL , \
                                JoinDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP); ") 

        # Now lets try to create the Database table for the Reviews. In this we will will have following columns.
        # Review_ID : this is the primary key autogenerated  for keeping the Review ID.
        # Book_ID : this is the refence of the Book whose review is this.its a forign key from BooksData table.
        # User_ID : this is the refence of the user who has given this review.its a forign key from UserData table.
        # Review : this is the review for the book by the selected user. This is an optional field for specifying any description.
        # Rating :Rating given by the customer. It should be in the range of 1 to 5.  Display name for the user. This filed is a string which can be null.
        # ReviewDate : Dat and time when this review was submitted. This field is of Datetime type and shold not be null.
        #
        #    
        connection.execute ( "CREATE TABLE BookReview ( \
                                Review_ID SERIAL PRIMARY KEY, \
                                Book_ID INTEGER NOT NULL REFERENCES BooksData, \
                                User_ID INTEGER NOT NULL REFERENCES UserData, \
                                Review VARCHAR(512), \
                                Rating INTEGER NOT NULL CHECK (Rating > 0 AND Rating < 6 ), \
                                ReviewDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP); ") 


    # Now we have create the database hence lets try to add all the data in our books csv file to the database.
    BooksCsvFile = open("books.csv")
    Bookreader = csv.reader(BooksCsvFile)

    # Generate the insert query string     
    sqlInsertQuery = "INSERT INTO BooksData (ISBN, Title , Author , PubYear ) VALUES ('{Isbn}', '{Title}', '{Author}' , {PubYear})"

    transactions = connection.begin()

    iCount = 0 
    iErrorEntries = 0 

    for isbn, title, author , year in Bookreader:
        try:
            iPubYear = int(year)

            # now there can be cases that we might have a ' in the string hence to make it proper we should add another ' in all the strings.
            isbn = isbn.replace ( "'" , "''")
            title = title.replace ( "'" , "''")
            author = author.replace ( "'" , "''")

            finalquery = sqlInsertQuery.format(Isbn=isbn , Title = title , Author = author , PubYear = iPubYear) 
            print (finalquery)
            connection.execute(finalquery)
            iCount += 1
            print (f'Total Entries Added : {iCount}')
        except :
            iErrorEntries += 1
            print (f'Unable to add Isbn: {isbn}, Title: {title}, Author: {author}, PubYear: {year}')
       
    # now lets commit all the additions..
    transactions.commit()
    print (f'Total Error Entries : {iErrorEntries}')





if __name__ == "__main__":
    main()
