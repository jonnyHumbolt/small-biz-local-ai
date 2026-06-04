import sqlite3
import streamlit as st
import ollama

# Page Configuration
st.set_page_config(page_title="Bayou Fresh Grocers - AI Procurement", page_icon="🥦", layout="wide")

st.title("🥦 Bayou Fresh Grocers")
st.subheader("Autonomous Inventory & AI Procurement Portal")
st.markdown("---")

def get_full_inventory():
    """Fetches the entire inventory list to display a master visual status table."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    query = """
        SELECT i.item_name, i.current_stock, i.reorder_level, s.supplier_name
        FROM inventory i
        JOIN suppliers s ON i.supplier_id = s.id
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_low_stock():
    """Queries only the data subsets that have breached safety thresholds."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
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

# Create Layout Columns: Left side for live data, Right side for AI operations
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("📦 Real-Time Inventory Monitoring")
    if st.button("🔄 Refresh Database Status"):
        st.toast("Database pipeline re-indexed!")

    # Master Inventory Table Visual
    all_items = get_full_inventory()
    inventory_data = []
    for item in all_items:
        # Determine status marker
        status = "🟢 Healthy" if item[1] >= item[2] else "🚨 Critical Shortage"
        inventory_data.append({
            "Item Name": item[0],
            "Current Stock": item[1],
            "Reorder Threshold": item[2],
            "Assigned Vendor": item[3],
            "Status": status
        })
    st.dataframe(inventory_data, use_container_width=True, hide_index=True)

with col2:
    st.header("🤖 AI Automated Procurement Engine")
    shortages = get_low_stock()

    if not shortages:
        st.success("All inventory levels are safe. No procurement tasks flagged.")
    else:
        st.warning(f"System flagged **{len(shortages)}** critical shortages requiring active orders.")
        
        # Display identified bottleneck items inside a scannable bullet list
        for item in shortages:
            st.markdown(f"- **{item[0]}**: Stock level at `{item[1]}` (Threshold: {item[2]})")
        
        st.markdown("### Generate Restock Communication")
        # Action button to trigger local inference
        if st.button("⚡ Run Local AI Agent Pipeline"):
            with st.spinner("Invoking local llama3.2:1b model..."):
                try:
		   # ⚠️ ADD THIS LINE RIGHT HERE: Directs Python to the separate AI backend container
                    ollama.CLIENT_HOST = "http://ai-backend:11434"
                    # Construct data string for the LLM
                    vendor_name = shortages[0][3]
                    vendor_email = shortages[0][4]
                    items_string = "".join([f"- {row[0]}: Stock {row[1]}, Threshold {row[2]}\n" for row in shortages])
                    
                    prompt = f"""
                    You are an automated logistics assistant for a grocery store.
                    Review the following inventory shortages for our vendor, {vendor_name}.
                    Write a concise, professional procurement email requesting a restock delivery for these specific items.
                    
                    ITEMS TO REORDER:
                    {items_string}
                    
                    Output ONLY the raw email text. Do not include any chatty openings, greetings to the programmer, markdown block ticks, or follow-up notes.
                    """
                    
                    # Connect to local background service
                    response = ollama.generate(model="llama3.2:1b", prompt=prompt)
                    email_draft = response['response'].strip()
                    
                    # Display structured output panel components
                    st.success("AI Drafting Completed Successfully!")
                    st.text_input("Recipient Vendor Email", value=vendor_email, disabled=True)
                    st.text_input("Email Subject Line", value=f"URGENT: Purchase Order Restock - Bayou Fresh Grocers", disabled=True)
                    st.text_area("Generated Document Body", value=email_draft, height=250)
                    
                except Exception as e:
                    st.error(f"Failed to communicate with local AI core: {e}")
