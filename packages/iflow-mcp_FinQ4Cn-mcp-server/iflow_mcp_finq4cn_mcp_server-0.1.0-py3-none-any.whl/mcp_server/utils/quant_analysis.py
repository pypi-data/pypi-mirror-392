import pandas as pd
from typing import Any, Dict, List, Optional, Union

from .stocks_common_metrics import StocksCommonMetrics


class QuantAnalysis:
    """
    量化分析类。于获取股票的量化分析数据。
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_stock_rsi_ma(self, 
                         stock_code: str ,
                         start_date: str,
                         end_date: str,
                         period: Optional[str] = 'daily',
                         adjust: Optional[str] = '',
                         min_window: Optional[int] = 50,
                         max_window: Optional[int] = 200) -> List[Dict[str, Any]]:
        """
        Fetch the moving average and RSI data for a stock, along with their buy/sell signals, to analyse the stock's strength and weakness.

        Args:
            stock_code: Stock code, e.g., "000001".
            start_date: Start date of the historical data (format: YYYYMMDD).
            end_date: End date of the historical data (format: YYYYMMDD).
            period: Time period of the data, e.g., "daily" (default: 'daily').
            adjust: Adjustment method for historical prices (default: '').
            min_window: Minimum window size for moving average calculation (default: 50).
            max_window: Maximum window size for moving average calculation (default: 200).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a trading day's stock volatility information.
            Each dictionary contains the following elements:
                | date         | str  | Trading Date (format: YYYY-MM-DD) |
                | close        | float| Closing Price |
                | MIN_MA       | float| Moving Average with a window size of min_window |
                | MAX_MA       | float| Moving Average with a window size of max_window |
                | MA_SIGNAL    | str  | Moving Average Signal ("Bullish" or "Bearish") |
                | RSI_SIGNAL   | str  | Relative Strength Index Signal ("Overbought", "Oversold", or "Neutral") |
        """
        # 获取历史数据
        # 这里使用了 StocksCommonMetrics 类来获取历史数据
        stocks_common_metrics = StocksCommonMetrics()
        historical_data = stocks_common_metrics.get_historical_stockprice_data(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust
        )
        # 转换为 DataFrame
        historical_data = pd.DataFrame(historical_data)  # Already a list of dictionaries
        # print(historical_data.head())  # Debugging line to check the data
        historical_data['MIN_MA'] = historical_data['close'].rolling(window=min_window).mean()
        historical_data['MAX_MA'] = historical_data['close'].rolling(window=max_window).mean()

        delta = historical_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        historical_data['RSI'] = rsi

        # 生成 MA 信号
        historical_data['MA_SIGNAL'] = "Bearish"  # 默认值
        historical_data.loc[historical_data['MIN_MA'] > historical_data['MAX_MA'], 'ma_signal'] = "Bullish"
        
        # 生成 RSI 信号
        historical_data['RSI_SIGNAL'] = "Neutral"  # 默认值
        historical_data.loc[historical_data['RSI'] > 70, 'rsi_signal'] = "Overbought"
        
        return historical_data[['date', 'close','MIN_MA','MAX_MA','MA_SIGNAL', 'RSI_SIGNAL']].to_dict(orient='records')


if __name__ == "__main__":
    # 示例用法
    quant_analysis = QuantAnalysis()
    stock_code = "601688"  # 股票代码
    quant_analysis.get_stock_rsi_ma(stock_code,
                                    start_date="20221001", 
                                    end_date="20231001", 
                                    period="daily", 
                                    adjust="",
                                    min_window=50, 
                                    max_window=200)

