import sqlite3
import os
import shutil
from typing import Dict, Any, List, Optional
from src.utils import get_db_path, resource_path, get_custom_assets_dir

def get_connection() -> sqlite3.Connection:
    """Return SQLite connection with Row factory."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize SQLite database tables and default data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            shop_name TEXT NOT NULL DEFAULT 'RetailBill Superstore',
            shop_tagline TEXT DEFAULT 'Quality Products & Fast Service',
            address TEXT DEFAULT '123 Market Road, Commercial Hub',
            phone TEXT DEFAULT '+91 98765 43210',
            email TEXT DEFAULT 'contact@retailbill.com',
            gstin TEXT DEFAULT '29ABCDE1234F1Z5',
            upi_id TEXT DEFAULT 'retailbill@upi',
            upi_name TEXT DEFAULT 'RetailBill Store',
            currency_symbol TEXT DEFAULT '₹',
            invoice_prefix TEXT DEFAULT 'INV-',
            next_bill_number INTEGER DEFAULT 1001,
            signature_path TEXT DEFAULT '',
            seal_path TEXT DEFAULT '',
            terms TEXT DEFAULT '1. Goods once sold cannot be returned.\n2. Warranty as per manufacturer terms.\n3. Thank you for your business!'
        )
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            unit TEXT DEFAULT 'Pcs',
            price REAL NOT NULL DEFAULT 0.0,
            tax_rate REAL NOT NULL DEFAULT 0.0,
            stock INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT UNIQUE NOT NULL,
            customer_name TEXT DEFAULT 'Walk-in Customer',
            customer_phone TEXT DEFAULT '',
            customer_address TEXT DEFAULT '',
            bill_date TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0.0,
            discount_amount REAL NOT NULL DEFAULT 0.0,
            tax_amount REAL NOT NULL DEFAULT 0.0,
            round_off REAL NOT NULL DEFAULT 0.0,
            grand_total REAL NOT NULL DEFAULT 0.0,
            payment_mode TEXT NOT NULL DEFAULT 'Cash',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bill items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            product_id INTEGER,
            item_name TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 1.0,
            unit_price REAL NOT NULL DEFAULT 0.0,
            discount_percent REAL NOT NULL DEFAULT 0.0,
            tax_percent REAL NOT NULL DEFAULT 0.0,
            total_price REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
        )
    """)

    # Ensure default settings row exists
    cursor.execute("SELECT COUNT(*) FROM settings WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        # Check if default sample signature & seal exist in assets
        default_sig = resource_path("assets/sample_signature.png")
        default_seal = resource_path("assets/sample_seal.png")
        
        # Copy to custom assets dir for user persistence
        custom_assets = get_custom_assets_dir()
        persisted_sig = os.path.join(custom_assets, "default_signature.png")
        persisted_seal = os.path.join(custom_assets, "default_seal.png")
        
        if os.path.exists(default_sig) and not os.path.exists(persisted_sig):
            shutil.copy2(default_sig, persisted_sig)
        if os.path.exists(default_seal) and not os.path.exists(persisted_seal):
            shutil.copy2(default_seal, persisted_seal)

        sig_to_store = persisted_sig if os.path.exists(persisted_sig) else default_sig
        seal_to_store = persisted_seal if os.path.exists(persisted_seal) else default_seal

        cursor.execute("""
            INSERT INTO settings (id, signature_path, seal_path)
            VALUES (1, ?, ?)
        """, (sig_to_store, seal_to_store))

    # Pre-seed some sample inventory if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("P101", "Wireless Optical Mouse", "Electronics", "Pcs", 499.00, 18.0, 45),
            ("P102", "Mechanical USB Keyboard", "Electronics", "Pcs", 1499.00, 18.0, 30),
            ("P103", "A4 Copier Paper 75 GSM (500 Sheets)", "Stationery", "Rim", 280.00, 12.0, 120),
            ("P104", "Gel Pen Blue Pack of 10", "Stationery", "Pack", 150.00, 12.0, 85),
            ("P105", "Fast Charger 30W Type-C", "Mobile Accessories", "Pcs", 850.00, 18.0, 50),
            ("P106", "Braided USB-C Cable 1.5m", "Mobile Accessories", "Pcs", 250.00, 18.0, 75),
            ("P107", "Desk Organizer Wooden Tray", "Office", "Pcs", 399.00, 12.0, 25),
            ("P108", "Executive Notebook Hardbound", "Stationery", "Pcs", 220.00, 5.0, 60),
            ("P109", "Laptop Cooling Stand Aluminum", "Accessories", "Pcs", 1199.00, 18.0, 15),
            ("P110", "HDMI 2.1 Cable 4K 60Hz 2m", "Electronics", "Pcs", 349.00, 18.0, 40),
        ]
        cursor.executemany("""
            INSERT INTO products (code, name, category, unit, price, tax_rate, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_products)

    conn.commit()
    conn.close()

def get_settings() -> Dict[str, Any]:
    """Retrieve shop and invoice configuration."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}

def update_settings(data: Dict[str, Any]):
    """Update application settings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE settings SET
            shop_name = :shop_name,
            shop_tagline = :shop_tagline,
            address = :address,
            phone = :phone,
            email = :email,
            gstin = :gstin,
            upi_id = :upi_id,
            upi_name = :upi_name,
            currency_symbol = :currency_symbol,
            invoice_prefix = :invoice_prefix,
            next_bill_number = :next_bill_number,
            signature_path = :signature_path,
            seal_path = :seal_path,
            terms = :terms
        WHERE id = 1
    """, data)
    conn.commit()
    conn.close()

