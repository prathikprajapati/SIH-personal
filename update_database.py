from app import create_app
from app.models import db

def update_database():
    """Update database schema for blockchain functionality"""
    app = create_app()

    with app.app_context():
        print("🔄 Updating database schema for blockchain functionality...")

        try:
            # Drop the existing table
            db.drop_all()
            print("✅ Dropped existing tables")

            # Recreate all tables with new schema
            db.create_all()
            print("✅ Recreated tables with blockchain fields")

            print("🎉 Database updated successfully!")
            print("📋 New fields added:")
            print("   - previous_hash: Links to previous certificate")
            print("   - certificate_hash: Hash of current certificate")
            print("   - chain_index: Position in blockchain")

        except Exception as e:
            print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    update_database()
