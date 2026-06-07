import os
import time
import logging
import streamlit as st
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

# 🛠️ SETUP STRUCTURED PRODUCTION LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("grocery_ai_frontend")

# 🔒 Pull configuration dynamically from secured container environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "inventory_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "local_secure_pass")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
VENDOR_API_URL = os.getenv("VENDOR_API_URL", "http://localhost:5000/api/v1/orders")

def get_db_connection():
    """Establishes a connection thread to the containerized PostgreSQL cluster."""
    try:
        return psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            cursor_factory=RealDictCursor, connect_timeout=5
        )
    except psycopg2.OperationalError as err:
        logger.error(f"Database infrastructure connection crash: {err}")
        raise err

def query_low_stock_items():
    """Queries the database cluster for critical stock parameters."""
    try:
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
        return records, None
    except Exception as ex:
        return [], f"The persistence data layer is currently unreachable. Detail: {ex}"

# 🧠 NEW RAG MECHANISM: VECTOR RECALL ENGINE
def retrieve_vector_context(search_term):
    """
    Executes a semantic database search using cosine distance vector operations.
    Bypasses local PyTorch completely by offloading matching to PostgreSQL!
    """
    try:
        # Step A: Ask your local running Llama 3.2 1B model to generate an embedding array for the item name
        # This keeps our frontend 100% free of heavy sentence-transformer libraries!
        logger.info(f"Generating ad-hoc query embedding array via Ollama for term: '{search_term}'")
        emb_res = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": "llama3.2:1b", "prompt": search_term},
            timeout=10
        )
        
        if emb_res.status_code != 200:
            logger.warning("Ollama embedding extraction returned a non-200 state.")
            return ""
            
        query_vector = emb_res.json().get("embedding")
        
        # Step B: Perform a Cosine Distance (<=>) vector search inside the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # We query the database to find the text snippet closest to our item coordinate
        cursor.execute("""
            SELECT content, (embedding <=> %s::vector) AS distance 
            FROM vendor_knowledge_vectors 
            ORDER BY distance ASC 
            LIMIT 1;
        """, (query_vector,))
        
        best_match = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if best_match and best_match['distance'] < 0.6: # Confidence boundary threshold filter
            logger.info(f"Vector Match Found! Distance: {round(best_match['distance'], 4)}")
            return best_match['content']
        else:
            logger.info("No highly relevant semantic vector context matched this query item.")
            return ""
    except Exception as ex:
        logger.error(f"Vector memory retrieval failure: {ex}")
        return ""

# --- Streamlit Visual UI Layout Assembly ---
st.set_page_config(page_title="Bayou Produce Logistics Dashboard", page_icon="📦", layout="wide")
st.title("📦 Bayou Produce Logistics Automation Engine")
st.subheader("Decoupled Enterprise Local AI Core (Phase 7 Local RAG Active)")

st.markdown("### 📊 Active Supply Chain Anomalies")
low_stock_data, db_error = query_low_stock_items()

if db_error:
    st.error(db_error)
elif low_stock_data:
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
        
        if st.button(f"Generate Procurement Draft for {item['item_name']}", key=f"gen_{item['item_name']}"):
            logger.info(f"Inference pipeline initialization requested for item: '{item['item_name']}'")
            st.info(f"Assembling contextual logistics schema payload and searching vector memories...")
            
            # 🔥 EXECUTING THE LOCAL RAG INJECTION
            retrieved_policy = retrieve_vector_context(item['item_name'])
            
            if retrieved_policy:
                st.caption(f"💡 **Retrieved System Context Matrix:** _{retrieved_policy}_")
            
            prompt_context = f"""
            You are an automated logistics management system operating at Bayou Produce Distribution.
            An inventory threshold breach has occurred for the following item:
            - Item: {item['item_name']}
            - Current Stock Level: {item['current_stock']} units
            - Target Safety Limit: {item['minimum_threshold']} units
            - Vendor Assignment Point: {item['vendor_email']}
            
            CRITICAL ADDITIONAL VENDOR CONTEXT FOUND IN VECTOR MEMORIES:
            {retrieved_policy if retrieved_policy else "No historical records matched this specific item routing."}
            
            Write a formal, brief procurement order email directed to the vendor assignment point requesting an expedited replenishment delivery of this product to reset our warehouse safety levels. If the vendor context dictates special shipping instructions or terms based on stock levels, explicitly include those professional demands in the email text. Maintain a clear supply chain tone.
            """
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": "llama3.2:1b", "prompt": prompt_context, "stream": False},
                    timeout=45
                )
                latency = round(time.time() - start_time, 2)
                
                if response.status_code == 200:
                    generated_draft = response.json().get("response", "Error: Failed to parse output.")
                    logger.info(f"Local LLM Inference Complete. Latency: {latency}s")
                    st.success(f"📬 Automated Vendor Procurement Order Draft Assembled! (Latency: {latency}s)")
                    
                    edited_draft = st.text_area(
                        label="Staged Email Transmission Text Container", 
                        value=generated_draft, 
                        height=280,
                        key=f"text_{item['item_name']}"
                    )
                    st.session_state[f"draft_{item['item_name']}"] = edited_draft
                else:
                    st.error(f"Failed to communicate with engine. Status: {response.status_code}")
            except Exception as e:
                st.error(f"Inference pipeline transport break: {e}")
        
        # Webhook routing mechanism
        if f"draft_{item['item_name']}" in st.session_state:
            st.markdown("#### 🚀 Automated Routing Core")
            if st.button(f"Transmit Document to Vendor Network via Webhook", key=f"send_{item['item_name']}"):
                webhook_payload = {
                    "item_name": item['item_name'],
                    "vendor_email": item['vendor_email'],
                    "procurement_draft": st.session_state[f"draft_{item['item_name']}"]
                }
                try:
                    res = requests.post(VENDOR_API_URL, json=webhook_payload, timeout=10)
                    if res.status_code == 200:
                        st.success(f"📥 Transaction Confirmed by Remote Endpoint: {res.json().get('message')}")
                    else:
                        st.error(f"Webhook rejected by target gateway. Status Code: {res.status_code}")
                except Exception as ex:
                    st.error(f"Network transport level connection failure: {ex}")
        st.markdown("---")
else:
    st.success("✅ All warehouse stock metrics currently reside safely above operating baselines.")
