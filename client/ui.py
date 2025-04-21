import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
from tkinter import messagebox
from queue_handler import *
import queue
from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import hashlib
import re
import os
from collections import deque
from create_student_id_card import process_single_card_creation, process_all_card_creation, create_barcode
import webbrowser
import urllib.parse

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def start_ui():
    root = ctk.CTk()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    app = App(root)
    root.mainloop()


def on_close(root):
    close_command_queue.put("close-conn")
    root.destroy()


class App:
    def __init__(self, root):
        self.root = root
        self.content_frame = None
        self.logo_photo = None
        self.sidebar_frame = None

        self.root.title("Libra-Lens")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.auth_frame = ctk.CTkFrame(self.root)
        self.main_frame = ctk.CTkFrame(self.root)
        self.start_authentication()
        self.wait_change_auth_frame()

    def start_authentication(self):
        if self.auth_frame is None:
            self.auth_frame = ctk.CTkFrame(self.root)
        self.auth_frame.pack(fill="both", expand=True)
        Authentication(self.auth_frame)

    def wait_change_auth_frame(self):
        try:
            change_mess = auth_ui_change_queue.get_nowait()
            if change_mess == "change":
                self.auth_frame.destroy()
                self.auth_frame = None
                self.main_widget()
            elif change_mess == "retry":
                messagebox.showerror("Error", "Password or Username is incorrect")
                self.root.after(500, self.wait_change_auth_frame)
        except queue.Empty:
            self.root.after(500, self.wait_change_auth_frame)

    def main_widget(self):
        self.main_frame.pack(fill="both", expand=True)
        self.sidebar_frame = ctk.CTkFrame(self.main_frame)
        self.sidebar_frame.pack(side="left", fill='y', padx=10, pady=10)
        self.sidebar_widget()
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill='both', expand=True, padx=10, pady=10)
        HomeFrame(self.content_frame)

    def sidebar_widget(self):
        try:
            logo_image = Image.open('../assets/LibraLens_Logo.png')
            self.logo_photo = ctk.CTkImage(logo_image, size=(160, 150))
            logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_photo, text="")
            logo_label.pack(padx=5, pady=50)

        except Exception as e:
            print(f"Fehler beim Laden des Logos: {e}")

        buttons = [
            ("Home", lambda: (self.destroy_all_children(), HomeFrame(self.content_frame))),
            ("Books", lambda: (self.destroy_all_children(), BooksFrame(self.content_frame))),
            ("Students", lambda: (self.destroy_all_children(), StudentsFrame(self.content_frame))),
            ("Loans", lambda: (self.destroy_all_children(), LoansFrame(self.content_frame)))
        ]
        for text, command in buttons:
            ctk.CTkButton(self.sidebar_frame, text=text, command=command).pack(padx=8, pady=25, fill='x')

        logout_button = ctk.CTkButton(self.sidebar_frame, text="Log Out", command=lambda: on_close(self.root))
        logout_button.pack(side='bottom', padx=20, pady=20)

    def destroy_all_children(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


class Authentication:
    def __init__(self, parent):
        self.to_many_attempts_label = None
        self.login_button = None
        self.registr_button = None
        self.error_message_label = None
        self.auth_frame = None
        self.registr_frame = None
        self.login_frame = None
        self.log_username_entry = None
        self.log_password_entry = None
        self.reg_username_entry = None
        self.reg_password_entry = None

        self.parent = parent
        self.login_attempts = deque(maxlen=5)
        self.block_until = 0

        self.main_frame = ctk.CTkFrame(parent)
        self.main_frame.pack(fill='both', expand=True)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.registration_frame_func()

    def registration_frame_func(self):
        if self.login_frame:
            self.login_frame.grid_forget()

        self.registr_frame = ctk.CTkFrame(self.main_frame, border_width=5)
        self.registr_frame.grid(ipadx=50)

        ctk.CTkLabel(self.registr_frame, text="Registration", font=("Arial", 25)).pack(pady=20)

        ctk.CTkLabel(self.registr_frame, text="Username").pack(pady=(12, 5))
        self.reg_username_entry = ctk.CTkEntry(self.registr_frame, width=250)
        self.reg_username_entry.pack()

        ctk.CTkLabel(self.registr_frame, text="Password").pack(pady=(12, 5))
        self.reg_password_entry = ctk.CTkEntry(self.registr_frame, show="*", width=250)
        self.reg_password_entry.pack()

        self.error_message_label = ctk.CTkLabel(self.registr_frame, text="", font=("Arial", 12), text_color="red")
        self.error_message_label.pack(pady=(2, 5))

        self.registr_button = ctk.CTkButton(self.registr_frame, text="Sign Up", state=tk.DISABLED,
                                            command=self.register, width=250)
        self.registr_button.pack(pady=10)

        self.reg_username_entry.bind("<KeyRelease>", self.validate_entry)
        self.reg_password_entry.bind("<KeyRelease>", self.validate_entry)

        login_button = ctk.CTkLabel(self.registr_frame, text="Already have an account? Login now")
        login_button.pack(pady=10)
        login_button.bind("<Button-1>", lambda event: self.login_frame_func())

    def validate_entry(self, event=None):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()

        if not username or not password:
            self.error_message_label.configure(text="", text_color="red")
            self.registr_button.configure(state=tk.DISABLED)
            return

        forbidden_pattern = [
            r"(--|\#|\/\*|\*\/|;)",
            r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bDELETE\b|\bUPDATE\b|\bINSERT\b)",
            r"('|\"|`)"
        ]

        for pattern in forbidden_pattern:
            if re.search(pattern, username, re.IGNORECASE) or re.search(pattern, password, re.IGNORECASE):
                self.error_message_label.configure(text="Input contains forbidden characters!", text_color="red")
                self.registr_button.configure(state=tk.DISABLED)
                return

        has_lower = re.search(r'[a-z]', password)
        has_upper = re.search(r'[A-Z]', password)
        has_digit = re.search(r'\d', password)
        has_symbol = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

        if not all([has_lower, has_upper, has_digit, has_symbol]):
            self.error_message_label.configure(text="Password must have lower, upper, digit, and symbol")
            self.registr_button.configure(state=tk.DISABLED)
            return

        if len(password) < 8:
            self.error_message_label.configure(text="Password should be at least 8 characters long")
            self.registr_button.configure(state=tk.DISABLED)
            return

        self.error_message_label.configure(text="")
        self.registr_button.configure(state=tk.NORMAL)

    def login_frame_func(self):
        if self.registr_frame:
            self.registr_frame.grid_forget()

        self.login_frame = ctk.CTkFrame(self.main_frame, border_width=5)
        self.login_frame.grid(ipadx=50)

        ctk.CTkLabel(self.login_frame, text="LogIn", font=("Arial", 25)).pack(pady=20)

        ctk.CTkLabel(self.login_frame, text="Username").pack(pady=(12, 5))
        self.log_username_entry = ctk.CTkEntry(self.login_frame, width=250)
        self.log_username_entry.pack()

        ctk.CTkLabel(self.login_frame, text="Password").pack(pady=(12, 5))
        self.log_password_entry = ctk.CTkEntry(self.login_frame, show="*", width=250)
        self.log_password_entry.pack()

        self.to_many_attempts_label = ctk.CTkLabel(self.login_frame, text="", font=("Arial", 12), text_color="red")
        self.to_many_attempts_label.pack(pady=(2, 5))

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login, width=250)
        self.login_button.pack(pady=10)

        reg_button = ctk.CTkLabel(self.login_frame, text="Don't have an account? Sign Up now")
        reg_button.pack(pady=10)
        reg_button.bind("<Button-1>", lambda event: self.registration_frame_func())

    def login(self):
        current_time = time.time()

        if current_time < self.block_until:
            remaining_time = int(self.block_until - current_time)
            if remaining_time > 60:
                (self.to_many_attempts_label
                 .configure(text=f"Too many attempts! Try again in {int((remaining_time / 60) + 1)} min."))
                return
            elif 0 < remaining_time < 60:
                self.to_many_attempts_label.configure(text=f"Too many attempts! Try again in {remaining_time} sec.")
                return
            else:
                self.to_many_attempts_label.configure(text=f"Something went wrong, try again later!")
                return

        self.login_attempts = deque([t for t in self.login_attempts if current_time - t < 180], maxlen=5)

        if len(self.login_attempts) >= 5:
            self.block_until = current_time + 180
            self.to_many_attempts_label.configure(text="Too many attempts, try again later!")
            return

        self.login_attempts.append(time.time())

        username = self.log_username_entry.get()
        password = self.log_password_entry.get()

        auth_data = {
            'auth_type': 'login',
            'username': username,
            'password': hashlib.sha256(password.encode()).hexdigest()
        }
        auth_data_queue.put(auth_data)

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()

        auth_data = {
            'auth_type': 'registration',
            'username': username,
            'password': hashlib.sha256(password.encode()).hexdigest()
        }
        auth_data_queue.put(auth_data)


