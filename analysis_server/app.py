from flask import Flask, request, jsonify
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/')
def index():
    """ Basic route to check if the server is running. """
    return "Analysis Server is running!"

@app.route('/log', methods=['POST'])
def receive_log():
    """ Endpoint to receive logs/data from the honeypot. """
    try:
        # Check if the request has JSON data
        if request.is_json:
            data = request.get_json()
            # Log the received data (you can process it further later)
            logging.info(f"Received data from honeypot: {data}")
            # Respond to the honeypot
            return jsonify({"status": "success", "message": "Data received"}), 200
        else:
            # Handle cases where data is not JSON (or add other content type checks)
            raw_data = request.get_data(as_text=True)
            logging.info(f"Received non-JSON data from honeypot: {raw_data}")
            return jsonify({"status": "warning", "message": "Received data, but expected JSON"}), 200

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Run the app, listening on all available interfaces (0.0.0.0)
    # and port 5000 (or choose another port if 5000 is taken)
    # Use debug=True only for development, remove or set to False for production
    logging.info("Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True) 