import pandas as pd
from typing import Any, Dict, List, Optional, Union

'''
import backtrader as bt
from .stocks_common_metrics import StocksCommonMetrics


# --- --- --- BackTesting --- --- ---
# 创建策略
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保持对数据[0]数据序列中“close”行的引用
        self.dataclose = self.datas[0].close

        # 跟踪挂单和买入价格/佣金
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 买入/卖出订单提交/接受经纪人 - 什么都不做
            return

        # 检查订单是否已完成
        # 注意：经纪人可能因为现金不足而拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 简单记录数据序列的收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 检查是否有挂单 ... 如果有，我们不能发送第二个订单
        if self.order:
            return

        # 检查是否在市场中 ... 如果没有，我们可能会买入
        if not self.position:

            # 还没有 ... 我们可能会买入如果 ...
            if self.dataclose[0] < self.dataclose[-1]:
                    # 当前收盘价小于前一个收盘价

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # 前一个收盘价小于前两个收盘价

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # 保持对创建订单的引用，以避免第二个订单
                        self.order = self.buy()

        else:

            # 已经在市场中 ... 我们可能会卖出
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # 保持对创建订单的引用，以避免第二个订单
                self.order = self.sell()


class BackTesting:
    """
    量化分析类。于获取股票的量化分析数据。
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def testing(self, 
                stock_code: str, 
                start_date: str, 
                end_date: str,
                init_capital: Optional[float] = 100000.0,
                init_commission: Optional[float] =0.01) -> None:

        # 创建Cerebro实体
        cerebro = bt.Cerebro()

        # 添加策略
        cerebro.addstrategy(TestStrategy)

        # 这里使用了 StocksCommonMetrics 类来获取历史数据
        stocks_common_metrics = StocksCommonMetrics()
        historical_data = stocks_common_metrics.get_historical_stockprice_data(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )

        # 转换为 DataFrame
        stock_data = pd.DataFrame(historical_data)  # Already a list of dictionaries
        data = bt.feeds.PandasData(dataname=stock_data)

        # 数据到Cerebro
        cerebro.adddata(data)

        # 设置初始现金
        #init_capital = 100000.0
        cerebro.broker.setcash(init_capital)

        # 设置佣金
        #init_commission = 0.001  # 0.1%
        cerebro.broker.setcommission(commission=init_commission)

        # 打印初始条件
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

        # 运行策略
        cerebro.run()

        # 打印最终结果
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
'''

# --- --- --- pybroker --- --- ---
import pybroker as pb
from pybroker import Strategy, ExecContext
from pybroker.ext.data import AKShare
from typing import Optional, Dict, Any, List

class pyStrategys(pb.Strategy):
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    # 策略1：如果当前没有持有该股票，则买入股票，并设置止盈点位
    # "percent"（持仓百分比）和 "stop_profit_pct"（止盈百分比）
    def strategy_buy_with_stop_loss(self, ctx: ExecContext, **kwargs):
        """
        对历史股票数据进行指定交易策略的回测，以评估其表现。策略为：如果当前没有持有该股票，则根据指定的持仓百分比（percent）买入股票，并设置止盈点位百分比（stop_profit_pct）。
        
        Args:
            ctx (ExecContext): 执行上下文。
            **kwargs: 动态参数，例如 percent 和 stop_profit_pct。
        """
        # 从 kwargs 或 _kwargs 获取默认值
        percent = kwargs.get("percent") or self._kwargs.get("percent")
        stop_profit_pct = kwargs.get("stop_profit_pct") or self._kwargs.get("stop_profit_pct")


        if percent is None or stop_profit_pct is None:
            raise ValueError(
                f"The following parameters are required: 'percent' (float, e.g., 35) and 'stop_profit_pct' (float, e.g., 10). "
            )

        pos = ctx.long_pos()
        if not pos:
            # 计算目标股票数量，根据 "percent" 参数确定应购买的股票数量
            ctx.buy_shares = percent
            ctx.hold_bars = 100
        else:
            ctx.sell_shares = pos.shares
            # 设置止盈点位，根据 "stop_profit_pct" 参数确定止盈点位
            ctx.stop_profit_pct = stop_profit_pct


class pyBackTesting:
    """
    量化分析类。于获取股票的量化分析数据。
    """
    def __init__(self):
        
        # 初始化 AKShare 数据源
        self.akshare = AKShare()

        # Dynamically map strategy names to their corresponding methods in pyStrategyDict
        self.strategy_map = {
            name: getattr(pyStrategys(), name)
            for name, method in pyStrategys.__dict__.items()
            if callable(method) and not name.startswith("__")  # Exclude special methods
        }

    def get_all_strategys(self) -> List[str]:
        """
        获取所有策略名称
        """
        return list(self.strategy_map.keys())

    def Btesting(self, stock_code: str, start_date: str, end_date: str, strategy_parm: Dict[str, Any]) -> str:

        # 提取策略名称和动态参数
        strategy_name = strategy_parm.get("strategy_name")
        dynamic_params = {k: v for k, v in strategy_parm.items() if k != "strategy_name"}

        if not strategy_name:
            raise ValueError(
                "Missing 'strategy_name' in strategy_parm."
                f"Invalid parameters in `strategy_parm`. 至少包含一个策略名称。 . Expected format: strategy_parm = {'strategy_name'=}. "
                f"The following parameters are required: 'percent' (float, e.g., 35) and 'stop_profit_pct' (float, e.g., 10). "
                f"Please ensure all required parameters are provided dynamically."
            )

        # 创建策略配置，初始资金10000
        initial_cash=10000.0
        my_config = pb.StrategyConfig(initial_cash=initial_cash)

        # 使用配置、数据源、起始日期、结束日期，以及刚才定义的交易策略创建策略对象
        strategy = Strategy(self.akshare, start_date=start_date, end_date=end_date, config=my_config)

        # Choose the strategy function dynamically
        selected_strategy = self.strategy_map.get(strategy_name)
        if not selected_strategy:
            raise ValueError(f"Strategy '{strategy_name}' not found in strategy_map.")

        # 添加执行策略，设置股票代码和要执行的函数 , **strategy_params
        strategy.add_execution(fn=lambda ctx: selected_strategy(ctx, **dynamic_params), symbols=stock_code)

        # 执行回测，并打印出回测结果的度量值（四舍五入到小数点后四位）
        backtest_result = strategy.backtest()
        result= backtest_result.metrics_df.round(4).to_dict(orient='records')
        
        #print(f"回测结果:\n {result}")
    
        return result

if __name__ == "__main__":
    # 示例用法
    back_testing = pyBackTesting()
    stock_code = "601688"  # 股票代码
    
    print(back_testing.get_all_strategys())

    back_testing.Btesting(
        stock_code=stock_code,
        start_date="20221001",
        end_date="20231001",
        strategy_parm ={
            'strategy_name': "strategy_buy_with_stop_loss",
            'percent':10,         # 动态传递的参数
            'stop_profit_pct':35  # 动态传递的参数
            }
    )
    