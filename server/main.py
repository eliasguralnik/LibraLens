import struct
import threading
import socket
from utils import order_book_data, prepare_student_data, prepare_loan_data
from modules import session, user_auth, email_notification, book_scraper, neural_network, imap_get_emails
import ssl
from server import database
import pickle
from datetime import datetime
import time
import json
from collections import defaultdict

clients = []
blocked_ips = {}

with open('config.json', 'r') as f:
    config_data = json.load(f)

MAX_CONNECTIONS = config_data.get('MAX_CONNECTIONS', 10)
MAX_CONNECTIONS_PER_IP = config_data.get('MAX_CONNECTIONS_PER_IP', 1)
MAX_REQUESTS_PER_SECOND = config_data.get('MAX_REQUESTS_PER_SECOND', 5)
BLOCK_TIME = config_data.get('BLOCK_TIME', 100)

active_connections = defaultdict(int)
request_times = defaultdict(list)


def start_server():
    server_connections = threading.Thread(target=start_connecting)
    server_connections.start()

    server_tasks = threading.Thread(target=handle_server_tasks)
    server_tasks.start()


def get_config():
    with open("config.json") as f:
        cfg = json.load(f)
        server_ip = cfg["server_ip"]
        port = cfg["port"]
    return server_ip, port


def start_connecting():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip, port = get_config()
    server.bind((server_ip, port))
    server.listen(MAX_CONNECTIONS)
    print("server is listening...")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="../docs/server.crt", keyfile="../docs/server.key")

    ssl_server = context.wrap_socket(server, server_side=True)

    try:
        while True:
            client, addr = ssl_server.accept()

            if client is None or addr is None:
                print("Keine Verbindung akzeptiert.")
                continue

            print(f"Connection from {addr}")
            clients.append(client)
            client_handler = threading.Thread(target=handle_client, args=(client, addr))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server wird heruntergefahren...")
        for client in clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except:
                pass
            clients.remove(client)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        ssl_server.shutdown(socket.SHUT_RDWR)
        ssl_server.close()
        print("Server gestoppt.")


def handle_client(client, addr):
    ip = addr[0]
    print(ip)

    if ip in blocked_ips and time.time() - blocked_ips[ip] < BLOCK_TIME:
        print(f"Blockierte IP {ip} versuchte zu verbinden.")
        clients.remove(client)
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    active_connections[ip] += 1
    if active_connections[ip] > MAX_CONNECTIONS_PER_IP:
        print(active_connections[ip])
        print(f"DDoS erkannt: {ip} hat zu viele Verbindungen!")
        blocked_ips[ip] = time.time()
        clients.remove(client)
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    session_id = session.create_session(client)
    print(session_id)

    def handle_worker():
        try:
            auth = client.recv(1024).decode()

            if auth == "close-conn":
                close_client_connection(client)
                print("Client will be closed before auth")
                return

            print(auth)
            status, existing_user = user_auth.auth_process(auth)
            if status is True:
                session.update_session(session_id, existing_user)
                try:
                    client.send("success".encode())
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Error: {e}")

                try:
                    approve_mess = client.recv(4)
                    unpacked_data = struct.unpack("!I", approve_mess)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Error: {e}")
                else:
                    if unpacked_data[0] == 1:
                        handle_client_in_main(client, ip)
                    else:
                        print("error")
            elif existing_user is False:
                try:
                    client.send("error-username-taken".encode())
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    handle_worker()
            else:
                try:
                    client.send("error-retry".encode())
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    handle_worker()

        except (socket.error, Exception) as e:
            print(f"An error occurred with client: {e}")
            clients.remove(client)
            client.shutdown(socket.SHUT_RDWR)
            client.close()

    print("Start worker")
    auth_thread = threading.Thread(target=handle_worker, daemon=True)
    auth_thread.start()


def is_rate_limited(ip):
    current_time = time.time()
    request_times[ip] = [t for t in request_times[ip] if current_time - t < 1]
    print(request_times[ip])

    if len(request_times[ip]) >= MAX_REQUESTS_PER_SECOND:
        return True
    else:
        request_times[ip].append(current_time)
        return False


