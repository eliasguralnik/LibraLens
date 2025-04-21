import sqlite3
import json
import os
import time
import datetime
import hashlib


def connect_to_database():
    try:
        conn = sqlite3.connect('../database/library.db')
        c = conn.cursor()
        return conn, c

    except Exception as e:
        print(e)


def create_database():
    print("Didn't find a valid database!!!")
    try:
        conn, c = connect_to_database()
        c.execute('''CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )''')
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def delete_book(isbn_to_delete):
    try:
        conn, c = connect_to_database()
        c.execute('''DELETE FROM books WHERE book_isbn = ?''', (isbn_to_delete,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def delete_student(student_id_to_delete):
    try:
        conn, c = connect_to_database()
        c.execute('''DELETE FROM students WHERE student_id = ?''', (student_id_to_delete,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def create_books_table():
    try:
        conn, c = connect_to_database()
        c.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            book_isbn TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            publish_date TEXT,
            status TEXT,
            genre TEXT,
            pages TEXT,
            language TEXT,
            thumbnail_link TEXT
            
        )''')
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def create_students_table():
    try:
        conn, c = connect_to_database()
        c.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            teacher TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT NOT NULL
        )''')
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def create_loans_table():
    try:
        conn, c = connect_to_database()
        c.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY,
            student_id TEXT NOT NULL,
            book_id TEXT NOT NULL,
            loan_date TEXT DEFAULT CURRENT_DATE,
            return_date TEXT,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        );
        """)
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def add_column_to_table(table_name, column_name, column_type):
    sql_command = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    conn, c = connect_to_database()
    try:
        c.execute(sql_command)
        print(f"Spalte '{column_name}' erfolgreich hinzugefügt.")

    except sqlite3.OperationalError:
        print(f"Spalte '{column_name}' existiert bereits.")

    conn.commit()
    conn.close()


def write_reg_data(username, password):
    try:
        print("start writing data...")
        conn, c = connect_to_database()

        c.execute('''SELECT username FROM user WHERE username = ?''', (username, ))
        already_existing_username = c.fetchone()
        if already_existing_username:
            return False, False

        salt = os.urandom(16)
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        combined_pass_salt = f"{hashed_password.hex()}-{salt.hex()}"

        c.execute('''
            INSERT INTO user (username, password) 
            VALUES (?, ?)
            ''', (username, combined_pass_salt))

        conn.commit()
        conn.close()
        print("Data was writen!!!")
        status, existing_user = check_log_data(username, password)
        return status, existing_user

    except Exception as e:
        print(e)


def check_log_data(username, password):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT password FROM user WHERE username = ?''', (username,))
        hashed_password = c.fetchone()
        if hashed_password:
            print("test1", hashed_password)
            hashed_password = hashed_password[0]
            print("test2", hashed_password)
            stored_hash, stored_salt = hashed_password.split('-')
            print("test---", stored_salt, "----", stored_hash)
            stored_salt = bytes.fromhex(stored_salt)
            input_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), stored_salt, 100000)
            if input_hash.hex() == stored_hash:
                return True, username
            else:
                return False, username
        else:
            print("login attempt denied!")
            return False, None

    except Exception as e:
        print(e)


def create_sessions_json(session):
    file_path = "../database/session.json"
    session["client_socket"] = str(session["client_socket"])
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        data.append(session)

    else:
        data = [session]

    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Daten wurden hinzugefügt oder bearbeitet!")


def update_session_json(session_id_update, user_name):
    file_path = "../database/session.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        for s in data:
            if s["session_id"] == session_id_update:
                s["last_activity"] = time.time()
                s["authenticated"] = True
                s["username"] = user_name

        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Sitzung {session_id_update} wurde aktualisiert!")
    else:
        print("Die Datei existiert nicht!")


def unauthenticated_session_json(session_id_update):
    file_path = "../database/session.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        for s in data:
            if s["session_id"] == session_id_update:
                s["last_activity"] = time.time()
                s["authenticated"] = False

        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Sitzung {session_id_update} wurde aktualisiert!")
    else:
        print("Die Datei existiert nicht!")


def get_all_json():
    with open("../database/session.json", "r") as json_file:
        json_file_data = json.load(json_file)

    return json_file_data


def get_book_data():
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT * FROM books''')
        books = c.fetchall()
        return books

    except Exception as e:
        print(e)


def get_student_data():
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT * FROM students''')
        students = c.fetchall()
        return students

    except Exception as e:
        print(e)


def get_loan_data():
    try:
        conn, c = connect_to_database()

        query = '''
        SELECT * FROM loans
        '''

        c.execute(query)

        data = c.fetchall()
        prepared_data = []
        for loan in data:
            student_id = loan[1]
            book_isbn = loan[2]
            title = get_title(book_isbn)
            student_name = get_name(student_id)
            new_data = (loan[0], student_name, title, loan[3], loan[4], loan[5])
            prepared_data.append(new_data)
        conn.close()

        return prepared_data

    except Exception as e:
        print(f"Fehler: {e}")
        return None


def add_new_book(book_data):
    try:
        print("start writing data...")
        conn, c = connect_to_database()

        c.execute('''
            INSERT INTO books (book_isbn, title, author, description, 
            publish_date, status, genre, pages, thumbnail_link, language) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            (book_data[3]).strip(), book_data[0], book_data[1], book_data[8], book_data[4],
            "available", book_data[2], book_data[6], book_data[7], book_data[5]))

        conn.commit()
        conn.close()
        print("Data was written!!!")
        return True

    except Exception as e:
        print(e)
        return False


def add_new_student(student_data):
    try:
        print("start writing data...")
        conn, c = connect_to_database()

        c.execute('''
            INSERT INTO students (student_id, name, class, teacher, 
            email, status) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
            student_data[0], student_data[1], student_data[2], student_data[3], student_data[4], "green"))

        conn.commit()
        conn.close()
        print("Data was written!!!")
        return True

    except Exception as e:
        print(e)
        return False


def check_exists(cursor, table, column, value):
    print("test2")
    cursor.execute(f"SELECT 1 FROM {table} WHERE {column} = ?", (value,))
    print("test3")
    return cursor.fetchone() is not None


def add_new_loan(loan_data):
    try:
        conn, c = connect_to_database()

        if not check_exists(c, "students", "student_id", loan_data[1]):
            print("error")
            conn.close()
            return False

        if not check_exists(c, "books", "book_isbn", loan_data[0]):
            print("error")
            conn.close()
            return False

        print("start writing data...")

        c.execute('''
            INSERT INTO loans (book_id, student_id, return_date, status) 
            VALUES (?, ?, ?, ?)
            ''', (
            loan_data[0], loan_data[1], loan_data[2], "green"))

        conn.commit()
        conn.close()
        print("Data was written!!!")
        return True

    except Exception as e:
        print(e)
        return False


def get_all_loans():
    try:
        conn, c = connect_to_database()

        c.execute("SELECT * FROM loans")

        data = c.fetchall()

        conn.close()

        return data

    except Exception as e:
        print(e)


def update_loan_status(status_value, loan_id):
    conn, c = connect_to_database()

    update_query = '''
    UPDATE loans
    SET status = ?
    WHERE loan_id = ?;
    '''
    values = (status_value, loan_id)

    c.execute(update_query, values)
    conn.commit()
    conn.close()


def update_students_status(status_value, id_):
    conn, c = connect_to_database()
    print(status_value, id_)
    update_query = '''
    UPDATE students
    SET status = ?
    WHERE student_id = ?;
    '''
    values = (status_value, id_)
    c.execute(update_query, values)
    conn.commit()
    conn.close()


def update_book_status(status_value, id_):
    conn, c = connect_to_database()

    update_query = '''
    UPDATE books
    SET status = ?
    WHERE id = ?;
    '''
    values = (status_value, id_)

    c.execute(update_query, values)
    conn.commit()
    conn.close()


def get_student_book(student_id):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT book_id FROM loans WHERE student_id = ?''', (student_id,))
        students = c.fetchone()
        return students

    except Exception as e:
        print(e)


def get_title(book_isbn):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT title FROM books WHERE book_isbn = ?''', (book_isbn,))
        result = c.fetchone()
        if result:
            book_title = result[0]
            return book_title
        else:
            return None

    except Exception as e:
        print(e)


def get_name(student_id):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT name FROM students WHERE student_id = ?''', (student_id,))
        result = c.fetchone()
        if result:
            name = result[0]
            return name
        else:
            return None

    except Exception as e:
        print(e)


def get_red_student_data(student_id):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT name, teacher, class FROM students WHERE student_id = ?''', (student_id,))
        red_student_data = c.fetchone()
        return red_student_data

    except Exception as e:
        print(e)


def delete_loan(book_isbn, student_id):
    try:
        save_returned_loan(book_isbn, student_id)
        conn, c = connect_to_database()
        c.execute('''DELETE FROM loans WHERE student_id = ? AND book_id = ?''', (student_id, book_isbn))

        conn.commit()
        conn.close()

        return True

    except sqlite3.Error as e:
        print("Fehler beim Löschen: ", e)

        return False


def save_returned_loan(book_isbn, student_id):
    file = '../docs/returned-loans.json'

    if os.path.exists(file):
        with open(file, "r") as f:
            try:
                all_returns = json.load(f)
            except json.JSONDecodeError:
                all_returns = []
    else:
        all_returns = []

    data = {
        "book_isbn": book_isbn.strip(),
        "student_id": student_id,
        "return_date": datetime.datetime.now().isoformat()
    }

    all_returns.append(data)

    with open(file, "w") as f:
        json.dump(all_returns, f, indent=4)


def get_red_loans(status):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT * FROM loans WHERE status = ?''', (status,))
        all_red_loans = c.fetchall()
        return all_red_loans

    except Exception as e:
        print(e)


def get_thumbnail(isbn):
    try:
        conn, c = connect_to_database()
        print(isbn)
        c.execute('''SELECT thumbnail_link FROM books WHERE book_isbn = ?''', (isbn,))
        thumbnail_link = c.fetchone()
        thumbnail_link = thumbnail_link[0]
        return thumbnail_link
    except Exception as e:
        print(e)
        return None


def get_student_data_by_id(student_id):
    try:
        conn, c = connect_to_database()
        c.execute('''Select * FROM students WHERE student_id = ?''', (student_id,))
        student_data = c.fetchone()
        return student_data
    except Exception as e:
        print(e)


def get_student_amount():
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT COUNT(*) FROM students''')
        students_count = c.fetchone()[0]
        return students_count
    except Exception as e:
        print(e)


def get_book_amount():
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT COUNT(*) FROM books''')
        book_count = c.fetchone()[0]
        return book_count
    except Exception as e:
        print(e)


def check_loan(book_id, student_id):
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT loan_id FROM loans WHERE book_id = ? AND student_id = ?''', (book_id, student_id))
        true_loan = c.fetchone()
        if true_loan is not None:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def update_loan_for_extend(book_id, student_id, new_due_date):
    try:
        conn, c = connect_to_database()

        update_query = '''
            UPDATE loans
            SET return_date = ?
            WHERE book_id = ? AND student_id = ?;
            '''
        values = (new_due_date, book_id, student_id)

        if c.execute(update_query, values):
            conn.commit()
            conn.close()
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def get_all_student_emails():
    try:
        conn, c = connect_to_database()
        c.execute('''SELECT email FROM students''')
        all_student_emails = c.fetchall()
        email_list = [email[0] for email in all_student_emails]
        return email_list

    except Exception as e:
        print(e)

