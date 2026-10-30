import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from src.database import get_settings, init_db
from src.utils import resource_path, get_db_path
from src.ui.pos_tab import POSTab
from src.ui.history_tab import HistoryTab
from src.ui.inventory_tab import InventoryTab
from src.ui.settings_tab import SettingsTab

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("RetailBill - Desktop Billing & Invoicing System")
        self.geometry("1180x760")
        self.minsize(980, 640)

        # Apply application icon
        icon_path = resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Configure TTK Styles
        self.setup_styles()

        # Build UI layout
        self.build_header()
        self.build_tabs()
        self.build_statusbar()

    def setup_styles(self):
        style = ttk.Style(self)
        # Use clam or default based on platform
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")

        # Global font and color styling
        bg_main = "#F8FAFC"
        self.configure(bg=bg_main)

        style.configure(".", background=bg_main, font=("Segoe UI", 9))
        style.configure("TFrame", background=bg_main)
        style.configure("TLabel", background=bg_main, foreground="#1E293B")
        style.configure("TLabelframe", background=bg_main, foreground="#0F172A")
        style.configure("TLabelframe.Label", font=("Segoe UI", 9, "bold"), foreground="#1E40AF")

        # Notebook (Tabs) styling
        style.configure("TNotebook", background=bg_main, tabmargins=[10, 5, 2, 0])
        style.configure(
            "TNotebook.Tab",
            padding=[18, 8],
            font=("Segoe UI", 10, "bold"),
            background="#E2E8F0",
            foreground="#334155"
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

        # Treeview styling
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#0F172A",
            fieldbackground="#FFFFFF",
            rowheight=26,
            font=("Segoe UI", 9)
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#F1F5F9",
            foreground="#1E293B"
        )
        style.map(
            "Treeview",
            background=[("selected", "#3B82F6")],
            foreground=[("selected", "#FFFFFF")]
        )

        # Buttons
        style.configure("TButton", font=("Segoe UI", 9), padding=[8, 4])

    def build_header(self):
        settings = get_settings()
        shop_name = settings.get("shop_name", "RetailBill Superstore")

        header_frame = tk.Frame(self, bg="#1E3A8A", height=60, padx=16, pady=8)
        header_frame.pack(side="top", fill="x")

        # Left: App Brand & Title
        title_box = tk.Frame(header_frame, bg="#1E3A8A")
        title_box.pack(side="left", fill="y")

        lbl_app = tk.Label(
            title_box,
            text="RetailBill",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#1E3A8A"
        )
        lbl_app.pack(anchor="w")

        self.lbl_shop_header = tk.Label(
            title_box,
            text=f"Store: {shop_name}",
            font=("Segoe UI", 9),
            fg="#93C5FD",
            bg="#1E3A8A"
        )
        self.lbl_shop_header.pack(anchor="w")

        # Right: Offline Status Badge & Mode
        right_box = tk.Frame(header_frame, bg="#1E3A8A")
        right_box.pack(side="right", fill="y")

        badge = tk.Label(
            right_box,
            text="● Offline SQLite Mode",
            font=("Segoe UI", 9, "bold"),
            fg="#10B981",
            bg="#064E3B",
            padx=10,
            pady=3,
            relief="flat"
        )
        badge.pack(side="right", pady=6)

    def build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side="top", fill="both", expand=True, padx=10, pady=8)

        # Tab 1: Billing / POS
        self.pos_tab = POSTab(self.notebook, on_bill_saved_callback=self.on_bill_saved)
        self.notebook.add(self.pos_tab, text="  💳  Billing / POS  ")

        # Tab 2: Invoices & History
        self.history_tab = HistoryTab(self.notebook)
        self.notebook.add(self.history_tab, text="  📄  Invoices & History  ")

        # Tab 3: Inventory
        self.inventory_tab = InventoryTab(self.notebook, on_inventory_changed_callback=self.on_inventory_changed)
        self.notebook.add(self.inventory_tab, text="  📦  Inventory Items  ")

        # Tab 4: Settings
        self.settings_tab = SettingsTab(self.notebook, on_settings_saved_callback=self.on_settings_saved)
        self.notebook.add(self.settings_tab, text="  ⚙️  Settings & Assets  ")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched)

    def build_statusbar(self):
        status_frame = tk.Frame(self, bg="#E2E8F0", height=24, padx=12, pady=3)
        status_frame.pack(side="bottom", fill="x")

        db_path = get_db_path()
        lbl_status = tk.Label(
            status_frame,
            text=f"Database: {db_path}  |  Standalone Windows Application  |  RetailBill v1.0.0",
            font=("Segoe UI", 8),
            fg="#475569",
            bg="#E2E8F0"
        )
        lbl_status.pack(side="left")

        lbl_shortcuts = tk.Label(
            status_frame,
            text="F5: Refresh | Esc: Clear",
            font=("Segoe UI", 8),
            fg="#64748B",
            bg="#E2E8F0"
        )
        lbl_shortcuts.pack(side="right")

    def on_bill_saved(self):
        self.history_tab.refresh_data()
        self.inventory_tab.refresh_products()

    def on_inventory_changed(self):
        self.pos_tab.refresh_products_list()

    def on_settings_saved(self):
        settings = get_settings()
        shop_name = settings.get("shop_name", "RetailBill Superstore")
        self.lbl_shop_header.configure(text=f"Store: {shop_name}")
        self.pos_tab.refresh_settings()
        self.history_tab.refresh_settings()
        self.inventory_tab.refresh_settings()

    def on_tab_switched(self, event):
        selected_index = self.notebook.index(self.notebook.select())
        if selected_index == 0:
            self.pos_tab.refresh_products_list()
        elif selected_index == 1:
            self.history_tab.refresh_data()
        elif selected_index == 2:
            self.inventory_tab.refresh_products()
