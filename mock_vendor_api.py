from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

@app.route('/api/v1/orders', methods=['POST'])
def receive_procurement_order():
    """🚀 Mock Gateway Endpoint acting as an external Vendor ERP System."""
    payload = request.get_json()
    
    if not payload:
        return jsonify({"status": "REJECTED", "error": "Missing JSON payload space"}), 400
        
    # Extract data fields transmitted across the virtual container network
    item = payload.get("item_name")
    vendor = payload.get("vendor_email")
    order_text = payload.get("procurement_draft")
    
    # Print a heavy structural confirmation receipt to the container log output
    print("\n" + "="*60, file=sys.stderr)
    print("📥 [MOCK VENDOR GATEWAY] INBOUND WEBHOOK TRANSMISSION DETECTED", file=sys.stderr)
    print(f"📦 Target Product  : {item}", file=sys.stderr)
    print(f"📧 Routing Point  : {vendor}", file=sys.stderr)
    print(f"📝 Document Payload:\n\n{order_text}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    
    return jsonify({
        "status": "SUCCESSFULLY_PROCESSED",
        "message": f"Procurement order payload for '{item}' received and logged securely by vendor system."
    }), 200

if __name__ == '__main__':
    # Listen on port 5000 inside the container virtual network space
    app.run(host='0.0.0.0', port=5000, debug=True)
