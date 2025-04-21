import random


def configure_port():
    port = random.randint(10000, 65000)
    with open('../docs/port.txt', 'w') as file:
        file.write(str(port))
    return port


def order_book_data(data):
    print(data)

    ordered_list = []

    for book in data:
        main_id = book[0]
        isbn = book[1]
        title = book[2]
        author = book[3]
        availability = book[6]
        genre = book[7]
        pages = book[8]
        language = book[9]

        ordered_book = (main_id, isbn, title, author, genre, language, pages, availability)

        ordered_list.append(ordered_book)

    return ordered_list


def prepare_student_data(student_data):
    prepared_list = []
    for student in student_data:
        status = student[6]
        if status == "green":
            new_status = "🟢"
        elif status == "yellow":
            new_status = "🟡"
        elif status == "orange":
            new_status = "🟠"
        elif status == "red":
            new_status = "🔴"
        else:
            new_status = status

        prepared_student = (student[0], student[1], student[2], student[3], student[4], student[5], new_status)
        prepared_list.append(prepared_student)

    return prepared_list


def prepare_loan_data(loan_data):
    prepared_list = []
    for loan in loan_data:
        status = loan[5]
        if status == "green":
            new_status = "🟢"
        elif status == "yellow":
            new_status = "🟡"
        elif status == "orange":
            new_status = "🟠"
        elif status == "red":
            new_status = "🔴"
        else:
            new_status = status

        prepared_loan = (loan[0], loan[1], loan[2], loan[3], loan[4], new_status)
        prepared_list.append(prepared_loan)

    return prepared_list
