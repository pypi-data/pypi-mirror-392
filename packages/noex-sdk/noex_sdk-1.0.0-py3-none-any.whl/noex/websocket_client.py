import json
import logging
import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple
import websocket
from .utils.constants import LOCAL_API_URL, WEBSOCKET_PING_INTERVAL
from .utils.error import WebSocketError
from .utils.types import Subscription, WsCallback, WsMessage

class WebSocketClient(threading.Thread):
    def __init__(self, url: Optional[str] = None):
        super().__init__()
        self.daemon = True
        self.url = url or LOCAL_API_URL
        ws_url = "ws" + self.url[len("http"):]+"/ws"
        self.ready = False
        self.subs: Dict[str, List[Tuple[int, WsCallback]]] = defaultdict(list)
        self.sid = 0
        self.q_subs: List[Tuple[Dict[str, Any], int, WsCallback]] = []
        self.ws = websocket.WebSocketApp(ws_url, on_message=self._on_msg,
                                        on_open=self._on_open, on_error=self._on_err,
                                        on_close=self._on_close)
        self.ping = threading.Thread(target=self._ping, daemon=True)
        self.stop_evt = threading.Event()
        self.l = logging.getLogger(__name__)

    def run(self) -> None:
        self.ping.start()
        self.ws.run_forever()

    def _ping(self) -> None:
        while not self.stop_evt.wait(WEBSOCKET_PING_INTERVAL):
            if not self.ws.keep_running:
                break
            try:
                self.l.debug("WebSocket sending ping")
                self.ws.send(json.dumps({"method": "ping"}))
            except Exception as e:
                self.l.error(f"Error sending ping: {e}")
                break
        self.l.debug("WebSocket ping sender stopped")

    def stop(self) -> None:
        self.stop_evt.set()
        self.ws.close()
        if self.ping.is_alive():
            self.ping.join(timeout=2)

    def _on_open(self, ws) -> None:
        self.l.info("WebSocket connection established")
        self.ready = True
        for s, sid, cb in self.q_subs:
            self._sub_internal(s, sid, cb)
        self.q_subs.clear()

    def _on_close(self, ws, csc, cm) -> None:
        self.l.info(f"WebSocket connection closed: {csc} - {cm}")
        self.ready = False

    def _on_err(self, ws, e) -> None:
        self.l.error(f"WebSocket error: {e}")

    def _on_msg(self, ws, m: str) -> None:
        if m == "Websocket connection established.":
            self.l.debug(m)
            return
        self.l.debug(f"WebSocket message: {m}")
        try:
            d: WsMessage = json.loads(m)
            mt = d.get("type")
            if mt == "pong":
                self.l.debug("WebSocket received pong")
                return
            ident = self._get_subscription_identifier(d)
            if ident and ident in self.subs:
                for sid, cb in self.subs[ident]:
                    try:
                        cb(d)
                    except Exception as e:
                        self.l.error(f"Error in callback for {ident}: {e}")
            else:
                self.l.debug(f"No subscription found for message type: {mt}")
        except json.JSONDecodeError:
            self.l.error(f"Failed to decode message: {m}")
        except Exception as e:
            self.l.error(f"Error processing message: {e}")

    def _get_subscription_identifier(self, m: WsMessage) -> Optional[str]:
        mt = m.get("type")
        if mt == "wallet":
            return "wallet"
        elif mt == "orderbook":
            p = m.get("data", {}).get("p", "")
            return f"orderbook:{p}"
        elif mt == "prices":
            return "allMids"
        return None

    def _sub_internal(self, s: Dict[str, Any], sid: int, cb: WsCallback) -> None:
        if s["type"] == "wallet":
            ident = "wallet"
        elif s["type"] == "l2Book":
            c = s["coin"]
            ident = f"orderbook:{c}/USDT"
        elif s["type"] == "allMids":
            ident = "allMids"
        else:
            ident = s["type"]
        self.subs[ident].append((sid, cb))
        m = {"action": "subscribe", **s}
        self.l.debug(f"Subscribing: {m}")
        self.ws.send(json.dumps(m))

    def subscribe(self, s: Subscription, cb: WsCallback) -> int:
        self.sid += 1
        sid = self.sid
        if not self.ready:
            self.l.debug("WebSocket not ready, queueing subscription")
            self.q_subs.append((s, sid, cb))
        else:
            self._sub_internal(s, sid, cb)
        return sid

    def unsubscribe(self, s: Subscription, sid: int) -> bool:
        if not self.ready:
            raise WebSocketError("Cannot unsubscribe before WebSocket is connected")
        if s["type"] == "wallet":
            ident = "wallet"
        elif s["type"] == "l2Book":
            c = s["coin"]
            ident = f"orderbook:{c}/USDT"
        elif s["type"] == "allMids":
            ident = "allMids"
        else:
            ident = s["type"]
        if ident in self.subs:
            ol = len(self.subs[ident])
            self.subs[ident] = [(sid2, cb2) for sid2, cb2 in self.subs[ident] if sid2 != sid]
            if len(self.subs[ident]) == 0:
                m = {"action": "unsubscribe", **s}
                self.l.debug(f"Unsubscribing: {m}")
                self.ws.send(json.dumps(m))
                del self.subs[ident]
            return len(self.subs[ident]) < ol
        return False

    def subscribe_wallet(self, ens: str, cb: WsCallback) -> int:
        return self.subscribe({"type": "wallet", "ens": ens}, cb)

    def subscribe_orderbook(self, c: str, cb: WsCallback) -> int:
        return self.subscribe({"type": "l2Book", "coin": c}, cb)

    def subscribe_all_prices(self, cb: WsCallback) -> int:
        return self.subscribe({"type": "allMids"}, cb)
