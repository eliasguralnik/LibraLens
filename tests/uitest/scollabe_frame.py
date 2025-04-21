import tkinter as tk

def create_scrollable_frame(root):
    canvas = tk.Canvas(root, borderwidth=0, background="#f0f0f0", height=400)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
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

    # 🖱 Mausrad-Scroll aktivieren (funktioniert unter Windows und Linux)
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # macOS braucht ein anderes Scroll-Verhalten
    def on_mousewheel_mac(event):
        canvas.yview_scroll(-1 * event.delta, "units")

    if root.tk.call("tk", "windowingsystem") == "aqua":
        canvas.bind_all("<MouseWheel>", on_mousewheel_mac)  # macOS
    else:
        canvas.bind_all("<MouseWheel>", on_mousewheel)      # Windows/Linux

    return scrollable_frame

# Anwendung
root = tk.Tk()
root.geometry("400x400")

frame = create_scrollable_frame(root)

# Beispiel: viele Labels zum Testen
for i in range(150):
    tk.Label(frame, text=f"Label {i}").pack()

root.mainloop()
