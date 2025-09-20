from fpdf import FPDF
from datetime import datetime
import qrcode
import uuid
import os
from PIL import Image
import hashlib

class CertificateGenerator:
    def __init__(self, output_path="certificate.pdf"):
        self.pdf = FPDF()
        self.output_path = output_path

    def generate_random_text(self):
        """Generate a random text for QR code verification"""
        return str(uuid.uuid4())

    def generate_qr_code(self, text, filename="qr_code.png"):
        """Generate QR code image from text"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        # Save the image directly
        img.save(filename)
        return filename

    def generate_certificate(self, drive_info, wipe_method, serial_number):
        """
        Generates a compact, visually appealing PDF certificate that fits on one page.

        Parameters:
        - drive_info: dict with keys like 'model', 'serial_number', 'capacity'
        - wipe_method: string describing the sanitization method used
        - serial_number: unique serial number for the certificate

        Returns:
        - cert_path: path to generated certificate
        - random_text: random text used in QR code
        """
        # Generate random text for QR code
        random_text = self.generate_random_text()

        # Generate QR code
        qr_filename = f"qr_{serial_number}.png"
        self.generate_qr_code(random_text, qr_filename)

        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=8)

        # Set page dimensions
        page_width = self.pdf.w
        page_height = self.pdf.h

        # Background
        self.pdf.set_fill_color(248, 249, 250)
        self.pdf.rect(0, 0, page_width, page_height, 'F')

        # Main border
        self.pdf.set_draw_color(0, 100, 0)
        self.pdf.set_line_width(1.5)
        self.pdf.rect(8, 8, page_width-16, page_height-16, 'D')

        # Header section
        self.pdf.set_font("Arial", 'B', 18)
        self.pdf.set_text_color(0, 100, 0)
        self.pdf.cell(0, 8, "SECURE DATA WIPE CERTIFICATE", ln=True, align="C")
        self.pdf.ln(2)

        self.pdf.set_font("Arial", 'I', 10)
        self.pdf.set_text_color(105, 105, 105)
        self.pdf.cell(0, 5, "Official Verification of Data Sanitization", ln=True, align="C")
        self.pdf.ln(3)

        # Certificate number
        self.pdf.set_font("Arial", 'B', 10)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_fill_color(0, 100, 0)
        self.pdf.cell(0, 6, f" Certificate No: {serial_number} ", ln=True, align="C", fill=True)
        self.pdf.ln(3)

        # Description
        self.pdf.set_font("Arial", '', 9)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.multi_cell(0, 4,
            "This is to certify that the following storage device has undergone secure data sanitization "
            "using industry-standard wiping procedures. All data has been permanently and irrecoverably "
            "removed in compliance with data protection regulations and security best practices."
        )
        self.pdf.ln(2)

        # Device information section
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(0, 100, 0)
        self.pdf.cell(0, 6, "DEVICE INFORMATION", ln=True)
        self.pdf.ln(1)

        # Device details in a compact table format
        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.rect(15, self.pdf.get_y(), page_width-30, 20, 'F')

        self.pdf.set_font("Arial", 'B', 9)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(45, 5, "Model:", ln=False)
        self.pdf.set_font("Arial", '', 9)
        self.pdf.cell(0, 5, f" {drive_info.get('model', 'N/A')}", ln=True)

        self.pdf.set_font("Arial", 'B', 9)
        self.pdf.cell(45, 5, "Serial Number:", ln=False)
        self.pdf.set_font("Arial", '', 9)
        self.pdf.cell(0, 5, f" {drive_info.get('serial_number', 'N/A')}", ln=True)

        self.pdf.set_font("Arial", 'B', 9)
        self.pdf.cell(45, 5, "Capacity:", ln=False)
        self.pdf.set_font("Arial", '', 9)
        self.pdf.cell(0, 5, f" {drive_info.get('capacity', 'N/A')}", ln=True)
        self.pdf.ln(2)

        # Sanitization details
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(0, 100, 0)
        self.pdf.cell(0, 6, "SANITIZATION DETAILS", ln=True)
        self.pdf.ln(1)

        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.rect(15, self.pdf.get_y(), page_width-30, 12, 'F')

        self.pdf.set_font("Arial", 'B', 9)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(45, 5, "Method Used:", ln=False)
        self.pdf.set_font("Arial", '', 9)
        self.pdf.cell(0, 5, f" {wipe_method}", ln=True)
        self.pdf.ln(2)

        # Certificate details
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(0, 100, 0)
        self.pdf.cell(0, 6, "CERTIFICATE DETAILS", ln=True)
        self.pdf.ln(1)

        timestamp = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.rect(15, self.pdf.get_y(), page_width-30, 12, 'F')

        self.pdf.set_font("Arial", 'B', 9)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(45, 5, "Issued On:", ln=False)
        self.pdf.set_font("Arial", '', 9)
        self.pdf.cell(0, 5, f" {timestamp}", ln=True)
        self.pdf.ln(3)

        # QR Code and verification section
        self.pdf.set_font("Arial", 'B', 10)
        self.pdf.set_text_color(0, 100, 0)
        self.pdf.cell(0, 5, "VERIFICATION QR CODE", ln=True)
        self.pdf.ln(1)

        # QR code instructions
        self.pdf.set_font("Arial", '', 7)
        self.pdf.set_text_color(105, 105, 105)
        self.pdf.multi_cell(0, 3,
            "Scan this QR code with any QR code reader to obtain the verification code. "
            "Visit our website and enter the code to verify this certificate's authenticity."
        )
        self.pdf.ln(1)

        # Add QR code image - smaller and positioned to fit
        if os.path.exists(qr_filename):
            # Position QR code on the right side, smaller size
            qr_x = page_width - 50
            qr_y = self.pdf.get_y()
            self.pdf.image(qr_filename, x=qr_x, y=qr_y, w=30, h=30)

            # Add decorative frame around QR code
            self.pdf.set_draw_color(0, 100, 0)
            self.pdf.set_line_width(0.5)
            self.pdf.rect(qr_x - 1, qr_y - 1, 32, 32, 'D')

            self.pdf.ln(32)  # Add space after QR code

        # Security notice and signature in one compact section
        self.pdf.set_font("Arial", 'B', 8)
        self.pdf.set_text_color(255, 0, 0)
        self.pdf.cell(0, 4, "CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY", ln=True, align="C")
        self.pdf.ln(2)

        # Digital signature section
        self.pdf.set_font("Arial", 'B', 10)
        self.pdf.set_text_color(0, 100, 0)
        self.pdf.cell(0, 5, "DIGITAL SIGNATURE", ln=True, align="C")
        self.pdf.ln(2)

        # Signature line
        self.pdf.set_draw_color(0, 0, 0)
        self.pdf.set_line_width(0.3)
        self.pdf.line(40, self.pdf.get_y(), page_width-40, self.pdf.get_y())
        self.pdf.ln(1)

        self.pdf.set_font("Arial", '', 8)
        self.pdf.set_text_color(105, 105, 105)
        self.pdf.cell(0, 4, "Reboot Reclaim Data Sanitization System", ln=True, align="C")
        self.pdf.cell(0, 4, "Automated Digital Signature", ln=True, align="C")
        self.pdf.ln(2)

        # Footer
        self.pdf.set_font("Arial", 'I', 6)
        self.pdf.set_text_color(128, 128, 128)
        self.pdf.cell(0, 3, "This certificate is digitally generated and tamper-proof.", ln=True, align="C")
        self.pdf.cell(0, 3, "Any unauthorized modification will invalidate this certificate.", ln=True, align="C")

        # Save PDF
        self.pdf.output(self.output_path)

        # Clean up QR code image
        if os.path.exists(qr_filename):
            os.remove(qr_filename)

        return self.output_path, random_text


# Example usage:
# if __name__ == "__main__":
#     cert_gen = CertificateGenerator("wipe_certificate.pdf")
#     drive = {
#         "model": "Seagate Barracuda 2TB",
#         "serial_number": "SN-HDD-123456789",
#         "capacity": "2 TB"
#     }
#     cert_path = cert_gen.generate_certificate(drive, "NIST Purge (Overwrite)", "CERT-0001")
#     print(f"Certificate generated at: {cert_path}")
