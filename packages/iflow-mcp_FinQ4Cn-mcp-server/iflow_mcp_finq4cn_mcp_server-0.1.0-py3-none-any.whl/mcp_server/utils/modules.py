from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from pydantic.functional_validators import field_validator
from datetime import datetime

class DateValidator(BaseModel):
    """
    用于验证和处理 YYYYMMDD 格式的日期类。
    """
    date: str

    @field_validator('date', mode='before')  # 使用 'before' 模式
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        """
        验证输入的日期是否符合 YYYYMMDD 格式。

        Args:
            value (str): 输入的日期字符串。

        Returns:
            str: 验证通过的日期字符串。
        """
        try:
            # 尝试将输入字符串解析为日期
            datetime.strptime(value, "%Y%m%d")
        except ValueError:
            raise ValueError(f"日期格式错误，应为 YYYYMMDD，实际输入：{value}")
        return value

    def to_datetime(self) -> datetime:
        """
        将日期字符串转换为 datetime 对象。

        Returns:
            datetime: 转换后的 datetime 对象。
        """
        return datetime.strptime(self.date, "%Y%m%d")

# 股票名称及股票代码
class StockCode(BaseModel):
    name: str
    stock_code: str

# 股价历史价格数据
class StockPricedata(BaseModel):
    date: datetime
    stock_code: object
    open: float
    close: float
    high: float
    low: float
    volume: int
    turnover: Optional[float] = None
    amplitude: Optional[float] = None
    change_rate: Optional[float] = None
    change_amount: Optional[float] = None
    turnover_rate: Optional[float] = None

# 财务报告概要
class FinancialAbstract(BaseModel):
    reporting_period: object
    net_profit: Optional[object] = None
    net_profit_growth_rate: Optional[object] = None
    non_recurring_net_profit: Optional[object] = None
    non_recurring_net_profit_growth_rate: Optional[object] = None
    total_operating_revenue: Optional[object] = None
    total_operating_revenue_growth_rate: Optional[object] = None
    basic_earnings_per_share: Optional[object] = None
    net_asset_per_share: Optional[object] = None
    capital_reserve_fund_per_share: Optional[object] = None
    undistributed_profit_per_share: Optional[object] = None
    operating_cash_flow_per_share: Optional[object] = None
    net_profit_margin: Optional[object] = None
    gross_profit_margin: Optional[object] = None
    return_on_equity_of_roe: Optional[object] = None
    diluted_return_on_equity_of_roe: Optional[object] = None
    operating_cycle: Optional[object] = None
    inventory_turnover_ratio: Optional[object] = None
    days_inventory_outstanding: Optional[object] = None
    days_sales_outstanding: Optional[object] = None
    current_ratio: Optional[object] = None
    quick_ratio: Optional[object] = None
    conservative_quick_ratio : Optional[object] = None
    debt_to_equity_ratio: Optional[object] = None
    asset_to_liability_ratio: Optional[object] = None


# 分红送配
class FhpsDetail(BaseModel):
    reporting_period: Optional[object] = None
    earnings_disclosure_date: Optional[object] = None
    total_share_conversion_ratio: Optional[float] = None
    bonus_share_ratio: Optional[float] = None
    capitalization_ratio: Optional[float] = None
    cash_dividend_payout_ratio: Optional[float] = None
    cash_dividend_payout_ratio_description: Optional[object] = None
    dividend_yield: Optional[float] = None
    earnings_per_share: Optional[float] = None
    net_asset_value_per_share: Optional[float] = None
    surplus_reserve_fund_per_share: Optional[float] = None
    undistributed_profit_per_share: Optional[float] = None
    net_profit_growth_rate: Optional[float] = None
    total_shares_outstanding: Optional[int] = None
    preliminary_plan_announcement_date: Optional[object] = None
    record_date: Optional[object] = None
    ex_dividend_date: Optional[object] = None
    proposal_progress: Optional[object] = None
    latest_announcement_date: Optional[object] = None

class BusinessStructure(BaseModel):
    reporting_period: Optional[str]  # 报告期
    classification_direction: Optional[str] = None  # 分类方向
    classification: Optional[str] = None  # 分类
    operating_revenue: Optional[str] = None  # 营业收入（注意单位: 元）
    operating_revenue_yoy_growth: Optional[str] = None  # 营业收入-同比增长
    operating_revenue_pct_of_main: Optional[str] = None  # 营业收入-占主营收入比
    operating_cost: Optional[str] = None  # 营业成本（注意单位: 元）
    operating_cost_yoy_growth: Optional[str]  = None # 营业成本-同比增长
    operating_cost_pct_of_main: Optional[str] = None  # 营业成本-占主营成本比
    gross_profit_margin: Optional[str] = None  # 毛利率
    gross_profit_margin_yoy_growth: Optional[str] = None  # 毛利率-同比增长

class NewsData(BaseModel):
    keyword: Optional[str]= None   # 关键词
    title: Optional[str]  # 新闻标题
    content: Optional[str]  # 新闻内容
    publish_time: Optional[datetime] # 发布时间
    source: Optional[str] = None  # 文章来源
    url: Optional[str]= None   # 新闻链接
