import pandas as pd
from CoreQuantUtilities.ta_strategies.TABot import getTACombinedSignals
from CoreQuantUtilities.backtester.backtester import StrategyBacktester

bt = StrategyBacktester(commission=0)
df = pd.read_pickle("/Users/vipultanwar/Projects/Similarity/data/APOHOS")

df['Signal'] =  getTACombinedSignals(df,True).sum(axis=1)
df.reset_index(inplace=True)
df.columns = ['date', 'Open', 'high', 'Low', 'close', 'volume', 'Signals']

bt.backtest(df)
bt.print_metrics()
bt.plot_results()