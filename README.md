# RetailBill - Windows Desktop Billing & Invoicing Application

**RetailBill** is a standalone, offline Windows desktop billing and Point-of-Sale (POS) application engineered with Python, Tkinter, SQLite, ReportLab, and Pillow, packaged using PyInstaller, and distributed with Inno Setup.

---

## 🌟 Key Features

1. **Standalone Windows Desktop Application**:
   - Zero dependencies required on client machines — Python is **not required**.
   - Built with `--windowed` / `--noconsole` mode: runs as a clean GUI application with no flashing command prompts or terminal windows.
   - Built-in Windows High-DPI screen awareness for sharp typography and scaling.

2. **100% Offline SQLite Database**:
   - Zero network connection or database server configuration required.
   - User database is stored in `%APPDATA%\RetailBill\retailbill.db`.
   - Never fails due to `C:\Program Files` write permission limitations.

3. **Editable Bill Numbers**:
   - Supports automated sequential bill generation (`INV-1001`, `INV-1002`, etc.) with customizable prefixes.
   - Retailers can manually edit, override, or customize any bill number directly on the billing screen with instant duplicate validation.

4. **Dynamic UPI QR Code Generation**:
   - Live on-screen UPI QR code generator for Indian Retail Payments (Google Pay, PhonePe, Paytm, BHIM, Cred).
   - Dynamically encodes exact bill amount, invoice number, and merchant UPI ID.
   - Automatically prints onto the generated Tax Invoice PDF.

5. **Authorized Signature & Shop Seal**:
   - Shop owners can browse and upload their official signature image and circular rubber stamp / seal.
   - Preserved permanently in `%APPDATA%\RetailBill\custom_assets`.
   - Elegantly embedded into the footer of every generated PDF invoice.

6. **Complete POS & Inventory Management**:
   - Point-of-Sale interface with fast item addition, discount %, tax %, and round-off calculation.
   - Automatic inventory stock deduction upon saving bills.
   - Product catalog with categories, SKU codes, tax rates, and low-stock alerts.
   - Invoices & Bill History browser with live sales metrics (Today's Sales, Total Revenue, Bill Count), reprint PDF, and search filters.

---

## 📁 Project Structure

```
RetailBill/
├── assets/                          # Application icons and default assets
│   ├── icon.ico                     # Multi-resolution Windows app icon
│   ├── icon.png                     # High-res icon
│   ├── sample_signature.png         # Default authorized signature template
│   └── sample_seal.png              # Default verified store stamp template
├── src/
│   ├── __init__.py
│   ├── database.py                  # SQLite schema, queries, migrations, seed data
│   ├── qr_generator.py              # Dynamic UPI QR generator (Pillow + qrcode)
│   ├── pdf_generator.py             # Professional ReportLab PDF invoice builder
│   ├── utils.py                     # Resource resolver, AppData directories, currency
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py           # High-DPI root window, header, tabs & status bar
│       ├── pos_tab.py               # POS billing screen with live UPI QR
│       ├── history_tab.py           # Invoices history, KPI dashboard & PDF reprint
│       ├── inventory_tab.py         # Product catalog management
│       └── settings_tab.py          # Shop profile, UPI & asset uploaders
├── main.py                          # Application entry point
├── generate_assets.py               # Asset generator script
├── test_retailbill.py               # Automated test suite
├── RetailBill.spec                  # PyInstaller build specification
├── setup.iss                        # Inno Setup installation compiler script
├── build_all.py                     # One-click master build pipeline
├── dist/RetailBill/RetailBill.exe   # Standalone executable
└── dist-installer/RetailBill-Setup.exe # Windows Installer (Inno Setup)
```

---

## 🚀 Generated Artifacts

| Artifact | File Path | Description |
| :--- | :--- | :--- |
| **Standalone Executable** | `dist\RetailBill\RetailBill.exe` | Standalone Windows application (no console, self-contained). |
| **Setup Installer** | `dist-installer\RetailBill-Setup.exe` | Inno Setup Windows installer with Start Menu & Desktop shortcuts. |

---

## 🛠️ Building From Source

To rebuild the executable and installer from source:

```powershell
# Navigate to the project directory
cd "C:\Users\ziaud\.gemini\antigravity\scratch\RetailBill"

# Run the automated build script
python build_all.py
```

### Manual Steps:

1. **Build Executable with PyInstaller**:
   ```powershell
   python -m PyInstaller --noconfirm --onedir --windowed --name "RetailBill" --icon "assets/icon.ico" --add-data "assets;assets" main.py
   ```

2. **Compile Installer with Inno Setup**:
   ```powershell
   & "$env:LOCALAPPDATA\Programs\Inno Setup 7\ISCC.exe" setup.iss
   ```

---

## 🧪 Testing & Verification

Run the automated test suite to verify database integrity, inventory stock deduction, dynamic QR generation, PDF invoice generation, and GUI rendering:

```powershell
python test_retailbill.py
```
