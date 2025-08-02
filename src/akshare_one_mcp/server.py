from datetime import datetime
from typing import Annotated, Literal

import akshare as ak
import akshare_one as ako
from akshare_one import indicators
from fastmcp import FastMCP
from pydantic import Field


mcp = FastMCP(name="akshare-one-mcp")


@mcp.tool
def get_hist_data(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    interval: Annotated[
        Literal["minute", "hour", "day", "week", "month", "year"],
        Field(description="Time interval"),
    ] = "day",
    interval_multiplier: Annotated[
        int, Field(description="Interval multiplier", ge=1)
    ] = 1,
    start_date: Annotated[
        str, Field(description="Start date in YYYY-MM-DD format")
    ] = "1970-01-01",
    end_date: Annotated[
        str, Field(description="End date in YYYY-MM-DD format")
    ] = "2030-12-31",
    adjust: Annotated[
        Literal["none", "qfq", "hfq"], Field(description="Adjustment type")
    ] = "none",
    source: Annotated[
        Literal["eastmoney", "eastmoney_direct", "sina"],
        Field(description="Data source"),
    ] = "eastmoney",
    indicators_list: Annotated[
        list[
            Literal[
                "SMA",
                "EMA",
                "RSI",
                "MACD",
                "BOLL",
                "STOCH",
                "ATR",
                "CCI",
                "ADX",
                "WILLR",
                "AD",
                "ADOSC",
                "OBV",
                "MOM",
                "SAR",
                "TSF",
                "APO",
                "AROON",
                "AROONOSC",
                "BOP",
                "CMO",
                "DX",
                "MFI",
                "MINUS_DI",
                "MINUS_DM",
                "PLUS_DI",
                "PLUS_DM",
                "PPO",
                "ROC",
                "ROCP",
                "ROCR",
                "ROCR100",
                "TRIX",
                "ULTOSC",
            ]
        ]
        | None,
        Field(description="Technical indicators to add"),
    ] = None,
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 100,
) -> str:
    """Get historical stock market data. 'eastmoney_direct' support all A,B,H shares"""
    df = ako.get_hist_data(
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
        source=source,
    )
    if indicators_list:
        indicator_map = {
            "SMA": (indicators.get_sma, {"window": 20}),
            "EMA": (indicators.get_ema, {"window": 20}),
            "RSI": (indicators.get_rsi, {"window": 14}),
            "MACD": (indicators.get_macd, {"fast": 12, "slow": 26, "signal": 9}),
            "BOLL": (indicators.get_bollinger_bands, {"window": 20, "std": 2}),
            "STOCH": (
                indicators.get_stoch,
                {"window": 14, "smooth_d": 3, "smooth_k": 3},
            ),
            "ATR": (indicators.get_atr, {"window": 14}),
            "CCI": (indicators.get_cci, {"window": 14}),
            "ADX": (indicators.get_adx, {"window": 14}),
            "WILLR": (indicators.get_willr, {"window": 14}),
            "AD": (indicators.get_ad, {}),
            "ADOSC": (indicators.get_adosc, {"fast_period": 3, "slow_period": 10}),
            "OBV": (indicators.get_obv, {}),
            "MOM": (indicators.get_mom, {"window": 10}),
            "SAR": (indicators.get_sar, {"acceleration": 0.02, "maximum": 0.2}),
            "TSF": (indicators.get_tsf, {"window": 14}),
            "APO": (
                indicators.get_apo,
                {"fast_period": 12, "slow_period": 26, "ma_type": 0},
            ),
            "AROON": (indicators.get_aroon, {"window": 14}),
            "AROONOSC": (indicators.get_aroonosc, {"window": 14}),
            "BOP": (indicators.get_bop, {}),
            "CMO": (indicators.get_cmo, {"window": 14}),
            "DX": (indicators.get_dx, {"window": 14}),
            "MFI": (indicators.get_mfi, {"window": 14}),
            "MINUS_DI": (indicators.get_minus_di, {"window": 14}),
            "MINUS_DM": (indicators.get_minus_dm, {"window": 14}),
            "PLUS_DI": (indicators.get_plus_di, {"window": 14}),
            "PLUS_DM": (indicators.get_plus_dm, {"window": 14}),
            "PPO": (
                indicators.get_ppo,
                {"fast_period": 12, "slow_period": 26, "ma_type": 0},
            ),
            "ROC": (indicators.get_roc, {"window": 10}),
            "ROCP": (indicators.get_rocp, {"window": 10}),
            "ROCR": (indicators.get_rocr, {"window": 10}),
            "ROCR100": (indicators.get_rocr100, {"window": 10}),
            "TRIX": (indicators.get_trix, {"window": 30}),
            "ULTOSC": (
                indicators.get_ultosc,
                {"window1": 7, "window2": 14, "window3": 28},
            ),
        }
        temp = []
        for indicator in indicators_list:
            if indicator in indicator_map:
                func, params = indicator_map[indicator]
                indicator_df = func(df, **params)
                temp.append(indicator_df)
        if temp:
            df = df.join(temp)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records")


@mcp.tool
def get_realtime_data(
    symbol: Annotated[
        str | None, Field(description="Stock symbol/ticker (e.g. '000001')")
    ] = None,
    source: Annotated[
        Literal["xueqiu", "eastmoney", "eastmoney_direct"],
        Field(description="Data source"),
    ] = "eastmoney_direct",
) -> str:
    """Get real-time stock market data. 'eastmoney_direct' support all A,B,H shares"""
    df = ako.get_realtime_data(symbol=symbol, source=source)
    return df.to_json(orient="records")


@mcp.tool
def get_news_data(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get stock-related news data."""
    df = ako.get_news_data(symbol=symbol, source="eastmoney")
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records")


@mcp.tool
def get_balance_sheet(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get company balance sheet data."""
    df = ako.get_balance_sheet(symbol=symbol, source="sina")
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records")


@mcp.tool
def get_income_statement(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get company income statement data."""
    df = ako.get_income_statement(symbol=symbol, source="sina")
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records")


@mcp.tool
def get_cash_flow(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    source: Annotated[str, Field(description="Data source")] = "sina",
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get company cash flow statement data."""
    df = ako.get_cash_flow(symbol=symbol, source=source)
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records")


@mcp.tool
def get_inner_trade_data(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
) -> str:
    """Get company insider trading data."""
    df = ako.get_inner_trade_data(symbol, source="xueqiu")
    return df.to_json(orient="records")


@mcp.tool
def get_financial_metrics(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """
    Get key financial metrics from the three major financial statements.
    """
    df = ako.get_financial_metrics(symbol)
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records")


@mcp.tool
def get_time_info() -> dict:
    """Get current time with ISO format, timestamp, and the last trading day."""
    local_time = datetime.now().astimezone()
    current_date = local_time.date()

    # Get trading calendar
    trade_date_df = ak.tool_trade_date_hist_sina()
    trade_dates = [d for d in trade_date_df["trade_date"]]

    # Filter dates <= current date and sort descending
    past_dates = sorted([d for d in trade_dates if d <= current_date], reverse=True)

    # Find the most recent trading day
    last_trading_day = past_dates[0].strftime("%Y-%m-%d") if past_dates else None

    return {
        "iso_format": local_time.isoformat(),
        "timestamp": local_time.timestamp(),
        "last_trading_day": last_trading_day,
    }
