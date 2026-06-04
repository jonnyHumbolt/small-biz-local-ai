import ollama

# Our mock business name variable
business_name = "Bayou Fresh Grocers"

print("🔄 Initializing connection to local Llama 3.2 1B model...")

try:
    # Trigger a clean handshake request with our local background service
    response = ollama.generate(
        model="llama3.2:1b", 
        prompt=f"Respond with exactly one sentence saying hello to the owner of {business_name}."
    )
    
    # Print the resulting text
    print("\n--- SYSTEM RESPONSE ---")
    print(response['response'].strip())
    print("-----------------------\n")
    print("✅ Infrastructure connection test: PASSED")

except Exception as e:
    print(f"\n❌ Connection failed. Error details: {e}")
