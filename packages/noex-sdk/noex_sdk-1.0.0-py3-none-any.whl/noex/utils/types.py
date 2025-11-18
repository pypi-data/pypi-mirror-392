from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union
OrderType = Literal["buy", "sell"]
OrderMode = Literal["limit", "market"]
OrderStatus = Literal["pending", "partial", "filled", "cancelled"]
TransactionType = Literal["deposit", "withdraw"]
TransactionStatus = Literal["pending", "confirmed", "failed"]
WalletSub = TypedDict("WalletSub", {"type": Literal["wallet"], "ens": str}, total=False)
OrderbookSub = TypedDict("OrderbookSub", {"type": Literal["l2Book"], "coin": str})
PricesSub = TypedDict("PricesSub", {"type": Literal["allMids"]})
Subscription = Union[WalletSub, OrderbookSub, PricesSub]
WalletBalance = TypedDict("WalletBalance", {"id": int, "s": str, "b": float, "l": float})
Order = TypedDict("Order", {"id": int, "p": str, "t": str, "m": str, "pr": float, "am": float, "f": float, "st": str, "c": str}, total=False)
Transaction = TypedDict("Transaction", {"id": int, "t": str, "s": str, "am": float, "st": str, "c": str, "ad": str}, total=False)
Trade = TypedDict("Trade", {"id": int, "p": str, "pr": float, "am": float, "c": str})
OrderbookLevel = TypedDict("OrderbookLevel", {"pr": float, "am": float})

Orderbook = TypedDict("Orderbook", {
    "p": str,
    "bids": List[OrderbookLevel],
    "asks": List[OrderbookLevel]
})

Price = TypedDict("Price", {
    "p": str,
    "pr": float
})
WalletData = TypedDict("WalletData", {
    "assets": List[WalletBalance],
    "orders": List[Order],
    "transactions": List[Transaction]
})

WalletMessage = TypedDict("WalletMessage", {
    "type": Literal["wallet"],
    "data": WalletData
})

OrderbookMessage = TypedDict("OrderbookMessage", {
    "type": Literal["orderbook"],
    "data": Orderbook
})

PricesMessage = TypedDict("PricesMessage", {
    "type": Literal["prices"],
    "data": List[Price]
})

WsMessage = Union[WalletMessage, OrderbookMessage, PricesMessage]
WsCallback = Callable[[Any], None]
