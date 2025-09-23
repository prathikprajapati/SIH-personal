#!/usr/bin/env python3
"""
Test script to verify blockchain functionality
"""
from app import create_app
from app.models import CertificateVerification, db
import json

def test_blockchain():
    """Test the blockchain functionality"""
    app = create_app()

    with app.app_context():
        print("🔗 Testing Blockchain Functionality")
        print("=" * 50)

        # Get all certificates
        certificates = CertificateVerification.query.order_by(CertificateVerification.chain_index).all()

        if not certificates:
            print("❌ No certificates found in database")
            print("💡 Generate some certificates first by visiting /demo")
            return

        print(f"✅ Found {len(certificates)} certificates in blockchain")
        print()

        # Test each certificate's chain integrity
        all_valid = True
        for i, cert in enumerate(certificates):
            print(f"Block #{cert.chain_index}")
            print(f"  Certificate ID: {cert.certificate_id}")
            print(f"  Certificate Hash: {cert.certificate_hash[:16]}...")
            print(f"  Previous Hash: {cert.previous_hash[:16] + '...' if cert.previous_hash else 'Genesis Block'}")
            print(f"  Created: {cert.created_at}")
            print(f"  Verified: {'✅' if cert.is_verified else '⏳'}")

            # Test chain integrity
            chain_valid = cert.verify_chain_integrity()
            if chain_valid:
                print("  Chain Status: ✅ Valid")
            else:
                print("  Chain Status: ❌ Invalid")
                all_valid = False

            print()

        # Overall blockchain status
        if all_valid:
            print("🎉 BLOCKCHAIN INTEGRITY: ✅ ALL CERTIFICATES VALID")
        else:
            print("⚠️ BLOCKCHAIN INTEGRITY: ❌ SOME CERTIFICATES COMPROMISED")

        print()
        print("📊 Blockchain Statistics:")
        print(f"  Total Blocks: {len(certificates)}")
        print(f"  Genesis Block: {certificates[0].certificate_id if certificates else 'None'}")
        print(f"  Latest Block: {certificates[-1].certificate_id if certificates else 'None'}")

if __name__ == "__main__":
    test_blockchain()
