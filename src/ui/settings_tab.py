import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from PIL import Image, ImageTk

from src.database import get_settings, update_settings
from src.utils import get_custom_assets_dir, get_db_path

class SettingsTab(ttk.Frame):
    def __init__(self, parent, on_settings_saved_callback=None):
        super().__init__(parent)
        self.on_settings_saved = on_settings_saved_callback
        self.sig_photo_ref: Optional[Any] = None
        self.seal_photo_ref: Optional[Any] = None
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        # Create a scrollable container for settings
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, padding=16)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Two-column layout in scroll_frame
        scroll_frame.columnconfigure(0, weight=1)
        scroll_frame.columnconfigure(1, weight=1)

        # -------------------------------------------------------------
        # LEFT COLUMN: Shop Info & Invoice Configuration
        # -------------------------------------------------------------
        left_box = ttk.Frame(scroll_frame)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_box.columnconfigure(1, weight=1)

        # 1. Shop Profile
        shop_group = ttk.LabelFrame(left_box, text="  Shop / Business Profile  ", padding=12)
        shop_group.pack(fill="x", pady=(0, 12))
        shop_group.columnconfigure(1, weight=1)

        ttk.Label(shop_group, text="Shop Name *:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.shop_name_var = tk.StringVar()
        ttk.Entry(shop_group, textvariable=self.shop_name_var).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(shop_group, text="Tagline / Slogan:").grid(row=1, column=0, sticky="w", pady=4)
        self.tagline_var = tk.StringVar()
        ttk.Entry(shop_group, textvariable=self.tagline_var).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(shop_group, text="Store Address:").grid(row=2, column=0, sticky="w", pady=4)
        self.address_var = tk.StringVar()
        ttk.Entry(shop_group, textvariable=self.address_var).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(shop_group, text="Phone Number:").grid(row=3, column=0, sticky="w", pady=4)
        self.phone_var = tk.StringVar()
        ttk.Entry(shop_group, textvariable=self.phone_var).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(shop_group, text="Email Address:").grid(row=4, column=0, sticky="w", pady=4)
        self.email_var = tk.StringVar()
        ttk.Entry(shop_group, textvariable=self.email_var).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(shop_group, text="GSTIN / Tax ID:").grid(row=5, column=0, sticky="w", pady=4)
        self.gstin_var = tk.StringVar()
        ttk.Entry(shop_group, textvariable=self.gstin_var).grid(row=5, column=1, sticky="ew", pady=4)

        # 2. Billing & UPI Settings
        inv_group = ttk.LabelFrame(left_box, text="  Invoice & UPI Payment Configuration  ", padding=12)
        inv_group.pack(fill="x", pady=(0, 12))
        inv_group.columnconfigure(1, weight=1)

        ttk.Label(inv_group, text="Currency Symbol:").grid(row=0, column=0, sticky="w", pady=4)
        self.curr_sym_var = tk.StringVar(value="₹")
        ttk.Combobox(inv_group, textvariable=self.curr_sym_var, values=["₹", "$", "€", "£", "AED", "Rs."], width=8).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(inv_group, text="Invoice Prefix:").grid(row=1, column=0, sticky="w", pady=4)
        self.prefix_var = tk.StringVar(value="INV-")
        ttk.Entry(inv_group, textvariable=self.prefix_var, width=12).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(inv_group, text="Next Bill Sequence #:").grid(row=2, column=0, sticky="w", pady=4)
        self.next_num_var = tk.StringVar(value="1001")
        ttk.Entry(inv_group, textvariable=self.next_num_var, width=12).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(inv_group, text="UPI ID (VPA):", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        self.upi_id_var = tk.StringVar()
        ttk.Entry(inv_group, textvariable=self.upi_id_var).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(inv_group, text="UPI Payee Name:").grid(row=4, column=0, sticky="w", pady=4)
        self.upi_name_var = tk.StringVar()
        ttk.Entry(inv_group, textvariable=self.upi_name_var).grid(row=4, column=1, sticky="ew", pady=4)

        # -------------------------------------------------------------
        # RIGHT COLUMN: Signatures, Seal Stamps & Terms
        # -------------------------------------------------------------
        right_box = ttk.Frame(scroll_frame)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_box.columnconfigure(1, weight=1)

        # 3. Authorized Signature Upload & Preview
        sig_group = ttk.LabelFrame(right_box, text="  Authorized Signatory Signature  ", padding=12)
        sig_group.pack(fill="x", pady=(0, 12))
        sig_group.columnconfigure(0, weight=1)

        self.sig_path_var = tk.StringVar()

        # Preview Container
        sig_preview_frame = ttk.Frame(sig_group, relief="solid", borderwidth=1, padding=4)
        sig_preview_frame.pack(fill="x", pady=(0, 8))
        self.sig_img_label = ttk.Label(sig_preview_frame, text="No signature loaded", anchor="center")
        self.sig_img_label.pack(fill="both", expand=True, ipady=10)

        sig_btn_box = ttk.Frame(sig_group)
        sig_btn_box.pack(fill="x")
        ttk.Button(sig_btn_box, text="📁 Browse / Upload Signature...", command=self.browse_signature).pack(side="left", padx=2)
        ttk.Button(sig_btn_box, text="Clear", command=self.clear_signature).pack(side="left", padx=2)

        # 4. Shop Seal / Stamp Upload & Preview
        seal_group = ttk.LabelFrame(right_box, text="  Shop Seal / Official Stamp  ", padding=12)
        seal_group.pack(fill="x", pady=(0, 12))
        seal_group.columnconfigure(0, weight=1)

        self.seal_path_var = tk.StringVar()

        seal_preview_frame = ttk.Frame(seal_group, relief="solid", borderwidth=1, padding=4)
        seal_preview_frame.pack(fill="x", pady=(0, 8))
        self.seal_img_label = ttk.Label(seal_preview_frame, text="No shop seal loaded", anchor="center")
        self.seal_img_label.pack(fill="both", expand=True, ipady=10)

        seal_btn_box = ttk.Frame(seal_group)
        seal_btn_box.pack(fill="x")
        ttk.Button(seal_btn_box, text="📁 Browse / Upload Seal...", command=self.browse_seal).pack(side="left", padx=2)
        ttk.Button(seal_btn_box, text="Clear", command=self.clear_seal).pack(side="left", padx=2)

        # 5. Terms & Conditions
        terms_group = ttk.LabelFrame(right_box, text="  Invoice Terms & Conditions  ", padding=12)
        terms_group.pack(fill="both", expand=True, pady=(0, 12))
        
        self.terms_text = tk.Text(terms_group, height=4, font=("Segoe UI", 9), wrap="word")
        self.terms_text.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # BOTTOM: Save Button and Info
        # -------------------------------------------------------------
        bottom_frame = ttk.Frame(scroll_frame, padding=(0, 10))
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)

        db_path = get_db_path()
        ttk.Label(bottom_frame, text=f"SQLite Database: {db_path}", font=("Segoe UI", 8), foreground="#64748B").pack(side="left")

        btn_save = tk.Button(
            bottom_frame,
            text="💾  Save All Settings",
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="raised",
            bd=1,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.save_all_settings
        )
        btn_save.pack(side="right", padx=4)

    def load_settings(self):
        settings = get_settings()
        self.shop_name_var.set(settings.get("shop_name", ""))
        self.tagline_var.set(settings.get("shop_tagline", ""))
        self.address_var.set(settings.get("address", ""))
        self.phone_var.set(settings.get("phone", ""))
        self.email_var.set(settings.get("email", ""))
        self.gstin_var.set(settings.get("gstin", ""))

        self.curr_sym_var.set(settings.get("currency_symbol", "₹"))
        self.prefix_var.set(settings.get("invoice_prefix", "INV-"))
        self.next_num_var.set(str(settings.get("next_bill_number", 1001)))
        self.upi_id_var.set(settings.get("upi_id", ""))
        self.upi_name_var.set(settings.get("upi_name", ""))

        self.sig_path_var.set(settings.get("signature_path", ""))
        self.seal_path_var.set(settings.get("seal_path", ""))

        self.terms_text.delete("1.0", tk.END)
        self.terms_text.insert("1.0", settings.get("terms", ""))

        self.update_signature_preview()
        self.update_seal_preview()

    def update_signature_preview(self):
        path = self.sig_path_var.get().strip()
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((200, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.sig_photo_ref = photo
                self.sig_img_label.configure(image=photo, text="")
            except Exception:
                self.sig_img_label.configure(image="", text="Error previewing signature image")
        else:
            self.sig_img_label.configure(image="", text="[No signature configured]")

    def update_seal_preview(self):
        path = self.seal_path_var.get().strip()
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((90, 90), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.seal_photo_ref = photo
                self.seal_img_label.configure(image=photo, text="")
            except Exception:
                self.seal_img_label.configure(image="", text="Error previewing seal image")
        else:
            self.seal_img_label.configure(image="", text="[No seal configured]")

    def browse_signature(self):
        file_path = filedialog.askopenfilename(
            title="Select Signature Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            # Copy to user custom assets dir
            custom_dir = get_custom_assets_dir()
            dest_name = f"signature_{os.path.basename(file_path)}"
            dest_path = os.path.join(custom_dir, dest_name)
            try:
                shutil.copy2(file_path, dest_path)
                self.sig_path_var.set(dest_path)
                self.update_signature_preview()
            except Exception as e:
                messagebox.showerror("Upload Error", f"Could not copy file:\n{str(e)}")

    def clear_signature(self):
        self.sig_path_var.set("")
        self.update_signature_preview()

    def browse_seal(self):
        file_path = filedialog.askopenfilename(
            title="Select Shop Seal / Stamp Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            custom_dir = get_custom_assets_dir()
            dest_name = f"seal_{os.path.basename(file_path)}"
            dest_path = os.path.join(custom_dir, dest_name)
            try:
                shutil.copy2(file_path, dest_path)
                self.seal_path_var.set(dest_path)
                self.update_seal_preview()
            except Exception as e:
                messagebox.showerror("Upload Error", f"Could not copy file:\n{str(e)}")

    def clear_seal(self):
        self.seal_path_var.set("")
        self.update_seal_preview()

    def save_all_settings(self):
        name = self.shop_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Shop Name cannot be empty.")
            return

        try:
            next_num = int(self.next_num_var.get().strip())
            if next_num <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Next Bill Sequence Number must be a positive integer.")
            return

        data = {
            "shop_name": name,
            "shop_tagline": self.tagline_var.get().strip(),
            "address": self.address_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "email": self.email_var.get().strip(),
            "gstin": self.gstin_var.get().strip(),
            "currency_symbol": self.curr_sym_var.get().strip() or "₹",
            "invoice_prefix": self.prefix_var.get().strip(),
            "next_bill_number": next_num,
            "upi_id": self.upi_id_var.get().strip(),
            "upi_name": self.upi_name_var.get().strip(),
            "signature_path": self.sig_path_var.get().strip(),
            "seal_path": self.seal_path_var.get().strip(),
            "terms": self.terms_text.get("1.0", tk.END).strip()
        }

        try:
            update_settings(data)
            messagebox.showinfo("Saved", "Settings updated successfully!")
            if self.on_settings_saved:
                self.on_settings_saved()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update settings:\n{str(e)}")
