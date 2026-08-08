"""
Generates a certificate PDF with an embedded QR code linking to the public
verification endpoint. Requires: reportlab, qrcode[pil].

    pip install reportlab "qrcode[pil]"
"""

import io
import secrets
import string

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import qrcode

from models import Certificate

# --- adjust to your deployment ---
VERIFY_BASE_URL = "https://your-domain.example.com/verify"
CERT_STORAGE_DIR = "/var/app/certificates"  # or push to S3 instead
# ------------------------------------

# MCI Platform palette (lighthouse logo: deep navy + light blue + white)
NAVY = HexColor("#0b1f3a")
SKY_BLUE = HexColor("#4a90d9")
LIGHT_BLUE = HexColor("#a9cdf0")
PARCHMENT = HexColor("#f4f7fb")


def make_verification_code(length: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _qr_image_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_certificate_pdf(db, certificate: Certificate) -> str:
    attempt = certificate.attempt
    level = attempt.level
    subject = level.subject
    institute = subject.institute

    verify_url = f"{VERIFY_BASE_URL}/{certificate.verification_code}"
    qr_bytes = _qr_image_bytes(verify_url)

    out_path = f"{CERT_STORAGE_DIR}/{certificate.id}.pdf"

    c = canvas.Canvas(out_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    # background
    c.setFillColor(PARCHMENT)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # border
    c.setStrokeColor(SKY_BLUE)
    c.setLineWidth(3)
    c.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm, fill=0, stroke=1)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 40 * mm, "MCI PLATFORM")
    c.setFont("Helvetica", 11)
    c.setFillColor(SKY_BLUE)
    c.drawCentredString(width / 2, height - 47 * mm, "MARITIME COMPETENCY INDEX")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 65 * mm, "Certificate of Achievement")

    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 85 * mm, "This certifies that")

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(SKY_BLUE)
    c.drawCentredString(width / 2, height - 100 * mm, attempt.trainee_name)

    c.setFillColor(NAVY)
    c.setFont("Helvetica", 15)
    c.drawCentredString(
        width / 2,
        height - 115 * mm,
        f"has successfully completed {subject.name_en} — {level.difficulty.value.title()} Level",
    )
    c.drawCentredString(
        width / 2, height - 125 * mm, f"Score: {attempt.pct}%  |  ID/Passport: {attempt.trainee_id_number}"
    )
    c.drawCentredString(
        width / 2, height - 135 * mm, f"Date: {attempt.submitted_at.strftime('%d %B %Y')}"
    )
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(LIGHT_BLUE)
    c.drawCentredString(width / 2, height - 145 * mm, f"Issued by {institute.name_en}")

    # QR code, bottom-right
    qr_image = ImageReader(io.BytesIO(qr_bytes))
    c.drawImage(qr_image, width - 55 * mm, 20 * mm, width=30 * mm, height=30 * mm)
    c.setFont("Helvetica", 8)
    c.setFillColor(NAVY)
    c.drawCentredString(width - 40 * mm, 17 * mm, f"Verify: {certificate.verification_code}")

    c.showPage()
    c.save()
    return out_path
