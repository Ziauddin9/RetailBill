import os
import tempfile
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from src.utils import get_invoices_dir, format_currency
from src.qr_generator import save_qr_temp_file

def generate_invoice_pdf(bill: Dict[str, Any], items: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
    """
    Generate professional invoice PDF with shop seal, authorized signature, and UPI QR code.
    Returns the file path of generated PDF.
    """
    invoices_dir = get_invoices_dir()
    safe_bill_no = bill["bill_number"].replace("/", "_").replace("\\", "_")
    pdf_filename = f"Invoice_{safe_bill_no}.pdf"
    pdf_path = os.path.join(invoices_dir, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ShopTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A")
    )
    subtitle_style = ParagraphStyle(
        "ShopSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569")
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#334155")
    )
    inv_title_style = ParagraphStyle(
        "InvTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#0F172A")
    )
    inv_meta_style = ParagraphStyle(
        "InvMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#1E293B")
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E40AF")
    )
    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    cell_style_bold = ParagraphStyle(
        "CellTextBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    cell_right = ParagraphStyle(
        "CellRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#0F172A")
    )
    cell_right_bold = ParagraphStyle(
        "CellRightBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#0F172A")
    )
    terms_style = ParagraphStyle(
        "TermsStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B")
    )

    story = []

    # 1. Header Section
    shop_info = [
        Paragraph(settings.get("shop_name", "RetailBill Superstore"), title_style),
        Paragraph(settings.get("shop_tagline", ""), subtitle_style),
        Spacer(1, 4),
        Paragraph(settings.get("address", ""), meta_style),
        Paragraph(f"Phone: {settings.get('phone', '')} | Email: {settings.get('email', '')}", meta_style),
        Paragraph(f"<b>GSTIN / Tax ID:</b> {settings.get('gstin', 'N/A')}", meta_style),
    ]

    inv_info = [
        Paragraph("TAX INVOICE", inv_title_style),
        Spacer(1, 4),
        Paragraph(f"<b>Invoice No:</b> {bill.get('bill_number', '')}", inv_meta_style),
        Paragraph(f"<b>Date:</b> {bill.get('bill_date', '')}", inv_meta_style),
        Paragraph(f"<b>Payment Mode:</b> {bill.get('payment_mode', 'Cash')}", inv_meta_style),
    ]

    header_table = Table([[shop_info, inv_info]], colWidths=[330, 190])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Decorative divider
    divider = Table([[""]], colWidths=[520], rowHeights=[2])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#2563EB")),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))

    # 2. Customer Section (Bill To)
    cust_content = [
        Paragraph("BILL TO (CUSTOMER DETAILS)", section_heading),
        Spacer(1, 3),
        Paragraph(f"<b>Name:</b> {bill.get('customer_name', 'Walk-in Customer')}", meta_style),
        Paragraph(f"<b>Phone:</b> {bill.get('customer_phone') or 'N/A'}", meta_style),
        Paragraph(f"<b>Address:</b> {bill.get('customer_address') or 'N/A'}", meta_style),
    ]
    cust_table = Table([[cust_content]], colWidths=[520])
    cust_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 10))

    # 3. Items Table
    curr_sym = settings.get("currency_symbol", "₹")
    headers = [
        Paragraph("<b>#</b>", cell_style_bold),
        Paragraph("<b>Item Description</b>", cell_style_bold),
        Paragraph("<b>Qty</b>", cell_right_bold),
        Paragraph(f"<b>Rate ({curr_sym})</b>", cell_right_bold),
        Paragraph("<b>Disc %</b>", cell_right_bold),
        Paragraph("<b>GST %</b>", cell_right_bold),
        Paragraph(f"<b>Total ({curr_sym})</b>", cell_right_bold)
    ]
    table_data = [headers]

    for idx, item in enumerate(items, 1):
        row = [
            Paragraph(str(idx), cell_style),
            Paragraph(str(item.get("item_name", "")), cell_style),
            Paragraph(f"{item.get('quantity', 1):g}", cell_right),
            Paragraph(f"{item.get('unit_price', 0.0):.2f}", cell_right),
            Paragraph(f"{item.get('discount_percent', 0.0):g}%", cell_right),
            Paragraph(f"{item.get('tax_percent', 0.0):g}%", cell_right),
            Paragraph(f"{item.get('total_price', 0.0):.2f}", cell_right_bold),
        ]
        table_data.append(row)

    col_widths = [24, 216, 40, 60, 50, 50, 80]
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEF2F6")),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]
    # Alternating row colors
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor("#F8FAFC")))
        t_style.append(('TOPPADDING', (0, r), (-1, r), 4))
        t_style.append(('BOTTOMPADDING', (0, r), (-1, r), 4))

    items_table.setStyle(TableStyle(t_style))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # 4. Calculation Summary Table & UPI QR Section
    # Left side: UPI QR Code
    qr_cell_content = []
    upi_id = settings.get("upi_id", "").strip()
    temp_qr_path = None
    if upi_id:
        try:
            temp_qr = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_qr_path = temp_qr.name
            temp_qr.close()
            save_qr_temp_file(
                upi_id=upi_id,
                payee_name=settings.get("upi_name", settings.get("shop_name", "Store")),
                amount=float(bill.get("grand_total", 0.0)),
                bill_number=str(bill.get("bill_number", "")),
                out_path=temp_qr_path,
                size=120
            )
            qr_cell_content.append(Paragraph("<b>Scan & Pay via UPI</b>", section_heading))
            qr_cell_content.append(Spacer(1, 2))
            qr_cell_content.append(ReportLabImage(temp_qr_path, width=80, height=80))
            qr_cell_content.append(Spacer(1, 2))
            qr_cell_content.append(Paragraph(f"UPI ID: <b>{upi_id}</b>", meta_style))
            qr_cell_content.append(Paragraph("Supports GPay, PhonePe, Paytm, BHIM", terms_style))
        except Exception as e:
            qr_cell_content.append(Paragraph(f"UPI: {upi_id}", meta_style))
    else:
        qr_cell_content.append(Paragraph("Thank you for shopping with us!", meta_style))

    # Right side: Totals breakdown
    subtotal = bill.get("subtotal", 0.0)
    discount = bill.get("discount_amount", 0.0)
    tax_amt = bill.get("tax_amount", 0.0)
    round_off = bill.get("round_off", 0.0)
    grand_total = bill.get("grand_total", 0.0)

    summary_rows = [
        [Paragraph("Subtotal:", meta_style), Paragraph(f"{curr_sym} {subtotal:,.2f}", cell_right)],
    ]
    if discount > 0:
        summary_rows.append([Paragraph("Total Discount:", meta_style), Paragraph(f"- {curr_sym} {discount:,.2f}", cell_right)])
    if tax_amt > 0:
        summary_rows.append([Paragraph("CGST / SGST (Taxes):", meta_style), Paragraph(f"+ {curr_sym} {tax_amt:,.2f}", cell_right)])
    if round_off != 0:
        summary_rows.append([Paragraph("Round Off:", meta_style), Paragraph(f"{round_off:+,.2f}", cell_right)])
    
    grand_total_style = ParagraphStyle(
        "GrandTotalStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#1E3A8A")
    )
    grand_label_style = ParagraphStyle(
        "GrandLabelStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E3A8A")
    )
    summary_rows.append([
        Paragraph("Grand Total:", grand_label_style),
        Paragraph(f"{curr_sym} {grand_total:,.2f}", grand_total_style)
    ])

    summary_subtable = Table(summary_rows, colWidths=[130, 110])
    summary_subtable.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, -2), (-1, -2), 0.5, colors.HexColor("#CBD5E1")),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#EFF6FF")),
    ]))

    calc_section = Table([[qr_cell_content, summary_subtable]], colWidths=[260, 260])
    calc_section.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
    ]))
    story.append(calc_section)
    story.append(Spacer(1, 14))

    # 5. Terms & Conditions and Authorized Signatory / Seal block
    terms_text = settings.get("terms", "Thank you for your business!").replace("\n", "<br/>")
    terms_block = [
        Paragraph("<b>Terms & Conditions:</b>", section_heading),
        Spacer(1, 2),
        Paragraph(terms_text, terms_style)
    ]

    # Signature and Seal graphics
    sig_path = settings.get("signature_path", "")
    seal_path = settings.get("seal_path", "")

    sign_elements = []
    stamp_seal_elements = []

    if seal_path and os.path.exists(seal_path):
        try:
            stamp_seal_elements.append(ReportLabImage(seal_path, width=54, height=54))
        except Exception:
            pass

    if sig_path and os.path.exists(sig_path):
        try:
            sign_elements.append(ReportLabImage(sig_path, width=90, height=36))
        except Exception:
            pass

    # Signature block table
    sig_subtable_content = []
    seal_row = []
    if stamp_seal_elements:
        seal_row.append(stamp_seal_elements[0])
    else:
        seal_row.append("")

    if sign_elements:
        seal_row.append(sign_elements[0])
    else:
        seal_row.append("")

    sig_table = Table(
        [
            seal_row,
            [
                Paragraph("<font size=7 color='#64748B'>Official Stamp</font>", ParagraphStyle('SealLbl', alignment=TA_CENTER)),
                Paragraph(f"<b>For {settings.get('shop_name', 'Store')}</b><br/><font size=7 color='#64748B'>Authorized Signatory</font>", ParagraphStyle('SigLbl', alignment=TA_CENTER))
            ]
        ],
        colWidths=[70, 140]
    )
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LINEABOVE', (1, 1), (1, 1), 0.5, colors.HexColor("#0F172A")),
    ]))

    footer_table = Table([[terms_block, sig_table]], colWidths=[290, 230])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(KeepTogether(footer_table))

    # Build PDF document
    doc.build(story)

    # Clean up temporary QR image file
    if temp_qr_path and os.path.exists(temp_qr_path):
        try:
            os.remove(temp_qr_path)
        except Exception:
            pass

    return pdf_path
