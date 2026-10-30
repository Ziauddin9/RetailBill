# RetailBill – Retail Billing & Inventory Management System

A modern, offline-first Windows desktop application for retail billing, invoice generation, inventory management, and sales tracking.

RetailBill is designed to simplify everyday retail operations with an easy-to-use interface, automated calculations, PDF invoice generation, and local database storage.

## ✨ Features

### 🧾 Point of Sale (POS)
- Create and manage customer bills.
- Add products with quantities and pricing.
- Automatic subtotal and total calculations.
- GST calculation and discount support.
- Editable invoice numbers.
- Automatic round-off calculation.
- UPI QR code generation for digital payments.
- Generate and print PDF invoices.

### 📦 Inventory Management
- Add, edit, and manage products.
- Maintain product names and SKU codes.
- Manage selling prices and GST rates.
- Track available stock quantities.
- Low-stock alerts.
- Automatic stock deduction after billing.

### 📋 Invoice History
- View previously generated invoices.
- Search and manage billing records.
- Track daily sales.
- Monitor overall revenue.
- Reprint previously generated invoices.

### ⚙️ Shop Settings
- Configure shop name and address.
- Add GSTIN and contact information.
- Configure UPI payment details.
- Customize invoice information.
- Add shop signature and seal/stamp.

### 📄 PDF Invoice Generation
- Professionally formatted invoices.
- Automatic invoice calculations.
- Shop and customer details.
- GST and discount breakdown.
- Signature and seal sections.
- PDF export and printing.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Tkinter | Desktop graphical interface |
| SQLite | Local database |
| ReportLab | PDF invoice generation |
| PyInstaller | Windows executable packaging |
| QR Code | UPI payment QR generation |

## 💻 System Requirements

- Operating System: Windows 10 / Windows 11
- Python 3.10 or later (for source execution)
- RAM: 4 GB minimum recommended
- Storage: 200 MB or more, depending on installation and data
- Internet: Not required for normal offline billing operations

## 📁 Project Structure

```text
RetailBill/
│
├── src/
│   ├── main.py
│   ├── database.py
│   ├── pos_tab.py
│   ├── inventory_tab.py
│   ├── history_tab.py
│   ├── settings_tab.py
│   ├── pdf_generator.py
│   ├── qr_generator.py
│   └── utils.py
│
├── dist/
│   └── RetailBill/
│       └── RetailBill.exe
│
├── dist-installer/
│   └── RetailBill-Setup.exe
│
├── test_retailbill.py
├── requirements.txt
└── README.md
```

*The structure above describes the main application components; additional configuration and asset files may also be present.*

## 🚀 Installation

### Option 1: Windows Installer (Recommended)

1. Download `RetailBill-Setup.exe` from the Releases section.
2. Run the installer.
3. Follow the installation instructions.
4. Launch RetailBill from the desktop shortcut or Start Menu.

### Option 2: Standalone Executable

1. Download the packaged RetailBill application.
2. Extract the application folder if distributed as an archive.
3. Run `RetailBill.exe`.

### Option 3: Run from Source Code

Clone the repository:

```bash
git clone https://github.com/Ziauddin9/RetailBill.git
```

Navigate to the project directory:

```bash
cd RetailBill
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python src/main.py
```

## 🏗️ Building the Windows Executable

RetailBill uses PyInstaller to package the Python application into a Windows executable.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build the executable using the project's PyInstaller configuration, if provided.

The generated application can be distributed as a Windows executable or packaged using the installer configuration.

## 🗄️ Database

RetailBill uses SQLite for local data storage.

The database manages:
- Product information.
- Inventory and stock quantities.
- Customer and invoice records.
- Billing information.
- Application settings.

The application is designed to operate locally without requiring a cloud database or external server.

**Important:** Back up your database regularly. Do not upload real customer information, financial records, or private business data to a public repository.

## 🧪 Testing

The project includes a test file:

```bash
python -m pytest test_retailbill.py
```

## 🔒 Privacy & Security

- Local database storage.
- No cloud server required for normal operation.
- Keep business data and customer information private.
- Avoid committing database files containing real business records.
- Back up important application data regularly.

## 🛣️ Future Improvements

Potential improvements include:

- Customer management system.
- Advanced sales analytics and reporting.
- Barcode scanner integration.
- Thermal receipt printer support.
- Excel sales reports.
- Database backup and restore.
- Multi-user support.
- Improved invoice customization.

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

## 📜 License

Choose an appropriate open-source license before distributing this project publicly. Until a license is added, all rights are reserved by the copyright holder.

## 👨‍💻 Developer

**Ziauddin**

Project: RetailBill  
Category: Desktop Application / Retail POS / Billing Software  
Platform: Windows  
Language: Python

---

**RetailBill – Simplifying Retail Billing and Inventory Management.**