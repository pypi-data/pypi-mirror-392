# noex Python SDK

Official Python SDK for the noex cryptocurrency exchange platform.

## Features

- 🔐 **Authentication**: Register and login with wallet-based authentication
- 💼 **Wallet Management**: View and manage multi-currency balances
- 📊 **Trading**: Place limit and market orders, view order history
- 📈 **Market Data**: Access orderbooks, prices, and recent trades
- 💸 **Transactions**: Deposit and withdraw cryptocurrencies
- 🔌 **WebSocket**: Real-time updates for wallet, orderbook, and prices
- ✅ **Fully Typed**: Complete type hints for better IDE support
- 🧪 **Well Tested**: Comprehensive unit tests

## Installation

```bash
pip install noex-sdk
```

Or install from source:

```bash
git clone https://github.com/noex/noex-sdk-python.git
cd noex-sdk-python
pip install -e .
```

## Quick Start

### Basic Usage

```python
from noex import Exchange

# Initialize the exchange client
exchange = Exchange(base_url="http://localhost:8000")

# Register a new account
exchange.register(
    public_key="0x37F5260604F3c346E0037619C34c1Ed260206B55",
    ens="user.eth",
    password="securePassword123"
)

# Or login to existing account
exchange.login("user.eth", "securePassword123")

# Get wallet balances
wallets = exchange.get_wallets()
for wallet in wallets:
    print(f"{wallet['s']}: {wallet['b']} (locked: {wallet['l']})")

# Get current price
price = exchange.get_price("BTC/USDT")
print(f"BTC/USDT: ${price['pr']}")

# Place a limit buy order
order = exchange.limit_buy("BTC/USDT", amount=0.01, price=45000.0)
print(f"Order placed: {order['id']}")

# Cancel an order
exchange.cancel_order(order['id'])
```

### WebSocket Usage

```python
from noex import Exchange
import time

# Initialize with WebSocket auto-connect
exchange = Exchange(base_url="http://localhost:8000", auto_connect_ws=True)
exchange.login("user.eth", "securePassword123")

# Define callback for price updates
def on_price_update(message):
    prices = message['data']
    for price in prices:
        print(f"{price['p']}: ${price['pr']}")

# Subscribe to price updates
sub_id = exchange.subscribe_all_prices(on_price_update)

# Listen for updates
time.sleep(30)

# Unsubscribe
exchange.unsubscribe({"type": "allMids"}, sub_id)
exchange.disconnect_websocket()
```

## API Reference

### Exchange Client

The `Exchange` class is the main entry point for the SDK.

#### Initialization

```python
Exchange(base_url=None, timeout=None, auto_connect_ws=False)
```

- `base_url`: API base URL (default: `http://localhost:8000`)
- `timeout`: Request timeout in seconds (default: 30)
- `auto_connect_ws`: Auto-connect WebSocket on initialization

#### Authentication

- `register(public_key, ens, password)` - Register new account
- `login(identifier, password)` - Login to existing account

#### Wallet

- `get_wallets()` - Get all wallet balances

#### Trading

- `create_order(pair, order_type, mode, amount, price=None)` - Create order
- `market_buy(pair, amount)` - Create market buy order
- `market_sell(pair, amount)` - Create market sell order
- `limit_buy(pair, amount, price)` - Create limit buy order
- `limit_sell(pair, amount, price)` - Create limit sell order
- `get_orders()` - Get all orders
- `cancel_order(order_id)` - Cancel an order

#### Market Data

- `l2Book(pair)` - Get orderbook
- `get_price(pair)` - Get current price
- `get_all_prices()` - Get all prices
- `get_pairs()` - Get available trading pairs
- `get_trades(pair)` - Get recent trades

#### Transactions

- `deposit(symbol, amount, address=None)` - Create deposit
- `withdraw(symbol, amount, address)` - Create withdrawal
- `get_transactions()` - Get transaction history

#### WebSocket

- `connect_websocket()` - Connect WebSocket client
- `disconnect_websocket()` - Disconnect WebSocket client
- `subscribe_wallet(ens, callback)` - Subscribe to wallet updates
- `subscribe_orderbook(coin, callback)` - Subscribe to orderbook updates
- `subscribe_all_prices(callback)` - Subscribe to price updates
- `subscribe(subscription, callback)` - Generic subscribe method
- `unsubscribe(subscription, subscription_id)` - Unsubscribe from updates

## Examples

The `examples/` directory contains complete working examples:

- `basic_usage.py` - Basic REST API operations
- `websocket_example.py` - WebSocket subscriptions
- `trading_bot.py` - Simple trading bot implementation

Run an example:

```bash
cd examples
python basic_usage.py
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/noex/noex-sdk-python.git
cd noex-sdk-python

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=noex --cov-report=html

# Run specific test file
python -m pytest tests/test_api_client.py
```

### Code Formatting

```bash
# Format code with black
black noex/ tests/ examples/

# Check with flake8
flake8 noex/ tests/ examples/

# Type checking with mypy
mypy noex/
```

## Data Types

The SDK uses abbreviated field names to match the API:

- `p` - pair (e.g., "BTC/USDT")
- `t` - type (e.g., "buy", "sell", "deposit")
- `m` - mode (e.g., "limit", "market")
- `pr` - price
- `am` - amount
- `f` - filled amount
- `st` - status
- `s` - symbol
- `b` - balance
- `l` - locked
- `c` - created_at
- `ad` - address

See `noex/utils/types.py` for complete type definitions.

## Error Handling

The SDK provides specific exception classes:

```python
from noex import NoexError, ClientError, ServerError, AuthenticationError, WebSocketError

try:
    exchange.login("user.eth", "wrong_password")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ClientError as e:
    print(f"Client error {e.status_code}: {e.error_message}")
except ServerError as e:
    print(f"Server error {e.status_code}: {e.message}")
```

## Configuration

### Environment Variables

You can configure the SDK using environment variables:

```bash
export NOEX_API_URL="http://localhost:8000"
export NOEX_API_TIMEOUT="30"
```

### API URLs

Predefined URL constants:

```python
from noex import LOCAL_API_URL, TESTNET_API_URL, MAINNET_API_URL

# Use testnet
exchange = Exchange(base_url=TESTNET_API_URL)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Email: dev@noex.io
- 💬 Discord: https://discord.gg/noex
- 📚 Documentation: https://docs.noex.io

## Links

- [API Documentation](../API_DOCUMENTATION.md)
- [WebSocket Documentation](../WEBSOCKET_UNIFIED.md)
- [GitHub Repository](https://github.com/noex/noex-sdk-python)
