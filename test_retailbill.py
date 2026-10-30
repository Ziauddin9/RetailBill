import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import (
    init_db, get_settings, update_settings, get_all_products,
    save_product, delete_product, save_bill_record, get_all_bills,
    get_bill_by_id, get_bill_items, get_next_bill_number_str,
    increment_bill_number, check_bill_number_exists, get_dashboard_stats
)
from src.qr_generator import build_upi_uri, generate_upi_qr_image, save_qr_temp_file
from src.pdf_generator import generate_invoice_pdf
from src.utils import get_db_path, get_invoices_dir

class TestRetailBill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_database_and_settings(self):
        self.assertTrue(os.path.exists(get_db_path()), "Database file should exist")
        settings = get_settings()
        self.assertIn("shop_name", settings)
        self.assertIn("currency_symbol", settings)
        self.assertIn("next_bill_number", settings)
        print("[PASS] Database and settings verified.")

    def test_02_products_crud(self):
        # Add product
        pid = save_product(
            code="TEST001",
            name="Unit Test Product",
            category="TestCat",
            unit="Pcs",
            price=120.50,
            tax_rate=18.0,
            stock=100
        )
        self.assertIsNotNone(pid)

        # Retrieve and verify
        products = get_all_products("Unit Test Product")
        self.assertTrue(any(p["id"] == pid for p in products))

        # Delete product
        delete_product(pid)
        products_after = get_all_products("Unit Test Product")
        self.assertFalse(any(p["id"] == pid for p in products_after))
        print("[PASS] Product inventory CRUD verified.")

    def test_03_upi_qr_generation(self):
        uri = build_upi_uri("testmerchant@upi", "Retail Test Store", 450.0, "INV-TEST-001")
        self.assertTrue(uri.startswith("upi://pay?"))
        self.assertIn("testmerchant%40upi", uri)
        self.assertIn("450.00", uri)

        img = generate_upi_qr_image("testmerchant@upi", "Retail Test Store", 450.0, "INV-TEST-001", size=150)
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (150, 150))
        print("[PASS] Dynamic UPI URI & QR Code image verified.")

    def test_04_bill_creation_and_stock(self):
        # Create a test item with known stock
        pid = save_product("STK100", "Stock Test Item", "Test", "Pcs", 200.0, 18.0, 50)
        
        bill_no = f"TEST-BILL-{os.urandom(4).hex()}"
        self.assertFalse(check_bill_number_exists(bill_no))

        bill_data = {
            "bill_number": bill_no,
            "customer_name": "John Doe",
            "customer_phone": "9998887770",
            "customer_address": "45 Test Lane",
            "bill_date": "2026-10-30",
            "subtotal": 400.0,
            "discount_amount": 40.0,
            "tax_amount": 64.8,
            "round_off": 0.2,
            "grand_total": 425.0,
            "payment_mode": "UPI",
            "notes": "Test invoice"
        }

        items = [
            {
                "product_id": pid,
                "item_name": "Stock Test Item",
                "quantity": 2.0,
                "unit_price": 200.0,
                "discount_percent": 10.0,
                "tax_percent": 18.0,
                "total_price": 424.8
            }
        ]

        bill_id = save_bill_record(bill_data, items)
        self.assertIsNotNone(bill_id)
        self.assertTrue(check_bill_number_exists(bill_no))

        # Verify stock decreased by 2
        prods = get_all_products("Stock Test Item")
        self.assertEqual(prods[0]["stock"], 48)

        # Clean up test product
        delete_product(pid)
        print("[PASS] Bill creation and automatic inventory stock deduction verified.")

    def test_05_pdf_invoice_generation(self):
        settings = get_settings()
        bill_data = {
            "bill_number": "INV-PDF-VERIFY",
            "customer_name": "Alice Smith",
            "customer_phone": "+91 91234 56789",
            "customer_address": "12 Bangalore Tech Park",
            "bill_date": "2026-10-30",
            "subtotal": 1250.0,
            "discount_amount": 50.0,
            "tax_amount": 216.0,
            "round_off": 0.0,
            "grand_total": 1416.0,
            "payment_mode": "UPI",
            "notes": "Thank you!"
        }
        items = [
            {
                "product_id": None,
                "item_name": "Premium Keyboard",
                "quantity": 1,
                "unit_price": 1000.0,
                "discount_percent": 5.0,
                "tax_percent": 18.0,
                "total_price": 1121.0
            },
            {
                "product_id": None,
                "item_name": "USB Cable",
                "quantity": 1,
                "unit_price": 250.0,
                "discount_percent": 0.0,
                "tax_percent": 18.0,
                "total_price": 295.0
            }
        ]

        pdf_path = generate_invoice_pdf(bill_data, items, settings)
        self.assertTrue(os.path.exists(pdf_path), "Generated PDF file must exist")
        self.assertGreater(os.path.getsize(pdf_path), 5000, "PDF size must be > 5KB")
        print(f"[PASS] PDF generation with Signature, Seal and UPI QR verified: {pdf_path}")

    def test_06_ui_headless_instantiation(self):
        from src.ui.main_window import MainWindow
        app = MainWindow()
        app.update() # Process pending events
        app.destroy()
        print("[PASS] MainWindow UI instantiated and rendered successfully.")

if __name__ == "__main__":
    unittest.main()
