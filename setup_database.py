import pymysql
from app import create_app

def setup_database():
    """Create the certificates_db database if it doesn't exist"""
    try:
        # Connect to MySQL server without specifying a database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='5680'
        )

        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS certificates_db")
            print("✅ Database 'certificates_db' created successfully!")

        connection.close()

        # Now test the Flask app connection
        app = create_app()
        print("✅ Flask app database connection successful!")

    except Exception as e:
        print(f"❌ Database setup error: {e}")

if __name__ == "__main__":
    setup_database()
