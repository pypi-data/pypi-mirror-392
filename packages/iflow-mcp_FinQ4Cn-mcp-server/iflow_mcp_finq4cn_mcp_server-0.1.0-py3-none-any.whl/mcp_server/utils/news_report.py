import pandas as pd
import akshare as ak
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta


from .modules import NewsData


class News_Report:
    """
    新闻报告类。用于获取股票相关的新闻报道。
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def stock_news(self, stock_code: str, start_date: Optional[ str] = None, end_date: Optional[ str] = None) -> List[Dict[str, Any]]:
        """
        Fetch the latest news articles and information related to a specific stock within a specified date range.

        Args:
            stock_code: Stock code, e.g., "000001".
            start_date: The start date of the query, formatted as 'YYYY-MM-DD'. If not provided, it defaults to one week before the current date.
            end_date: The end date of the query, formatted as 'YYYY-MM-DD'. If not provided, it defaults to the current date.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a news article record.
            Each dictionary contains the following elements:
                | keyword       | str  | Keywords |
                | title         | str  | News Title |
                | content       | str  | News Content |
                | publish_time  | str  | Publication Time (format: YYYY-MM-DD HH:MM:SS) |
                | source        | str  | Source of the Article |
                | url           | str  | URL Link to the News Article |
        """
        # 如果 start_date 和 end_date 为 None，则设置默认值
        if start_date is None:
            start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")  # 默认开始日期为一周前
        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")  # 默认结束日期为今天

        column_mapping = {
            "关键词": "keyword",
            "新闻标题": "title",
            "新闻内容": "content",
            "发布时间": "publish_time",
            "文章来源": "source",
            "新闻链接": "url",
        }

        result  = ak.stock_news_em(symbol=stock_code)
        result.rename(columns=column_mapping, inplace=True)
        result['publish_time'] = pd.to_datetime(result['publish_time'], errors='coerce')
        result = result.dropna(subset=['publish_time'])

        result = result[
            (result['publish_time'] >= pd.to_datetime(start_date)) & 
            (result['publish_time'] <= pd.to_datetime(end_date))
        ]

        news = result.to_dict(orient="records")

        return news

    def financial_news(self, start_date: Optional[ str] = None, end_date: Optional[ str] = None) -> List[Dict[str, Any]]:
        """
        Fetch the latest financial news and market trends within a specified date range.

        Args:
            start_date: The start date of the query, formatted as 'YYYY-MM-DD'. If not provided, it defaults to one week before the current date.
            end_date: The end date of the query, formatted as 'YYYY-MM-DD'. If not provided, it defaults to the current date.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a news record.
            Each dictionary contains the following elements:
                | title         | str  | News Title |
                | content       | str  | News Content |
                | pub_time      | str  | Publication Time (format: YYYY-MM-DD HH:MM:SS) |
                | url           | str  | URL Link to the News Article |
        """
        # 如果 start_date 和 end_date 为 None，则设置默认值
        if start_date is None:
            start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")  # 默认开始日期为一周前
        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")  # 默认结束日期为今天

        column_mapping = {
            "tag": "title",
            "summary": "content",
            "pub_time": "publish_time",
            "url": "url",
        }

        result = ak.stock_news_main_cx()
        result.drop(columns=["interval_time"], inplace=True)
        result.rename(columns=column_mapping, inplace=True)

        result['publish_time'] = pd.to_datetime(result['publish_time'], errors='coerce')
        result = result.dropna(subset=['publish_time'])
        result = result[
            (result['publish_time'] >= pd.to_datetime(start_date)) & 
            (result['publish_time'] <= pd.to_datetime(end_date))
        ]

        news = result.apply(lambda row: NewsData(**row).model_dump(), axis=1).tolist()

        return news

