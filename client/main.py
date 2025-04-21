import socket
import struct

import ui
import ssl
from queue_handler import *
import queue
import threading
import pickle
import json


def get_port():
    with open("config.json") as f:
        cfg = json.load(f)
        server_ip = cfg["server_ip"]
        port = cfg["port"]
    return server_ip, port


def connect_to_server():
    try:
        context = ssl.create_default_context()
        context.load_verify_locations("../docs/server.crt")

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_secure = context.wrap_socket(client, server_hostname="localhost")
        server_ip, port = get_port()
        client_secure.connect((server_ip, port))
        process_auth_thread = threading.Thread(target=process_auth, args=(client_secure,))
        process_auth_thread.daemon = True
        process_auth_thread.start()

        quiting_thread = threading.Thread(target=wait_for_interface_close, args=(client_secure,))
        quiting_thread.start()
        ui.start_ui()

    except Exception as e:
        print("eee", e)
        ui.error_main_interface()


def process_auth(client_secure):
    def auth_worker():
        while True:
            try:
                auth_data = auth_data_queue.get(timeout=5)

                message = f"{auth_data['auth_type']} {auth_data['username']} {auth_data['password']}"
                try:
                    client_secure.send(message.encode())
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                print(f"Authentifizierungsdaten gesendet: {message}")

                try:
                    response = client_secure.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    print(f"Serverantwort: {response}")

                    if response == "success":
                        print("authenticated")
                        auth_ui_change_queue.put("change")
                        print("nachstes test1")
                        break
                    elif response == "error-retry":
                        auth_ui_change_queue.put("retry")
                        continue
                    elif response == "error-username-taken":
                        print("username taken")
                        continue
                    else:
                        print("error")
                        ui.error_main_interface()

            except queue.Empty:
                print("Warte auf Authentifizierungsdaten...")

            except Exception as e:
                print(f"Fehler im Authentifizierungsprozess: {e}")
                ui.error_main_interface()

    auth_thread = threading.Thread(target=auth_worker)
    auth_thread.daemon = True
    auth_thread.start()
    auth_thread.join()

    process_main_program(client_secure)


def process_main_program(client):
    try:
        client.send(struct.pack("!I", 1))
    except socket.timeout:
        print("Timeout beim Senden")
    except socket.error as e:
        print(f"Fehler beim Senden: {e}")

    data_exchange_thread = threading.Thread(target=process_data_exchange_treeview, args=(client,))
    data_exchange_thread.daemon = True
    data_exchange_thread.start()

    adding_book_thread = threading.Thread(target=process_book_adding, args=(client,))
    adding_book_thread.daemon = True
    adding_book_thread.start()

    adding_student_thread = threading.Thread(target=process_student_adding, args=(client,))
    adding_student_thread.daemon = True
    adding_student_thread.start()

    adding_loans_thread = threading.Thread(target=process_loan_data_exchange, args=(client,))
    adding_loans_thread.daemon = True
    adding_loans_thread.start()

    return_book_thread = threading.Thread(target=process_book_returning, args=(client,))
    return_book_thread.daemon = True
    return_book_thread.start()

    red_loans_request_thread = threading.Thread(target=process_all_red_loans, args=(client,))
    red_loans_request_thread.daemon = True
    red_loans_request_thread.start()

    catalog_request_thread = threading.Thread(target=process_catalog_data_requests, args=(client,))
    catalog_request_thread.daemon = True
    catalog_request_thread.start()

    barcode_card_creation_thread = threading.Thread(target=process_data_for_barcode_card_creation, args=(client,))
    barcode_card_creation_thread.daemon = True
    barcode_card_creation_thread.start()

    extending_thread_thread = threading.Thread(target=process_loan_extending, args=(client,))
    extending_thread_thread.daemon = True
    extending_thread_thread.start()

    emails_thread_thread = threading.Thread(target=process_all_emails, args=(client,))
    emails_thread_thread.daemon = True
    emails_thread_thread.start()

    delete_book_thread = threading.Thread(target=process_delete_book, args=(client,))
    delete_book_thread.daemon = True
    delete_book_thread.start()

    delete_student_thread = threading.Thread(target=process_delete_student, args=(client,))
    delete_student_thread.daemon = True
    delete_student_thread.start()


