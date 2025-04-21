import tkinter as tk
from tkinter import ttk
from tests.imap_email_show import *
import re


def on_tree_click(event):
    selected_item = tree.identify_row(event.y)

    if selected_item:
        values = tree.item(selected_item, "values")
        value_id, value_title, value_sender, value_content = values

        match = re.search(r'<(.+?)>', value_sender)
        if match:
            sender = match.group(1)
        else:
            sender = value_sender

        popup = tk.Toplevel(root)
        tk.Label(popup, text=value_title).pack()
        tk.Label(popup, text=sender).pack()
        tk.Label(popup, text=value_content).pack()
        tk.Label(popup, text=value_id).pack()


root = tk.Tk()

main_email_frame = tk.Frame(root)
main_email_frame.pack()

data = main_process()

columns = ("col1", "col2", "col3", "col4")
tree = ttk.Treeview(main_email_frame, columns=columns, show="headings")
column_settings = [
    ("col1", "ID", 35),
    ("col2", "Sender", 150),
    ("col3", "Title", 180),
    ("col4", "Content", 200)
]
counter = 0
for col, text, width in column_settings:
    tree.heading(col, text=text)
    tree.column(col, width=width, anchor="center")

if data:
    for email in data:
        content = email["content"]
        short_content = content[:30] + "..." if len(content) > 30 else content

        tree.insert("", "end", values=(counter, email["from"], email["subject"], short_content))

        counter += 1

tree.pack(padx=10, pady=10, fill="x", expand=True)
tree.bind("<ButtonRelease-1>", on_tree_click)

root.mainloop()
