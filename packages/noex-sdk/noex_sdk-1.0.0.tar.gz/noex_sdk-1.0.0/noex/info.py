import logging
from typing import Any, Dict, List, Optional
from .api import API
from .websocket_client import WebSocketClient
from .utils.constants import LOCAL_API_URL
from .utils.types import Order, OrderMode, OrderType, Subscription, Transaction, WalletBalance, WsCallback
from .utils.util import p2c
class Info:
    def __init__(self, url: Optional[str] = None, t: Optional[int] = None, ws_auto: bool = False):
        self.url = url or LOCAL_API_URL
        self.api = API(url=self.url, t=t)
        self.ws: Optional[WebSocketClient] = None
        self.l = logging.getLogger(__name__)
        if ws_auto:
            self.ws_connect()
    
    def ws_connect(self) -> None:
        if self.ws is None or not self.ws.is_alive():
            self.ws = WebSocketClient(url=self.url)
            self.ws.start()
            self.l.info("WebSocket client started")

    def ws_disconnect(self) -> None:
        if self.ws and self.ws.is_alive():
            self.ws.stop()
            self.l.info("WebSocket client stopped")

    def __enter__(self):
        self.ws_connect()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ws_disconnect()

    def l2_book(self, co: str) -> Dict[str, Any]:
        p = p2c(co).replace("/", "-")
        return self.api.l2Book(p)
    
    def wallets(self, wallets: List[str]) -> List[WalletBalance]:
        return self.api.get_wallets(wallets)
    
    def transactions(self, ens: str, limit: int = 100) -> List[Transaction]:
        return self.api.get_transactions(ens, limit)
    
    def orders(self) -> List[Order]:
        return self.api.get_orders()
    def mid_prices(self) -> Dict[str, Any]:
        return self.api.get_price()
    
    def trades(self) -> List[Dict[str, Any]]:
        return self.api.get_trades()
    
    def subscribe(self, sub: Subscription, cb: WsCallback) -> int:
        if self.ws is None or not self.ws.is_alive():
            raise RuntimeError("WebSocket not connected. Call connect_websocket() first.")
        return self.ws.subscribe(sub, cb)

    def unsubscribe(self, sub: Subscription, sid: int) -> bool:
        if self.ws is None or not self.ws.is_alive():
            return False
        return self.ws.unsubscribe(sub, sid)

    def subscribe_wallet(self, ens: str, cb: WsCallback) -> int:
        if self.ws is None or not self.ws.is_alive():
            raise RuntimeError("WebSocket not connected. Call connect_websocket() first.")
        return self.ws.subscribe_wallet(ens, cb)

    def subscribe_orderbook(self, c: str, cb: WsCallback) -> int:
        if self.ws is None or not self.ws.is_alive():
            raise RuntimeError("WebSocket not connected. Call connect_websocket() first.")
        return self.ws.subscribe_orderbook(c, cb)

    def subscribe_all_prices(self, cb: WsCallback) -> int:
        if self.ws is None or not self.ws.is_alive():
            raise RuntimeError("WebSocket not connected. Call connect_websocket() first.")
        return self.ws.subscribe_all_prices(cb)

    def health_check(self) -> Dict[str, str]:
        return self.api.health_check()
