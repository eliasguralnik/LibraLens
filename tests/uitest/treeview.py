import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Dynamische Tabelle mit Treeview")

# Treeview-Widget erstellen
columns = ("ID", "Name", "Alter")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.pack(expand=True, fill="both")

# Spaltenüberschriften setzen
for col in columns:
    tree.heading(col, text=col)

# Beispiel-Daten hinzufügen
data = [
    ("1", "xxx", "19"),
    ("2", "xxx", "17"),
    ("3", "xxx", "14"),

]
for row in data:
    tree.insert("", "end", values=row)

# Scrollbar hinzufügen
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

root.mainloop()
