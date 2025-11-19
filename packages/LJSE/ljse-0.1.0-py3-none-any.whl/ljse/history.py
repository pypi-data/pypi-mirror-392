import pandas as pd
import datetime

from .tickers import get_tickers

def get_ticker_data(symbol: str, start: str = None, end: str = None, model: str = None):
    """
    Fetch historical trading data for a selected LJSE ticker.

    Parameters
    ----------
    symbol : str
        The ticker symbol of the security (e.g., "KRKG", "TLSG").
        Must exist in the list returned by `get_tickers()`.

    start : str, optional
        Start date in the format 'YYYY-MM-DD'.
        If None, the function automatically uses the `segment_listing_date`
        provided by the LJSE securities API.

    end : str, optional
        End date in the format 'YYYY-MM-DD'.
        If None, today's date is used.

    model : str, optional
        Trading model used by the LJSE API.
        Valid values:
            - "AUCT"  → Auction model
            - "CT"    → Continuous trading
            - "BLOCK" → Block trades
            - "ALL"   → All models combined (default)
        If None, it defaults to "ALL".

    Returns
    -------
    pandas.DataFrame
        A DataFrame indexed by date (DatetimeIndex) containing only one column:
        the last traded price named after the ticker symbol.

        Example:
                KRKG
        2023-01-02  56.2
        2023-01-03  56.4
        2023-01-04  57.0

    Raises
    ------
    ValueError
        If the provided ticker symbol does not exist on the LJSE.

    Notes
    -----
    - The function automatically resolves the correct ISIN using `get_tickers()`.
    - The LJSE historical endpoint requires dates in ISO format (YYYY-MM-DD).
    - If the API returns no data, an empty DataFrame is returned.
    """

    if model is None:
        model = "ALL"

    df = get_tickers()

    row = df[df["symbol"] == symbol]
    if row.empty:
        raise ValueError(f"Ticker '{symbol}' not found on LJSE")

    isin = row["isin"].iloc[0]

    # resolve start date
    if start is None:
        raw = row["segment_listing_date"].iloc[0]
        try:
            start = pd.to_datetime(raw).strftime("%Y-%m-%d")
        except:
            start = "2000-01-01"

    # resolve end date
    if end is None:
        end = datetime.date.today().strftime("%Y-%m-%d")

    # request historical data
    url_hist = (
        f"https://rest.ljse.si/web/Bvt9fe2peQ7pwpyYqODM/security-history/XLJU/"
        f"{isin}/{start}/{end}/csv?trading_model_id={model}&language=SI"
    )

    df_hist = pd.read_csv(url_hist, sep=";")

    if "date" not in df_hist.columns:
        return pd.DataFrame()

    df_hist["date"] = pd.to_datetime(df_hist["date"])
    df_hist = df_hist.set_index("date")
    df_hist = df_hist.rename(columns={"last_price": symbol})

    return df_hist[[symbol]]