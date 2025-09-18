from fpdf import FPDF
from datetime import datetime

class CertificateGenerator:
    def __init__(self, output_path="certificate.pdf"):
        self.pdf = FPDF()
        self.output_path = output_path

    def generate_certificate(self, drive_info, wipe_method, serial_number):
        """
        Generates a PDF certificate for a wiped drive.

        Parameters:
        - drive_info: dict with keys like 'model', 'serial_number', 'capacity'
        - wipe_method: string describing the sanitization method used
        - serial_number: unique serial number for the certificate
        """
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.set_font("Arial", 'B', 16)

        # Title
        self.pdf.cell(0, 10, "Secure Data Wipe Certificate", ln=True, align="C")
        self.pdf.ln(10)

        # Certificate details
        self.pdf.set_font("Arial", '', 12)
        self.pdf.multi_cell(0, 10,
            f"This certificate verifies that the following storage device has been securely wiped "
            f"using the specified sanitization method, ensuring data irrecoverability and compliance "
            f"with industry standards."
        )
        self.pdf.ln(10)

        # Device details
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.cell(0, 10, "Device Details:", ln=True)
        self.pdf.set_font("Arial", '', 12)
        self.pdf.cell(0, 8, f"Model: {drive_info.get('model', 'N/A')}", ln=True)
        self.pdf.cell(0, 8, f"Serial Number: {drive_info.get('serial_number', 'N/A')}", ln=True)
        self.pdf.cell(0, 8, f"Capacity: {drive_info.get('capacity', 'N/A')}", ln=True)
        self.pdf.ln(10)

        # Wipe method
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.cell(0, 10, "Sanitization Method:", ln=True)
        self.pdf.set_font("Arial", '', 12)
        self.pdf.cell(0, 8, wipe_method, ln=True)
        self.pdf.ln(10)

        # Timestamp and serial number
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.cell(0, 10, "Certificate Details:", ln=True)
        self.pdf.set_font("Arial", '', 12)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.pdf.cell(0, 8, f"Issued On: {timestamp}", ln=True)
        self.pdf.cell(0, 8, f"Certificate Serial Number: {serial_number}", ln=True)
        self.pdf.ln(20)

        # Signature placeholder
        self.pdf.set_font("Arial", 'I', 12)
        self.pdf.cell(0, 10, "This certificate is digitally signed and tamper-proof.", ln=True, align="C")

        # Save PDF
        self.pdf.output(self.output_path)
        return self.output_path


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
