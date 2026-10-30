import os
import sys
import ctypes
import traceback
import tkinter as tk
from tkinter import messagebox

# Ensure current directory and src directory are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import init_db
from src.ui.main_window import MainWindow

def enable_high_dpi_awareness():
    """Enable crisp rendering on Windows High-DPI screens."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def main():
    enable_high_dpi_awareness()

    try:
        # Initialize SQLite database and default assets
        init_db()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "RetailBill Startup Error",
            f"Failed to initialize database:\n{str(e)}\n\n{traceback.format_exc()}"
        )
        return

    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "RetailBill Application Error",
            f"An unexpected error occurred:\n{str(e)}\n\n{traceback.format_exc()}"
        )

if __name__ == "__main__":
    main()
