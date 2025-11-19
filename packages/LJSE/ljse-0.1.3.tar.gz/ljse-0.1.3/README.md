# LJSE

A lightweight Python package for accessing Ljubljana Stock Exchange (LJSE) data through the official REST API.

## Features

### `get_tickers()`
Returns a DataFrame containing all currently listed equities on the LJSE, including:
- symbol  
- ISIN  
- name  
- segment listing date  

Useful for discovering available tickers and metadata.

---

### `get_ticker_data(symbol)`
Downloads historical trading data for a specific LJSE symbol.  
The function automatically:
- resolves the correct ISIN  
- determines the listing date  
- fetches daily historical prices from the LJSE API  
- returns a time-indexed DataFrame containing only the column with the ticker’s last traded price  

## Example Usage

```python
from ljse import get_tickers, get_ticker_data

# list all securities
tickers = get_tickers()
print(tickers)

# download historical data for KRKA
df = get_ticker_data("KRKG")
print(df.tail())
```

© 2025 Janez Bučar. All rights reserved.