class HomeFrame:
    def __init__(self, parent):
        self.data = None
        self.email_tree = None
        self.email_frame = None
        self.temp_extend_data_list = None
        self.popup_extend = None
        self.return_date_entry_extend = None
        self.student_id_entry_extend = None
        self.book_id_entry_extend = None
        self.next_button = None
        self.book_isbn_for_barcode_entry = None
        self.student_id_for_card_entry = None
        self.picked_content_frame = None
        self.selected_radio_2 = None
        self.second_frame = None
        self.first_frame = None
        self.selected_radio = None
        self.popup_add_doc = None
        self.tabs = None
        self.note_name_counter = None
        self.notebook = None
        self.text_area = None
        self.message_entry = None
        self.chat_display = None
        self.catalog_frame = None
        self.notes_frame = None
        self.red_loans_frame = None
        self.main_content_widget_frame = None
        self.student_id_entry_return = None
        self.book_id_entry_return = None
        self.popup_return_book = None
        self.return_date_entry = None
        self.book_id_entry = None
        self.student_id_entry = None
        self.popup_add_loan = None
        self.upper_content_widget_frame = None
        self.parent = parent  # content_frame

        self.home_frame = self.create_scrollable_main_frame()
        self.home_frame_widget()

    def create_scrollable_main_frame(self):
        canvas = tk.Canvas(self.parent, borderwidth=0, background="#f0f0f0", height=400)
        scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, background="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_mac(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(-1 * event.delta, "units")

        if self.parent.tk.call("tk", "windowingsystem") == "aqua":
            canvas.bind_all("<MouseWheel>", on_mousewheel_mac)  # macOS
        else:
            canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/Linux

        return scrollable_frame

    def home_frame_widget(self):
        self.upper_content_widget_frame = tk.Frame(self.home_frame)
        self.upper_content_widget_frame.pack(fill='both', expand=True, ipady=20)
        self.upper_content_widget()

        self.main_content_widget_frame = tk.Frame(self.home_frame)
        self.main_content_widget_frame.pack(fill='both', expand=True)
        self.main_content_widget()

    def upper_content_widget(self):
        add_loan_button = ctk.CTkButton(self.upper_content_widget_frame, text="Add new loan",
                                        command=self.create_add_loan_widget, width=250, height=50)
        add_loan_button.grid(column=0, row=0, padx=40)

        return_book_button = ctk.CTkButton(self.upper_content_widget_frame, text="Return Book",
                                           command=self.create_return_book_widget, width=250, height=50)
        return_book_button.grid(column=1, row=0, padx=40)

        extend_loan_button = ctk.CTkButton(self.upper_content_widget_frame, text="Extend Loan",
                                           command=self.create_extend_loan_widget, width=250, height=50)
        extend_loan_button.grid(column=2, row=0, padx=40)

        print_barcodes_button = ctk.CTkButton(self.upper_content_widget_frame, text=" 📁 ", font=("Arial", 25),
                                              command=self.create_documents_widget, width=100, height=50)
        print_barcodes_button.grid(column=3, row=0, padx=40)

    def main_content_widget(self):
        self.red_loans_frame = tk.Frame(self.main_content_widget_frame)
        self.red_loans_frame.grid(column=0, row=0, sticky="nsew", padx=(30, 0), pady=10)
        self.red_loans_widget()

        self.notes_frame = tk.Frame(self.main_content_widget_frame)
        self.notes_frame.grid(column=1, row=0, sticky="nsew")
        self.create_notes_widget()

        self.catalog_frame = tk.Frame(self.main_content_widget_frame)
        self.catalog_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(40, 5), padx=55)
        self.create_catalog_widget()

        self.email_frame = tk.Frame(self.main_content_widget_frame)
        self.email_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(40, 5), padx=55)
        self.create_email_widget()

        self.main_content_widget_frame.grid_rowconfigure(0, weight=1)
        self.main_content_widget_frame.grid_rowconfigure(1, weight=1)

        self.main_content_widget_frame.grid_columnconfigure(0, weight=1)
        self.main_content_widget_frame.grid_columnconfigure(1, weight=1)

    def create_email_widget(self):
        main_email_frame = tk.Frame(self.email_frame)
        main_email_frame.pack()

        ctk.CTkLabel(main_email_frame, text="Emails", font=("Arial", 25)).pack(pady=20)

        self.data = self.get_emails()

        columns = ("col1", "col2", "col3", "col4", "col5")
        self.email_tree = ttk.Treeview(main_email_frame, columns=columns, show="headings")
        column_settings = [
            ("col1", "ID", 50),
            ("col2", "Sender", 250),
            ("col3", "Title", 300),
            ("col4", "Content", 250),
            ("col5", "", 0)
        ]
        counter = 0
        for col, text, width in column_settings:
            self.email_tree.heading(col, text=text)
            self.email_tree.column(col, width=width, anchor="center")
        self.email_tree.column("col5", width=0, stretch=False)

        if self.data:
            for email in self.data:
                content = email["content"]
                short_content = content[:30] + "..." if len(content) > 30 else content

                self.email_tree.insert("", "end", values=(counter, email["from"], email["subject"], short_content, email["id"]))

                counter += 1

        self.email_tree.pack(padx=10, pady=10, fill="x", expand=True)
        self.email_tree.bind("<ButtonRelease-1>", self.on_tree_click_email)

    def on_tree_click_email(self, event):
        selected_item = self.email_tree.identify_row(event.y)

        if selected_item:
            values = self.email_tree.item(selected_item, "values")
            value_id, value_sender, value_title, value_content, mess_id = values

            popup = ctk.CTkToplevel(self.main_content_widget_frame)
            popup.geometry("350x400+500+200")
            popup.title(f"Manage Message: {value_title}")
            popup.resizable(False, False)

            ctk.CTkLabel(popup, text=value_title, font=("Arial", 22)).pack(pady=20)

            sender_grid_frame = ctk.CTkFrame(popup)
            sender_grid_frame.pack(fill='x', expand=True, pady=15, padx=10)

            ctk.CTkLabel(sender_grid_frame, text="From: ").grid(column=0, row=0, padx=3)
            ctk.CTkLabel(sender_grid_frame, text=value_sender).grid(column=1, row=0, padx=3)

            ctk.CTkLabel(popup, text="Message:").pack()
            text_widget = tk.Text(popup, wrap="word", width=50, height=10)
            text_widget.insert("1.0", value_content)
            text_widget.config(state="disabled")
            text_widget.pack(padx=10)

            button_grid_button_frame = ctk.CTkFrame(popup)
            button_grid_button_frame.pack(pady=20)

            gmail_url = f"https://mail.google.com/mail/u/0/#msgid={mess_id}"

            open_mess_button = ctk.CTkButton(button_grid_button_frame, text="Open Message in Browser",
                                             command=lambda: self.open_gmail_link(gmail_url))
            open_mess_button.grid(column=0, row=0, padx=5)

            mailto_button = ctk.CTkButton(button_grid_button_frame, text="Respond",
                                          command=lambda: self.process_mailto(value_sender))
            mailto_button.grid(column=1, row=0, padx=5)

    def process_mailto(self, sender):
        title = "Reply from Libra Lens"
        body_text = """\
        Dear customer,






        Best regards
        Libra Lens 
        """
        subject_encoded = urllib.parse.quote(title)
        body_encoded = urllib.parse.quote(body_text)
        mailto_link = f"mailto:{sender}?subject={subject_encoded}&body={body_encoded}"
        webbrowser.open(mailto_link)

    def open_gmail_link(self, url):
        webbrowser.open(url)

    def get_emails(self):
        get_all_emails_queue.put("get-all-emails")

        data = emails_data_queue.get()
        return data

    def create_extend_loan_widget(self):
        self.popup_extend = ctk.CTkToplevel(self.home_frame)
        self.popup_extend.title("Popup")
        self.popup_extend.geometry("350x400+500+200")
        self.popup_extend.resizable(False, False)

        ctk.CTkLabel(self.popup_extend, text="Extend Loan", font=("Arial", 20)).pack(pady=20)

        book_id_entry_label = ctk.CTkLabel(self.popup_extend, text="Book ID")
        book_id_entry_label.pack()
        self.book_id_entry_extend = ctk.CTkEntry(self.popup_extend, width=250)
        self.book_id_entry_extend.pack()

        student_id_entry_label = ctk.CTkLabel(self.popup_extend, text="Student ID")
        student_id_entry_label.pack()
        self.student_id_entry_extend = ctk.CTkEntry(self.popup_extend, width=250)
        self.student_id_entry_extend.pack()

        button_grid_frame = ctk.CTkFrame(self.popup_extend)
        button_grid_frame.pack(pady=35)

        add_button = ctk.CTkButton(button_grid_frame, text="next", command=self.extend_after_prove_widget)
        add_button.grid(column=0, row=0, padx=10)

        cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.cancel_process)
        cancel_button.grid(column=1, row=0, padx=10)

    def extend_after_prove_widget(self):
        book_id_for_extend = self.book_id_entry_extend.get()
        student_id_for_extend = self.student_id_entry_extend.get()
        data = [book_id_for_extend, student_id_for_extend]
        prove_if_loan_queue.put(data)
        bool_ans = prove_if_loan_ans_queue.get()
        if bool_ans is True:
            self.temp_extend_data_list = [book_id_for_extend, student_id_for_extend]
            self.clear_frame(self.popup_extend)
            ctk.CTkLabel(self.popup_extend, text=f"Book ISBN: {book_id_for_extend}", font=("Arial", 18)).pack(pady=10)
            ctk.CTkLabel(self.popup_extend, text=f"Student ID: {student_id_for_extend}",
                         font=("Arial", 18)).pack(pady=10)

            return_date_entry_label = ctk.CTkLabel(self.popup_extend, text="Return Date")
            return_date_entry_label.pack(pady=(25, 0))

            grid_frame_return_date = ctk.CTkFrame(self.popup_extend)
            grid_frame_return_date.pack()

            self.return_date_entry_extend = DateEntry(grid_frame_return_date,
                                                      width=12, background="darkblue", foreground="white",
                                                      borderwidth=2,
                                                      date_pattern="yyyy-mm-dd")
            self.return_date_entry_extend.grid(column=0, row=1, padx=10)

            suggest_return_date_button = ctk.CTkButton(grid_frame_return_date, text="Suggest",
                                                       command=self.suggest_extended_date, width=50)
            suggest_return_date_button.grid(column=1, row=1, padx=10)

            button_grid_frame = ctk.CTkFrame(self.popup_extend)
            button_grid_frame.pack(pady=35)

            finish_button = ctk.CTkButton(button_grid_frame, text="finish", command=self.process_loan_extend)
            finish_button.grid(column=0, row=0, padx=10)

            cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.cancel_process)
            cancel_button.grid(column=1, row=0, padx=10)

        elif bool_ans is False:
            messagebox.showinfo("Error", "No such loan")
            self.popup_extend.destroy()
        else:
            messagebox.showerror("Error", "Something went wrong")
            self.popup_extend.destroy()

    def suggest_extended_date(self):
        today = datetime.today()
        suggested_return_date = today + timedelta(days=14)
        self.return_date_entry_extend.delete(0, tk.END)
        self.return_date_entry_extend.insert(0, suggested_return_date.strftime("%Y-%m-%d"))

    def process_loan_extend(self):
        book_id = self.temp_extend_data_list[0]
        student_id = self.temp_extend_data_list[1]
        new_return_date = self.return_date_entry_extend.get()
        loan_extend_data = [book_id, student_id, new_return_date]
        process_loan_extend_queue.put(loan_extend_data)
        ans = process_loan_extend_ans_queue.get()
        if ans is True:
            messagebox.showinfo("Success", f"Due date was extended to: \n {new_return_date}")
            self.popup_extend.destroy()
        elif ans is False:
            messagebox.showinfo("Error", "It was not possible to extend the due date")
            self.popup_extend.destroy()

        else:
            messagebox.showerror("Error", "Something went wrong")
            self.popup_extend.destroy()

    def create_documents_widget(self):
        self.popup_add_doc = ctk.CTkToplevel(self.home_frame)
        self.popup_add_doc.title("Documents")
        self.popup_add_doc.geometry("350x400+500+200")
        self.popup_add_doc.resizable(False, False)

        self.first_frame = ctk.CTkFrame(self.popup_add_doc)
        self.first_frame.pack(fill='both', expand=True)

        self.second_frame = ctk.CTkFrame(self.popup_add_doc)

        ctk.CTkLabel(self.first_frame, text="Do you want to create a Student ID card or a Book ISBN Barcode?",
                     wraplength=250, font=("Arial", 15)).pack(pady=20)

        self.selected_radio = tk.StringVar()

        radio_card = ctk.CTkRadioButton(self.first_frame, text="Create Student ID card",
                                        value="card", variable=self.selected_radio,
                                        command=lambda: (self.add_content_to_first(), self.check_radios()))
        radio_barcode = ctk.CTkRadioButton(self.first_frame, text="Create Book ISBN Barcode",
                                           value="barcode", variable=self.selected_radio,
                                           command=lambda: (self.add_content_to_first(), self.check_radios()))

        radio_card.pack(pady=5)
        radio_barcode.pack(pady=5)

        self.picked_content_frame = ctk.CTkFrame(self.first_frame, height=150)
        self.picked_content_frame.pack(fill='x', expand=True)

        button_grid_frame = ctk.CTkFrame(self.first_frame)
        button_grid_frame.pack(pady=20)

        self.next_button = ctk.CTkButton(button_grid_frame, text="next", command=self.next_add_doc, state=tk.DISABLED)
        self.next_button.grid(column=0, row=0, padx=5)

        cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.cancel_add_doc)
        cancel_button.grid(column=1, row=0, padx=5)

    def check_radios(self):
        if self.selected_radio.get() and self.selected_radio_2.get():
            self.next_button.configure(state=tk.NORMAL)
        else:
            self.next_button.configure(state=tk.DISABLED)

    def clear_frame(self, to_clear_frame):
        for widget in to_clear_frame.winfo_children():
            widget.destroy()

    def add_content_to_first(self):
        self.clear_frame(self.picked_content_frame)
        if self.selected_radio.get() == "card":
            ctk.CTkLabel(self.picked_content_frame, text="Do you want to do it for all students or for a specific one?",
                         wraplength=250, font=("Arial", 15)).pack(pady=20)

            self.selected_radio_2 = tk.StringVar()

            radio_all = ctk.CTkRadioButton(self.picked_content_frame, text="All Students",
                                           value="all", variable=self.selected_radio_2, command=self.check_radios)
            radio_specific = ctk.CTkRadioButton(self.picked_content_frame, text="Specific Student", value="specific",
                                                variable=self.selected_radio_2, command=self.check_radios)
            radio_all.pack(pady=5)
            radio_specific.pack(pady=5)

        if self.selected_radio.get() == "barcode":
            ctk.CTkLabel(self.picked_content_frame, text="Do you want to do it for all books or for a specific one?",
                         wraplength=250, font=("Arial", 15)).pack(pady=20)

            self.selected_radio_2 = tk.StringVar()

            radio_all = ctk.CTkRadioButton(self.picked_content_frame, text="All Books", value="all",
                                           variable=self.selected_radio_2, command=self.check_radios)
            radio_specific = ctk.CTkRadioButton(self.picked_content_frame, text="Specific Book", value="specific",
                                                variable=self.selected_radio_2, command=self.check_radios)
            radio_all.pack(pady=5)
            radio_specific.pack(pady=5)

    def cancel_add_doc(self):
        self.popup_add_doc.destroy()

    def next_add_doc(self):
        request_radio_type = self.selected_radio.get()
        request_radio_amount = self.selected_radio_2.get()
        self.first_frame.forget()
        self.second_frame.pack(fill='both', expand=True)

        if request_radio_type == "card":
            if request_radio_amount == "all":

                ctk.CTkLabel(self.second_frame, text="Create Student ID Cards for all students",
                             font=("Arial", 20)).pack(pady=20)

                students_amount = self.get_students_amount()
                text_for_label = f"You are creating ID Cards for {students_amount} students"
                ctk.CTkLabel(self.second_frame, text=text_for_label, font=("Arial", 17)).pack(pady=20)

                buttons_grid_frame = ctk.CTkFrame(self.second_frame)
                buttons_grid_frame.pack(pady=30)

                create_button = ctk.CTkButton(buttons_grid_frame, text="create", command=self.create_all_students_cards)
                create_button.grid(column=0, row=0, padx=5)

                cancel_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.cancel_add_doc)
                cancel_button.grid(column=1, row=0, padx=5)

            elif request_radio_amount == "specific":

                ctk.CTkLabel(self.second_frame, text="Student ID").pack()
                self.student_id_for_card_entry = ctk.CTkEntry(self.second_frame, width=250)
                self.student_id_for_card_entry.pack(pady=10)

                get_student_data_button = ctk.CTkButton(self.second_frame, text="Get Student info by Student ID",
                                                        width=150, command=self.get_student_data)
                get_student_data_button.pack(pady=10)

            else:
                messagebox.showerror("Error", "Something went wrong!")
                self.popup_add_doc.destroy()

        elif request_radio_type == "barcode":
            if request_radio_amount == "all":

                ctk.CTkLabel(self.second_frame, text="Create ISBN Barcode for all Books",
                             font=("Arial", 20)).pack(pady=20)

                book_amount = self.get_books_amount()
                text_for_label = f"You are creating ISBN Barcodes for {book_amount} books"
                ctk.CTkLabel(self.second_frame, text=text_for_label, font=("Arial", 17)).pack(pady=20)

                buttons_grid_frame = ctk.CTkFrame(self.second_frame)
                buttons_grid_frame.pack(pady=30)

                create_button = ctk.CTkButton(buttons_grid_frame, text="create", command=self.create_book_barcode_all)
                create_button.grid(column=0, row=0, padx=5)

                cancel_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.cancel_add_doc)
                cancel_button.grid(column=1, row=0, padx=5)

            elif request_radio_amount == "specific":

                ctk.CTkLabel(self.second_frame, text="Book ISBN").pack()
                self.book_isbn_for_barcode_entry = ctk.CTkEntry(self.second_frame, width=250)
                self.book_isbn_for_barcode_entry.pack()

                buttons_grid_frame = ctk.CTkFrame(self.second_frame)
                buttons_grid_frame.pack(pady=30)

                create_button = ctk.CTkButton(buttons_grid_frame, text="create", command=self.create_specific_barcode)
                create_button.grid(column=0, row=0, padx=5)

                cancel_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.cancel_add_doc)
                cancel_button.grid(column=1, row=0, padx=5)

            else:
                messagebox.showerror("Error", "Something went wrong!")
                self.popup_add_doc.destroy()

        else:
            messagebox.showerror("Error", "Something went wrong!")
            self.popup_add_doc.destroy()

    def get_students_amount(self):
        mess = f"student_all-amount"
        send_for_card_barcode_creation_queue.put(mess)
        student_amount_answer = get_for_card_barcode_creation_queue.get()
        return student_amount_answer

    def get_books_amount(self):
        mess = f"books_all-amount"
        send_for_card_barcode_creation_queue.put(mess)
        book_amount_answer = get_for_card_barcode_creation_queue.get()
        return book_amount_answer

    def get_student_data(self):
        student_id = self.student_id_for_card_entry.get()
        mess = f"student_specific-{student_id}"
        send_for_card_barcode_creation_queue.put(mess)
        student_data_answer = get_for_card_barcode_creation_queue.get()
        print(student_data_answer)

        student_data_frame = ctk.CTkFrame(self.second_frame)
        student_data_frame.pack(fill='x', expand=True, pady=20)

        ctk.CTkLabel(student_data_frame, text=student_data_answer[2], font=("Arial", 22)).pack(pady=5)

        content_text = f"Student ID: {student_data_answer[1]}"
        ctk.CTkLabel(student_data_frame, text=content_text, font=("Arial", 15)).pack(pady=5)

        content_text = f"Class: {student_data_answer[3]}"
        ctk.CTkLabel(student_data_frame, text=content_text, font=("Arial", 15)).pack(pady=5)

        content_text = f"Teacher: {student_data_answer[4]}"
        ctk.CTkLabel(student_data_frame, text=content_text, font=("Arial", 15)).pack(pady=5)

        buttons_grid_frame = ctk.CTkFrame(self.second_frame)
        buttons_grid_frame.pack(pady=30)

        create_button = ctk.CTkButton(buttons_grid_frame, text="create",
                                      command=lambda: self.process_create_student_specific(student_data_answer))
        create_button.grid(column=0, row=0, padx=5)

        cancel_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.cancel_add_doc)
        cancel_button.grid(column=1, row=0, padx=5)

    def create_all_students_cards(self):
        send_for_card_barcode_creation_queue.put("student_all-data")
        all_students_data = get_for_card_barcode_creation_queue.get()
        print(all_students_data)

        student_card_list = []

        for student in all_students_data:
            student_card = process_all_card_creation(student[2], student[3], student[4], student[1])

            student_card_list.append({
                "student_card": student_card,
                "id": student[1]
            })

        save_folder = filedialog.askdirectory(title="Wählen Sie einen Ordner zum Speichern der Karten")

        if save_folder:
            for card in student_card_list:
                save_path = os.path.join(save_folder, f"student_card_{card["id"]}.png")
                card["student_card"].save(save_path)
                print(f"Bild gespeichert unter {save_path}")

                self.clear_frame(self.popup_add_doc)
                ctk.CTkLabel(self.popup_add_doc, text="All student ID cards were created").pack()
                text = f"File saved in: {save_path}"
                ctk.CTkLabel(self.popup_add_doc, text=text).pack()
                ctk.CTkButton(self.popup_add_doc, text="Print Student Cards").pack()
                ctk.CTkButton(self.popup_add_doc, text="Close", command=self.cancel_add_doc).pack()
        else:
            print("Kein Ordner gewählt.")

    def process_create_student_specific(self, data):
        try:
            path = process_single_card_creation(data[2], data[3], data[4], data[1])
            self.clear_frame(self.popup_add_doc)
            ctk.CTkLabel(self.popup_add_doc, text="The student ID card was created").pack()
            text = f"File saved in: {path}"
            ctk.CTkLabel(self.popup_add_doc, text=text).pack()
            ctk.CTkButton(self.popup_add_doc, text="Print Student Card").pack()
            ctk.CTkButton(self.popup_add_doc, text="Close", command=self.cancel_add_doc).pack()

        except Exception as e:
            print(e)

    def create_book_barcode_all(self):
        send_for_card_barcode_creation_queue.put("books_all-data")
        print("test1--")
        all_books_data = get_for_card_barcode_creation_queue.get()
        print(all_books_data)

        books_barcode_list = []

        for book in all_books_data:
            barcode = create_barcode(book[1])

            books_barcode_list.append({
                "barcode": barcode,
                "isbn": book[1]
            })

        save_folder = filedialog.askdirectory(title="Wählen Sie einen Ordner zum Speichern der Karten")

        if save_folder:
            for b in books_barcode_list:
                save_path = os.path.join(save_folder, f"barcode_{b["isbn"]}.png")
                b["barcode"].save(save_path)
                print(f"Bild gespeichert unter {save_path}")

                self.clear_frame(self.popup_add_doc)
                ctk.CTkLabel(self.popup_add_doc, text="All book isbn Barcodes were created").pack()
                text = f"File saved in: {save_path}"
                ctk.CTkLabel(self.popup_add_doc, text=text).pack()
                ctk.CTkButton(self.popup_add_doc, text="Print Barcodes").pack()
                ctk.CTkButton(self.popup_add_doc, text="Close", command=self.cancel_add_doc).pack()
        else:
            print("Kein Ordner gewählt.")

    def create_specific_barcode(self):
        isbn = self.book_isbn_for_barcode_entry.get()
        book_barcode = create_barcode(isbn)

        save_folder = filedialog.askdirectory(title="Wählen Sie einen Ordner zum Speichern des Barcodes")

        if save_folder:
            save_path = os.path.join(save_folder, f"barcode_{isbn}.png")
            book_barcode.save(save_path)
            print(f"Bild gespeichert unter {save_path}")

            self.clear_frame(self.popup_add_doc)
            ctk.CTkLabel(self.popup_add_doc, text="Book isbn Barcodes was created").pack()
            text = f"File saved in: {save_path}"
            ctk.CTkLabel(self.popup_add_doc, text=text).pack()
            ctk.CTkButton(self.popup_add_doc, text="Print Barcode").pack()
            ctk.CTkButton(self.popup_add_doc, text="Close", command=self.cancel_add_doc).pack()

        else:
            print("Kein Ordner gewählt.")

    def red_loans_widget(self):
        tk.Label(self.red_loans_frame, text="Overdue Loans", font=("Arial", 25)).pack()

        data = self.process_red_loans()
        if data:
            table_frame = tk.Frame(self.red_loans_frame)
            table_frame.pack()

            columns = ("col1", "col2", "col3", "col4", "col5", "col6")
            red_loans_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
            column_settings = [
                ("col1", "ID", 25),
                ("col2", "Student", 100),
                ("col3", "Title", 140),
                ("col4", "Class", 35),
                ("col5", "Teacher", 80),
                ("col6", "Due date", 90),
            ]

            for col, text, width in column_settings:
                red_loans_tree.heading(col, text=text)
                red_loans_tree.column(col, width=width, anchor="center")
            for loan in data:
                red_loans_tree.insert("", "end", values=(loan[0], loan[1],
                                                         loan[2], loan[3], loan[4], loan[5]))

            red_loans_tree.pack(padx=10, pady=10)

        else:
            tk.Label(self.red_loans_frame, text="There are no overdue loans").pack()

    def process_red_loans(self):
        get_all_red_loans_queue.put("request-all-red-loans")
        print("test-ui-request")
        red_loans_data = get_all_red_loans_data_queue.get()
        return red_loans_data

    def create_notes_widget(self):
        self.notebook = ttk.Notebook(self.notes_frame, width=40, height=20)
        self.notebook.pack(padx=10, fill="both", expand=True)

        self.note_name_counter = 1
        self.tabs = []

        self.create_new_tab()

        menu_bar_grid_frame = tk.Frame(self.notes_frame)
        menu_bar_grid_frame.pack()

        create_tab_button = ctk.CTkButton(menu_bar_grid_frame, text="New Note", command=self.create_new_tab)
        create_tab_button.grid(column=0, row=0, padx=5)

        delete_tab_button = ctk.CTkButton(menu_bar_grid_frame, text="Delete Note", command=self.remove_current_tab)
        delete_tab_button.grid(column=1, row=0, padx=5)

    def create_new_tab(self):
        new_tab = tk.Frame(self.notebook)

        self.text_area = tk.Text(new_tab, wrap="word", font=("Arial", 12))
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)

        self.notebook.add(new_tab, text=f"Note {self.note_name_counter}")

        self.tabs.append(new_tab)

        self.note_name_counter += 1

    def remove_current_tab(self):
        current_tab_index = self.notebook.index("current")

        if current_tab_index != -1:
            current_tab = self.notebook.tabs()[current_tab_index]
            self.notebook.forget(current_tab)

    def create_catalog_widget(self):
        tk.Label(self.catalog_frame, text="Book Catalog", font=("Arial", 30)).grid(row=0, column=0, columnspan=8,
                                                                                   pady=20)
        column = 0
        catalog_book_data = self.get_catalog_data()
        for book in catalog_book_data:
            try:
                print(book[1])
                response = requests.get(book[1])
                img_data = response.content
                img = Image.open(BytesIO(img_data))
            except (requests.RequestException, IOError):
                print(f"Bildadresse für {book[1]} ist falsch!")
                img = Image.open("../assets/no_image_avl.png")

            img_resized = img.resize((125, 190))
            img_tk = ImageTk.PhotoImage(img_resized)

            label = tk.Label(self.catalog_frame, text=book[0], image=img_tk)
            label.image = img_tk
            label.grid(row=1, column=column, padx=5, pady=20)
            label.bind("<Button-1>", lambda event, b=book: self.show_book_details(b))
            column += 1

    def show_book_details(self, book):
        print(book, "--------")
        isbn = book[2]
        print(isbn, "--------")
        url = f"https://www.bookfinder.com/search/?isbn={isbn}&mode=isbn&st=sr&ac=qr"
        webbrowser.open(url)

    def get_catalog_data(self):
        get_catalog_data_request_queue.put("catalog-data-request")
        print("catalog-data-request")
        catalog_data = get_catalog_data_answer_queue.get()
        return catalog_data

    def create_add_loan_widget(self):
        self.popup_add_loan = ctk.CTkToplevel(self.home_frame)
        self.popup_add_loan.title("Popup")
        self.popup_add_loan.geometry("350x400+500+200")
        self.popup_add_loan.resizable(False, False)

        ctk.CTkLabel(self.popup_add_loan, text="Add new Loan", font=("Arial", 20)).pack(pady=20)

        book_id_entry_label = ctk.CTkLabel(self.popup_add_loan, text="Book ID")
        book_id_entry_label.pack()
        self.book_id_entry = ctk.CTkEntry(self.popup_add_loan, width=250)
        self.book_id_entry.pack()

        student_id_entry_label = ctk.CTkLabel(self.popup_add_loan, text="Student ID")
        student_id_entry_label.pack()
        self.student_id_entry = ctk.CTkEntry(self.popup_add_loan, width=250)
        self.student_id_entry.pack()

        return_date_entry_label = ctk.CTkLabel(self.popup_add_loan, text="Return Date")
        return_date_entry_label.pack(pady=(25, 0))

        grid_frame_return_date = ctk.CTkFrame(self.popup_add_loan)
        grid_frame_return_date.pack()

        self.return_date_entry = DateEntry(grid_frame_return_date,
                                           width=12, background="darkblue", foreground="white", borderwidth=2,
                                           date_pattern="yyyy-mm-dd")
        self.return_date_entry.grid(column=0, row=1, padx=10)

        suggest_return_date_button = ctk.CTkButton(grid_frame_return_date, text="Suggest",
                                                   command=self.suggest_return_date, width=50)
        suggest_return_date_button.grid(column=1, row=1, padx=10)

        button_grid_frame = ctk.CTkFrame(self.popup_add_loan)
        button_grid_frame.pack(pady=35)

        add_button = ctk.CTkButton(button_grid_frame, text="finish", command=self.process_add_loan)
        add_button.grid(column=0, row=0, padx=10)

        cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.cancel_process)
        cancel_button.grid(column=1, row=0, padx=10)

    def suggest_return_date(self):
        today = datetime.today()
        suggested_return_date = today + timedelta(days=14)
        self.return_date_entry.delete(0, tk.END)
        self.return_date_entry.insert(0, suggested_return_date.strftime("%Y-%m-%d"))

    def process_add_loan(self):
        loan_data = self.get_loan_data()

        loan_data_adding_queue.put(loan_data)

        answer = loan_adding_data_answer_queue.get()
        if answer == "success":
            messagebox.showinfo("Success", "Loan was added")
            self.popup_add_loan.destroy()
        elif answer == "declined":
            messagebox.showerror("Error", "Loan was declined!")
            self.popup_add_loan.destroy()
        else:
            messagebox.showerror("Error", "Something went wrong!")
            self.popup_add_loan.destroy()

    def cancel_process(self):
        self.popup_add_loan.destroy()

    def get_loan_data(self):
        book_id = self.book_id_entry.get() if self.book_id_entry.get() else ''
        student_id = self.student_id_entry.get() if self.student_id_entry.get() else ''
        return_date = self.return_date_entry.get() if self.return_date_entry.get() else ''

        loan_list = [book_id, student_id, return_date]

        return loan_list

    def create_return_book_widget(self):
        self.popup_return_book = ctk.CTkToplevel(self.home_frame)
        self.popup_return_book.title("Return Book")
        self.popup_return_book.geometry("350x400+500+200")
        self.popup_return_book.resizable(False, False)

        ctk.CTkLabel(self.popup_return_book, text="Return Book", font=("Arial", 20)).pack(pady=30)

        book_id_entry_label = ctk.CTkLabel(self.popup_return_book, text="Book ISBN")
        book_id_entry_label.pack()
        self.book_id_entry_return = ctk.CTkEntry(self.popup_return_book, width=250)
        self.book_id_entry_return.pack()

        student_id_entry_label = ctk.CTkLabel(self.popup_return_book, text="Student ID")
        student_id_entry_label.pack(pady=(20, 0))
        self.student_id_entry_return = ctk.CTkEntry(self.popup_return_book, width=250)
        self.student_id_entry_return.pack()

        button_grid_frame = ctk.CTkFrame(self.popup_return_book)
        button_grid_frame.pack(pady=45)

        add_button = ctk.CTkButton(button_grid_frame, text="finish", command=self.process_return_book)
        add_button.grid(column=0, row=0, padx=10)

        cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.popup_return_book.destroy)
        cancel_button.grid(column=1, row=0, padx=10)

    def process_return_book(self):
        book_id = self.book_id_entry_return.get()
        student_id = self.student_id_entry_return.get()
        return_data = [book_id, student_id]
        return_book_request_queue.put(return_data)
        answer = return_book_answer_queue.get()
        if answer == "success":
            messagebox.showinfo("Success", "Book successfully returned")
            self.popup_return_book.destroy()
        elif answer == "declined":
            messagebox.showerror("Declined", "Book returning was declined")
            self.popup_return_book.destroy()

        else:
            messagebox.showerror("Error", "Something went wrong")
            self.popup_return_book.destroy()


