import sqlite3

def setup_database():
    # Connects to a local file database. If it doesn't exist, SQLite creates it instantly.
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    print("📦 Creating local database tables...")

    # 1. Create the Inventory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        current_stock INTEGER NOT NULL,
        reorder_level INTEGER NOT NULL,
        supplier_id INTEGER,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """)

    # 2. Create the Suppliers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact_email TEXT NOT NULL
    )
    """)

    # Clear out old data if re-running the script
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM suppliers")

    # 3. Insert Mock Supplier Data
    cursor.execute("INSERT INTO suppliers (supplier_name, contact_email) VALUES ('Bayou Produce Distribution', 'orders@bayouproduce.com')")
    produce_supplier_id = cursor.lastrowid

    # 4. Insert Mock Inventory Data (Some items are safe, some are critically low)
    mock_items = [
        ('Avocados', 150, 50, produce_supplier_id),       # Safe
        ('Roma Tomatoes', 12, 40, produce_supplier_id),    # LOW STOCK (12 < 40)
        ('Cilantro Bunches', 8, 25, produce_supplier_id),  # LOW STOCK (8 < 25)
        ('Yellow Onions', 200, 75, produce_supplier_id)    # Safe
    ]
    
    cursor.executemany("INSERT INTO inventory (item_name, current_stock, reorder_level, supplier_id) VALUES (?, ?, ?, ?)", mock_items)

    # Commit changes and close the connection safely
    conn.commit()
    conn.close()
    print("✅ Local 'inventory.db' generated and populated successfully!")

if __name__ == "__main__":
    setup_database()
