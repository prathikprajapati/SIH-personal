# This is an expanded set of mock data for the Secure Data Wiping Prototype.
# It includes a greater variety of drives and simulates different states for a more realistic demo.

mock_drives_data = [
    {
        "id": "drive-1",
        "model": "Seagate Barracuda 2TB",
        "type": "HDD",
        "capacity": "2 TB",
        "serial_number": "SN-HDD-123456789",
        "status": "Ready",
        "is_wipeable": True,
        "supported_methods": ["NIST Clear", "NIST Purge (Overwrite)"]
    },
    {
        "id": "drive-2",
        "model": "Samsung 970 EVO Plus 1TB",
        "type": "NVMe",
        "capacity": "1 TB",
        "serial_number": "SN-NVMe-987654321",
        "status": "Ready",
        "is_wipeable": True,
        "supported_methods": ["NIST Purge (Crypto Erase)"]
    },
    {
        "id": "drive-3",
        "model": "Crucial MX500 500GB",
        "type": "SSD",
        "capacity": "500 GB",
        "serial_number": "SN-SSD-456789123",
        "status": "Ready",
        "is_wipeable": True,
        "supported_methods": ["NIST Purge (Secure Erase)"]
    },
    {
        "id": "drive-4",
        "model": "Western Digital Blue 500GB",
        "type": "HDD",
        "capacity": "500 GB",
        "serial_number": "SN-HDD-741852963",
        "status": "Wiping in progress",
        "is_wipeable": True,
        "progress_percentage": 45,
        "supported_methods": ["NIST Clear", "NIST Purge (Overwrite)"]
    },
    {
        "id": "drive-5",
        "model": "SanDisk SSD Plus 240GB",
        "type": "SSD",
        "capacity": "240 GB",
        "serial_number": "SN-SSD-369258147",
        "status": "Wiped",
        "is_wipeable": False,  # No longer wipeable after being wiped
        "supported_methods": []
    },
    {
        "id": "drive-6",
        "model": "WD Black 4TB",
        "type": "HDD",
        "capacity": "4 TB",
        "serial_number": "SN-HDD-159357486",
        "status": "Error",
        "is_wipeable": False,
        "error_message": "Device not responding.",
        "supported_methods": []
    }
]
