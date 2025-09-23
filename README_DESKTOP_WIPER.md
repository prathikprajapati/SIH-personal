# 🔒 Secure Data Wiper - Desktop Tool

Professional data sanitization tool for secure drive wiping with certificate generation and blockchain verification.

## 🚀 Features

- **Hardware-level secure erase** (ATA Secure Erase, NVMe commands)
- **Multiple wipe methods** (NIST, DoD, Zero Fill, etc.)
- **Certificate generation** with cryptographic signatures
- **Offline operation** capability
- **Web hub integration** for certificate upload
- **Cross-platform support** (Windows, Linux, macOS)
- **Blockchain verification** integration

## 📋 Requirements

### System Requirements
- Python 3.8+
- Administrative/root privileges for hardware wipe commands
- Internet connection (optional, for web hub integration)

### Hardware Requirements
- **Linux**: `hdparm` and `nvme-cli` packages
- **Windows**: Administrator privileges
- **macOS**: Administrator privileges

## 🛠️ Installation

### Option 1: Using the Build Script (Recommended)

1. **Install dependencies:**
   ```bash
   pip install requests pyinstaller
   ```

2. **Run the build script:**
   ```bash
   python build_wiper.py
   ```

3. **Install the application:**
   - **Windows**: Run `install.bat`
   - **Linux/macOS**: Run `sudo ./install.sh`

### Option 2: Manual Installation

1. **Clone or download the project**
2. **Install Python dependencies:**
   ```bash
   pip install requests
   ```
3. **Run directly:**
   ```bash
   python desktop_wiper/wiper_cli.py
   ```

## 🎯 Usage

### Interactive Mode

Run the application:
```bash
secure-data-wiper
```

Or run directly:
```bash
python desktop_wiper/wiper_cli.py
```

### Command Line Mode

**Scan for drives:**
```bash
python desktop_wiper/wiper_cli.py --scan
```

**Wipe a specific drive:**
```bash
python desktop_wiper/wiper_cli.py --wipe /dev/sda NIST_Purge
```

## 🔧 Configuration

Edit `wiper_config.json` to customize settings:

```json
{
    "web_hub_url": "http://localhost:5000",
    "offline_mode": true,
    "log_level": "INFO",
    "supported_methods": {
        "HDD": ["ATA_Secure_Erase", "NIST_Purge", "DoD_Wipe"],
        "SSD": ["ATA_Secure_Erase", "NIST_Purge", "Secure_Erase"],
        "NVMe": ["NVMe_Secure_Erase", "NVMe_Format", "Crypto_Erase"]
    }
}
```

### Configuration Options

- **`web_hub_url`**: URL of the web hub for certificate upload
- **`offline_mode`**: Set to `true` to disable web hub integration
- **`log_level`**: Logging level (DEBUG, INFO, WARNING, ERROR)
- **`supported_methods`**: Available wipe methods per drive type

## 🧹 Wipe Methods

### Hardware Methods (Recommended)
- **ATA_Secure_Erase**: Hardware-level secure erase for HDD/SSD
- **NVMe_Secure_Erase**: NVMe-specific secure erase
- **NVMe_Format**: NVMe format with secure erase

### Software Methods (Fallback)
- **NIST_Purge**: 3-pass wipe following NIST SP 800-88
- **DoD_Wipe**: Department of Defense 5220.22-M standard
- **Zero_Fill**: Single pass zero fill

## 📋 Certificate Management

### Generated Certificates Include:
- Unique certificate ID
- Device information (model, serial, size)
- Wipe method used
- Timestamp
- Cryptographic hash and signature
- Blockchain integration data

### Certificate Storage
- Certificates saved to `certificates/` directory
- JSON format for easy parsing
- Tamper-proof with cryptographic signatures

## 🌐 Web Hub Integration

### Upload Certificates
1. Ensure web hub is running
2. Set `offline_mode: false` in config
3. Use "Upload certificates to hub" option in CLI
4. Certificates are automatically verified and added to blockchain

### API Endpoints
- `POST /upload_certificate` - Upload single certificate
- `POST /sync_certificates` - Upload multiple certificates
- `GET /desktop_status` - Get desktop tool status

## ⚠️ Safety Warnings

- **PERMANENT DATA LOSS**: All wipe operations are irreversible
- **ADMINISTRATOR PRIVILEGES**: Required for hardware wipe commands
- **PHYSICAL ACCESS**: Ensure correct drive selection
- **BACKUP DATA**: Always backup important data before wiping
- **POWER STABILITY**: Ensure stable power during wipe operations

## 🔍 Troubleshooting

### Common Issues

1. **Drive not detected:**
   - Check permissions (run as administrator/root)
   - Verify drive is connected and powered
   - Check system logs for hardware errors

2. **Hardware wipe fails:**
   - Drive may not support hardware commands
   - Try software wipe methods instead
   - Check drive health with manufacturer tools

3. **Web hub connection fails:**
   - Verify web hub URL in configuration
   - Check network connectivity
   - Enable offline mode if needed

4. **Permission errors:**
   - Run with administrator/root privileges
   - Check file system permissions
   - Verify user has access to drive devices

### Logs
- Application logs saved to `wiper.log`
- Check logs for detailed error information
- Increase log level in config for more details

## 📊 Performance

### Wipe Speed Estimates
- **Hardware methods**: Minutes to hours (drive dependent)
- **Software methods**: Hours to days (drive size dependent)
- **NIST/DoD methods**: 3-7 passes, significantly slower

### Factors Affecting Speed
- Drive type (HDD vs SSD vs NVMe)
- Drive size and interface speed
- Wipe method selected
- System performance

## 🔐 Security Features

- **Cryptographic certificates** with unique signatures
- **Blockchain integration** for tamper-proof verification
- **Hardware-level wiping** when available
- **Multi-pass software wiping** as fallback
- **Comprehensive logging** for audit trails

## 📝 Compliance

This tool helps achieve compliance with:
- NIST SP 800-88 Guidelines for Media Sanitization
- DoD 5220.22-M Data Sanitization Standard
- HIPAA data disposal requirements
- GDPR data protection requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check web hub logs if using integration
4. Ensure all system requirements are met

---

**⚠️ IMPORTANT**: This tool performs destructive operations. Always double-check drive selection and ensure you have backups of important data before proceeding with any wipe operation.
