import tkinter as tk
from tkcalendar import DateEntry

root = tk.Tk()

def get_date():
    print("Ausgewähltes Datum:", cal.get_date())

cal = DateEntry(root, width=12, background="darkblue", foreground="white", borderwidth=2)
cal.pack(pady=20)

btn = tk.Button(root, text="Datum abrufen", command=get_date)
btn.pack()

root.mainloop()


