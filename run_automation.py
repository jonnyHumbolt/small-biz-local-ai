import sqlite3
import ollama

def fetch_low_stock_items():
    """Scans the local SQLite database for inventory shortages."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # SQL query that joins the inventory and supplier tables to find shortages
    query = """
        SELECT i.item_name, i.current_stock, i.reorder_level, s.supplier_name, s.contact_email
        FROM inventory i
        JOIN suppliers s ON i.supplier_id = s.id
        WHERE i.current_stock < i.reorder_level
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def generate_supplier_email(low_stock_data):
    """Feeds the database results into the local LLM for context-aware drafting."""
    if not low_stock_data:
        print("☀️ All inventory levels are healthy. No automation required.")
        return

    print(f"📋 Found {len(low_stock_data)} items requiring restock. Processing with local AI...")
    
    # Format the structured database rows into a clean text snippet for the model
    supplier_name = low_stock_data[0][3]
    supplier_email = low_stock_data[0][4]
    
    item_list_string = ""
    for row in low_stock_data:
        item_list_string += f"- {row[0]}: Current Stock: {row[1]}, Reorder Threshold: {row[2]}\n"

    # Construct a highly targeted, strict system instruction prompt
    prompt = f"""
    You are an automated logistics assistant for a grocery store.
    Review the following inventory shortages for our vendor, {supplier_name}.
    Write a concise, professional procurement email requesting a restock delivery for these specific items.
    
    ITEMS TO REORDER:
    {item_list_string}
    
    Output ONLY the raw email text. Do not include any conversational introductions, markdown styling, or post-completion chat notes.
    """

    # Trigger the local inference handshake
    response = ollama.generate(
        model="llama3.2:1b",
        prompt=prompt
    )
    
    # Display the final optimized operational output
    print(f"\n📧 TO: {supplier_email}")
    print(f"📝 SUBJECT: Urgent Restock Order - Urgent Purchase Order Request")
    print("\n--- GENERATED EMAIL DRAFT ---")
    print(response['response'].strip())
    print("--------------------------------\n")

if __name__ == "__main__":
    shortages = fetch_low_stock_items()
    generate_supplier_email(shortages)
