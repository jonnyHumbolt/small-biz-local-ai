import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import ollama

DB_HOST = "127.0.0.1"
DB_NAME = "inventory_db"
DB_USER = "postgres"
DB_PASSWORD = "local_secure_pass"
MODEL_NAME = "llama3.2:1b"

def execute_local_sql(sql_query):
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=5432
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        return f"❌ SQL Runtime Error: {e}"

def run_agent_loop():
    print("\n" + "="*60)
    print("🤖 Bayou Produce Data Analyst Agent Terminal Active")
    print(f"🧠 Local Model Engine: {MODEL_NAME} | ⚡ Architecture: Decoupled CLI")
    print("Type 'exit' or 'quit' to terminate the session.")
    print("="*60 + "\n")

    system_prompt = """
    You are an autonomous AI Data Analyst operating locally at Bayou Produce Distribution.
    Your job is to translate user natural language questions into precise, raw PostgreSQL queries.
    
    You have direct visibility over the following database tables and columns:
    1. Table: inventory_health
       Columns:
       - item_name (TEXT, Primary Key)
       - current_stock (INTEGER)
       - minimum_threshold (INTEGER)
       - vendor_email (TEXT)
       - status (TEXT, values: 'OK', 'CRITICAL_LOW')
       
    2. Table: vendor_knowledge_vectors
       Columns:
       - id (SERIAL, Primary Key)
       - content (TEXT)
       - embedding (vector)
       
    CRITICAL OUTPUT RULE:
    When a user asks a data question, you must answer ONLY with the raw SQL code block. 
    Do not include markdown code ticks (like ```sql), do not write conversational filler, and do not explain your thought process. 
    Just output a single executable SQL string that begins with SELECT.

    EXAMPLES OF CORRECT LOGIC:
    User: "How many total vendor policies do we have stored?"
    Query: SELECT COUNT(*) FROM vendor_knowledge_vectors;

    User: "Give me just the item names and their current stock numbers."
    Query: SELECT item_name, current_stock FROM inventory_health;

    User: "Show me all items that are critically low."
    Query: SELECT * FROM inventory_health WHERE status = 'CRITICAL_LOW';
    """

    while True:
        try:
            user_input = input("✨ Ask the Agent: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("\n👋 Powering down Analyst Agent Core. Exiting pipeline workspace.")
                break
                
            if not user_input.strip():
                continue

            print("🧠 Analyzing intent and generating SQL block via Ollama...")
            
            response = ollama.generate(
                model=MODEL_NAME,
                system=system_prompt,
                prompt=user_input,
                options={"temperature": 0.0}
            )
            
            generated_sql = response['response'].strip()
            
            if generated_sql.startswith("```"):
                generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
            
            print(f"⚙️  Generated Tool Call: \033[94m{generated_sql}\033[0m")
            print("🚀 Executing raw SQL inside database container network...")
            
            query_results = execute_local_sql(generated_sql)
            
            print("\n📊 Database Results Summary:")
            print("-" * 40)
            if isinstance(query_results, list):
                if len(query_results) == 0:
                    print("⚠️  Query successfully processed, but returned zero rows.")
                else:
                    for row in query_results:
                        print(dict(row))
            else:
                print(query_results)
            print("-" * 40 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Terminal interrupt intercepted. Shutting down loop.")
            break
        except Exception as ex:
            print(f"❌ Core Pipeline Exception: {ex}\n")

if __name__ == "__main__":
    run_agent_loop()
