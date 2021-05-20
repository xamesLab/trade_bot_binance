import websocket
from threading import *

msg, prev_msg = None, None

def on_message(ws, message):
    global msg
    msg = message

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("### connected ###")

def connection():
        ws = websocket.WebSocketApp("wss://fstream.binance.com/stream?streams=btcusdt@kline_5m",#/btcusdt@aggTrade
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()
        return

def start():
        t = Thread(target=connection)
        t.start()






    