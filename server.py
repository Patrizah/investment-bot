import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Використання змінних середовища для захисту конфіденційних даних
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

portfolio = []

@app.route('/buy_asset', methods=['POST'])
def buy_asset():
    try:
        app.logger.info("Received request to buy asset.")
        data = request.get_json()
        if not data or 'asset_name' not in data:
            app.logger.warning("Missing asset_name in the request.")
            return jsonify({"status": "error", "message": "Missing asset_name"}), 400
        asset_name = data['asset_name']
        portfolio.append(asset_name)
        send_telegram_message(f"Bought {asset_name}")
        return jsonify({"status": "success", "message": f"Bought {asset_name}"}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sell_asset', methods=['POST'])
def sell_asset():
    try:
        app.logger.info("Received request to sell asset.")
        data = request.get_json()
        if not data or 'asset_name' not in data:
            app.logger.warning("Missing asset_name in the request.")
            return jsonify({"status": "error", "message": "Missing asset_name"}), 400
        asset_name = data['asset_name']
        if asset_name in portfolio:
            portfolio.remove(asset_name)
            send_telegram_message(f"Sold {asset_name}")
            return jsonify({"status": "success", "message": f"Sold {asset_name}"}), 200
        else:
            app.logger.warning(f"Asset {asset_name} not found in portfolio.")
            return jsonify({"status": "error", "message": f"{asset_name} not found in portfolio"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/view_portfolio', methods=['GET'])
def view_portfolio():
    try:
        app.logger.info("Received request to view portfolio.")
        return jsonify({"status": "success", "message": f"Current portfolio: {portfolio}"}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            app.logger.error(f"Error sending message to Telegram: {response.text}")
            raise Exception(f"Error sending message: {response.text}")
    except Exception as e:
        app.logger.error(f"Failed to send Telegram message: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
