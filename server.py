import logging
from flask import Flask, request, jsonify
import os
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

portfolio = []

@app.route('/buy_asset', methods=['POST'])
def buy_asset():
    try:
        logger.info("Received request to buy asset.")
        data = request.get_json()
        if not data or 'asset_name' not in data:
            logger.warning("Missing asset_name in the request.")
            return jsonify({"status": "error", "message": "Missing asset_name"}), 400
        asset_name = data['asset_name']
        portfolio.append(asset_name)
        send_telegram_message(f"Bought {asset_name}")
        logger.info(f"Asset {asset_name} successfully bought.")
        return jsonify({"status": "success", "message": f"Bought {asset_name}"}), 200
    except Exception as e:
        logger.error(f"Error occurred while buying asset: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sell_asset', methods=['POST'])
def sell_asset():
    try:
        logger.info("Received request to sell asset.")
        data = request.get_json()
        if not data or 'asset_name' not in data:
            logger.warning("Missing asset_name in the request.")
            return jsonify({"status": "error", "message": "Missing asset_name"}), 400
        asset_name = data['asset_name']
        if asset_name in portfolio:
            portfolio.remove(asset_name)
            send_telegram_message(f"Sold {asset_name}")
            logger.info(f"Asset {asset_name} successfully sold.")
            return jsonify({"status": "success", "message": f"Sold {asset_name}"}), 200
        else:
            logger.warning(f"Asset {asset_name} not found in portfolio.")
            return jsonify({"status": "error", "message": f"{asset_name} not found in portfolio"}), 404
    except Exception as e:
        logger.error(f"Error occurred while selling asset: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/view_portfolio', methods=['GET'])
def view_portfolio():
    try:
        logger.info("Received request to view portfolio.")
        return jsonify({"status": "success", "message": f"Current portfolio: {portfolio}"}), 200
    except Exception as e:
        logger.error(f"Error occurred while viewing portfolio: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def send_telegram_message(message):
    try:
        logger.info("Sending message to Telegram.")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"Error sending message to Telegram: {response.text}")
            raise Exception(f"Error sending message: {response.text}")
        logger.info("Message successfully sent to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
