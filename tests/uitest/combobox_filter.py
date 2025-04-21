import tkinter as tk
from tkinter import ttk

class LibraryApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data  # Originaldaten

        # Combobox für die Filterwahl
        self.filter_choice = ttk.Combobox(root, values=["all", "available", "taken"], state="readonly")
        self.filter_choice.pack(pady=5)
        self.filter_choice.set("all")
        self.filter_choice.bind("<<ComboboxSelected>>", self.apply_filter)

        # Treeview für die Datenanzeige
        self.tree = ttk.Treeview(root, columns=("ID", "Title", "Status"), show="headings")
        self.tree.pack(pady=10, expand=True, fill="both")

        for col in ("ID", "Title", "Status"):
            self.tree.heading(col, text=col)

        self.load_data(self.data)  # Start: Alle Daten anzeigen

    def load_data(self, data):
        """Lädt die Daten in das Treeview-Widget."""
        self.tree.delete(*self.tree.get_children())  # Vorherige Einträge löschen
        for row in data:
            self.tree.insert("", "end", values=row)

    def apply_filter(self, event=None):
        selected_filter = self.filter_choice.get()

        if selected_filter == "all":
            self.load_data(self.data)
        elif selected_filter == "available":
            filtered_data = [row for row in self.data if row[2] == "available"]
            self.load_data(filtered_data)
        elif selected_filter == "taken":
            filtered_data = [row for row in self.data if row[2] != "available"]
            self.load_data(filtered_data)


# Beispiel-Daten
sample_data = [
    (1, "Book A", "available"),
    (2, "Book B", "taken"),
    (3, "Book C", "available"),
    (4, "Book D", "30"),
]

root = tk.Tk()
app = LibraryApp(root, sample_data)
root.mainloop()
