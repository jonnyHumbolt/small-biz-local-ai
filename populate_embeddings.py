import os
import sys
import psycopg2
from sentence_transformers import SentenceTransformer

# 🔒 Pull configuration dynamically from local host environment defaults
DB_HOST = "127.0.0.1"  # Script runs locally from the terminal to hit the exposed port
DB_NAME = "inventory_db"
DB_USER = "postgres"
DB_PASSWORD = "local_secure_pass"

print("🚀 Waking up Ephemeral Embedding Engine...")
print("📦 Loading PyTorch and sentence-transformers into host RAM (allocating ~750MB)...")
# Initialize the high-efficiency 384-dimension embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def ingest_knowledge():
    # 1. Establish connection to your active containerized database
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=5432
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Connection Failure: Ensure 'docker compose up -d' is active. Detail: {e}")
        sys.exit(1)

    # 2. Build the dedicated Vector Knowledge table
    # We define a 'vector(384)' column matching the mathematical size of all-MiniLM-L6-v2
    cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE IF NOT EXISTS vendor_knowledge_vectors (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(384)
        );
        TRUNCATE TABLE vendor_knowledge_vectors; -- Clear old runs for a fresh chunk ingest
    """)
    conn.commit()

    # 3. Read and process our source knowledge documents
    doc_path = "knowledge_base/vendor_policies.txt"
    if not os.path.exists(doc_path):
        print(f"❌ Target document not found at {doc_path}")
        return

    with open(doc_path, "r") as file:
        lines = file.readlines()

    print(f"📥 Found {len(lines)} distinct semantic blocks to vectorize.")

    # 4. Sequential Stream Pattern: Generate vectors and insert line-by-line
    for line in lines:
        clean_line = line.strip()
        if not clean_line or len(clean_line) < 10:
            continue # Skip blank lines or line breaks

        print(f"🧠 Vectorizing text fragment: '{clean_line[:40]}...'")
        
        # Compute the mathematical vector array (384 floating-point coordinates)
        vector_embedding = model.encode(clean_line).tolist()

        # Insert the string alongside its vector coordinates directly into PostgreSQL
        cursor.execute(
            "INSERT INTO vendor_knowledge_vectors (content, embedding) VALUES (%s, %s);",
            (clean_line, vector_embedding)
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Vector data successfully pushed into the containerized PostgreSQL engine.")

if __name__ == "__main__":
    ingest_knowledge()
    print("💀 Terminating script context. Releasing PyTorch framework from active RAM...")
    # Script exits here, instantly cleaning your machine's 8GB memory footprint.
