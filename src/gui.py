# src/gui.py
import tkinter as tk
from tkinter import ttk
from db import search_verses

def on_search():
    keyword = search_var.get().strip()
    results_box.delete("1.0", tk.END)

    if not keyword:
        results_box.insert(tk.END, "Please enter a search term.\n")
        return

    results = search_verses(keyword)
    if not results:
        results_box.insert(tk.END, "No results found.\n")
        return

    for book, chapter, verse, text in results:
        results_box.insert(tk.END, f"{book} {chapter}:{verse} — {text}\n\n")

# Set up window
root = tk.Tk()
root.title("Scriptorium")
root.geometry("800x800")

# Input bar
search_var = tk.StringVar()
search_frame = ttk.Frame(root)
search_frame.pack(pady=10, padx=10, fill="x")
book_var    = tk.StringVar()  # holds a string
chapter_var = tk.IntVar()     # holds an int
verse_var   = tk.IntVar()

ttk.Label(search_frame, text="Search:").pack(side="left")
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=50)
search_entry.pack(side="left", padx=5)
ttk.Button(search_frame, text="Go", command=on_search).pack(side="left")

# Scrollable text box for results
results_frame = ttk.Frame(root)
results_frame.pack(pady=10, padx=10, fill="both", expand=True)

results_box = tk.Text(results_frame, wrap="word")
results_box.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_box.yview)
scrollbar.pack(side="right", fill="y")
results_box.config(yscrollcommand=scrollbar.set)

# Start the app
root.mainloop()
