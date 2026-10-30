import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional

from src.database import (
    get_settings, get_all_products, get_next_bill_number_str,
    increment_bill_number, check_bill_number_exists, save_bill_record
)
from src.qr_generator import get_upi_qr_tk_photo
from src.pdf_generator import generate_invoice_pdf
from src.utils import format_currency

class POSTab(ttk.Frame):
    def __init__(self, parent, on_bill_saved_callback=None):
        super().__init__(parent)
        self.on_bill_saved = on_bill_saved_callback
        self.settings = get_settings()
        self.bill_items: List[Dict[str, Any]] = []
        self.current_qr_img: Optional[Any] = None # Keep reference to prevent GC

        self.setup_ui()
        self.reset_form()

    def refresh_settings(self):
        """Reload settings from database."""
        self.settings = get_settings()
        self.update_live_calculations()

    def setup_ui(self):
        # Main layout: Split into Left Panel (Form & Table) and Right Panel (Totals & UPI QR)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(self, padding=(12, 10))
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)

        right_frame = ttk.Frame(self, padding=(10, 10))
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT PANEL: 1. Bill & Customer Details Card
        # -------------------------------------------------------------
        meta_card = ttk.LabelFrame(left_frame, text="  Invoice & Customer Information  ", padding=10)
        meta_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        meta_card.columnconfigure(1, weight=1)
        meta_card.columnconfigure(3, weight=1)

        # Row 1: Bill Number (Editable!) & Date
        ttk.Label(meta_card, text="Bill / Invoice #:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=4)
        
        bill_no_container = ttk.Frame(meta_card)
        bill_no_container.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        bill_no_container.columnconfigure(0, weight=1)
        
        self.bill_no_var = tk.StringVar()
        self.bill_no_entry = ttk.Entry(bill_no_container, textvariable=self.bill_no_var, font=("Segoe UI", 9, "bold"))
        self.bill_no_entry.grid(row=0, column=0, sticky="ew")
        
        self.btn_auto_num = ttk.Button(bill_no_container, text="Auto Next", width=9, command=self.generate_next_bill_no)
        self.btn_auto_num.grid(row=0, column=1, padx=(4, 0))

        ttk.Label(meta_card, text="Invoice Date:", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.bill_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.bill_date_entry = ttk.Entry(meta_card, textvariable=self.bill_date_var, width=14)
        self.bill_date_entry.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        # Row 2: Customer Name & Phone
        ttk.Label(meta_card, text="Customer Name:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.cust_name_var = tk.StringVar(value="Walk-in Customer")
        self.cust_name_entry = ttk.Entry(meta_card, textvariable=self.cust_name_var)
        self.cust_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(meta_card, text="Customer Phone:", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.cust_phone_var = tk.StringVar()
        self.cust_phone_entry = ttk.Entry(meta_card, textvariable=self.cust_phone_var, width=16)
        self.cust_phone_entry.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        # Row 3: Payment Mode & Address
        ttk.Label(meta_card, text="Payment Mode:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.pay_mode_var = tk.StringVar(value="Cash")
        self.pay_mode_cb = ttk.Combobox(meta_card, textvariable=self.pay_mode_var, values=["Cash", "UPI", "Card", "Net Banking", "Credit / Due"], state="readonly", width=12)
        self.pay_mode_cb.grid(row=2, column=1, sticky="w", padx=5, pady=4)
        self.pay_mode_cb.bind("<<ComboboxSelected>>", lambda e: self.update_live_calculations())

        ttk.Label(meta_card, text="Customer Address:", font=("Segoe UI", 9)).grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.cust_addr_var = tk.StringVar()
        self.cust_addr_entry = ttk.Entry(meta_card, textvariable=self.cust_addr_var)
        self.cust_addr_entry.grid(row=2, column=3, sticky="ew", padx=5, pady=4)

        # -------------------------------------------------------------
        # LEFT PANEL: 2. Add Item Bar Card
        # -------------------------------------------------------------
        item_card = ttk.LabelFrame(left_frame, text="  Add Item to Bill  ", padding=8)
        item_card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        item_card.columnconfigure(1, weight=2)

        # Select Product / Custom Item
        ttk.Label(item_card, text="Item Name:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.item_name_var = tk.StringVar()
        self.item_cb = ttk.Combobox(item_card, textvariable=self.item_name_var)
        self.item_cb.grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        self.item_cb.bind("<<ComboboxSelected>>", self.on_inventory_item_selected)

        ttk.Label(item_card, text="Qty:").grid(row=0, column=2, sticky="w", padx=4, pady=2)
        self.item_qty_var = tk.StringVar(value="1")
        self.item_qty_entry = ttk.Entry(item_card, textvariable=self.item_qty_var, width=6)
        self.item_qty_entry.grid(row=0, column=3, padx=4, pady=2)

        ttk.Label(item_card, text="Rate (₹):").grid(row=0, column=4, sticky="w", padx=4, pady=2)
        self.item_rate_var = tk.StringVar(value="0.00")
        self.item_rate_entry = ttk.Entry(item_card, textvariable=self.item_rate_var, width=8)
        self.item_rate_entry.grid(row=0, column=5, padx=4, pady=2)

        ttk.Label(item_card, text="Disc %:").grid(row=0, column=6, sticky="w", padx=4, pady=2)
        self.item_disc_var = tk.StringVar(value="0")
        self.item_disc_entry = ttk.Entry(item_card, textvariable=self.item_disc_var, width=5)
        self.item_disc_entry.grid(row=0, column=7, padx=4, pady=2)

        ttk.Label(item_card, text="GST %:").grid(row=0, column=8, sticky="w", padx=4, pady=2)
        self.item_tax_var = tk.StringVar(value="0")
        self.item_tax_entry = ttk.Entry(item_card, textvariable=self.item_tax_var, width=5)
        self.item_tax_entry.grid(row=0, column=9, padx=4, pady=2)

        self.btn_add_item = ttk.Button(item_card, text=" + Add Item ", command=self.add_item_to_table)
        self.btn_add_item.grid(row=0, column=10, padx=(8, 4), pady=2)

        # Selected product reference
        self.selected_prod_id: Optional[int] = None
        self.refresh_products_list()

        # -------------------------------------------------------------
        # LEFT PANEL: 3. Bill Items Table
        # -------------------------------------------------------------
        table_frame = ttk.Frame(left_frame)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("sno", "name", "qty", "rate", "disc", "tax", "total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("sno", text="#")
        self.tree.heading("name", text="Item Name / Description")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("rate", text="Rate (₹)")
        self.tree.heading("disc", text="Disc %")
        self.tree.heading("tax", text="GST %")
        self.tree.heading("total", text="Total (₹)")

        self.tree.column("sno", width=36, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("qty", width=55, anchor="center")
        self.tree.column("rate", width=75, anchor="e")
        self.tree.column("disc", width=55, anchor="center")
        self.tree.column("tax", width=55, anchor="center")
        self.tree.column("total", width=90, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Table Action Toolbar
        action_bar = ttk.Frame(left_frame)
        action_bar.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        
        btn_remove = ttk.Button(action_bar, text="Delete Selected Item", command=self.remove_selected_item)
        btn_remove.pack(side="left", padx=4)

        btn_clear = ttk.Button(action_bar, text="Clear All Items", command=self.clear_table_items)
        btn_clear.pack(side="left", padx=4)

        # -------------------------------------------------------------
        # RIGHT PANEL: Summary, Live UPI QR Code & Action Buttons
        # -------------------------------------------------------------
        # Summary Card
        sum_card = ttk.LabelFrame(right_frame, text="  Bill Calculation Summary  ", padding=10)
        sum_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        sum_card.columnconfigure(1, weight=1)

        row_idx = 0
        def add_summary_row(label_text, is_bold=False):
            nonlocal row_idx
            font = ("Segoe UI", 9, "bold" if is_bold else "normal")
            val_var = tk.StringVar(value="₹ 0.00")
            ttk.Label(sum_card, text=label_text, font=font).grid(row=row_idx, column=0, sticky="w", pady=3)
            val_lbl = ttk.Label(sum_card, textvariable=val_var, font=font, anchor="e")
            val_lbl.grid(row=row_idx, column=1, sticky="e", pady=3)
            row_idx += 1
            return val_var

        self.subtotal_var = add_summary_row("Subtotal:")
        self.discount_var = add_summary_row("Discount:")
        self.tax_var = add_summary_row("Taxes (GST):")
        self.round_var = add_summary_row("Round Off:")

        ttk.Separator(sum_card, orient="horizontal").grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=6)
        row_idx += 1

        # Grand Total Large Display
        ttk.Label(sum_card, text="GRAND TOTAL:", font=("Segoe UI", 12, "bold"), foreground="#1E40AF").grid(row=row_idx, column=0, sticky="w", pady=4)
        self.grand_total_var = tk.StringVar(value="₹ 0.00")
        self.grand_total_lbl = ttk.Label(sum_card, textvariable=self.grand_total_var, font=("Segoe UI", 15, "bold"), foreground="#1E40AF", anchor="e")
        self.grand_total_lbl.grid(row=row_idx, column=1, sticky="e", pady=4)

        # UPI QR Code Card
        self.qr_card = ttk.LabelFrame(right_frame, text="  Live UPI QR Payment  ", padding=8)
        self.qr_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.qr_label = ttk.Label(self.qr_card, text="Generating UPI QR Code...", anchor="center", justify="center")
        self.qr_label.pack(fill="x", expand=True, pady=4)
        
        self.qr_info_label = ttk.Label(self.qr_card, text="Scan with PhonePe, GPay, Paytm", font=("Segoe UI", 7), anchor="center")
        self.qr_info_label.pack(fill="x")

        # Master Action Buttons
        btn_box = ttk.Frame(right_frame)
        btn_box.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        btn_box.columnconfigure(0, weight=1)

        self.btn_save_print = tk.Button(
            btn_box,
            text="🖨️  Save & Print / View PDF",
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="raised",
            bd=1,
            pady=8,
            cursor="hand2",
            command=self.save_and_print_bill
        )
        self.btn_save_print.grid(row=0, column=0, sticky="ew", pady=4)

        self.btn_save_only = tk.Button(
            btn_box,
            text="💾  Save Bill Only",
            font=("Segoe UI", 9, "bold"),
            bg="#059669",
            fg="white",
            activebackground="#047857",
            activeforeground="white",
            relief="raised",
            bd=1,
            pady=6,
            cursor="hand2",
            command=self.save_bill_only
        )
        self.btn_save_only.grid(row=1, column=0, sticky="ew", pady=4)

        self.btn_reset = ttk.Button(btn_box, text="New / Clear Bill", command=self.reset_form)
        self.btn_reset.grid(row=2, column=0, sticky="ew", pady=4)

    def refresh_products_list(self):
        """Load inventory products into combobox."""
        products = get_all_products()
        self.products_cache = {p["name"]: p for p in products}
        names = list(self.products_cache.keys())
        self.item_cb["values"] = names

    def on_inventory_item_selected(self, event=None):
        name = self.item_name_var.get().strip()
        if name in self.products_cache:
            p = self.products_cache[name]
            self.selected_prod_id = p["id"]
            self.item_rate_var.set(f"{p['price']:.2f}")
            self.item_tax_var.set(f"{p['tax_rate']:.0f}")
            self.item_disc_var.set("0")
            self.item_qty_var.set("1")
            self.item_qty_entry.focus()
            self.item_qty_entry.select_range(0, tk.END)

    def generate_next_bill_no(self):
        self.bill_no_var.set(get_next_bill_number_str())

    def add_item_to_table(self):
        name = self.item_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Item", "Please enter or select an item name.")
            return

        try:
            qty = float(self.item_qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Quantity", "Quantity must be a positive number.")
            return

        try:
            rate = float(self.item_rate_var.get())
            if rate < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Rate", "Rate must be a non-negative number.")
            return

        try:
            disc_pct = float(self.item_disc_var.get())
            if disc_pct < 0 or disc_pct > 100:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Discount", "Discount must be between 0% and 100%.")
            return

        try:
            tax_pct = float(self.item_tax_var.get())
            if tax_pct < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Tax Rate", "GST Tax rate must be a non-negative number.")
            return

        # Calculate item total: (rate * qty) - discount + tax
        gross = rate * qty
        disc_val = gross * (disc_pct / 100.0)
        taxable = gross - disc_val
        tax_val = taxable * (tax_pct / 100.0)
        line_total = taxable + tax_val

        item_data = {
            "product_id": self.selected_prod_id,
            "item_name": name,
            "quantity": qty,
            "unit_price": rate,
            "discount_percent": disc_pct,
            "tax_percent": tax_pct,
            "total_price": round(line_total, 2)
        }
        self.bill_items.append(item_data)
        self.render_table()

        # Reset item input fields
        self.selected_prod_id = None
        self.item_name_var.set("")
        self.item_qty_var.set("1")
        self.item_rate_var.set("0.00")
        self.item_disc_var.set("0")
        self.item_tax_var.set("0")
        self.item_cb.focus()

    def render_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, item in enumerate(self.bill_items, 1):
            self.tree.insert("", "end", values=(
                idx,
                item["item_name"],
                f"{item['quantity']:g}",
                f"{item['unit_price']:.2f}",
                f"{item['discount_percent']:g}%",
                f"{item['tax_percent']:g}%",
                f"{item['total_price']:.2f}"
            ))

        self.update_live_calculations()

    def remove_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Item", "Please select an item from the table to delete.")
            return
        index = self.tree.index(selected[0])
        if 0 <= index < len(self.bill_items):
            del self.bill_items[index]
            self.render_table()

    def clear_table_items(self):
        if not self.bill_items:
            return
        if messagebox.askyesno("Clear Table", "Are you sure you want to remove all items from this bill?"):
            self.bill_items.clear()
            self.render_table()

    def update_live_calculations(self):
        sym = self.settings.get("currency_symbol", "₹")
        subtotal = 0.0
        total_discount = 0.0
        total_tax = 0.0

        for item in self.bill_items:
            qty = item["quantity"]
            rate = item["unit_price"]
            disc_pct = item.get("discount_percent", 0.0)
            tax_pct = item.get("tax_percent", 0.0)

            gross = qty * rate
            disc = gross * (disc_pct / 100.0)
            taxable = gross - disc
            tax = taxable * (tax_pct / 100.0)

            subtotal += gross
            total_discount += disc
            total_tax += tax

        raw_grand_total = (subtotal - total_discount) + total_tax
        rounded_grand_total = round(raw_grand_total)
        round_off = rounded_grand_total - raw_grand_total

        self.calc_cache = {
            "subtotal": round(subtotal, 2),
            "discount_amount": round(total_discount, 2),
            "tax_amount": round(total_tax, 2),
            "round_off": round(round_off, 2),
            "grand_total": round(rounded_grand_total, 2)
        }

        self.subtotal_var.set(f"{sym} {subtotal:,.2f}")
        self.discount_var.set(f"{sym} {total_discount:,.2f}")
        self.tax_var.set(f"{sym} {total_tax:,.2f}")
        self.round_var.set(f"{round_off:+,.2f}")
        self.grand_total_var.set(f"{sym} {rounded_grand_total:,.2f}")

        # Update UPI QR Code in real time!
        upi_id = self.settings.get("upi_id", "").strip()
        payee = self.settings.get("upi_name", self.settings.get("shop_name", "RetailBill"))
        bill_no = self.bill_no_var.get().strip()

        if upi_id and rounded_grand_total > 0:
            try:
                photo = get_upi_qr_tk_photo(upi_id, payee, rounded_grand_total, bill_no, size=140)
                if photo:
                    self.current_qr_img = photo
                    self.qr_label.configure(image=photo, text="")
                    self.qr_info_label.configure(text=f"Pay ₹{rounded_grand_total:.2f} to {upi_id}")
                else:
                    self.qr_label.configure(image="", text="UPI QR unavailable")
            except Exception:
                self.qr_label.configure(image="", text="UPI QR preview")
        else:
            self.qr_label.configure(image="", text="[UPI QR Code will appear\nwhen items are added]")
            if not upi_id:
                self.qr_info_label.configure(text="Set UPI ID in Settings to enable")
            else:
                self.qr_info_label.configure(text=f"Ready for {upi_id}")

    def validate_bill(self) -> bool:
        bill_no = self.bill_no_var.get().strip()
        if not bill_no:
            messagebox.showerror("Error", "Bill / Invoice Number cannot be empty.")
            self.bill_no_entry.focus()
            return False

        if check_bill_number_exists(bill_no):
            messagebox.showerror("Duplicate Bill #", f"Bill number '{bill_no}' already exists in database!\nPlease choose a unique number or click 'Auto Next'.")
            self.bill_no_entry.focus()
            return False

        if not self.bill_items:
            messagebox.showerror("No Items", "Please add at least one item to save the bill.")
            return False

        return True

    def build_bill_record(self) -> Dict[str, Any]:
        return {
            "bill_number": self.bill_no_var.get().strip(),
            "customer_name": self.cust_name_var.get().strip() or "Walk-in Customer",
            "customer_phone": self.cust_phone_var.get().strip(),
            "customer_address": self.cust_addr_var.get().strip(),
            "bill_date": self.bill_date_var.get().strip(),
            "subtotal": self.calc_cache["subtotal"],
            "discount_amount": self.calc_cache["discount_amount"],
            "tax_amount": self.calc_cache["tax_amount"],
            "round_off": self.calc_cache["round_off"],
            "grand_total": self.calc_cache["grand_total"],
            "payment_mode": self.pay_mode_var.get(),
            "notes": ""
        }

    def save_bill_only(self):
        if not self.validate_bill():
            return

        bill_data = self.build_bill_record()
        try:
            bill_id = save_bill_record(bill_data, self.bill_items)
            increment_bill_number()
            messagebox.showinfo("Success", f"Bill '{bill_data['bill_number']}' saved successfully!")
            if self.on_bill_saved:
                self.on_bill_saved()
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save bill:\n{str(e)}")

    def save_and_print_bill(self):
        if not self.validate_bill():
            return

        bill_data = self.build_bill_record()
        try:
            bill_id = save_bill_record(bill_data, self.bill_items)
            increment_bill_number()
            
            # Generate PDF
            pdf_path = generate_invoice_pdf(bill_data, self.bill_items, self.settings)
            
            # Open PDF with default Windows viewer
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)

            messagebox.showinfo("Success", f"Bill '{bill_data['bill_number']}' saved and PDF generated!\nSaved at: {pdf_path}")
            if self.on_bill_saved:
                self.on_bill_saved()
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save and generate invoice:\n{str(e)}")

    def reset_form(self):
        self.generate_next_bill_no()
        self.bill_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.cust_name_var.set("Walk-in Customer")
        self.cust_phone_var.set("")
        self.cust_addr_var.set("")
        self.pay_mode_var.set("Cash")

        self.selected_prod_id = None
        self.item_name_var.set("")
        self.item_qty_var.set("1")
        self.item_rate_var.set("0.00")
        self.item_disc_var.set("0")
        self.item_tax_var.set("0")

        self.bill_items.clear()
        self.render_table()
        self.refresh_products_list()
