import threading
import json
import urllib.request
from gi.repository import GLib, GObject

class PriceService(GObject.Object):
    __gsignals__ = {
        'prices-updated': (GObject.SignalFlags.RUN_LAST, None, ()),
        'update-failed': (GObject.SignalFlags.RUN_LAST, None, (str,))
    }

    def __init__(self):
        super().__init__()
        self.btc_price = 0.0
        self.stx_price = 0.0

    def fetch_prices(self):
        thread = threading.Thread(target=self._fetch_worker)
        thread.daemon = True
        thread.start()

    def _fetch_worker(self):
        try:
            # Fetch BOTH Bitcoin and Stacks in a single request
            # IDs: bitcoin, blockstack (STX)
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,blockstack&vs_currencies=usd"

            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 FireFinance/1.0'}
            )

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

                # Parse BTC
                if "bitcoin" in data and "usd" in data["bitcoin"]:
                    self.btc_price = data["bitcoin"]["usd"]

                # Parse STX
                if "blockstack" in data and "usd" in data["blockstack"]:
                    self.stx_price = data["blockstack"]["usd"]

            GLib.idle_add(self._emit_success)

        except Exception as e:
            # If network fails, we just log it and don't emit success,
            # so the UI keeps using the default/cached values.
            error_msg = str(e)
            print(f"Network Error: {error_msg}")
            GLib.idle_add(self._emit_failure, error_msg)

    def _emit_success(self):
        self.emit('prices-updated')
        return False

    def _emit_failure(self, error_msg):
        self.emit('update-failed', error_msg)
        return False
