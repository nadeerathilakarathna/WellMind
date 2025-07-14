import socket
import threading
import time

class InternetEventListener:
    def __init__(self, on_internet_change=None):
        self.was_connected = None
        self.on_internet_change = on_internet_change
        self._thread = threading.Thread(target=self._monitor, daemon=True)

    def start(self):
        self._thread.start()

    def _monitor(self):
        while True:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                if self.was_connected is not True:
                    print("[🌐] Internet Connected")
                    self.was_connected = True
                    if self.on_internet_change:
                        self.on_internet_change("connected")
            except OSError:
                if self.was_connected is not False:
                    print("[❌] Internet Disconnected")
                    self.was_connected = False
                    if self.on_internet_change:
                        self.on_internet_change("disconnected")
            time.sleep(5)
