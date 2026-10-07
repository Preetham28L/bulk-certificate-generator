from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


CERTIFICATE_DIR = Path("certificates")


def generate_certificate(
    recipient_name: str,
    event_name: str,
    issuer_name: str,
    output_path: str,
) -> str:

    output_file = Path(output_path)

    # Create parent directory if it doesn't exist
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    width, height = landscape(A4)

    pdf = canvas.Canvas(
        str(output_file),
        pagesize=(width, height)
    )

    # Title
    pdf.setFont("Helvetica-Bold", 32)

    pdf.drawCentredString(
        width / 2,
        height - 60 * mm,
        "CERTIFICATE OF PARTICIPATION"
    )

    # Introductory text
    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        width / 2,
        height - 90 * mm,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 28)

    pdf.drawCentredString(
        width / 2,
        height - 115 * mm,
        recipient_name
    )

    # Event text
    pdf.setFont("Helvetica", 15)

    pdf.drawCentredString(
        width / 2,
        height - 145 * mm,
        f"for participating in {event_name}"
    )

    # Issuer
    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawCentredString(
        width / 2,
        45 * mm,
        f"Issued by {issuer_name}"
    )

    pdf.save()

    return str(output_file)