def process_book_adding(client):
    while True:
        try:
            book_data_message = book_adding_data_exchange_queue.get()
            print(book_data_message)
            if book_data_message:
                try:
                    client.send(struct.pack("!I", 9))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                book_data_message_bytes = pickle.dumps(book_data_message)
                try:
                    client.send(book_data_message_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    answer = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    if answer == "success-book-adding":
                        book_adding_data_answer_queue.put("success")
                    elif answer == "declined-book-adding":
                        book_adding_data_answer_queue.put("declined")
                    else:
                        print("error")
                        book_adding_data_answer_queue.put("error")
        except Exception as e:
            print(e)


def process_book_returning(client):
    while True:
        try:
            book_return_request = return_book_request_queue.get()
            print(book_return_request)
            if book_return_request:
                try:
                    client.send(struct.pack("!I", 19))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                book_return_request_bytes = pickle.dumps(book_return_request)
                try:
                    client.send(book_return_request_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    answer = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    print(answer)
                    if answer == "success-returning-book":
                        return_book_answer_queue.put("success")
                    elif answer == "declined-returning-book":
                        return_book_answer_queue.put("declined")
                    else:
                        print("error")
                        return_book_answer_queue.put("error")
        except Exception as e:
            print(e)


def process_loan_extending(client):
    while True:
        try:
            data = prove_if_loan_queue.get()
            try:
                client.send(struct.pack("!I", 10))
            except socket.timeout:
                print("Timeout beim Senden")
            except socket.error as e:
                print(f"Fehler beim Senden: {e}")

            data_bytes = pickle.dumps(data)
            try:
                client.send(data_bytes)
            except socket.timeout:
                print("Timeout beim Senden")
            except socket.error as e:
                print(f"Fehler beim Senden: {e}")

            try:
                bool_ans_bytes = client.recv(1024)
            except socket.timeout:
                print("Timeout beim Senden")
            except socket.error as e:
                print(f"Fehler beim Senden: {e}")
            else:
                bool_ans = bool(bool_ans_bytes[0])
                print(bool_ans)
                prove_if_loan_ans_queue.put(bool_ans)
                new_loan_data = process_loan_extend_queue.get()
                if new_loan_data:
                    try:
                        client.send(struct.pack("!I", 11))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        client.send(pickle.dumps(new_loan_data))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        ans_bytes = client.recv(1024)
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        ans = bool(ans_bytes[0])
                        process_loan_extend_ans_queue.put(ans)

        except Exception as e:
            print(e)


def process_delete_book(client):
    while True:
        try:
            isbn_data_for_for_delete = send_delete_book_queue.get()
            if isbn_data_for_for_delete:
                try:
                    client.send(struct.pack("!I", 6))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    try:
                        client.send(isbn_data_for_for_delete.encode())
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        try:
                            ans_bytes = client.recv(1024).decode()
                            ans = bool(ans_bytes[0])
                            get_approve_delete_book_queue.put(ans)
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")

            else:
                print("Error")
        except Exception as e:
            print(e)


def process_delete_student(client):
    while True:
        try:
            student_id_data_for_for_delete = send_delete_student_queue.get()
            if student_id_data_for_for_delete:
                try:
                    client.send(struct.pack("!I", 7))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    try:
                        client.send(student_id_data_for_for_delete.encode())
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        try:
                            ans_bytes = client.recv(1024).decode()
                            ans = bool(ans_bytes[0])
                            if ans:
                                get_approve_delete_student_queue.put(ans)
                            else:
                                get_approve_delete_student_queue.put(False)
                        except socket.timeout:
                            print("Timeout beim Senden")
                        except socket.error as e:
                            print(f"Fehler beim Senden: {e}")

            else:
                print("Error")
        except Exception as e:
            print(e)


def process_student_adding(client):
    while True:
        try:
            student_data_message = student_adding_data_exchange_queue.get()
            print(student_data_message)
            if student_data_message:
                try:
                    client.send(struct.pack("!I", 12))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                student_data_message_bytes = pickle.dumps(student_data_message)
                try:
                    client.send(student_data_message_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    answer = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    if answer == "success-student-adding":
                        student_adding_data_answer_queue.put("success")
                    elif answer == "declined-student-adding":
                        student_adding_data_answer_queue.put("declined")
                    else:
                        print("error")
                        student_adding_data_answer_queue.put("error")
        except Exception as e:
            print(e)


def process_loan_data_exchange(client):
    while True:
        try:
            loan_data = loan_data_adding_queue.get()
            print(loan_data)
            if loan_data:
                try:
                    client.send(struct.pack("!I", 20))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                loan_data_bytes = pickle.dumps(loan_data)
                try:
                    client.send(loan_data_bytes)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    answer = client.recv(1024).decode()
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    if answer == "success-loan-adding":
                        loan_adding_data_answer_queue.put("success")
                    elif answer == "declined-loan-adding":
                        loan_adding_data_answer_queue.put("declined")
                    else:
                        print("error")
                        loan_adding_data_answer_queue.put("error")

        except Exception as e:
            print(e)


def process_data_exchange_treeview(client):
    while True:
        try:
            data_request_message = treeview_data_exchange_queue.get()
            print(data_request_message)
            if data_request_message == "get-book-treeview-data":
                try:
                    client.send(struct.pack("!I", 3))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    data_request_answer_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    data_request_answer = pickle.loads(data_request_answer_bytes)
                    treeview_data_request_answer_queue.put(data_request_answer)

            elif data_request_message == "get-student-treeview-data":
                try:
                    client.send(struct.pack("!I", 4))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                try:
                    data_request_answer_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    data_request_answer = pickle.loads(data_request_answer_bytes)
                    treeview_data_request_answer_queue.put(data_request_answer)

            elif data_request_message == "get-loan-treeview-data":
                try:
                    client.send(struct.pack("!I", 5))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    data_request_answer_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    data_request_answer = pickle.loads(data_request_answer_bytes)
                    treeview_data_request_answer_queue.put(data_request_answer)
            else:
                print("error")

        except Exception as e:
            print(e)


def process_all_emails(client):
    while True:
        try:
            request_message = get_all_emails_queue.get()
            if request_message == "get-all-emails":
                try:
                    client.send(struct.pack("!I", 18))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    recv_data_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    recv_data = pickle.loads(recv_data_bytes)

                    emails_data_queue.put(recv_data)
            else:
                print("Error")

        except Exception as e:
            print(e)


def process_all_red_loans(client):
    while True:
        try:
            request_message = get_all_red_loans_queue.get()

            if request_message == "request-all-red-loans":
                try:
                    client.send(struct.pack("!I", 8))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    client_answer_in_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    client_answer = pickle.loads(client_answer_in_bytes)
                    get_all_red_loans_data_queue.put(client_answer)
            else:
                print("error")

        except Exception as e:
            print(e)


def process_catalog_data_requests(client):
    while True:
        try:
            data_request = get_catalog_data_request_queue.get()
            if data_request == "catalog-data-request":
                try:
                    client.send(struct.pack("!I", 21))
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")

                try:
                    catalog_data_bytes = client.recv(4096)
                except socket.timeout:
                    print("Timeout beim Senden")
                except socket.error as e:
                    print(f"Fehler beim Senden: {e}")
                else:
                    catalog_data = pickle.loads(catalog_data_bytes)
                    get_catalog_data_answer_queue.put(catalog_data)
        except Exception as e:
            print(e)


def process_data_for_barcode_card_creation(client):
    while True:
        try:
            mess = send_for_card_barcode_creation_queue.get()
            mess_type, message = mess.split("-", 1)
            if mess_type == "student_specific":
                if message:
                    try:
                        client.send(struct.pack("!I", 13))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    try:
                        client.send(message.encode())
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        answer_student_data_bytes = client.recv(4096)
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        answer_student_data = pickle.loads(answer_student_data_bytes)
                        get_for_card_barcode_creation_queue.put(answer_student_data)
                else:
                    print("error")
                    get_for_card_barcode_creation_queue.put("error")

            elif mess_type == "student_all":
                if message == "amount":
                    try:
                        client.send(struct.pack("!I", 14))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        students_amount = client.recv(1024).decode()
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        get_for_card_barcode_creation_queue.put(students_amount)
                elif message == "data":
                    try:
                        client.send(struct.pack("!I", 15))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        all_student_data_bytes = client.recv(4096)
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        all_student_data = pickle.loads(all_student_data_bytes)
                        get_for_card_barcode_creation_queue.put(all_student_data)

            elif mess_type == "books_all":
                if message == "amount":
                    try:
                        client.send(struct.pack("!I", 17))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        books_amount = client.recv(1024).decode()
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        get_for_card_barcode_creation_queue.put(books_amount)
                elif message == "data":
                    try:
                        client.send(struct.pack("!I", 16))
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")

                    try:
                        all_book_data_bytes = client.recv(4096)
                    except socket.timeout:
                        print("Timeout beim Senden")
                    except socket.error as e:
                        print(f"Fehler beim Senden: {e}")
                    else:
                        all_book_data = pickle.loads(all_book_data_bytes)
                        get_for_card_barcode_creation_queue.put(all_book_data)
        except Exception as e:
            print(e)


def wait_for_interface_close(client):
    try:
        close_mess = close_command_queue.get()
        if close_mess == "close-conn":
            try:
                client.send(struct.pack("!I", 2))
            except socket.timeout:
                print("Timeout beim Senden")
            except socket.error as e:
                print(f"Fehler beim Senden: {e}")

            try:
                answer = client.recv(1024).decode()
            except socket.timeout:
                print("Timeout beim Senden")
            except socket.error as e:
                print(f"Fehler beim Senden: {e}")
            else:
                if answer == "BYE":
                    print("successful closed connection")
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()

        else:
            print("error")
    except Exception as e:
        print(e)


connect_to_server()