def handle_client_in_main(client, ip):
    while True:
        if is_rate_limited(ip):
            print(f"DDoS erkannt: {ip} gesperrt!///")
            blocked_ips[ip] = time.time()
            clients.remove(client)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            break

        try:
            client_message_bytes = client.recv(1024)
            client_message = struct.unpack("!I", client_message_bytes)

            if not client_message:
                print(f"Client {ip} hat die Verbindung geschlossen.")
                close_client_connection(client)
                break

            elif client_message[0] == 2:
                close_client_connection(client, ip)
                print(client, "closed")
                break

            elif client_message[0] == 3:
                book_data = database.get_book_data()
                ordered_book_data = order_book_data(book_data)
                book_data_bytes = pickle.dumps(ordered_book_data)
                try:
                    client.send(book_data_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 4:
                student_data = database.get_student_data()
                student_data = prepare_student_data(student_data)
                student_data_bytes = pickle.dumps(student_data)
                try:
                    client.send(student_data_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 5:
                loan_data = database.get_loan_data()
                loan_data = prepare_loan_data(loan_data)
                loan_data_bytes = pickle.dumps(loan_data)
                try:
                    client.send(loan_data_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 6:
                try:
                    isbn_to_delete = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    ans_to_approve = database.delete_book(isbn_to_delete)
                    if ans_to_approve:
                        try:
                            ans_to_approve_bytes = bytes([int(ans_to_approve)])
                            client.send(ans_to_approve_bytes)
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    else:
                        print("error")

            elif client_message[0] == 7:
                try:
                    student_id_to_delete = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    ans_to_approve_student = database.delete_student(student_id_to_delete)
                    if ans_to_approve_student:
                        try:
                            ans_to_approve_student_bytes = bytes([int(ans_to_approve_student)])
                            client.send(ans_to_approve_student_bytes)
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    else:
                        print("error")

            elif client_message[0] == 8:
                all_red_loans = database.get_red_loans("red")
                red_loan_data = get_full_red_loan_data(all_red_loans)
                all_red_loans_bytes = pickle.dumps(red_loan_data)
                try:
                    client.send(all_red_loans_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 9:
                book_data_message = client.recv(4096)
                adding_book_data = pickle.loads(book_data_message)
                answer = database.add_new_book(adding_book_data)
                if answer is True:
                    try:
                        client.send("success-book-adding".encode())
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                elif answer is False:
                    try:
                        client.send("declined-book-adding".encode())
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                else:
                    print("error")
                    try:
                        client.send("error".encode())
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 10:
                try:
                    loan_data_for_prove_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    loan_data_for_prove = pickle.loads(loan_data_for_prove_bytes)
                    bool_ans = database.check_loan(loan_data_for_prove[0], loan_data_for_prove[1])
                    bool_ans_bytes = bytes([int(bool_ans)])
                    try:
                        client.send(bool_ans_bytes)
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 11:
                try:
                    loan_data_for_extend_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    data_extend = pickle.loads(loan_data_for_extend_bytes)
                    extend_update_ans = database.update_loan_for_extend(data_extend[0], data_extend[1], data_extend[2])
                    try:
                        client.send(bytes([int(extend_update_ans)]))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 12:
                try:
                    student_data_message = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    adding_student_data = pickle.loads(student_data_message)
                    answer = database.add_new_student(adding_student_data)
                    if answer is True:
                        try:
                            client.send("success-student-adding".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    elif answer is False:
                        try:
                            client.send("declined-student-adding".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    else:
                        print("error")
                        try:
                            client.send("error".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 13:
                try:
                    student_id = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    if student_id:
                        student_data_req = database.get_student_data_by_id(student_id)
                        student_data_req_bytes = pickle.dumps(student_data_req)
                        try:
                            client.send(student_data_req_bytes)
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    else:
                        print("error")
            elif client_message[0] == 14:
                student_amount = str(database.get_student_amount())
                try:
                    client.send(student_amount.encode())
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 15:
                all_student_data = database.get_student_data()
                all_student_data_bytes = pickle.dumps(all_student_data)
                try:
                    client.send(all_student_data_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 16:
                all_book_data = database.get_book_data()
                all_book_data_bytes = pickle.dumps(all_book_data)
                try:
                    client.send(all_book_data_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 17:
                book_amount = str(database.get_book_amount())
                try:
                    client.send(book_amount.encode())
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 18:
                all_emails = imap_get_emails.main_process()
                all_emails_bytes = pickle.dumps(all_emails)
                try:
                    client.send(all_emails_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 19:
                try:
                    return_book_request = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    return_book_data = pickle.loads(return_book_request)
                    book_id = return_book_data[0]
                    student_id = return_book_data[1]
                    answer = database.delete_loan(book_id, student_id)
                    if answer is True:
                        try:
                            client.send("success-returning-book".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Error: {e}")
                        else:
                            update_after_book_return(book_id, student_id)
                    elif answer is False:
                        try:
                            client.send("declined-returning-book".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Error: {e}")
                    else:
                        print("error")
                        try:
                            client.send("error".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 20:
                try:
                    loan_data_message = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    adding_loan_data = pickle.loads(loan_data_message)
                    answer = database.add_new_loan(adding_loan_data)
                    if answer is True:
                        try:
                            client.send("success-loan-adding".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    elif answer is False:
                        try:
                            client.send("declined-loan-adding".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    else:
                        print("error")
                        try:
                            client.send("error".encode())
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")

            elif client_message[0] == 21:
                with open("../docs/scored_books.json", "r") as json_file:
                    data = json.load(json_file)

                if data:
                    to_send_list = []
                    try:
                        for book in data:
                            new_data = (book["book"], book["thumbnail"], book["isbn"])
                            to_send_list.append(new_data)
                        data_bytes = pickle.dumps(to_send_list)
                        try:
                            client.send(data_bytes)
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")
                    except Exception as e:
                        print(e)
                else:
                    dummy_data = [
                        ("x", "x"), ("x", "x"), ("x", "x"), ("x", "x"),
                        ("x", "x"), ("x", "x"), ("x", "x"), ("x", "x")
                    ]
                    data_bytes = pickle.dumps(dummy_data)
                    try:
                        client.send(data_bytes)
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
            else:
                print("error")
        except Exception as e:
            print(f"Fehler bei der Client-Kommunikation ({ip}): {e}")
            break


def update_after_book_return(book_id, student_id):
    database.update_book_status("available", book_id)
    database.update_students_status("green", student_id)


def get_full_red_loan_data(all_red_loans):
    counter = 0
    red_loans = []
    for loan in all_red_loans:
        student_id = loan[1]
        book_id = loan[2]
        return_date = loan[4]

        student_data = database.get_red_student_data(student_id)
        student_name = student_data[0]
        teacher = student_data[1]
        class_ = student_data[2]
        book_title = database.get_title(book_id)
        database.get_title(book_id)
        red_loan_id = counter

        red_loan = (red_loan_id, student_name, book_title, class_, teacher, return_date)

        counter += 1

        red_loans.append(red_loan)

    return red_loans


def close_client_connection(client, ip):
    try:
        client.send("BYE".encode())
    except socket.timeout:
        print("Timeout beim Senden")
    except socket.error as e:
        print(f"Fehler beim Senden: {e}")

    print("Client closed")
    active_connections[ip] -= 1

    uuid = get_uuid_from_socket(client)
    session.unauthenticated_session(uuid)
    clients.remove(client)
    client.shutdown(socket.SHUT_RDWR)
    client.close()


def get_uuid_from_socket(client_socket):
    data = database.get_all_json()
    for entry in data:
        if entry["client_socket"] == client_socket:
            return entry["session_id"]
    return None


def handle_server_tasks():
    print("start")
    while True:
        update_database_status()

        send_mail_notifications()

        scored_book_list = []
        answer = book_scraper.process_book_scraper()
        if answer is True:
            similar_books = neural_network.calculate_similarity()
            for book, score in similar_books:
                isbn = get_isbn_from_json_by_title(book)
                thumbnail = book_scraper.scrape_thumbnail_link(isbn)
                scored = {
                    "isbn": isbn,
                    "book": book,
                    "score": score,
                    "thumbnail": thumbnail
                }
                scored_book_list.append(scored)
            best_books_list = []
            for best_book in range(8):
                best_books = scored_book_list[best_book]
                best_books_list.append(best_books)

            with open("../docs/scored_books.json", "w") as json_file:
                json.dump(best_books_list, json_file, indent=4)

        else:
            print("error")
        time.sleep(43200)  # 12h


def get_isbn_from_json_by_title(title):
    with open("../docs/books_data.json", "r") as json_file:
        data = json.load(json_file)

    for book in data:
        if book.get("title") == title:
            return book.get("isbn")

    return None


def update_database_status():
    today_date = datetime.today().date()
    loan_data = database.get_all_loans()

    for loan in loan_data:
        return_date = loan[4]
        student_id = loan[1]
        formated_return_date = datetime.strptime(return_date, "%Y-%m-%d").date()
        days_remaining = (formated_return_date - today_date).days
        if days_remaining > 3:
            database.update_loan_status("green", loan[0])
            database.update_students_status("green", student_id)
        elif 0 < days_remaining <= 3:
            database.update_loan_status("yellow", loan[0])
            database.update_students_status("yellow", student_id)
        elif days_remaining == 0:
            database.update_loan_status("orange", loan[0])
            database.update_students_status("orange", student_id)
        elif days_remaining < 0:
            database.update_loan_status("red", loan[0])
            database.update_students_status("red", student_id)
        else:
            print("error")


def send_mail_notifications():
    student_data = database.get_student_data()
    for student in student_data:
        student_id = student[1]
        status = student[6]
        if status == "green":
            pass
        elif status == "yellow":
            title = get_book_title(student_id)
            email_notification.send_message(student[2], student[5], "yellow", title)
        elif status == "orange":
            title = get_book_title(student_id)
            email_notification.send_message(student[2], student[5], "orange", title)
        elif status == "red":
            title = get_book_title(student_id)
            email_notification.send_message(student[2], student[5], "red", title)
        else:
            print("error! No such status")


def get_book_title(student_id):
    book_id = database.get_student_book(student_id)
    book_id = book_id[0]
    book_title = database.get_title(book_id)
    return book_title


start_server()
