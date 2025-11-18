import akshare as ak
from typing import Any, Dict, List, Optional, Union

from .modules import DateValidator, StockCode, StockPricedata, FinancialAbstract, FhpsDetail

class StocksRiskAlert:
    """
    股票风险提示类。
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_stock_zh_a_st(self, stock_code: str)  -> List[Dict[str, Any]]:
        """
        获取股票价格波动较大的上市公司的详细波动情况。

        Args:
            name: 股票名称

        Returns:
            List[Dict[str, Any]]: 返回字典的列表，每个字典表示一个交易日上市公司的股票波动情况。每条记录包含以下字段: 
                | serial_number | int  | 序号 |
                | stock_code    | object | 股票代码 |
                | name          | object | 股票名称 |
                | latest_price  | float| 最新价 |
                | change_percentage | float | 涨跌幅（注意单位: %） |
                | change_amount | float| 涨跌额 |
                | trading_volume| float| 成交量 |
                | turnover      | float| 成交额 |
                | amplitude     | float| 振幅（注意单位: %） |
                | highest_price | float| 最高价 |
                | lowest_price  | float| 最低价 |
                | opening_price_today | float | 今开 |
                | closing_price_yesterday | float | 昨收 |
                | volume_ratio  | float| 量比 |
                | turnover_rate | float| 换手率（注意单位: %） |
                | dynamic_pe_ratio | float | 市盈率-动态 |
                | pb_ratio      | float| 市净率 |
        """
        column_mapping = {
            "序号": "serial_number",
            "代码": "code",
            "名称": "name",
            "最新价": "latest_price",
            "涨跌幅": "change_percentage",
            "涨跌额": "change_amount",
            "成交量": "trading_volume",
            "成交额": "turnover",
            "振幅": "amplitude",
            "最高": "highest_price",
            "最低": "lowest_price",
            "今开": "opening_price_today",
            "昨收": "closing_price_yesterday",
            "量比": "volume_ratio",
            "换手率": "turnover_rate",
            "市盈率-动态": "dynamic_pe_ratio",
            "市净率": "pb_ratio",
        }

        stock_zh_a_st_em_df = ak.stock_zh_a_st_em()
        print(stock_zh_a_st_em_df)

