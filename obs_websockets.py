import time
import sys
from obswebsocket import obsws, requests
from websockets_auth import WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_PASSWORD

class OBSWebsocketsManager:
    ws = None

    def __init__(self):
        self.ws = obsws(WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_PASSWORD)

        try:
            self.ws.connect()
        except:
            print("\nPANIC!!\nCOULD NOT CONNECT TO OBS!\nDouble check that you have OBS open and that your websockets server is enabled in OBS.")
            time.sleep(10)
            sys.exit()
        
        print("Connected to OBS Websockets\n")

    def disconnect(self):
        self.ws.disconnect()