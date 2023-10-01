import sqlite3

# Connect to the database
conn = sqlite3.connect('library.db')
c = conn.cursor()

# Create the Books table
c.execute('''CREATE TABLE IF NOT EXISTS Books
             (BookID TEXT PRIMARY KEY,
              Title TEXT,
              Author TEXT,
              ISBN TEXT,
              Status TEXT)''')

# Create the Users table
c.execute('''CREATE TABLE IF NOT EXISTS Users
             (UserID INTEGER PRIMARY KEY,
              Name TEXT,
              Email TEXT)''')

# Create the Reservations table
c.execute('''CREATE TABLE IF NOT EXISTS Reservations
             (ReservationID INTEGER PRIMARY KEY,
              BookID TEXT,
              UserID INTEGER,
              ReservationDate TEXT,
              FOREIGN KEY (BookID) REFERENCES Books (BookID),
              FOREIGN KEY (UserID) REFERENCES Users (UserID))''')

# Add initial users with the names of my girlfriend and myself BTW :)
c.execute("INSERT OR IGNORE INTO Users (UserID, Name, Email) VALUES (1, 'Huang Dongfeng', '123@123.com')")
c.execute("INSERT OR IGNORE INTO Users (UserID, Name, Email) VALUES (2, 'Xie Kaining', '456@456.com')")


# Function to add a new book to the database
def add_book():
    book_id = input("Enter the BookID: ")
    title = input("Enter the Title: ")
    author = input("Enter the Author: ")
    isbn = input("Enter the ISBN: ")

    # Assume the status of the new book is not reserved
    status = "Not Reserved"

    c.execute("INSERT INTO Books (BookID, Title, Author, ISBN, Status) VALUES (?, ?, ?, ?, ?)",
              (book_id, title, author, isbn, status))
    conn.commit()
    print("Book added successfully.")


# Function to find a book's details based on BookID
def find_book_details():
    book_id = input("Enter the BookID: ")

    c.execute('''SELECT Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status,
                        Users.UserID, Users.Name, Users.Email
                 FROM Books
                 LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                 LEFT JOIN Users ON Reservations.UserID = Users.UserID
                 WHERE Books.BookID = ?''', (book_id,))

    result = c.fetchone()

    if result:
        print("BookID:", result[0])
        print("Title:", result[1])
        print("Author:", result[2])
        print("ISBN:", result[3])
        print("Status:", result[4])

        if result[5]:
            print("Reserved by:")
            print("UserID:", result[5])
            print("Name:", result[6])
            print("Email:", result[7])
    else:
        print("Book not found.")


# Function to find a book's reservation status based on BookID, Title, UserID, or ReservationID
def find_reservation_status():
    search_text = input("Enter BookID, Title, UserID, or ReservationID: ")
    found = False  # Flag to track if a match is found

    if search_text.startswith("LB"):
        # Remove the "LB" prefix and treat the remaining part as BookID
        book_id = search_text[2:]
        c.execute('''SELECT Books.Status,
                            Users.UserID, Users.Name, Users.Email,
                            Reservations.ReservationID, Reservations.ReservationDate
                     FROM Books
                     LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                     LEFT JOIN Users ON Reservations.UserID = Users.UserID
                     WHERE Books.BookID = ?''', (book_id,))
        found = True
    elif search_text.startswith("LU"):
        # Remove the "LU" prefix and treat the remaining part as UserID
        user_id = search_text[2:]
        c.execute('''SELECT Books.Status,
                            Users.UserID, Users.Name, Users.Email,
                            Reservations.ReservationID, Reservations.ReservationDate
                     FROM Books
                     LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                     LEFT JOIN Users ON Reservations.UserID = Users.UserID
                     WHERE Users.UserID = ?''', (user_id,))
        found = True
    elif search_text.startswith("LR"):
        # Remove the "LR" prefix and treat the remaining part as ReservationID
        reservation_id = search_text[2:]
        c.execute('''SELECT Books.Status,
                            Users.UserID, Users.Name, Users.Email,
                            Reservations.ReservationID, Reservations.ReservationDate
                     FROM Books
                     LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                     LEFT JOIN Users ON Reservations.UserID = Users.UserID
                     WHERE Reservations.ReservationID = ?''', (reservation_id,))
        found = True
    else:
        c.execute('''SELECT Books.Status,
                            Users.UserID, Users.Name, Users.Email,
                            Reservations.ReservationID, Reservations.ReservationDate
                     FROM Books
                     LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                     LEFT JOIN Users ON Reservations.UserID = Users.UserID
                     WHERE Books.Title LIKE ?''', ('%' + search_text + '%',))
        found = True

    result = c.fetchone()

    if result:
        print("Reservation Status:", result[0])

        if result[1]:
            print("Reserved by:")
            print("UserID:", result[1])
            print("Name:", result[2])
            print("Email:", result[3])
        if result[4]:
            print("ReservationID:", result[4])
            print("Reservation Date:", result[5])

    if not found:
        print("No matching book found.")


