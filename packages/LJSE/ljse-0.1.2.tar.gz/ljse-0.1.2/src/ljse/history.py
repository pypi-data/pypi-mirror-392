# Copyright (c) 2025 Janez Bučar
# All rights reserved.

import pandas as pd
import datetime

from .tickers import get_tickers


def get_ticker_data(symbol: str, start: str = None, end: str = None, model: str = "ALL"):
    """
    Fetch historical trading data for a single LJSE ticker.

    Parameters
    ----------
    symbol : str
        LJSE ticker symbol (e.g. "KRKG", "TLSG").
        Must exist in the list returned by `get_tickers()`.

    start : str, optional
        Start date in 'YYYY-MM-DD' format.
        If None, the security's segment_listing_date is used.

    end : str, optional
        End date in 'YYYY-MM-DD' format.
        If None, today's date is used.

    model : str, optional
        Trading model:
            - "CT"    → Continuous trading
            - "AUCT"  → Auction model
            - "BLOCK" → Block trades
            - "ALL"   → All models (default)

    Returns
    -------
    pandas.DataFrame
        One-column DataFrame (column named after ticker), indexed by date.

    Raises
    ------
    ValueError
        If ticker does not exist on LJSE.

    Notes
    -----
    - Automatically resolves ISIN from get_tickers().
    - API returns CSV with an English schema.
    - If no data is returned, an empty DataFrame is returned.
    """

    # load listing table
    df = get_tickers()

    row = df[df["symbol"] == symbol]
    if row.empty:
        raise ValueError(f"Ticker '{symbol}' not found on LJSE")

    isin = row["isin"].iloc[0]

    # resolve start date
    if start is None:
        #raw = row["segment_listing_date"].iloc[0]
        raw = "2018-01-01" # ***** LJSE RESTRICTIONS
        try:
            start = pd.to_datetime(raw).strftime("%Y-%m-%d")
        except:
            start = "2018-01-01"

    # resolve end date
    if end is None:
        end = datetime.date.today().strftime("%Y-%m-%d")

    # ---- URL switching logic ----
    if model.upper() == "ALL":
        # correct ALL endpoint (NO trading_model_id)
        url_hist = (
            f"https://rest.ljse.si/web/Bvt9fe2peQ7pwpyYqODM/"
            f"security-history/XLJU/{isin}/{start}/{end}/csv?language=SI"
        )
    else:
        # CT / AUCT / BLOCK endpoint (WITH trading_model_id)
        url_hist = (
            f"https://rest.ljse.si/web/Bvt9fe2peQ7pwpyYqODM/"
            f"security-history/XLJU/{isin}/{start}/{end}/"
            f"csv?trading_model_id={model}&language=SI"
        )

    # fetch CSV
    df_hist = pd.read_csv(url_hist, sep=";")

    if "date" not in df_hist.columns:
        return pd.DataFrame()

    df_hist["date"] = pd.to_datetime(df_hist["date"])
    df_hist = df_hist.set_index("date")

    return df_hist