class BooksFrame:
    def __init__(self, parent):
        self.book_isbn_entry_for_delete = None
        self.delete_frame = None
        self.popup_delete_book = None
        self.add_delete_book_frame = None
        self.filter_choice = None
        self.search_entry = None
        self.treeview = None
        self.popup_add_book = None
        self.language_entry = None
        self.description_entry = None
        self.thumbnail_link_entry = None
        self.pages_entry = None
        self.date_entry = None
        self.main_frame = None
        self.genre_entry = None
        self.author_entry = None
        self.title_entry = None
        self.book_isbn_entry = None
        self.parent = parent  # content_frame
        self.books_frame = tk.Frame(self.parent)
        self.books_frame.pack(fill="both", expand=True)
        self.books_frame_widget()

    def books_frame_widget(self):
        # navigation bar
        nav_bar_frame = tk.Frame(self.books_frame, height=50)
        nav_bar_frame.pack(fill="x", side="top")

        nav_bar_frame.columnconfigure(0, weight=2)
        nav_bar_frame.columnconfigure(1, weight=3)
        nav_bar_frame.columnconfigure(2, weight=1)
        nav_bar_frame.columnconfigure(3, weight=1)

        self.filter_choice = ttk.Combobox(nav_bar_frame, values=["all", "available", "taken"], state="readonly")
        self.filter_choice.grid(column=0, row=1)
        self.filter_choice.set("all")
        self.filter_choice.bind("<<ComboboxSelected>>", self.apply_filter)

        search_entry_label = tk.Label(nav_bar_frame, text="Search Books")
        search_entry_label.grid(column=1, row=0)
        self.search_entry = ctk.CTkEntry(nav_bar_frame)
        self.search_entry.grid(column=1, row=1, sticky="nsew", padx=10)
        self.search_entry.focus_set()
        self.search_entry.bind("<KeyRelease>", self.filter_treeview)

        add_book_button = ctk.CTkButton(nav_bar_frame, text="add Book", command=self.add_book)
        add_book_button.grid(column=2, row=1, sticky="nsew", padx=10)

        delete_book_button = ctk.CTkButton(nav_bar_frame, text="delete Book", command=self.delete_book)
        delete_book_button.grid(column=3, row=1, sticky="nsew", padx=10)

        # treeview
        treeview_frame = tk.Frame(self.books_frame)
        treeview_frame.pack(pady=50, padx=50, fill="both", expand=True)

        columns = ("", "ISBN", "Title", "Author", "Genre", "Language", "Pages", "Availability")
        self.treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings")
        self.treeview.pack(side="left", expand=True, fill="both")

        for column in columns:
            self.treeview.heading(column, text=column)
            self.treeview.column(column, width=100)

        self.update_treeview()

        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def apply_filter(self, event=None):
        choice = self.filter_choice.get()
        print(choice)

        all_data = self.get_treeview_data()

        if choice == "all":
            filtered_data = all_data
        elif choice == "available":
            filtered_data = [row for row in all_data if row[7] == "available"]
        elif choice == "taken":
            filtered_data = [row for row in all_data if row[7] != "available"]
        else:
            filtered_data = []

        self.update_treeview(filtered_data)

    def filter_treeview(self, event=None):
        search_term = self.search_entry.get().lower().strip()

        if not search_term:
            self.update_treeview()
            return

        search_columns = [2, 3, 4]

        filtered_data = [
            row for row in self.get_treeview_data()
            if any(str(row[i]).lower().startswith(search_term) for i in search_columns)
        ]

        self.update_treeview(filtered_data)

    def get_treeview_data(self):
        treeview_data_exchange_queue.put("get-book-treeview-data")
        data_request_answer = treeview_data_request_answer_queue.get()
        return data_request_answer

    def update_treeview(self, data=None):
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if data is None:
            data = self.get_treeview_data()

        for row in data:
            self.treeview.insert("", "end", values=row)

    def delete_book(self):
        self.popup_delete_book = ctk.CTkToplevel(self.parent)
        self.popup_delete_book.title("Delete Book")
        self.popup_delete_book.geometry("350x450+500+200")
        self.popup_delete_book.resizable(False, False)

        self.delete_frame = ctk.CTkFrame(self.popup_delete_book)
        self.delete_frame.pack(fill='both', expand=True)
        self.pack_delete_frame()

    def pack_delete_frame(self):
        label = ctk.CTkLabel(self.delete_frame, text="Delete a book", font=("Arial", 22))
        label.pack(pady=(5, 10))

        book_isbn_label = ctk.CTkLabel(self.delete_frame, text="ISBN")
        book_isbn_label.pack()
        self.book_isbn_entry_for_delete = ctk.CTkEntry(self.delete_frame, width=250)
        self.book_isbn_entry_for_delete.pack()

        buttons_grid_frame = ctk.CTkFrame(self.delete_frame)
        buttons_grid_frame.pack(pady=20)

        delete_process_button = ctk.CTkButton(buttons_grid_frame, text="delete", command=self.process_delete_button)
        delete_process_button.grid(column=0, row=0, padx=5)

        cancel_book_data_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.popup_delete_book.destroy)
        cancel_book_data_button.grid(column=1, row=0, padx=5)

    def process_delete_button(self):
        to_delete_isbn = self.book_isbn_entry_for_delete.get()
        send_delete_book_queue.put(to_delete_isbn)

        ans = get_approve_delete_book_queue.get()
        if ans is True:
            messagebox.showinfo("Success", "Book successfully deleted")
            self.popup_delete_book.destroy()
        else:
            messagebox.showerror("Error", "Something went wrong, try again later!")
            self.popup_delete_book.destroy()

    def add_book(self):
        self.popup_add_book = ctk.CTkToplevel(self.parent)
        self.popup_add_book.title("Add Book")
        self.popup_add_book.geometry("350x450+500+200")
        self.popup_add_book.resizable(False, False)

        self.main_frame = ctk.CTkFrame(self.popup_add_book)
        self.main_frame.pack(fill='both', expand=True)
        self.pack_main_frame()

    def pack_main_frame(self):
        label = ctk.CTkLabel(self.main_frame, text="Add a book", font=("Arial", 22))
        label.pack(pady=(5, 10))

        book_isbn_label = ctk.CTkLabel(self.main_frame, text="ISBN")
        book_isbn_label.pack()
        self.book_isbn_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.book_isbn_entry.pack()

        auto_fill_button = ctk.CTkButton(self.main_frame, text="Auto-fill by ISBN", command=self.auto_fill_process)
        auto_fill_button.pack(pady=(7, 12))

        book_title_label = ctk.CTkLabel(self.main_frame, text="Title")
        book_title_label.pack(pady=(10, 0))
        self.title_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.title_entry.pack()

        book_author_label = ctk.CTkLabel(self.main_frame, text="Author")
        book_author_label.pack()
        self.author_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.author_entry.pack()

        book_genre_label = ctk.CTkLabel(self.main_frame, text="Genre")
        book_genre_label.pack()
        self.genre_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.genre_entry.pack()

        book_language_label = ctk.CTkLabel(self.main_frame, text="Language")
        book_language_label.pack()
        self.language_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.language_entry.pack()

        buttons_grid_frame = ctk.CTkFrame(self.main_frame)
        buttons_grid_frame.pack(pady=20)

        customize_book_data_button = ctk.CTkButton(buttons_grid_frame, text="more", command=self.customize_button)
        customize_book_data_button.grid(column=0, row=0, padx=5)

        save_book_data_button = ctk.CTkButton(buttons_grid_frame, text="save", command=self.process_save_button)
        save_book_data_button.grid(column=1, row=0, padx=5)

    def customize_button(self):
        try:
            temp_data_list = self.save_temp_entry_data()
            print(temp_data_list)
        except Exception:
            temp_data_list = ["", "", "", "", "", "", "", "", ""]
        self.pack_forget_all_children(self.main_frame)

        book_date_label = ctk.CTkLabel(self.main_frame, text="Publishing Date")
        book_date_label.pack()
        self.date_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.date_entry.pack()

        book_pages_label = ctk.CTkLabel(self.main_frame, text="Pages")
        book_pages_label.pack()
        self.pages_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.pages_entry.pack()

        book_thumbnail_link_label = ctk.CTkLabel(self.main_frame, text="Thumbnail Link")
        book_thumbnail_link_label.pack()
        self.thumbnail_link_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.thumbnail_link_entry.pack()

        book_description_label = ctk.CTkLabel(self.main_frame, text="Description")
        book_description_label.pack()
        self.description_entry = ctk.CTkTextbox(self.main_frame, width=250, height=200)
        self.description_entry.pack()

        buttons_grid_frame = ctk.CTkFrame(self.main_frame)
        buttons_grid_frame.pack(pady=10)

        back_to_main_button = ctk.CTkButton(buttons_grid_frame, text="back",
                                            command=self.back_to_main)
        back_to_main_button.grid(column=0, row=0, padx=5)

        save_custom_data = ctk.CTkButton(buttons_grid_frame, text="save", command=self.process_save_button)
        save_custom_data.grid(column=1, row=0, padx=5)
        try:
            self.insert_all_data(temp_data_list)
        except Exception as e:
            print(e)

    def insert_all_data(self, temp_data_list):
        if self.book_isbn_entry:
            self.book_isbn_entry.insert(0, temp_data_list[0] if temp_data_list[0] else "")

        if self.title_entry:
            self.title_entry.insert(0, temp_data_list[1] if temp_data_list[1] else "")

        if self.author_entry:
            self.author_entry.insert(0, temp_data_list[2] if temp_data_list[2] else "")

        if self.genre_entry:
            self.genre_entry.insert(0, temp_data_list[3] if temp_data_list[3] else "")

        if self.language_entry:
            self.language_entry.insert(0, temp_data_list[4] if temp_data_list[4] else "")

        if self.date_entry:
            self.date_entry.insert(0, temp_data_list[5] if temp_data_list[5] else "")

        if self.pages_entry:
            self.pages_entry.insert(0, temp_data_list[6] if temp_data_list[6] else "")

        if self.thumbnail_link_entry:
            self.thumbnail_link_entry.insert(0, temp_data_list[7] if temp_data_list[7] else "")

        if self.description_entry:
            self.description_entry.insert("1.0", temp_data_list[8] if temp_data_list[8] else "")

    def save_temp_entry_data(self):
        if self.book_isbn_entry:
            book_isbn_entry_data = self.book_isbn_entry.get() if self.book_isbn_entry.get() else ''
        else:
            book_isbn_entry_data = ""

        if self.title_entry:
            title_entry_data = self.title_entry.get() if self.title_entry.get() else ''
        else:
            title_entry_data = ""

        if self.author_entry:
            author_entry_data = self.author_entry.get() if self.author_entry.get() else ''
        else:
            author_entry_data = ""

        if self.genre_entry:
            genre_entry_data = self.genre_entry.get() if self.genre_entry.get() else ''
        else:
            genre_entry_data = ""

        if self.language_entry:
            language_entry_data = self.language_entry.get() if self.language_entry.get() else ''
        else:
            language_entry_data = ""

        if self.date_entry:
            date_entry_data = self.date_entry.get() if self.date_entry.get() else ''
        else:
            date_entry_data = ""

        if self.pages_entry:
            pages_entry_data = self.pages_entry.get() if self.pages_entry.get() else ''
        else:
            pages_entry_data = ""

        if self.thumbnail_link_entry:
            thumbnail_link_entry_data = self.thumbnail_link_entry.get() if self.thumbnail_link_entry.get() else ''
        else:
            thumbnail_link_entry_data = ""

        if self.description_entry:
            description_entry_data = self.description_entry.get("1.0", "end-1c") \
                if self.description_entry.get("1.0", "end-1c") else ''
        else:
            description_entry_data = ""

        temp_entry_data = []
        temp_entry_data.extend([
            book_isbn_entry_data,
            title_entry_data,
            author_entry_data,
            genre_entry_data,
            language_entry_data,
            date_entry_data,
            pages_entry_data,
            thumbnail_link_entry_data,
            description_entry_data
        ])
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
        return temp_entry_data

    def process_save_button(self):
        book_data = self.save_book_data()

        self.destroy_all_children()

        show_content_frame = ctk.CTkFrame(self.main_frame)
        show_content_frame.pack(fill='both', expand=True)

        ctk.CTkLabel(show_content_frame, text=book_data[0], font=("Arial", 30)).pack(pady=20)

        sub_title_grid_frame = ctk.CTkFrame(show_content_frame)
        sub_title_grid_frame.pack()

        ctk.CTkLabel(sub_title_grid_frame, text=book_data[1], font=("Arial", 20)).grid(column=0, row=0, padx=10)
        ctk.CTkLabel(sub_title_grid_frame, text=book_data[2], font=("Arial", 20)).grid(column=1, row=0, padx=10)

        content_headers = ["ISBN: ", "Publishing date: ", "Language: ", "Pages: "]
        for i, content in enumerate(book_data[3:7]):
            content_text = f"{content_headers[i]} {content}"
            ctk.CTkLabel(show_content_frame, text=content_text).pack()

        photo_descrp_grid_frame = ctk.CTkFrame(show_content_frame)
        photo_descrp_grid_frame.pack(fill='x', expand=True)

        try:
            response = requests.get(book_data[7])
            img_data = response.content

            img = Image.open(BytesIO(img_data))
        except (requests.RequestException, IOError):
            print("bildadresse falsch!")
            img = Image.open("../assets/no_image_avl.png")

        img_resized = img.resize((100, 160))

        img_tk = ImageTk.PhotoImage(img_resized)

        label = tk.Label(photo_descrp_grid_frame, image=img_tk, text="")
        label.image = img_tk
        label.grid(column=0, row=0, padx=15)

        ctk.CTkLabel(photo_descrp_grid_frame, text=book_data[8], wraplength=200).grid(column=1, row=0, padx=15)

        button_grid_frame = ctk.CTkFrame(show_content_frame)
        button_grid_frame.pack(pady=10)

        finish_button = ctk.CTkButton(button_grid_frame, text="finish", command=lambda: self.send_new_book(book_data))
        finish_button.grid(column=0, row=0, padx=5)

        cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.popup_add_book.destroy)
        cancel_button.grid(column=1, row=0, padx=5)

    def send_new_book(self, book_data):
        book_adding_data_exchange_queue.put(book_data)

        answer = book_adding_data_answer_queue.get()
        if answer == "success":
            self.success_adding_book()
        elif answer == "declined":
            self.error_adding_book()
        else:
            print("error")
            self.error_adding_book()

    def success_adding_book(self):
        messagebox.showinfo("Success", "Book was added")
        self.popup_add_book.destroy()
        self.update_treeview()

    def error_adding_book(self):
        messagebox.showerror("Error", "Something went wrong!")
        self.popup_add_book.destroy()

    def save_book_data(self):
        book_isbn_entry_data = self.book_isbn_entry.get() if self.book_isbn_entry.get() else 'No ISBN'
        title_entry_data = self.title_entry.get() if self.title_entry.get() else 'No Title'
        author_entry_data = self.author_entry.get() if self.author_entry.get() else 'No Author'
        genre_entry_data = self.genre_entry.get() if self.genre_entry.get() else 'No Genre'
        date_entry_data = self.date_entry.get() \
            if self.date_entry and self.date_entry.get() else 'No Publishing Date'
        language_entry_data = self.language_entry.get() if self.language_entry.get() else 'No Language'
        pages_entry_data = self.pages_entry.get() \
            if self.pages_entry and self.pages_entry.get() else 'No Pages'
        thumbnail_link_entry_data = self.thumbnail_link_entry.get() \
            if self.thumbnail_link_entry and self.thumbnail_link_entry.get() else 'No Thumbnail'
        description_text_data = self.description_entry.get("1.0", "end-1c").strip() \
            if self.description_entry and self.description_entry.get("1.0", "end-1c").strip() else 'No Description'

        book_data = [title_entry_data, author_entry_data, genre_entry_data, book_isbn_entry_data, date_entry_data,
                     language_entry_data, pages_entry_data, thumbnail_link_entry_data, description_text_data]

        return book_data

    def back_to_main(self):
        temp_data_list = self.save_temp_entry_data()
        print(temp_data_list)

        self.pack_forget_all_children(self.main_frame)
        self.pack_main_frame()
        self.insert_all_data(temp_data_list)

    def pack_forget_all_children(self, parent):
        for widget in parent.winfo_children():
            widget.pack_forget()

    def destroy_all_children(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def auto_fill_process(self):
        target_book_isbn = self.book_isbn_entry.get() if self.book_isbn_entry.get() else None
        if target_book_isbn:
            book_data = self.auto_fill_book_scraper(target_book_isbn)
            if book_data:
                self.destroy_all_children()

                show_content_frame = ctk.CTkFrame(self.main_frame)
                show_content_frame.pack(fill='both', expand=True)

                buttons_grid_frame = ctk.CTkFrame(self.main_frame)
                buttons_grid_frame.pack(pady=10)

                ctk.CTkLabel(show_content_frame, text=book_data[0], font=("Arial", 30)).pack(pady=20)

                sub_title_grid_frame = ctk.CTkFrame(show_content_frame)
                sub_title_grid_frame.pack()

                ctk.CTkLabel(sub_title_grid_frame, text=book_data[1], font=("Arial", 20)).grid(column=0, row=0)
                ctk.CTkLabel(sub_title_grid_frame, text=book_data[2], font=("Arial", 20)).grid(column=1, row=0)

                ctk.CTkLabel(show_content_frame, text=target_book_isbn).pack()

                content_headers = ["Language: ", "Publishing date: ", "Pages: "]
                for i, content in enumerate(book_data[3:6]):
                    content_text = f"{content_headers[i]} {content}"
                    ctk.CTkLabel(show_content_frame, text=content_text).pack()

                photo_descrp_grid_frame = ctk.CTkFrame(show_content_frame)
                photo_descrp_grid_frame.pack(fill='x', expand=True)

                try:
                    response = requests.get(book_data[6])
                    img_data = response.content

                    img = Image.open(BytesIO(img_data))

                except (requests.RequestException, IOError):
                    print("bildadresse falsch!")
                    img = Image.open("../assets/no_image_avl.png")

                img_resized = img.resize((100, 160))

                img_tk = ImageTk.PhotoImage(img_resized)

                label = tk.Label(photo_descrp_grid_frame, image=img_tk)
                label.image = img_tk
                label.grid(column=0, row=0, padx=15)

                ctk.CTkLabel(photo_descrp_grid_frame, text=book_data[7], wraplength=200).grid(column=1, row=0, padx=15)

                new_book_data_list = [book_data[0], book_data[1], book_data[2], target_book_isbn, book_data[4],
                                      book_data[3], book_data[5], book_data[6], book_data[7]]

                finish_button = ctk.CTkButton(buttons_grid_frame, text="finish",
                                              command=lambda: self.send_new_book(new_book_data_list))
                finish_button.grid(column=0, row=0, padx=5)

                cancel_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.popup_add_book.destroy)
                cancel_button.grid(column=1, row=0, padx=5)

        else:
            messagebox.showinfo("Error", "NO ISBN found")

    def auto_fill_book_scraper(self, isbn):
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                book_info = data["items"][0]["volumeInfo"]
                title = book_info.get("title", "No title")
                authors = ", ".join(book_info.get("authors", []))
                published_date = book_info.get("publishedDate", "No Author")
                genre = ", ".join(book_info.get("categories", ["No genre"]))
                language = book_info.get("language", "No Language")
                thumbnail_link = book_info.get("imageLinks", {}).get("thumbnail", "No Thumbnail")
                page_count = book_info.get("pageCount", 0)
                if page_count == 0:
                    page_count = "No pages"
                description = book_info.get("description", "No description")

                book_data_list = [title, authors, genre, language, published_date,
                                  page_count, thumbnail_link, description]
                return book_data_list
            else:
                messagebox.showerror("Error", "Didn't find data for this book")
        else:
            messagebox.showerror("Error", "Something went wrong! Please type in the data manually!")


