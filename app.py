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
    handlers=[
        logging.StreamHandler() # Output directly to container logs for real-time observability
    ]
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
    """Establishes a connection thread to the containerized PostgreSQL cluster with graceful failover."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor,
            connect_timeout=5 # Prevent hanging indefinitely if DB is unresponsive
        )
    except psycopg2.OperationalError as err:
        logger.error(f"Database infrastructure connection crash: {err}")
        raise err

def query_low_stock_items():
    """Queries the enterprise database cluster for critical stock parameters with error mitigation."""
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
        logger.info(f"Successfully polled data layer. Found {len(records)} active anomalies.")
        return records, None
    except Exception as ex:
        # Catch connection failures and pass the context up to the UI gracefully
        return [], f"The persistence data layer is currently unreachable or initializing. Detail: {ex}"

# --- Streamlit Visual UI Layout Assembly ---
st.set_page_config(page_title="Bayou Produce Logistics Dashboard", page_icon="📦", layout="wide")
st.title("📦 Bayou Produce Logistics Automation Engine")
st.subheader("Decoupled Enterprise Local AI Core (Phase 6 Production Hardened)")

st.write("This dashboard monitors our local relational PostgreSQL layer inside a decoupled virtual container network, executing automated procurement logic and outbound webhook transfers on-premise.")

# Active Database Records Table Rendering
st.markdown("### 📊 Active Supply Chain Anomalies")
low_stock_data, db_error = query_low_stock_items()

# 🛡️ GRACEFUL ERROR HANDLING INTERFACE
if db_error:
    st.warning("⚠️ System Hardening Fallback Triggered")
    st.error(db_error)
    st.info("The application logging matrix has cataloged this event. Please verify that your container infrastructure is fully provisioned (`docker compose ps`).")
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
        
        # Unique target triggers for each independent item anomaly
        if st.button(f"Generate Procurement Draft for {item['item_name']}", key=f"gen_{item['item_name']}"):
            logger.info(f"Inference pipeline initialization requested for item: '{item['item_name']}'")
            st.info(f"Assembling contextual logistics schema payload and transferring to local LLM core...")
            
            prompt_context = f"""
            You are an automated logistics management system operating at Bayou Produce Distribution.
            An inventory threshold breach has occurred for the following item:
            - Item: {item['item_name']}
            - Current Stock Level: {item['current_stock']} units
            - Target Safety Limit: {item['minimum_threshold']} units
            - Vendor Assignment Point: {item['vendor_email']}
            
            Write a formal, brief procurement order email directed to the vendor assignment point requesting an expedited replenishment delivery of this product to reset our warehouse safety levels. Maintain a clear, professional supply chain tone. Do not generate placeholder text.
            """
            
            # ⏱️ INFRASTRUCTURE TELEMETRY: START PERFORMANCE TIMER
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": "llama3.2:1b", "prompt": prompt_context, "stream": False},
                    timeout=45 # Hard fence to prevent application hangs during heavy hardware strains
                )
                
                # ⏱️ INFRASTRUCTURE TELEMETRY: COMPUTE ELAPSED TIME
                latency = round(time.time() - start_time, 2)
                
                if response.status_code == 200:
                    generated_draft = response.json().get("response", "Error: Failed to safely parse output string.")
                    
                    # Log telemetric output data to terminal logs
                    logger.info(f"Local LLM Inference Complete. Latency: {latency}s | Token Payload generated for '{item['item_name']}'")
                    
                    st.success(f"📬 Automated Vendor Procurement Order Draft Assembled Successfully! (Inference Latency: {latency}s)")
                    
                    edited_draft = st.text_area(
                        label="Staged Email Transmission Text Container", 
                        value=generated_draft, 
                        height=280,
                        key=f"text_{item['item_name']}"
                    )
                    st.session_state[f"draft_{item['item_name']}"] = edited_draft
                else:
                    logger.warning(f"Ollama backend returned non-200 state: {response.status_code}")
                    st.error(f"Failed to communicate with inference engine. Status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                latency = round(time.time() - start_time, 2)
                logger.error(f"Local inference engine timeout triggered after {latency}s under heavy hardware load.")
                st.error("🚨 Local AI Inference Timeout: The system took longer than 45 seconds to generate a response. Please check local hardware utilization.")
            except Exception as e:
                logger.error(f"Critical execution break in local inference pipeline: {e}")
                st.error(f"Inference pipeline transport break: {e}")
        
        # Webhook routing mechanism
        if f"draft_{item['item_name']}" in st.session_state:
            st.markdown("#### 🚀 Automated Routing Core")
            if st.button(f"Transmit Document to Vendor Network via Webhook", key=f"send_{item['item_name']}"):
                logger.info(f"Outbound transmission pipeline initiated for payload: '{item['item_name']}'")
                st.info("Serializing document structures and executing HTTP POST transaction...")
                
                webhook_payload = {
                    "item_name": item['item_name'],
                    "vendor_email": item['vendor_email'],
                    "procurement_draft": st.session_state[f"draft_{item['item_name']}"]
                }
                
                try:
                    res = requests.post(VENDOR_API_URL, json=webhook_payload, timeout=10)
                    if res.status_code == 200:
                        server_response = res.json().get("message", "Processed successfully.")
                        logger.info(f"Webhook transmission confirmed by remote gateway. Destination: {VENDOR_API_URL}")
                        st.success(f"📥 Transaction Confirmed by Remote Endpoint: {server_response}")
                    else:
                        logger.warning(f"Remote gateway rejected webhook format. Status: {res.status_code}")
                        st.error(f"Webhook rejected by target gateway. Status Code: {res.status_code}")
                except Exception as ex:
                    logger.error(f"Network transport level connection failure during outbound webhook transmission: {ex}")
                    st.error(f"Network transport level connection failure: {ex}")
                    
        st.markdown("---")
else:
    st.success("✅ All warehouse stock metrics currently reside safely above operating baselines.")
