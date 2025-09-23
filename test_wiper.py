#!/usr/bin/env python3
"""
Test script for the Secure Data Wiper desktop tool
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from desktop_wiper.wiper_core import SecureWiper

        print("✅ SecureWiper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SecureWiper: {e}")
        return False

    try:
        from desktop_wiper.wiper_cli import WipingToolCLI

        print("✅ WipingToolCLI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WipingToolCLI: {e}")
        return False

    return True


def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing configuration...")

    try:
        from desktop_wiper.wiper_core import SecureWiper

        wiper = SecureWiper()

        # Check if config has required keys
        required_keys = [
            "web_hub_url",
            "offline_mode",
            "log_level",
            "supported_methods",
        ]
        for key in required_keys:
            if key in wiper.config:
                print(f"✅ Config key '{key}' found")
            else:
                print(f"❌ Config key '{key}' missing")
                return False

        print("✅ Configuration loaded successfully")
        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_drive_detection():
    """Test drive detection (without actually wiping)"""
    print("🧪 Testing drive detection...")

    try:
        from desktop_wiper.wiper_core import SecureWiper

        wiper = SecureWiper()

        drives = wiper.detect_drives()

        print(f"✅ Drive detection completed. Found {len(drives)} drive(s)")

        # Display detected drives (without sensitive info)
        for i, drive in enumerate(drives, 1):
            print(
                f"   {i}. {drive.get('type', 'Unknown')} - {drive.get('model', 'Unknown')[:30]}..."
            )

        return True

    except Exception as e:
        print(f"❌ Drive detection test failed: {e}")
        return False


def test_certificate_generation():
    """Test certificate generation"""
    print("🧪 Testing certificate generation...")

    try:
        from desktop_wiper.wiper_core import SecureWiper

        wiper = SecureWiper()

        # Create mock drive info for testing
        mock_drive_info = {
            "device": "/dev/sda",
            "type": "HDD",
            "model": "Test Drive",
            "serial": "TEST123456",
            "size": "1TB",
        }

        certificate = wiper._generate_certificate(mock_drive_info, "NIST_Purge")

        # Verify certificate structure
        required_fields = [
            "certificate_id",
            "device_info",
            "wipe_method",
            "timestamp",
            "certificate_hash",
            "signature",
        ]
        for field in required_fields:
            if field in certificate:
                print(f"✅ Certificate field '{field}' present")
            else:
                print(f"❌ Certificate field '{field}' missing")
                return False

        print("✅ Certificate generation test passed")
        return True

    except Exception as e:
        print(f"❌ Certificate generation test failed: {e}")
        return False


def test_cli_interface():
    """Test CLI interface creation"""
    print("🧪 Testing CLI interface...")

    try:
        from desktop_wiper.wiper_cli import WipingToolCLI

        # Just test that we can create the CLI object
        cli = WipingToolCLI()
        print("✅ CLI interface created successfully")

        return True

    except Exception as e:
        print(f"❌ CLI interface test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🔬 SECURE DATA WIPER - TEST SUITE")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration),
        ("Drive Detection Tests", test_drive_detection),
        ("Certificate Generation Tests", test_certificate_generation),
        ("CLI Interface Tests", test_cli_interface),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! The desktop wiper is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python desktop_wiper/wiper_cli.py' to start the tool")
        print("2. Use 'python build_wiper.py' to create a standalone executable")
        print("3. Configure your web hub URL in wiper_config.json")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("- Ensure all dependencies are installed")
        print("- Check that you're running with appropriate permissions")
        print("- Verify configuration file exists and is valid")
        return 1


if __name__ == "__main__":
    sys.exit(main())
