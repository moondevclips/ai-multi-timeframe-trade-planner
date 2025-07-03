# To run this server:
# 1. Make sure you have Python installed.
# 2. Install the necessary libraries:
#    pip install Flask flask-cors alpaca-trade-api
# 3. Save this code as a file (e.g., server.py).
# 4. In your terminal, run the server: python server.py
# 5. Your backend will now be running at http://127.0.0.1:5000

from flask import Flask, request, jsonify
from flask_cors import CORS
import alpaca_trade_api as tradeapi

# --- Configuration ---
# IMPORTANT: For production, use environment variables instead of hardcoding keys.
# For local testing, you can place your keys here.
# These are your SANDBOX (Paper Trading) keys.
API_KEY = "CKB9CEGLVQ5AGAWLUFDL"
API_SECRET = "yBSIXCL4HNvwXJ2ZOd4Vu6zIbFdTYjqy1G60djct"
BASE_URL = "https://paper-api.alpaca.markets" # This is the sandbox URL

# --- Flask App Setup ---
app = Flask(__name__)
# CORS allows your frontend (running on a different domain) to talk to this backend.
CORS(app) 

# --- Alpaca API Client ---
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

# --- API Endpoint for Executing Trades ---
@app.route('/execute-trade', methods=['POST'])
def execute_trade():
    """
    Receives a trade plan from the frontend and submits it to the Alpaca API.
    """
    # Get the trade data sent from the frontend
    trade_data = request.get_json()

    if not trade_data:
        return jsonify({"message": "Invalid request body."}), 400

    # Extract required fields from the frontend data
    symbol = trade_data.get('symbol')
    qty = trade_data.get('qty')
    side = trade_data.get('side')
    order_type = trade_data.get('type')
    time_in_force = trade_data.get('time_in_force')
    order_class = trade_data.get('order_class')
    take_profit = trade_data.get('take_profit')
    stop_loss = trade_data.get('stop_loss')

    # Basic validation
    if not all([symbol, qty, side, order_type, time_in_force]):
        return jsonify({"message": "Missing required fields in trade data."}), 400

    try:
        # Log the order we are about to place
        print(f"Placing order for {qty} of {symbol}...")
        print(f"Details: {trade_data}")

        # Place the bracket order using the Alpaca API
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force,
            order_class=order_class,
            take_profit=take_profit,
            stop_loss=stop_loss
        )

        # Log the successful order response from Alpaca
        print(f"Order placed successfully. Order ID: {order.id}")

        # Send a success response back to the frontend
        return jsonify({
            "message": "Order submitted successfully!",
            "id": order.id,
            "symbol": order.symbol,
            "qty": order.qty,
            "status": order.status
        }), 200

    except Exception as e:
        # If anything goes wrong, log the error and send an error response
        print(f"Error placing order: {e}")
        return jsonify({"message": str(e)}), 500

# --- Main entry point to run the server ---
if __name__ == '__main__':
    # Runs the Flask app on localhost, port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
