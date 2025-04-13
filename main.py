# main.py
import tkinter as tk
from gui import ArticleApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ArticleApp(root)
    root.mainloop()