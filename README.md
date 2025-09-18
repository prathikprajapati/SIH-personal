# **Wipe.io: The Ultimate Secure Data Sanitization Tool**

`Wipe.io` is a bootable, cross-platform utility designed to securely wipe data from any storage media, ensuring compliance with global standards. Our tool transforms a complex, risky task into a simple, one-click process for both individuals and IT professionals.

**Our Vision:** To provide a reliable and accessible solution for the secure disposal and recycling of IT assets, promoting a safer, more sustainable circular economy.

---

### **The Problem We Solve**

*  **Inadequate Tools:** Standard methods like simple file deletion or formatting leave sensitive data vulnerable to recovery.  This poses a significant security risk for businesses and individuals.
*  **Compliance Risks:** Regulations like GDPR and HIPAA require verifiable proof of data destruction, which many tools fail to provide.
*  **Technical Complexity:** Securely wiping hidden areas like the Host Protected Area (HPA) and Device Configuration Overlay (DCO) requires deep technical knowledge and command-line expertise.

---

### **How We Reboot & Reclaim**

Our solution is a self-contained, offline bootable environment that addresses these challenges head-on.

#### **Core Features**

*  **NIST SP 800-88 Compliant:** Our tool adheres to the NIST standard, implementing **Purge** methods that render data irrecoverable even with state-of-the-art laboratory techniques.
* **Cross-Platform Erase Engine:** It automatically detects the drive type (HDD, SATA SSD, NVMe) and applies the correct firmware-level command:
    *  **HDDs & SATA SSDs:** Uses ATA "Secure Erase" to wipe all sectors, including hidden HPA and DCO areas.
    *  **NVMe Drives:** Utilizes the advanced `nvme sanitize` or `nvme format` commands, supporting Overwrite, Block Erase, and Cryptographic Erase.
*  **Tamper-Proof Certificates:** Every successful wipe generates a digitally signed, tamper-proof **PDF certificate** for audit and compliance purposes.  The certificate includes key details like the sanitization method, timestamps, and a unique serial number, all protected by a cryptographic signature to ensure its integrity.
* **Intuitive "One-Click" UI:** The complex backend is abstracted by a simple, user-friendly interface.  Users boot from a USB stick, see a list of drives, and execute a secure wipe with a single click.

---

### **Technical Architecture**

The application is delivered as a lightweight, bootable Linux ISO.

*  **Backend:** A Python-based engine that uses command-line tools like `hdparm` and `nvme-cli` to interact directly with the drive's firmware.
*  **Frontend:** A responsive web interface built with **React** and **Tailwind CSS**, rendered within a live Linux environment.
*  **Certificate Engine:** A dedicated module collects audit data and uses **SHA-256 hashing** and **RSA signing** to create a verifiable certificate.
*  **Certificate Generation:** Added a new Python module using the FPDF library to generate tamper-proof PDF certificates dynamically after each successful wipe.

---

### **Getting Started**

**1. Create the Bootable USB:**
* Download the latest `Wipe.io` ISO from our GitHub Releases page.
* Use a tool like BalenaEtcher or Rufus to flash the ISO to a USB drive.

**2. Boot from USB:**
* Insert the USB and restart your computer.
* Enter your BIOS/UEFI settings and change the boot order to prioritize the USB drive.

**3. Wipe Your Device:**
* The application will automatically launch, detect your drives, and present the UI.
* Select the drive you wish to wipe and click the "Wipe My Device" button. The application will handle the rest, from sanitizing the drive to generating your certificate.

---

### **Contribution & Roadmap**

We welcome contributions to this project!

* **Bug Reports:** If you encounter a bug, please open a new issue.
* **Feature Ideas:** We have a few ideas for future scope, including support for mobile devices and cloud-based verification.
* **Pull Requests:** Feel free to fork the repository, make changes, and submit a pull request.

**Team:** 

* Harsh
* Srishti
* Sejal
* Shreya
* Yashit Mital
* Prathik