def get_next_bill_number_str() -> str:
    """Generate next bill number string based on settings prefix and counter."""
    settings = get_settings()
    prefix = settings.get("invoice_prefix", "INV-")
    num = settings.get("next_bill_number", 1001)
    return f"{prefix}{num}"

def increment_bill_number():
    """Increment next bill number counter in settings."""
    conn = get_connection()
    conn.execute("UPDATE settings SET next_bill_number = next_bill_number + 1 WHERE id = 1")
    conn.commit()
    conn.close()

def check_bill_number_exists(bill_number: str, exclude_id: Optional[int] = None) -> bool:
    """Check if bill number already exists."""
    conn = get_connection()
    if exclude_id:
        row = conn.execute("SELECT id FROM bills WHERE bill_number = ? AND id != ?", (bill_number, exclude_id)).fetchone()
    else:
        row = conn.execute("SELECT id FROM bills WHERE bill_number = ?", (bill_number,)).fetchone()
    conn.close()
    return row is not None

# Product CRUD
def get_all_products(search: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    if search:
        query = "%" + search.strip() + "%"
        rows = conn.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR code LIKE ? OR category LIKE ?
            ORDER BY name ASC
        """, (query, query, query)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def save_product(code: str, name: str, category: str, unit: str, price: float, tax_rate: float, stock: int, product_id: Optional[int] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    if product_id:
        cursor.execute("""
            UPDATE products SET
                code = ?, name = ?, category = ?, unit = ?, price = ?, tax_rate = ?, stock = ?
            WHERE id = ?
        """, (code, name, category, unit, price, tax_rate, stock, product_id))
        res_id = product_id
    else:
        cursor.execute("""
            INSERT INTO products (code, name, category, unit, price, tax_rate, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (code, name, category, unit, price, tax_rate, stock))
        res_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return res_id

def delete_product(product_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

# Bill CRUD
def save_bill_record(bill_data: Dict[str, Any], items: List[Dict[str, Any]]) -> int:
    """Save a bill and its items atomically with inventory stock deduction."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bills (
                bill_number, customer_name, customer_phone, customer_address,
                bill_date, subtotal, discount_amount, tax_amount, round_off,
                grand_total, payment_mode, notes
            ) VALUES (
                :bill_number, :customer_name, :customer_phone, :customer_address,
                :bill_date, :subtotal, :discount_amount, :tax_amount, :round_off,
                :grand_total, :payment_mode, :notes
            )
        """, bill_data)
        bill_id = cursor.lastrowid

        for item in items:
            cursor.execute("""
                INSERT INTO bill_items (
                    bill_id, product_id, item_name, quantity, unit_price,
                    discount_percent, tax_percent, total_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_id,
                item.get("product_id"),
                item["item_name"],
                item["quantity"],
                item["unit_price"],
                item.get("discount_percent", 0.0),
                item.get("tax_percent", 0.0),
                item["total_price"]
            ))

            # Deduct stock if linked to product
            if item.get("product_id"):
                cursor.execute("""
                    UPDATE products 
                    SET stock = MAX(0, stock - ?) 
                    WHERE id = ?
                """, (item["quantity"], item["product_id"]))

        conn.commit()
        return bill_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_bills(search: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    if search:
        query = "%" + search.strip() + "%"
        rows = conn.execute("""
            SELECT b.*, COUNT(bi.id) AS item_count
            FROM bills b
            LEFT JOIN bill_items bi ON b.id = bi.bill_id
            WHERE b.bill_number LIKE ? OR b.customer_name LIKE ? OR b.customer_phone LIKE ?
            GROUP BY b.id
            ORDER BY b.id DESC
        """, (query, query, query)).fetchall()
    else:
        rows = conn.execute("""
            SELECT b.*, COUNT(bi.id) AS item_count
            FROM bills b
            LEFT JOIN bill_items bi ON b.id = bi.bill_id
            GROUP BY b.id
            ORDER BY b.id DESC
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_bill_by_id(bill_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM bills WHERE id = ?", (bill_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_bill_items(bill_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id ASC", (bill_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_bill(bill_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()

def get_dashboard_stats() -> Dict[str, Any]:
    """Calculate summary statistics for dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total revenue and bill count
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(grand_total), 0) FROM bills")
    total_bills, total_revenue = cursor.fetchone()

    # Today's sales
    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(grand_total), 0) 
        FROM bills 
        WHERE bill_date = date('now', 'localtime')
    """)
    today_bills, today_revenue = cursor.fetchone()

    # Total products and low stock count (< 5)
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN stock <= 5 THEN 1 ELSE 0 END) FROM products")
    total_prods, low_stock = cursor.fetchone()

    conn.close()
    return {
        "total_bills": total_bills or 0,
        "total_revenue": total_revenue or 0.0,
        "today_bills": today_bills or 0,
        "today_revenue": today_revenue or 0.0,
        "total_products": total_prods or 0,
        "low_stock_products": low_stock or 0
    }
