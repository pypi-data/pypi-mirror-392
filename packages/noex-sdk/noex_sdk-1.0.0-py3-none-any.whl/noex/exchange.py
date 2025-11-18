import logging
from typing import Any, Dict, List, Optional

from .info import Info
from .api import API
from .websocket_client import WebSocketClient
from .utils.constants import LOCAL_API_URL
from .utils.types import Order, OrderMode, OrderType, Subscription, Transaction, WalletBalance, WsCallback
from .utils.util import p2c
class Exchange:
    def __init__(self, url: Optional[str] = None, t: Optional[int] = None, ws_auto: bool = False):
        self.url = url or LOCAL_API_URL
        self.api = API(url=self.url, t=t)
        self.info = Info(url=self.url, t=t)
        self.ws: Optional[WebSocketClient] = None
        self.l = logging.getLogger(__name__)
        self.pk = ""
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

    def reg(self, pk: str, ens: str, pw: str) -> Dict[str, str]:
        r = self.api.reg(pk, ens, pw)
        self.pk = pk
        return r
        
    def login(self, pk: str, pw: str) -> Dict[str, str]:
        r = self.api.login(pk, pw)
        self.pk = pk
        return r
    
    def place_order(self, co: str, t: OrderType, m: OrderMode, am: float, pr: Optional[float] = None) -> Order:
        p = p2c(co)
        return self.api.create_order(p, t, m, am, pr)

    def m_buy(self, co: str, am: float) -> Order:
        return self.place_order(co, "buy", "market", am)

    def m_sell(self, co: str, am: float) -> Order:
        return self.place_order(co , "sell", "market", am)

    def l_buy(self, co: str, am: float, pr: float) -> Order:
        return self.place_order(co, "buy", "limit", am, pr)
    
    def l_sell(self, co: str, am: float, pr: float) -> Order:
        return self.place_order(co, "sell", "limit", am, pr)

    def cancel_order(self, oid: int) -> Dict[str, bool]:
        return self.api.cancel_order(oid)

    def deposit(self, s: str, am: float, ad: Optional[str] = None) -> Transaction:
        return self.api.create_transaction("deposit", s, am, ad)

    def withdraw(self, s: str, am: float, ad: str) -> Transaction:
        return self.api.create_transaction("withdraw", s, am, ad)

    def health_check(self) -> Dict[str, str]:
        return self.api.health_check()
