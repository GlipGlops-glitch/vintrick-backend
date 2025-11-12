#    python tools/bit/socket_hummy.py
import websocket
import json

def on_message(ws, message):
    msg = json.loads(message)
    if msg.get("type") == "ticker":
        # Print the whole ticker message in pretty JSON for debugging
        print("Full ticker message:")
        print(json.dumps(msg, indent=2))
        # Print just the price and some other key fields for quick viewing
        print(f"BTC/USD Price: {msg.get('price')}")
        print(f"Best Bid: {msg.get('best_bid')}")
        print(f"Best Ask: {msg.get('best_ask')}")
        print(f"Time: {msg.get('time')}")
        print('-' * 40)  # separator

def on_open(ws):
    subscribe_message = {
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channels": ["ticker"]
    }
    ws.send(json.dumps(subscribe_message))

if __name__ == "__main__":
    ws_url = "wss://ws-feed.exchange.coinbase.com"
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_open=on_open)
    ws.run_forever()