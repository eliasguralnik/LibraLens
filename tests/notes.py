import tkinter as tk
from tkinter import filedialog, messagebox

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Notizblock")
        self.root.geometry("600x500")

        # Textfeld für die Notizen
        self.text_area = tk.Text(self.root, wrap="word", font=("Arial", 12))
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)

        # Menüleiste
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Datei-Menü
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Speichern", command=self.save_note)
        file_menu.add_command(label="Neue Notiz", command=self.new_note)
        file_menu.add_command(label="Vorherige Notiz", command=self.open_last_note)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        self.menu_bar.add_cascade(label="Datei", menu=file_menu)

        # Buttons unter dem Textbereich
        self.save_button = tk.Button(self.root, text="Speichern", command=self.save_note, width=20)
        self.save_button.pack(side="left", padx=5, pady=5)

        self.new_button = tk.Button(self.root, text="Neue Notiz", command=self.new_note, width=20)
        self.new_button.pack(side="left", padx=5, pady=5)

        self.previous_button = tk.Button(self.root, text="Vorherige Notiz", command=self.open_last_note, width=20)
        self.previous_button.pack(side="left", padx=5, pady=5)

        # Datei-Pfad für Speichern und Laden
        self.current_file = None
        self.last_file = None  # Speicherort der letzten geöffneten Datei

    def new_note(self):
        """Erstellt eine neue leere Notiz."""
        self.text_area.delete("1.0", tk.END)
        self.current_file = None  # Setzt den aktuellen Dateipfad auf None

    def save_note(self):
        """Speichert die aktuelle Notiz als Datei."""
        if self.current_file is None:
            # Wenn keine Datei geladen wurde, nach dem Pfad fragen
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Textdateien", "*.txt")])
            if file_path:
                self.current_file = file_path
                self.last_file = file_path  # Speichert die Datei als letzte Notiz
        else:
            file_path = self.current_file

        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get("1.0", tk.END))
            messagebox.showinfo("Erfolg", "Notiz gespeichert!")

    def open_last_note(self):
        """Öffnet die zuletzt gespeicherte Notiz."""
        if self.last_file:
            with open(self.last_file, "r", encoding="utf-8") as file:
                content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.current_file = self.last_file  # Setzt die aktuelle Datei auf die letzte geladene Datei
        else:
            messagebox.showwarning("Warnung", "Es wurde noch keine Notiz gespeichert!")

if __name__ == "__main__":
    root = tk.Tk()
    app = Notepad(root)
    root.mainloop()