class StudentsFrame:
    def __init__(self, parent):
        self.student_id_entry_to_delete = None
        self.delete_frame = None
        self.popup_delete_student = None
        self.filter_choice = None
        self.email_entry = None
        self.teacher_entry = None
        self.class_entry = None
        self.name_entry = None
        self.student_id_entry = None
        self.search_entry = None
        self.treeview = None
        self.popup_add_student = None
        self.main_frame = None
        self.parent = parent  # content_frame
        self.students_frame = tk.Frame(self.parent)
        self.students_frame.pack(fill="both", expand=True)
        self.students_frame_widget()

    def students_frame_widget(self):
        # navigation bar
        nav_bar_frame = tk.Frame(self.students_frame, height=50)
        nav_bar_frame.pack(fill="x", side="top")

        nav_bar_frame.columnconfigure(0, weight=2)
        nav_bar_frame.columnconfigure(1, weight=3)
        nav_bar_frame.columnconfigure(2, weight=1)
        nav_bar_frame.columnconfigure(3, weight=1)

        self.filter_choice = ttk.Combobox(nav_bar_frame, values=["all", "🟢", "🟡", "🟠", "🔴"], state="readonly")
        self.filter_choice.grid(column=0, row=1)
        self.filter_choice.set("all")
        self.filter_choice.bind("<<ComboboxSelected>>", self.apply_filter)

        search_entry_label = tk.Label(nav_bar_frame, text="Search for students")
        search_entry_label.grid(column=1, row=0)
        self.search_entry = ctk.CTkEntry(nav_bar_frame)
        self.search_entry.grid(column=1, row=1, sticky="nsew", padx=10)
        self.search_entry.focus_set()
        self.search_entry.bind("<KeyRelease>", self.filter_treeview)

        add_student_button = ctk.CTkButton(nav_bar_frame, text="add Student", command=self.add_student)
        add_student_button.grid(column=2, row=1, sticky="nsew", padx=10)

        delete_student_button = ctk.CTkButton(nav_bar_frame, text="delete Student", command=self.delete_student)
        delete_student_button.grid(column=3, row=1, sticky="nsew", padx=10)

        # treeview
        treeview_frame = tk.Frame(self.students_frame)
        treeview_frame.pack(pady=50, padx=50, fill="both", expand=True)

        columns = ("", "ID", "Name", "Class", "Teacher", "Email", "Status")
        self.treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings")
        self.treeview.pack(side="left", expand=True, fill="both")

        for column in columns:
            self.treeview.heading(column, text=column)
            self.treeview.column(column, width=100)

        self.update_treeview()

        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def apply_filter(self, event=None):
        choice = self.filter_choice.get()
        print(choice)

        all_data = self.get_treeview_data()

        if choice == "all":
            filtered_data = all_data
        elif choice == "🟢":
            filtered_data = [row for row in all_data if row[6] == "🟢"]
        elif choice == "🟡":
            filtered_data = [row for row in all_data if row[6] == "🟡"]
        elif choice == "🟠":
            filtered_data = [row for row in all_data if row[6] == "🟠"]
        elif choice == "🔴":
            filtered_data = [row for row in all_data if row[6] == "🔴"]
        else:
            filtered_data = []

        self.update_treeview(filtered_data)

    def update_treeview(self, data=None):
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if data is None:
            data = self.get_treeview_data()

        for row in data:
            self.treeview.insert("", "end", values=row)

    def filter_treeview(self, event=None):
        search_term = self.search_entry.get().lower().strip()

        if not search_term:
            self.update_treeview()
            return

        search_columns = [1, 2, 3, 4]

        filtered_data = [
            row for row in self.get_treeview_data()
            if any(str(row[i]).lower().startswith(search_term) for i in search_columns)
        ]

        self.update_treeview(filtered_data)

    def get_treeview_data(self):
        treeview_data_exchange_queue.put("get-student-treeview-data")
        data_request_answer = treeview_data_request_answer_queue.get()
        return data_request_answer

    def delete_student(self):
        self.popup_delete_student = ctk.CTkToplevel(self.parent)
        self.popup_delete_student.title("Delete Student")
        self.popup_delete_student.geometry("350x420+500+200")
        self.popup_delete_student.resizable(False, False)

        self.delete_frame = ctk.CTkFrame(self.popup_delete_student)
        self.delete_frame.pack(fill='both', expand=True)
        self.pack_delete_frame()

    def pack_delete_frame(self):
        label = ctk.CTkLabel(self.delete_frame, text="Delete a student", font=("Arial", 22))
        label.pack()

        student_id_label = ctk.CTkLabel(self.delete_frame, text="Student ID")
        student_id_label.pack()
        self.student_id_entry_to_delete = ctk.CTkEntry(self.delete_frame, width=250)
        self.student_id_entry_to_delete.pack()

        buttons_grid_frame = ctk.CTkFrame(self.delete_frame)
        buttons_grid_frame.pack(pady=20)

        delete_student_button = ctk.CTkButton(buttons_grid_frame, text="delete", command=self.process_delete_button)
        delete_student_button.grid(column=0, row=0, padx=5)

        cancel_student_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.process_cancel_button)
        cancel_student_button.grid(column=1, row=0, padx=5)

    def process_delete_button(self):
        student_id_to_delete = self.student_id_entry_to_delete.get()
        if student_id_to_delete:
            send_delete_student_queue.put(student_id_to_delete)
            ans = get_approve_delete_student_queue.get()
            if ans is True:
                messagebox.showinfo("Success", "Student successfully deleted")
                self.popup_delete_student.destroy()
            else:
                messagebox.showinfo("Error", "Delete Student declined")
                self.popup_delete_student.destroy()
        else:
            messagebox.showerror("Error", "Type in a valid student id")

    def add_student(self):
        self.popup_add_student = ctk.CTkToplevel(self.parent)
        self.popup_add_student.title("Add Student")
        self.popup_add_student.geometry("350x420+500+200")
        self.popup_add_student.resizable(False, False)

        self.main_frame = ctk.CTkFrame(self.popup_add_student)
        self.main_frame.pack(fill='both', expand=True)
        self.pack_main_frame()

    def pack_main_frame(self):
        label = ctk.CTkLabel(self.main_frame, text="Add a student", font=("Arial", 22))
        label.pack()

        student_id_label = ctk.CTkLabel(self.main_frame, text="Student ID")
        student_id_label.pack()
        self.student_id_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.student_id_entry.pack()

        student_name_label = ctk.CTkLabel(self.main_frame, text="Full Name")
        student_name_label.pack(pady=(30, 0))
        self.name_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.name_entry.pack()

        student_class_label = ctk.CTkLabel(self.main_frame, text="Class")
        student_class_label.pack()
        self.class_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.class_entry.pack()

        student_teacher_label = ctk.CTkLabel(self.main_frame, text="Teacher")
        student_teacher_label.pack()
        self.teacher_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.teacher_entry.pack()

        student_email_label = ctk.CTkLabel(self.main_frame, text="Email")
        student_email_label.pack()
        self.email_entry = ctk.CTkEntry(self.main_frame, width=250)
        self.email_entry.pack()

        buttons_grid_frame = ctk.CTkFrame(self.main_frame)
        buttons_grid_frame.pack(pady=20)

        save_student_data_button = ctk.CTkButton(buttons_grid_frame, text="save", command=self.process_save_button)
        save_student_data_button.grid(column=0, row=0, padx=5)

        cancel_student_button = ctk.CTkButton(buttons_grid_frame, text="cancel", command=self.process_cancel_button)
        cancel_student_button.grid(column=1, row=0, padx=5)

    def process_cancel_button(self):
        self.popup_add_student.destroy()

    def process_save_button(self):
        student_data = self.save_student_data()

        self.destroy_all_children()

        show_content_frame = ctk.CTkFrame(self.main_frame)
        show_content_frame.pack(fill='both', expand=True)

        ctk.CTkLabel(show_content_frame, text=student_data[1], font=("Arial", 30)).pack(pady=20)

        ctk.CTkLabel(show_content_frame, text=student_data[0], font=("Arial", 20)).pack(pady=20)

        content_headers = ["Class: ", "Teacher: ", "Email: "]
        for i, content in enumerate(student_data[2:5]):
            content_text = f"{content_headers[i]} {content}"
            ctk.CTkLabel(show_content_frame, text=content_text).pack()

        button_grid_frame = ctk.CTkFrame(show_content_frame)
        button_grid_frame.pack(pady=35)

        finish_button = ctk.CTkButton(button_grid_frame, text="finish",
                                      command=lambda: self.send_new_student(student_data))
        finish_button.grid(column=0, row=0, padx=5)

        cancel_button = ctk.CTkButton(button_grid_frame, text="cancel", command=self.popup_add_student.destroy)
        cancel_button.grid(column=1, row=0, padx=5)

    def send_new_student(self, student_data):
        student_adding_data_exchange_queue.put(student_data)

        answer = student_adding_data_answer_queue.get()
        if answer == "success":
            self.success_adding_student()
        elif answer == "declined":
            self.error_adding_student()
        else:
            print("error")
            self.error_adding_student()

    def success_adding_student(self):
        messagebox.showinfo("Success", "student was added")
        self.popup_add_student.destroy()
        self.update_treeview()

    def error_adding_student(self):
        messagebox.showerror("Error", "Something went wrong!")
        self.popup_add_student.destroy()

    def save_student_data(self):
        student_id_entry_data = self.student_id_entry.get() if self.student_id_entry.get() else 'No ID'
        name_entry_data = self.name_entry.get() if self.name_entry.get() else 'No Name'
        class_entry_data = self.class_entry.get() if self.class_entry.get() else 'No Class'
        teacher_entry_data = self.teacher_entry.get() if self.teacher_entry.get() else 'No teacher'
        email_entry_data = self.email_entry.get() if self.email_entry.get() else 'No Email'

        student_data = [student_id_entry_data, name_entry_data, class_entry_data, teacher_entry_data, email_entry_data]

        return student_data

    def destroy_all_children(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


class LoansFrame:
    def __init__(self, parent):
        self.filter_choice = None
        self.treeview = None
        self.search_entry = None
        self.main_frame = None
        self.parent = parent  # content_frame
        self.loans_frame = tk.Frame(self.parent)
        self.loans_frame.pack(fill="both", expand=True)
        self.loans_frame_widget()

    def loans_frame_widget(self):
        # navigation bar
        nav_bar_frame = tk.Frame(self.loans_frame, height=50)
        nav_bar_frame.pack(fill="x", side="top")

        nav_bar_frame.columnconfigure(0, weight=1)
        nav_bar_frame.columnconfigure(1, weight=2)
        nav_bar_frame.columnconfigure(2, weight=1)

        self.filter_choice = ttk.Combobox(nav_bar_frame, values=["all", "🟢", "🟡", "🟠", "🔴"],
                                          state="readonly")
        self.filter_choice.grid(column=0, row=1)
        self.filter_choice.set("all")
        self.filter_choice.bind("<<ComboboxSelected>>", self.apply_filter)

        search_entry_label = tk.Label(nav_bar_frame, text="Search for loans")
        search_entry_label.grid(column=1, row=0)
        self.search_entry = ctk.CTkEntry(nav_bar_frame)
        self.search_entry.grid(column=1, row=1, sticky="nsew", padx=10)
        self.search_entry.focus_set()
        self.search_entry.bind("<KeyRelease>", self.filter_treeview)

        # treeview
        treeview_frame = tk.Frame(self.loans_frame)
        treeview_frame.pack(pady=50, padx=50, fill="both", expand=True)

        columns = ("", "Student Name", "Book Title", "Loan Date", "Return Date", "Status")
        self.treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings")
        self.treeview.pack(side="left", expand=True, fill="both")

        for column in columns:
            self.treeview.heading(column, text=column)
            self.treeview.column(column, width=100)

        self.update_treeview()

        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def apply_filter(self, event=None):
        choice = self.filter_choice.get()
        print(choice)

        all_data = self.get_treeview_data()

        if choice == "all":
            filtered_data = all_data
        elif choice == "🟢":
            filtered_data = [row for row in all_data if row[5] == "🟢"]
        elif choice == "🟡":
            filtered_data = [row for row in all_data if row[5] == "🟡"]
        elif choice == "🟠":
            filtered_data = [row for row in all_data if row[5] == "🟠"]
        elif choice == "🔴":
            filtered_data = [row for row in all_data if row[5] == "🔴"]
        else:
            filtered_data = []

        self.update_treeview(filtered_data)

    def update_treeview(self, data=None):
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if data is None:
            data = self.get_treeview_data()

        for row in data:
            self.treeview.insert("", "end", values=row)

    def filter_treeview(self, event=None):
        search_term = self.search_entry.get().lower().strip()

        if not search_term:
            self.update_treeview()
            return

        search_columns = [1, 2, 3, 4]

        filtered_data = [
            row for row in self.get_treeview_data()
            if any(str(row[i]).lower().startswith(search_term) for i in search_columns)
        ]

        self.update_treeview(filtered_data)

    def get_treeview_data(self):
        treeview_data_exchange_queue.put("get-loan-treeview-data")
        data_request_answer = treeview_data_request_answer_queue.get()
        print(data_request_answer)
        return data_request_answer


def error_main_interface():
    root = tk.Tk()
    root.geometry("200x70")
    root.title("Libra-Lens")

    tk.Label(root, text="An error occurred").pack()

    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=10)

    root.mainloop()
