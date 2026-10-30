import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List

from src.database import get_all_bills, get_bill_by_id, get_bill_items, delete_bill, get_settings, get_dashboard_stats
from src.pdf_generator import generate_invoice_pdf
from src.utils import format_currency

class HistoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.settings = get_settings()
        self.setup_ui()
        self.refresh_data()

    def refresh_settings(self):
        self.settings = get_settings()
        self.refresh_data()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # 1. Top KPI Summary Dashboard Cards
        kpi_frame = ttk.Frame(self, padding=(12, 10, 12, 5))
        kpi_frame.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            kpi_frame.columnconfigure(i, weight=1)

        def create_kpi_card(parent, col, title, initial_val, color="#1E40AF"):
            card = ttk.Frame(parent, relief="solid", borderwidth=1, padding=8)
            card.grid(row=0, column=col, padx=4, sticky="nsew")
            
            lbl_title = ttk.Label(card, text=title, font=("Segoe UI", 8), foreground="#64748B")
            lbl_title.pack(anchor="w")

            val_var = tk.StringVar(value=initial_val)
            lbl_val = ttk.Label(card, textvariable=val_var, font=("Segoe UI", 13, "bold"), foreground=color)
            lbl_val.pack(anchor="w", pady=(2, 0))
            return val_var

        self.kpi_today_rev = create_kpi_card(kpi_frame, 0, "TODAY'S REVENUE", "₹ 0.00", "#059669")
        self.kpi_today_count = create_kpi_card(kpi_frame, 1, "BILLS TODAY", "0", "#2563EB")
        self.kpi_total_rev = create_kpi_card(kpi_frame, 2, "TOTAL REVENUE", "₹ 0.00", "#7C3AED")
        self.kpi_total_count = create_kpi_card(kpi_frame, 3, "TOTAL INVOICES", "0", "#0284C7")

        # 2. Search & Filter Bar
        filter_frame = ttk.Frame(self, padding=(12, 5))
        filter_frame.grid(row=1, column=0, sticky="ew")
        filter_frame.columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Search Bills:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        self.search_entry.bind("<Return>", lambda e: self.refresh_data())
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search_change())

        btn_search = ttk.Button(filter_frame, text="Search", command=self.refresh_data)
        btn_search.grid(row=0, column=2, padx=4)

        btn_clear = ttk.Button(filter_frame, text="Clear", command=self.clear_search)
        btn_clear.grid(row=0, column=3, padx=4)

        btn_refresh = ttk.Button(filter_frame, text="🔄 Refresh", command=self.refresh_data)
        btn_refresh.grid(row=0, column=4, padx=4)

        # 3. Bill Records Treeview
        tree_frame = ttk.Frame(self, padding=(12, 5))
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("id", "bill_no", "date", "customer", "phone", "items_count", "total", "mode")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("bill_no", text="Invoice Number")
        self.tree.heading("date", text="Date")
        self.tree.heading("customer", text="Customer Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("items_count", text="Items")
        self.tree.heading("total", text="Grand Total")
        self.tree.heading("mode", text="Payment Mode")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("bill_no", width=120, anchor="w")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("customer", width=180, anchor="w")
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("items_count", width=60, anchor="center")
        self.tree.column("total", width=110, anchor="e")
        self.tree.column("mode", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", lambda e: self.reprint_selected_pdf())

        # 4. Action Toolbar
        action_bar = ttk.Frame(self, padding=(12, 8))
        action_bar.grid(row=3, column=0, sticky="ew")

        btn_view_pdf = ttk.Button(action_bar, text="📄 View / Reprint Invoice PDF", command=self.reprint_selected_pdf)
        btn_view_pdf.pack(side="left", padx=4)

        btn_delete = ttk.Button(action_bar, text="🗑️ Delete Invoice", command=self.delete_selected_bill)
        btn_delete.pack(side="left", padx=4)

        ttk.Label(action_bar, text="* Double-click any row to view / reprint PDF", font=("Segoe UI", 8, "italic"), foreground="#64748B").pack(side="right", padx=6)

    def on_search_change(self):
        # Debounce or search directly
        self.refresh_data()

    def clear_search(self):
        self.search_var.set("")
        self.refresh_data()

    def refresh_data(self):
        # Update KPIs
        stats = get_dashboard_stats()
        sym = self.settings.get("currency_symbol", "₹")
        self.kpi_today_rev.set(f"{sym} {stats['today_revenue']:,.2f}")
        self.kpi_today_count.set(str(stats['today_bills']))
        self.kpi_total_rev.set(f"{sym} {stats['total_revenue']:,.2f}")
        self.kpi_total_count.set(str(stats['total_bills']))

        # Update Treeview
        query = self.search_var.get().strip()
        bills = get_all_bills(query)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for b in bills:
            self.tree.insert("", "end", values=(
                b["id"],
                b["bill_number"],
                b["bill_date"],
                b["customer_name"],
                b["customer_phone"] or "-",
                b["item_count"],
                f"{sym} {b['grand_total']:,.2f}",
                b["payment_mode"]
            ))

    def get_selected_bill_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0], "values")
        return int(values[0])

    def reprint_selected_pdf(self):
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            messagebox.showinfo("Select Bill", "Please select a bill from the list.")
            return

        bill = get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Could not locate bill details.")
            return

        items = get_bill_items(bill_id)
        try:
            pdf_path = generate_invoice_pdf(bill, items, self.settings)
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)
            messagebox.showinfo("PDF Generated", f"Invoice PDF generated successfully!\nPath: {pdf_path}")
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to generate invoice PDF:\n{str(e)}")

    def delete_selected_bill(self):
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            messagebox.showinfo("Select Bill", "Please select a bill from the list to delete.")
            return

        bill = get_bill_by_id(bill_id)
        bill_no = bill["bill_number"] if bill else f"#{bill_id}"

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete invoice '{bill_no}'?\nThis will remove the bill record permanently."):
            try:
                delete_bill(bill_id)
                self.refresh_data()
                messagebox.showinfo("Deleted", f"Invoice '{bill_no}' has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete bill:\n{str(e)}")
