import io
import urllib.parse
from typing import Optional
from PIL import Image, ImageTk
import qrcode

def build_upi_uri(upi_id: str, payee_name: str, amount: float, bill_number: str = "") -> str:
    """
    Build standard NPCI UPI payment URL.
    Format: upi://pay?pa=...&pn=...&am=...&cu=INR&tn=...
    """
    clean_upi = upi_id.strip()
    if not clean_upi:
        return ""
    
    clean_name = payee_name.strip() or "Merchant"
    note = f"Bill {bill_number}" if bill_number else "RetailBill Payment"
    
    params = {
        "pa": clean_upi,
        "pn": clean_name,
        "am": f"{amount:.2f}",
        "cu": "INR",
        "tn": note
    }
    query_string = urllib.parse.urlencode(params)
    return f"upi://pay?{query_string}"

def generate_upi_qr_image(upi_id: str, payee_name: str, amount: float, bill_number: str = "", size: int = 180) -> Optional[Image.Image]:
    """
    Generate PIL Image of UPI QR code.
    """
    uri = build_upi_uri(upi_id, payee_name, amount, bill_number)
    if not uri:
        return None
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert("RGBA")
    if size:
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def get_upi_qr_tk_photo(upi_id: str, payee_name: str, amount: float, bill_number: str = "", size: int = 180) -> Optional[ImageTk.PhotoImage]:
    """
    Generate Tk PhotoImage directly for embedding in Tkinter UI.
    """
    pil_img = generate_upi_qr_image(upi_id, payee_name, amount, bill_number, size)
    if pil_img:
        return ImageTk.PhotoImage(pil_img)
    return None

def save_qr_temp_file(upi_id: str, payee_name: str, amount: float, bill_number: str, out_path: str, size: int = 200) -> bool:
    """Save QR code image to specified path for PDF inclusion."""
    pil_img = generate_upi_qr_image(upi_id, payee_name, amount, bill_number, size)
    if pil_img:
        pil_img.save(out_path, format="PNG")
        return True
    return False
