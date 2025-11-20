import numpy as np

def get_annualization_factor(timeframe):
    """Calculates the annualization factor based on the timeframe."""
    if timeframe.endswith('m') and len(timeframe) > 1: # Handle minutes (e.g., '5m', '30m')
        minutes = int(timeframe.replace('m', ''))
        # Assuming 252 trading days/year, 6.5 trading hours/day
        return (60 / minutes) * 6.5 * 252
    elif timeframe.endswith('h'): # Handle hours (e.g., '1h', '4h')
        hours = int(timeframe.replace('h', ''))
        # Assuming 252 trading days/year, 6.5 trading hours/day
        return (6.5 / hours) * 252
    elif timeframe.endswith('d'): # Handle days (e.g., '1d', '5d')
        days = int(timeframe.replace('d', ''))
        return 252 / days # 252 trading days in a year
    elif timeframe.endswith('wk'): # Handle weeks (e.g., '1wk')
        weeks = int(timeframe.replace('wk', ''))
        return 52 / weeks # 52 weeks in a year
    elif timeframe.endswith('mo'): # Handle months (e.g., '1mo')
        months = int(timeframe.replace('mo', ''))
        return 12 / months # 12 months in a year
    else:
        raise ValueError(f"Unsupported timeframe format for annualization: {timeframe}. "
                         "Supported formats: Xm, Xh, Xd, Xwk, Xmo (e.g., '5m', '1h', '1d', '1wk', '1mo')")

def short_backtest(pnl_returns, timeframe):
    """A simplified, vectorized backtest to quickly rank strategies."""
    if pnl_returns.std() == 0:
        sharpe = 0
    else:
        # Annualize Sharpe based on the dynamic timeframe
        annualization_factor = get_annualization_factor(timeframe)
        sharpe = (pnl_returns.mean() / pnl_returns.std()) * np.sqrt(annualization_factor)

    pos_returns = pnl_returns[pnl_returns > 0].sum()
    neg_returns = pnl_returns[pnl_returns < 0].sum()

    if neg_returns == 0:
        profit_factor = np.inf
    else:
        profit_factor = abs(pos_returns / neg_returns)

    final_return = (pnl_returns + 1).prod()
    return {'sharpe': sharpe, 'profit_factor': profit_factor, 'final_return': final_return}