# Function to find all the books in the database
def find_all_books():
    c.execute('''SELECT Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status,
                        Users.UserID, Users.Name, Users.Email,
                        Reservations.ReservationID, Reservations.ReservationDate
                 FROM Books
                 LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                 LEFT JOIN Users ON Reservations.UserID = Users.UserID''')

    results = c.fetchall()

    if results:
        for result in results:
            print("BookID:", result[0])
            print("Title:", result[1])
            print("Author:", result[2])
            print("ISBN:", result[3])
            print("Status:", result[4])

            if result[5]:
                print("Reserved by:")
                print("UserID:", result[5])
                print("Name:", result[6])
                print("Email:", result[7])

            if result[8]:
                print("ReservationID:", result[8])
                print("Reservation Date:", result[9])

            print()
    else:
        print("No books found.")


# Function to modify/update book details based on BookID
def update_book_details():
    book_id = input("Enter the BookID: ")

    c.execute("SELECT * FROM Books WHERE BookID = ?", (book_id,))
    result = c.fetchone()

    if result:
        print("Current details:")
        print("Title:", result[1])
        print("Author:", result[2])
        print("ISBN:", result[3])
        print("Status:", result[4])

        choice = input("Do you want to update the reservation status as well? (y/n): ")

        if choice.lower() == "y":
            new_status = input("Enter the new reservation status (Reserved/Not Reserved): ")
            user_id = input("Enter the UserID of the user who reserved the book: ")
            reservation_date = input("Enter the reservation date: ")

            c.execute("UPDATE Books SET Status = ? WHERE BookID = ?", (new_status, book_id))

            c.execute("SELECT * FROM Reservations WHERE BookID = ?", (book_id,))
            reservation_result = c.fetchone()

            if reservation_result:
                c.execute("UPDATE Reservations SET UserID = ?, ReservationDate = ? WHERE BookID = ?",
                          (user_id, reservation_date, book_id))
            else:
                c.execute("INSERT INTO Reservations (BookID, UserID, ReservationDate) VALUES (?, ?, ?)",
                          (book_id, user_id, reservation_date))
        else:
            new_title = input("Enter the new Title: ")
            new_author = input("Enter the new Author: ")
            new_isbn = input("Enter the new ISBN: ")

            c.execute("UPDATE Books SET Title = ?, Author = ?, ISBN = ? WHERE BookID = ?",
                      (new_title, new_author, new_isbn, book_id))

        conn.commit()
        print("Book details updated successfully.")
    else:
        print("Book not found.")


# Function to delete a book based on its BookID
def delete_book():
    book_id = input("Enter the BookID: ")

    c.execute("SELECT * FROM Books WHERE BookID = ?", (book_id,))
    result = c.fetchone()

    if result:
        if result[4] == "Reserved":
            c.execute("DELETE FROM Reservations WHERE BookID = ?", (book_id,))

        c.execute("DELETE FROM Books WHERE BookID = ?", (book_id,))
        conn.commit()
        print("Book deleted successfully.")
    else:
        print("Book not found.")


# Main loop
while True:
    print()
    print("Library Management System Menu:")
    print("1. Add a new book")
    print("2. Find a book's details")
    print("3. Find a book's reservation status")
    print("4. Find all books")
    print("5. Modify/update book details")
    print("6. Delete a book")
    print("7. Exit")

    choice = input("Enter your choice (1-7): ")

    if choice == "1":
        add_book()
    elif choice == "2":
        find_book_details()
    elif choice == "3":
        find_reservation_status()
    elif choice == "4":
        find_all_books()
    elif choice == "5":
        update_book_details()
    elif choice == "6":
        delete_book()
    elif choice == "7":
        break
    else:
        print("Invalid choice. Please enter a number from 1 to 7.")

# Close the database connection
conn.close()