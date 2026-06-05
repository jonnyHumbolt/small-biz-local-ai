import os
import psycopg2
from psycopg2 import DatabaseError

# 🔐 Pull configuration directly from our secured environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "inventory_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "local_secure_pass")

def init_postgres():
    try:
        # Establish connection with the PostgreSQL cluster container
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # 🛠️ Drop table if it exists to start fresh, then build the enterprise schema
        cursor.execute("DROP TABLE IF EXISTS inventory_health;")
        
        cursor.execute("""
            CREATE TABLE inventory_health (
                id SERIAL PRIMARY KEY,
                item_name VARCHAR(100) NOT NULL,
                current_stock INT NOT NULL,
                minimum_threshold INT NOT NULL,
                vendor_email VARCHAR(150) NOT NULL,
                status VARCHAR(50) NOT NULL
            );
        """)

        # 💾 Seed the database with identical mock produce parameters
        mock_data = [
            ('Organic Bananas', 45, 100, 'procurement@bayouproduce.com', 'CRITICAL_LOW'),
            ('Honeycrisp Apples', 210, 150, 'orders@deltafresh.com', 'HEALTHY'),
            ('Hass Avocados', 12, 75, 'supply@gulfcoastdistributors.com', 'CRITICAL_LOW'),
            ('Baby Spinach Bags', 85, 80, 'fulfillment@bayouproduce.com', 'HEALTHY')
        ]

        for item in mock_data:
            cursor.execute("""
                INSERT INTO inventory_health (item_name, current_stock, minimum_threshold, vendor_email, status)
                VALUES (%s, %s, %s, %s, %s);
            """, item)

        conn.commit()
        print("🚀 Enterprise PostgreSQL Layer successfully initialized and seeded with mock logistics records!")
        
        cursor.close()
        conn.close()

    except DatabaseError as error:
        print(f"❌ Error while initializing PostgreSQL database: {error}")

if __name__ == "__main__":
    init_postgres()
