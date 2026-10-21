import uuid
import hashlib
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from datetime import datetime

# 1. Dummy Data for Local Testing
name = "Tushar"
course = "Cloud Computing 101"
cert_id = str(uuid.uuid4())
date_issued = datetime.now().strftime("%Y-%m-%d")

# Fake URL for the QR code (this will be your API Gateway URL in production)
verify_url = f"https://example.com/verify?id={cert_id}"

print(f"Generating certificate for {name}...")

# 2. Generate the QR Code
qr = qrcode.QRCode(version=1, box_size=5, border=2)
qr.add_data(verify_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")

qr_io = BytesIO()
img.save(qr_io, format="PNG")
qr_io.seek(0)

# 3. Draw the PDF (Aligned to Canva Template)
pdf_io = BytesIO()
width, height = landscape(letter)
c = canvas.Canvas(pdf_io, pagesize=(width, height))

try:
    c.drawImage("template.jpg", 0, 0, width=width, height=height)
except Exception:
    print("Warning: template.jpg not found. Drawing on a blank page.")

# Draw the Dynamic Name (Moved UP by 40 points)
c.setFillColor(HexColor("#C19A6B")) 
c.setFont("Helvetica-Bold", 42)
c.drawCentredString(width / 2.0, height / 2.0 + 20, name)

# Draw the Dynamic Course Paragraph (Moved UP to clear the signature)
c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica", 16)
c.drawCentredString(width / 2.0, height / 2.0 - 50, "In recognition of successful completion of the course:")

c.setFont("Helvetica-Bold", 20)
c.drawCentredString(width / 2.0, height / 2.0 - 80, course)

# Draw Date and Certificate ID (Moved down slightly, font reduced, ID truncated)
c.setFont("Helvetica", 10)
c.setFillColor(HexColor("#777777"))
c.drawCentredString(width / 2.0, 30, f"Issued: {date_issued}  |  Verification ID: {cert_id[:12]}")

# Paste QR Code in the bottom left corner
qr_img = ImageReader(qr_io)
c.drawImage(qr_img, 50, 40, width=80, height=80)

c.save()

pdf_bytes = pdf_io.getvalue()

# 4. Hash the PDF for tamper-proofing
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

# 5. Save directly to your local folder
file_name = "test_certificate.pdf"
with open(file_name, "wb") as f:
    f.write(pdf_bytes)

print(f"\nSuccess! Saved locally as: {file_name}")
print(f"Tamper-proof SHA-256 Hash: {pdf_hash}")