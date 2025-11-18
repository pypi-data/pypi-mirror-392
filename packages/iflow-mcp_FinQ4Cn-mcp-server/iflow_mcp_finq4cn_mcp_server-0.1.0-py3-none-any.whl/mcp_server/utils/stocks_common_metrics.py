import pandas as pd
import akshare as ak
import re
from typing import Any, Dict, List, Optional, Union

from .modules import DateValidator, StockCode, StockPricedata, FinancialAbstract, FhpsDetail, BusinessStructure

class StocksCommonMetrics:
    """
    股票常用指标类。
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_stock_code(self, name: str)  -> List[Dict[str, Any]]:
        """
        Retrieve the stock codes of companies listed on China's A-share market.

        Args:
            name: Stock name.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents the stock name and stock code of a listed company. Each dictionary contains the following elements:
                | name          | str  | Stock name |
                | stock_code    | str  | Stock code |
        """
        result = []
        for stock_data in [
                ak.stock_info_a_code_name()
        ]:
            result.extend(
                [
                    {"name": item['name'], "stock_code": item['code']}
                    for item in stock_data[["name", "code"]].to_dict(orient="records")
                    if re.search(name, item['name'])
                ]
            )

        stock_codes = [StockCode(**row).model_dump() for row in result]

        return stock_codes

    # 经营业务结构
    def get_stock_business_structure(self, stock_code: str)  -> List[Dict[str, Any]]:
        """
        Retrieve the main business structure of Chinese A-share listed companies for analyzing the company's core business, products, services, and revenue distribution.

        Args:
            stock_code: Stock code, e.g., "000001".

        Returns:
            List[Dict[str, Any]]: Returns a list of dictionaries, where each dictionary represents the report content for a specific reporting period. Each dictionary contains the following elements:
                | reporting_period               | str  | Reporting period |
                | classification_direction       | str  | Classification direction |
                | classification                 | str  | Classification |
                | operating_revenue              | str  | Operating revenue (Note: Unit is in yuan) |
                | operating_revenue_yoy_growth   | str  | Year-on-year growth of operating revenue |
                | operating_revenue_pct_of_main  | str  | Percentage of operating revenue to main business revenue |
                | operating_cost                 | str  | Operating cost (Note: Unit is in yuan) |
                | operating_cost_yoy_growth      | str  | Year-on-year growth of operating cost |
                | operating_cost_pct_of_main     | str  | Percentage of operating cost to main business cost |
                | gross_profit_margin            | str  | Gross profit margin |
                | gross_profit_margin_yoy_growth | str  | Year-on-year growth of gross profit margin |
        """

        result = ak.stock_zygc_ym(symbol=stock_code)
        column_mapping = {
            "报告期": "reporting_period",
            "分类方向": "classification_direction",
            "分类": "classification",
            "营业收入": "operating_revenue",  # 注意单位: 元
            "营业收入-同比增长": "operating_revenue_yoy_growth",
            "营业收入-占主营收入比": "operating_revenue_pct_of_main_revenue",
            "营业成本": "operating_cost",  # 注意单位: 元
            "营业成本-同比增长": "operating_cost_yoy_growth",
            "营业成本-占主营成本比": "operating_cost_pct_of_main_cost",
            "毛利率": "gross_profit_margin",
            "毛利率-同比增长": "gross_profit_margin_yoy_growth",
        }
        result.rename(columns=column_mapping, inplace=True)
        
        stock_structure = result.apply(lambda row: BusinessStructure(**row).model_dump(), axis=1).tolist()

        return stock_structure

    # 历史价格数据。
    def get_historical_stockprice_data(self, 
                                       stock_code: str ,
                                       start_date: str, 
                                       end_date: str,
                                       period: Optional[str] = 'daily',
                                       adjust: Optional[str] = '') -> List[Dict[str, Any]]:
        """
        Retrieve historical price data of companies listed on China's A-share market.

        Args:
            stock_code: Stock code.
            start_date: The start date of the query, formatted as 'YYYYMMDD'.
            end_date: The end date of the query, formatted as 'YYYYMMDD'.
            period: Data frequency. Optional values: {'daily', 'weekly', 'monthly'}, representing daily, weekly, and monthly data respectively.
            adjust: Whether to adjust prices. Optional values: {'', 'qfq', 'hfq'}, representing no adjustment, forward adjustment, and backward adjustment respectively.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents the stock price for a specific period. Each dictionary contains the following elements:
                | date          | object  | Trading date              |
                | stock_code    | object  | Stock code (without market identifier) |
                | open          | float | Opening price             |
                | close         | float | Closing price             |
                | high          | float | Highest price             |
                | low           | float | Lowest price              |
                | volume        | int   | Trading volume (unit: lots)|
                | turnover      | float | Trading turnover (unit: yuan)|
                | amplitude     | float | Amplitude (unit: %)       |
                | change_rate   | float | Change rate (unit: %)     |
                | change_amount | float | Change amount (unit: yuan)|
                | turnover_rate | float | Turnover rate (unit: %)   |
        """
        if not DateValidator(date=start_date).validate_date_format(start_date) or not DateValidator(date=end_date).validate_date_format(end_date):
            raise ValueError(f"日期格式错误，应为 YYYYMMDD，实际输入：{start_date} 或 {end_date}")

        result = ak.stock_zh_a_hist(symbol=stock_code, 
                                    period=period, 
                                    start_date=start_date, 
                                    end_date=end_date, 
                                    adjust=adjust)
        column_mapping = {
            "日期": "date",
            "股票代码": "stock_code",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume", 
            "成交额": "turnover",
            "振幅": "amplitude",
            "涨跌幅": "change_rate",
            "涨跌额": "change_amount",
            "换手率": "turnover_rate"
        }
        result.rename(columns=column_mapping, inplace=True)
        result['date'] = pd.to_datetime(result['date'])

        stock_hist = result.apply(lambda row: StockPricedata(**row).model_dump(), axis=1).tolist()

        return stock_hist

    # 关键财报数据
    def get_stock_financial_abstract(self,
                                     stock_code: str ,
                                     indicator: Optional[str] = '按报告期')  -> List[Dict[str, Any]]:
        """
        Retrieve the financial report summary data of companies listed on China's A-share market.

        Args:
            stock_code: Stock code.
            indicator: Type of indicator. Optional values: {'按报告期', '按年度', '按单季度'} (By reporting period, by year, or by single quarter).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a financial summary record.  Each dictionary contains the following elements:
                | reporting_period               | object   | Reporting period              |
                | net_profit                     | object   | Net profit                    |
                | net_profit_growth_rate         | object   | Net profit growth rate (YoY)  |
                | non_recurring_net_profit       | object   | Non-recurring net profit      |
                | non_recurring_net_profit_growth_rate | object | Non-recurring net profit growth rate (YoY) |
                | total_operating_revenue        | object   | Total operating revenue       |
                | total_operating_revenue_growth_rate | object | Total operating revenue growth rate (YoY) |
                | basic_earnings_per_share       | object   | Basic earnings per share      |
                | net_asset_per_share            | object   | Net assets per share          |
                | capital_reserve_fund_per_share | object   | Capital reserve fund per share|
                | undistributed_profit_per_share | object   | Undistributed profit per share|
                | operating_cash_flow_per_share  | object   | Operating cash flow per share |
                | net_profit_margin              | object   | Net profit margin             |
                | gross_profit_margin            | object   | Gross profit margin           |
                | return_on_equity_of_roe        | object   | Return on equity (ROE)        |
                | diluted_return_on_equity_of_roe| object   | Diluted return on equity (ROE)|
                | operating_cycle                | object   | Operating cycle               |
                | inventory_turnover_ratio       | object   | Inventory turnover ratio      |
                | days_inventory_outstanding     | object   | Days inventory outstanding    |
                | days_sales_outstanding         | object   | Days sales outstanding         |
                | current_ratio                  | object   | Current ratio                 |
                | quick_ratio                    | object   | Quick ratio                   |
                | conservative_quick_ratio       | object   | Conservative quick ratio      |
                | debt_to_equity_ratio           | object   | Debt to equity ratio          |
                | asset_to_liability_ratio       | object   | Asset to liability ratio      |
        """

        result = ak.stock_financial_abstract_ths(symbol=stock_code, indicator=indicator)
        column_mapping = {
            "报告期" : "reporting_period",
            "净利润" : "net_profit",
            "净利润同比增长率" : "net_profit_growth_rate",
            "扣非净利润" : "non_recurring_net_profit",
            "扣非净利润同比增长率" : "non_recurring_net_profit_growth_rate",
            "营业总收入" : "total_operating_revenue",
            "营业总收入同比增长率" : "total_operating_revenue_growth_rate",
            "基本每股收益" : "basic_earnings_per_share",
            "每股净资产" : "net_asset_per_share",
            "每股资本公积金" : "capital_reserve_fund_per_share" ,
            "每股未分配利润" : "undistributed_profit_per_share" ,
            "每股经营现金流" : "operating_cash_flow_per_share" ,
            "销售净利率" : "net_profit_margin" ,
            "销售毛利率" : "gross_profit_margin",
            "净资产收益率" : "return_on_equity_of_roe" ,
            "净资产收益率-摊薄" : "diluted_return_on_equity_of_roe" ,
            "营业周期" : "operating_cycle" ,
            "存货周转率" : "inventory_turnover_ratio" ,
            "存货周转天数" : "days_inventory_outstanding" ,
            "应收账款周转天数" : "days_sales_outstanding" ,
            "流动比率" : "current_ratio" ,
            "速动比率" : "quick_ratio" ,
            "保守速动比率" : "conservative_quick_ratio" ,
            "产权比率" : "debt_to_equity_ratio" ,
            "资产负债率" : "asset_to_liability_ratio" ,
        }
        result.rename(columns=column_mapping, inplace=True)
        financial_abstracts = result.apply(lambda row: FinancialAbstract(**row).model_dump(), axis=1).tolist()
        
        return financial_abstracts

    # 融资融券明细数据。
    def get_stock_margin_detail(self, stock_code: str, start_date: str, end_date: str, freq: str = "D") -> List[Dict[str, Any]]:
        """
        Retrieve the margin trading and short selling details of companies listed on China's A-share market.

        Args:
            stock_code: Stock code, e.g., "000001".
            start_date: Start date, formatted as YYYYMMDD.
            end_date: End date, formatted as YYYYMMDD.
            freq: Date interval type, default is "D" (daily). Optional values include:
                        - "D": Daily
                        - "W": Weekly
                        - "MS": First day of each month
                        - "ME": Last day of each month
                        - "Q": Quarterly
                        - "Y": Annually

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a summary of margin trading and short selling for a trading day. Each dictionary contains the following elements:
                | trading_date           | str        | Trading date                       |
                | target_security_code   | str        | Target security code               |
                | target_security_name   | str        | Target security abbreviation       |
                | margin_balance         | int        | Margin balance (unit: yuan)        |
                | margin_buy_amount      | int        | Margin purchase amount (unit: yuan)|
                | margin_repayment       | int        | Margin repayment amount (unit: yuan)|
                | short_selling_balance  | int        | Short selling balance              |
                | short_selling_volume   | int        | Short selling volume               |
                | short_selling_repayment| int        | Short selling repayment volume     |
        """
        # 初始化空的 DataFrame 用于存储所有数据
        all_filtered_df = pd.DataFrame()

        # 定义字段映射（中文字段名 -> 英文字段名）
        column_mapping = {
            "信用交易日期": "trading_date",
            "标的证券代码": "target_security_code",
            "标的证券简称": "target_security_name",
            "融资余额": "margin_balance",
            "融资买入额": "margin_buy_amount",
            "融资偿还额": "margin_repayment",
            "融券余量": "short_selling_balance",
            "融券卖出量": "short_selling_volume",
            "融券偿还量": "short_selling_repayment",
        }

        # 将日期范围转换为日期列表
        for date in pd.date_range(start=start_date, end=end_date, freq=freq):
            # 格式化日期为字符串
            data_date = date.strftime('%Y%m%d')

            try:
                # 获取当天的融资融券数据
                stock_margin_detail_sse_df = ak.stock_margin_detail_sse(date=data_date)

                # 检查返回的数据是否为空
                if stock_margin_detail_sse_df is None or stock_margin_detail_sse_df.empty:
                    print(f"No data for date: {data_date}")
                    continue  # 跳过没有数据的日期

                # 过滤证券代码为指定的 stock_code
                filtered_df = stock_margin_detail_sse_df[
                    stock_margin_detail_sse_df['标的证券代码'] == stock_code
                ].copy()

                # 再次检查过滤后的数据是否为空
                if filtered_df is None or filtered_df.empty:
                    print(f"No data for stock code {stock_code} on date: {data_date}")
                    continue  # 跳过没有匹配数据的日期

                # 翻译字段名为英文
                filtered_df.rename(columns=column_mapping, inplace=True)

                # 将当天数据添加到总数据中
                all_filtered_df = pd.concat([all_filtered_df, filtered_df], ignore_index=True)

            except Exception as e:
                print(f"Error fetching data for date {data_date}: {e}")
                continue  # 跳过发生错误的日期

        # 将 DataFrame 转换为字典列表
        result = all_filtered_df.to_dict(orient="records")

        return result

    # 分红送配详情数据。
    def get_stock_fhps_detail(self, stock_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve the historical dividend and rights issue details of companies listed on China's A-share market.

        Args:
            stock_code: Stock code, e.g., "600000".

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents the details of a dividend or rights distribution.  Each dictionary contains the following elements:
                | reporting_period                     | Reporting period                        | object  |
                | earnings_disclosure_date             | Earnings disclosure date                | object  |
                | total_share_conversion_ratio         | Share conversion - Total conversion ratio | float |
                | bonus_share_ratio                    | Share conversion - Bonus share ratio     | float |
                | capitalization_ratio                 | Share conversion - Capitalization ratio  | float |
                | cash_dividend_payout_ratio           | Cash dividend - Payout ratio             | float |
                | cash_dividend_payout_ratio_description | Cash dividend - Payout ratio description | object  |
                | dividend_yield                       | Cash dividend - Dividend yield           | float |
                | earnings_per_share                   | Earnings per share                      | float |
                | net_asset_value_per_share            | Net asset value per share               | float |
                | surplus_reserve_fund_per_share       | Surplus reserve fund per share          | float |
                | undistributed_profit_per_share       | Undistributed profit per share          | float |
                | net_profit_growth_rate               | Net profit growth rate (YoY)            | float |
                | total_shares_outstanding             | Total shares outstanding                | int   |
                | preliminary_plan_announcement_date   | Preliminary plan announcement date      | object  |
                | record_date                          | Record date                             | object  |
                | ex_dividend_date                     | Ex-dividend and ex-rights date          | object  |
                | proposal_progress                    | Proposal progress                       | object  |
                | latest_announcement_date             | Latest announcement date                | object  |
        """

        result = ak.stock_fhps_detail_em(symbol=stock_code)
        column_mapping = {
            "报告期": "reporting_period",
            "业绩披露日期": "earnings_disclosure_date",
            "送转股份-送转总比例": "total_share_conversion_ratio",
            "送转股份-送股比例": "bonus_share_ratio",
            "送转股份-转股比例": "capitalization_ratio",
            "现金分红-现金分红比例": "cash_dividend_payout_ratio",
            "现金分红-现金分红比例描述": "cash_dividend_payout_ratio_description",
            "现金分红-股息率": "dividend_yield",
            "每股收益": "earnings_per_share",
            "每股净资产": "net_asset_value_per_share",
            "每股公积金": "surplus_reserve_fund_per_share",
            "每股未分配利润": "undistributed_profit_per_share",
            "净利润同比增长": "net_profit_growth_rate",
            "总股本": "total_shares_outstanding",
            "预案公告日": "preliminary_plan_announcement_date",
            "股权登记日": "record_date",
            "除权除息日": "ex_dividend_date",
            "方案进度": "proposal_progress",
            "最新公告日期": "latest_announcement_date",
        }
        result.rename(columns=column_mapping, inplace=True)
        fhps_detail = result.apply(lambda row: FhpsDetail(**row).model_dump(), axis=1).tolist()

        return fhps_detail


if __name__ == "__main__":
    # 示例用法
    # 创建 StockUtils 实例
    stockutils = StocksCommonMetrics()
    # 获取股票名称及股票代码
    stock_codes = stockutils.get_stock_code(name="华泰证券")

    if stock_codes:
        stock_code = []
        for item in stock_codes:

            # 获取股票代码
            stock_code= item['stock_code']
            print(f"处理股票代码：{stock_code}")

            # 获取股价历史数据
            historical_stockprice_data = stockutils.get_historical_stockprice_data(stock_code=stock_code, start_date="20230101", end_date="20231001")
            print(historical_stockprice_data)
            
            # 获取财务概要数据
            stock_financial_abstract = stockutils.get_stock_financial_abstract(stock_code=stock_code, indicator='按报告期')
            print(stock_financial_abstract)

            # 获取融资融券明细数据
            stock_margin_detail = stockutils.get_stock_margin_detail(stock_code=stock_code, start_date="20230102", end_date="20230110")
            print(stock_margin_detail)
    else:
        print("No stock codes found.")
