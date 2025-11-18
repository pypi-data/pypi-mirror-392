import json
import logging
from typing import Any, Dict, List, Optional
import requests
from .utils.constants import DEFAULT_TIMEOUT, LOCAL_API_URL
from .utils.error import AuthenticationError, ClientError, ServerError
from .utils.types import Order, OrderMode, OrderType, Transaction, TransactionType, WalletBalance

class API:
    def __init__(self, url: Optional[str] = None, t: Optional[int] = None):
        self.url = url or LOCAL_API_URL
        self.s = requests.Session()
        self.s.headers.update({"Content-Type": "application/json"})
        self.t = t or DEFAULT_TIMEOUT
        self.l = logging.getLogger(__name__)
        self.tk: Optional[str] = None

    def set_token(self, tk: str) -> None:
        self.tk = tk
        self.s.headers.update({"Authorization": f"Bearer {tk}"})

    def clear_token(self) -> None:
        self.tk = None
        if "Authorization" in self.s.headers:
            del self.s.headers["Authorization"]

    def req(self, m: str, p: str, **kw) -> Any:
        u = self.url + p
        kw.setdefault("timeout", self.t)
        try:
            r = self.s.request(m, u, **kw)
            self.handle_exc(r)
            if r.text:
                try:
                    return r.json()
                except ValueError:
                    return {"error": f"Could not parse JSON: {r.text}"}
            return {}
        except requests.exceptions.RequestException as e:
            self.l.error(f"Request failed: {e}")
            raise

    def handle_exc(self, r: requests.Response) -> None:
        sc = r.status_code
        if sc < 400:
            return
        if 400 <= sc < 500:
            try:
                err = r.json()
                em = err.get("detail", r.text)
            except (ValueError, json.JSONDecodeError):
                em = r.text
            if sc == 401:
                raise AuthenticationError(em)
            raise ClientError(sc, em, r.text, r.headers)
        raise ServerError(sc, r.text)

    def reg(self, pk: str, ens: str, pw: str) -> Dict[str, str]:
        pl = {"pk": pk, "ens": ens, "pw": pw}
        r = self.req("POST", "/auth/register", json=pl)
        if "access_token" in r:
            self.set_token(r["access_token"])
        self.tk = r.get("access_token")
        return r

    def login(self, id: str, pw: str) -> Dict[str, str]:
        pl = {"identifier": id, "pw": pw}
        r = self.req("POST", "/auth/login", json=pl)
        if "access_token" in r:
            self.set_token(r["access_token"])
        self.tk = r.get("access_token")
        return r

    def get_wallets(self, ids: List[str]) -> List[WalletBalance]:
        return self.req("GET", f"/wallets?ids={','.join(ids)}")

    def create_order(self, p: str, t: OrderType, m: OrderMode, am: float, pr: Optional[float] = None) -> Order:
        pl = {"p": p, "t": t, "m": m, "am": am}
        if pr is not None:
            pl["pr"] = pr
        return self.req("POST", "/orders", json=pl)

    def get_orders(self) -> List[Order]:
        return self.req("GET", "/orders")

    def cancel_order(self, oid: int) -> Dict[str, bool]:
        return self.req("DELETE", f"/orders/{oid}")

    def l2Book(self, p: str) -> Dict[str, Any]:
        return self.req("GET", f"/orderbook/{p}")

    def get_price(self, p: str) -> Dict[str, Any]:
        return self.req("GET", f"/price/{p}")

    def get_all_prices(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.req("GET", "/prices")

    def get_pairs(self) -> Dict[str, List[str]]:
        return self.req("GET", "/pairs")

    def get_trades(self, p: str) -> List[Dict[str, Any]]:
        return self.req("GET", f"/trades/{p}")

    def create_transaction(self, t: TransactionType, s: str, am: float, ad: Optional[str] = None) -> Transaction:
        pl = {"t": t, "s": s, "am": am}
        if ad:
            pl["ad"] = ad
        return self.req("POST", "/transactions", json=pl)

    def get_transactions(self) -> List[Transaction]:
        return self.req("GET", "/transactions")

    def health_check(self) -> Dict[str, str]:
        return self.req("GET", "/")
