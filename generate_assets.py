import os
from PIL import Image, ImageDraw, ImageFont

def generate_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Generate App Icon (256x256)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background with modern indigo/blue gradient
    for y in range(size):
        r = int(30 + (10 - 30) * (y / size))
        g = int(64 + (100 - 64) * (y / size))
        b = int(175 + (220 - 175) * (y / size))
        draw.line([(24, y), (size - 25, y)], fill=(r, g, b, 255))

    # Mask to rounded corner rectangle
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([16, 16, size - 16, size - 16], radius=48, fill=255)
    
    final_icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    final_icon.paste(img, (0, 0), mask=mask)
    icon_draw = ImageDraw.Draw(final_icon)

    # Inner border
    icon_draw.rounded_rectangle([18, 18, size - 18, size - 18], radius=46, outline=(255, 255, 255, 70), width=3)

    # Draw a stylized Receipt / Bill icon
    # Receipt paper shape
    rx1, ry1, rx2, ry2 = 64, 50, 192, 206
    icon_draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=16, fill=(255, 255, 255, 250), outline=(220, 225, 235, 255), width=3)

    # Receipt header bar
    icon_draw.rounded_rectangle([rx1 + 10, ry1 + 12, rx2 - 10, ry1 + 36], radius=6, fill=(16, 185, 129, 255))
    
    # Receipt lines (simulating items)
    line_color = (140, 150, 170, 255)
    accent_color = (37, 99, 235, 255)
    
    # Line 1
    icon_draw.rounded_rectangle([rx1 + 14, ry1 + 50, rx1 + 80, ry1 + 58], radius=3, fill=line_color)
    icon_draw.rounded_rectangle([rx2 - 50, ry1 + 50, rx2 - 14, ry1 + 58], radius=3, fill=accent_color)

    # Line 2
    icon_draw.rounded_rectangle([rx1 + 14, ry1 + 70, rx1 + 95, ry1 + 78], radius=3, fill=line_color)
    icon_draw.rounded_rectangle([rx2 - 40, ry1 + 70, rx2 - 14, ry1 + 78], radius=3, fill=accent_color)

    # Line 3
    icon_draw.rounded_rectangle([rx1 + 14, ry1 + 90, rx1 + 70, ry1 + 98], radius=3, fill=line_color)
    icon_draw.rounded_rectangle([rx2 - 45, ry1 + 90, rx2 - 14, ry1 + 98], radius=3, fill=accent_color)

    # Separator dash line
    for x in range(rx1 + 14, rx2 - 14, 10):
        icon_draw.line([(x, ry1 + 112), (x + 5, ry1 + 112)], fill=(180, 190, 205, 255), width=2)

    # Total bold line
    icon_draw.rounded_rectangle([rx1 + 14, ry1 + 126, rx1 + 60, ry1 + 138], radius=4, fill=(30, 41, 59, 255))
    icon_draw.rounded_rectangle([rx2 - 60, ry1 + 126, rx2 - 14, ry1 + 138], radius=4, fill=(16, 185, 129, 255))

    # Small QR code mockup at the bottom of the bill
    qr_x, qr_y, qr_s = rx1 + 14, ry1 + 150, 40
    icon_draw.rectangle([qr_x, qr_y, qr_x + qr_s, qr_y + qr_s], fill=(240, 245, 250, 255), outline=(100, 116, 139, 255), width=2)
    icon_draw.rectangle([qr_x + 4, qr_y + 4, qr_x + 14, qr_y + 14], fill=(30, 41, 59, 255))
    icon_draw.rectangle([qr_x + qr_s - 14, qr_y + 4, qr_x + qr_s - 4, qr_y + 14], fill=(30, 41, 59, 255))
    icon_draw.rectangle([qr_x + 4, qr_y + qr_s - 14, qr_x + 14, qr_y + qr_s - 4], fill=(30, 41, 59, 255))
    icon_draw.rectangle([qr_x + 20, qr_y + 20, qr_x + 26, qr_y + 26], fill=(30, 41, 59, 255))

    # Checkmark badge
    badge_x, badge_y = 195, 195
    icon_draw.ellipse([badge_x - 32, badge_y - 32, badge_x + 32, badge_y + 32], fill=(16, 185, 129, 255), outline=(255, 255, 255, 255), width=4)
    # Checkmark lines
    icon_draw.line([(badge_x - 14, badge_y), (badge_x - 4, badge_y + 11)], fill=(255, 255, 255, 255), width=5)
    icon_draw.line([(badge_x - 4, badge_y + 11), (badge_x + 14, badge_y - 11)], fill=(255, 255, 255, 255), width=5)

    png_path = os.path.join(assets_dir, "icon.png")
    ico_path = os.path.join(assets_dir, "icon.ico")
    final_icon.save(png_path, format="PNG")
    final_icon.save(ico_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Saved {png_path} and {ico_path}")

    # 2. Generate Sample Authorized Signature
    sig_img = Image.new("RGBA", (300, 100), (255, 255, 255, 0))
    sig_draw = ImageDraw.Draw(sig_img)
    # Elegant cursive stroke
    points = [
        (25, 65), (45, 30), (60, 75), (80, 20), (105, 70),
        (130, 45), (150, 60), (170, 35), (200, 55), (230, 40),
        (250, 50), (275, 45)
    ]
    # Draw smooth curve
    for i in range(len(points) - 1):
        sig_draw.line([points[i], points[i+1]], fill=(15, 23, 42, 240), width=3)
    # Add a flourish flourish underline
    sig_draw.arc([40, 60, 260, 95], start=180, end=360, fill=(15, 23, 42, 220), width=2)
    sig_draw.line([(150, 85), (280, 60)], fill=(15, 23, 42, 220), width=2)
    sig_path = os.path.join(assets_dir, "sample_signature.png")
    sig_img.save(sig_path, format="PNG")
    print(f"Saved {sig_path}")

    # 3. Generate Sample Seal Stamp
    seal_size = 200
    seal_img = Image.new("RGBA", (seal_size, seal_size), (255, 255, 255, 0))
    seal_draw = ImageDraw.Draw(seal_img)
    # Double circle
    seal_color = (194, 65, 12, 220) # Deep rust/stamp orange-red
    seal_draw.ellipse([10, 10, seal_size - 10, seal_size - 10], outline=seal_color, width=4)
    seal_draw.ellipse([20, 20, seal_size - 20, seal_size - 20], outline=seal_color, width=2)
    # Inner star / badge & text representation
    seal_draw.ellipse([60, 60, seal_size - 60, seal_size - 60], outline=seal_color, width=2)
    # Horizontal text bars
    seal_draw.rectangle([35, 88, seal_size - 35, 112], fill=seal_color)
    seal_draw.line([(30, 70), (seal_size - 30, 70)], fill=seal_color, width=2)
    seal_draw.line([(30, 130), (seal_size - 30, 130)], fill=seal_color, width=2)
    # Star dots
    for angle in [0, 90, 180, 270]:
        pass
    seal_path = os.path.join(assets_dir, "sample_seal.png")
    seal_img.save(seal_path, format="PNG")
    print(f"Saved {seal_path}")

if __name__ == "__main__":
    generate_assets()
