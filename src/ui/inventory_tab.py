import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List

from src.database import get_all_products, get_product_by_id, save_product, delete_product, get_settings
from src.utils import format_currency

class InventoryTab(ttk.Frame):
    def __init__(self, parent, on_inventory_changed_callback=None):
        super().__init__(parent)
        self.on_inventory_changed = on_inventory_changed_callback
        self.settings = get_settings()
        self.setup_ui()
        self.refresh_products()

    def refresh_settings(self):
        self.settings = get_settings()
        self.refresh_products()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # 1. Top Search and Action Bar
        top_bar = ttk.Frame(self, padding=(12, 10))
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(1, weight=1)

        ttk.Label(top_bar, text="Search Products:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_bar, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_products())

        btn_add = tk.Button(
            top_bar,
            text="+ Add New Product",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="raised",
            bd=1,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.open_add_product_dialog
        )
        btn_add.grid(row=0, column=2, padx=4)

        btn_refresh = ttk.Button(top_bar, text="🔄 Refresh", command=self.refresh_products)
        btn_refresh.grid(row=0, column=3, padx=4)

        # 2. Products Table
        table_frame = ttk.Frame(self, padding=(12, 5))
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "code", "name", "category", "unit", "price", "tax", "stock")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Item Code / SKU")
        self.tree.heading("name", text="Product / Service Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("unit", text="Unit")
        self.tree.heading("price", text="Price")
        self.tree.heading("tax", text="GST %")
        self.tree.heading("stock", text="Stock Qty")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("code", width=110, anchor="w")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("unit", width=65, anchor="center")
        self.tree.column("price", width=95, anchor="e")
        self.tree.column("tax", width=65, anchor="center")
        self.tree.column("stock", width=75, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", lambda e: self.open_edit_product_dialog())

        # 3. Action Toolbar
        action_bar = ttk.Frame(self, padding=(12, 8))
        action_bar.grid(row=2, column=0, sticky="ew")

        btn_edit = ttk.Button(action_bar, text="✏️ Edit Selected Product", command=self.open_edit_product_dialog)
        btn_edit.pack(side="left", padx=4)

        btn_del = ttk.Button(action_bar, text="🗑️ Delete Product", command=self.delete_selected_product)
        btn_del.pack(side="left", padx=4)

        ttk.Label(action_bar, text="* Double click any product to edit details", font=("Segoe UI", 8, "italic"), foreground="#64748B").pack(side="right", padx=6)

    def refresh_products(self):
        query = self.search_var.get().strip()
        products = get_all_products(query)
        sym = self.settings.get("currency_symbol", "₹")

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in products:
            self.tree.insert("", "end", values=(
                p["id"],
                p["code"] or "-",
                p["name"],
                p["category"] or "-",
                p["unit"] or "Pcs",
                f"{sym} {p['price']:,.2f}",
                f"{p['tax_rate']:g}%",
                p["stock"]
            ))

    def get_selected_product_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0], "values")
        return int(values[0])

    def open_add_product_dialog(self):
        self.show_product_dialog(title="Add New Product")

    def open_edit_product_dialog(self):
        pid = self.get_selected_product_id()
        if not pid:
            messagebox.showinfo("Select Product", "Please select a product from the list to edit.")
            return
        prod = get_product_by_id(pid)
        if prod:
            self.show_product_dialog(title=f"Edit Product - {prod['name']}", initial_data=prod)

    def show_product_dialog(self, title: str, initial_data: Optional[Dict[str, Any]] = None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("450x380")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        # Fields
        ttk.Label(frame, text="Product Name *:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        name_var = tk.StringVar(value=initial_data.get("name", "") if initial_data else "")
        entry_name = ttk.Entry(frame, textvariable=name_var)
        entry_name.grid(row=0, column=1, sticky="ew", pady=6)
        entry_name.focus()

        ttk.Label(frame, text="Item Code / SKU:").grid(row=1, column=0, sticky="w", pady=6)
        code_var = tk.StringVar(value=initial_data.get("code", "") if initial_data else "")
        entry_code = ttk.Entry(frame, textvariable=code_var)
        entry_code.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky="w", pady=6)
        cat_var = tk.StringVar(value=initial_data.get("category", "General") if initial_data else "General")
        entry_cat = ttk.Entry(frame, textvariable=cat_var)
        entry_cat.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Unit (Pcs, Kg, Box):").grid(row=3, column=0, sticky="w", pady=6)
        unit_var = tk.StringVar(value=initial_data.get("unit", "Pcs") if initial_data else "Pcs")
        entry_unit = ttk.Combobox(frame, textvariable=unit_var, values=["Pcs", "Box", "Kg", "Ltr", "Pack", "Rim", "Meter", "Set"])
        entry_unit.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Selling Price (₹) *:").grid(row=4, column=0, sticky="w", pady=6)
        price_var = tk.StringVar(value=f"{initial_data.get('price', 0.0):.2f}" if initial_data else "0.00")
        entry_price = ttk.Entry(frame, textvariable=price_var)
        entry_price.grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="GST Tax Rate (%):").grid(row=5, column=0, sticky="w", pady=6)
        tax_var = tk.StringVar(value=f"{initial_data.get('tax_rate', 0.0):g}" if initial_data else "18")
        entry_tax = ttk.Combobox(frame, textvariable=tax_var, values=["0", "5", "12", "18", "28"])
        entry_tax.grid(row=5, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Initial Stock Qty:").grid(row=6, column=0, sticky="w", pady=6)
        stock_var = tk.StringVar(value=str(initial_data.get("stock", 50)) if initial_data else "50")
        entry_stock = ttk.Entry(frame, textvariable=stock_var)
        entry_stock.grid(row=6, column=1, sticky="ew", pady=6)

        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Product Name is required.", parent=dialog)
                return

            try:
                price = float(price_var.get())
                if price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid price entered.", parent=dialog)
                return

            try:
                tax = float(tax_var.get())
                if tax < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid tax rate entered.", parent=dialog)
                return

            try:
                stock = int(stock_var.get())
                if stock < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid stock quantity entered.", parent=dialog)
                return

            pid = initial_data["id"] if initial_data else None
            try:
                save_product(
                    code=code_var.get().strip(),
                    name=name,
                    category=cat_var.get().strip(),
                    unit=unit_var.get().strip(),
                    price=price,
                    tax_rate=tax,
                    stock=stock,
                    product_id=pid
                )
                dialog.destroy()
                self.refresh_products()
                if self.on_inventory_changed:
                    self.on_inventory_changed()
                messagebox.showinfo("Saved", f"Product '{name}' saved successfully!")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save product:\n{str(e)}", parent=dialog)

        # Buttons
        btn_box = ttk.Frame(frame)
        btn_box.grid(row=7, column=0, columnspan=2, sticky="e", pady=(16, 0))

        btn_cancel = ttk.Button(btn_box, text="Cancel", command=dialog.destroy)
        btn_cancel.pack(side="right", padx=4)

        btn_ok = ttk.Button(btn_box, text="Save Product", command=save)
        btn_ok.pack(side="right", padx=4)

    def delete_selected_product(self):
        pid = self.get_selected_product_id()
        if not pid:
            messagebox.showinfo("Select Product", "Please select a product from the list to delete.")
            return
        prod = get_product_by_id(pid)
        name = prod["name"] if prod else f"#{pid}"

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{name}'?"):
            try:
                delete_product(pid)
                self.refresh_products()
                if self.on_inventory_changed:
                    self.on_inventory_changed()
                messagebox.showinfo("Deleted", f"Product '{name}' deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product:\n{str(e)}")
