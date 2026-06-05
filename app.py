import os
import streamlit as st
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

# 🔒 Pull configuration dynamically from our secured container environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "inventory_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "local_secure_pass")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def get_db_connection():
    """Establishes a connection thread to the containerized PostgreSQL cluster."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

def query_low_stock_items():
    """Queries the enterprise database cluster for critical stock parameters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT item_name, current_stock, minimum_threshold, vendor_email, status 
        FROM inventory_health 
        WHERE status = 'CRITICAL_LOW';
    """)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records

# --- Streamlit Visual UI Layout Assembly ---
st.set_page_config(page_title="Bayou Produce Logistics Dashboard", page_icon="📦", layout="wide")
st.title("📦 Bayou Produce Logistics Automation Engine")
st.subheader("Decoupled Enterprise Local AI Core (Phase 4 Deployment)")

st.write("This dashboard monitors our local relational PostgreSQL layer inside a decoupled virtual container network, executing automated procurement logic on-premise.")

# Active Database Records Table Rendering
st.markdown("### 📊 Active Supply Chain Anomalies")
low_stock_data = query_low_stock_items()

if low_stock_data:
    st.error(f"Alert: Detected {len(low_stock_data)} logistics bottlenecks requiring automated procurement actions.")
    for item in low_stock_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Item Name", value=item['item_name'])
        with col2:
            st.metric(label="Current Stock", value=f"{item['current_stock']} units", delta=f"-{item['minimum_threshold'] - item['current_stock']} below safety limit", delta_color="inverse")
        with col3:
            st.metric(label="Safety Threshold", value=f"{item['minimum_threshold']} units")
        with col4:
            st.text(f"Assigned Vendor:\n{item['vendor_email']}")
        
        # Unique target triggers for each independent item anomaly
        if st.button(f"Generate Procurement Draft for {item['item_name']}", key=item['item_name']):
            st.info(f"Assembling contextual logistics schema payload and transferring to local LLM core...")
            
            # Formulate the contextual input string prompt for the 1B parameter model
            prompt_context = f"""
            You are an automated logistics management system operating at Bayou Produce Distribution.
            An inventory threshold breach has occurred for the following item:
            - Item: {item['item_name']}
            - Current Stock Level: {item['current_stock']} units
            - Target Safety Limit: {item['minimum_threshold']} units
            - Vendor Assignment Point: {item['vendor_email']}
            
            Write a formal, brief procurement order email directed to the vendor assignment point requesting an expedited replenishment delivery of this product to reset our warehouse safety levels. Maintain a clear, professional supply chain tone. Do not generate placeholder text.
            """
            
            try:
                # Transmit inference payload request across the internal Docker virtual bridge
                response = requests.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": "llama3.2:1b", "prompt": prompt_context, "stream": False},
                    timeout=45
                )
                
                if response.status_code == 200:
                    generated_draft = response.json().get("response", "Error: Failed to safely parse output string.")
                    st.success("📬 Automated Vendor Procurement Order Draft Assembled Successfully!")
                    st.text_area(label="Staged Email Transmission Text Container", value=generated_draft, height=280)
                else:
                    st.error(f"Failed to communicate with inference engine. Status: {response.status_code}")
            except Exception as e:
                st.error(f"Inference pipeline timeout or processing break: {e}")
        st.markdown("---")
else:
    st.success("✅ All warehouse stock metrics currently reside safely above operating baselines.")
