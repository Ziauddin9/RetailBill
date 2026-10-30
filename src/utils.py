import os
import sys

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.normpath(os.path.join(base_path, relative_path))

def get_app_data_dir() -> str:
    """Get persistent directory in user's AppData for database and custom user assets."""
    app_data = os.environ.get("APPDATA")
    if not app_data:
        app_data = os.path.expanduser("~")
    data_dir = os.path.join(app_data, "RetailBill")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_db_path() -> str:
    """Get path to SQLite database."""
    return os.path.join(get_app_data_dir(), "retailbill.db")

def get_custom_assets_dir() -> str:
    """Directory for storing user-uploaded signatures and shop seals."""
    assets_dir = os.path.join(get_app_data_dir(), "custom_assets")
    os.makedirs(assets_dir, exist_ok=True)
    return assets_dir

def get_invoices_dir() -> str:
    """Directory for generated PDF invoices in user's Documents or AppData."""
    docs = os.path.join(os.path.expanduser("~"), "Documents", "RetailBill Invoices")
    try:
        os.makedirs(docs, exist_ok=True)
        return docs
    except Exception:
        fallback = os.path.join(get_app_data_dir(), "invoices")
        os.makedirs(fallback, exist_ok=True)
        return fallback

def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format floating point currency."""
    try:
        val = float(amount)
        return f"{symbol} {val:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0.00"
