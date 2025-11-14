import numpy as np

def get_annualization_factor(timeframe):
    """Calculates the annualization factor based on the timeframe."""
    if 'm' in timeframe:
        minutes = int(timeframe.replace('m', ''))
        return (60 / minutes) * 24 * 365.25
    elif 'h' in timeframe:
        hours = int(timeframe.replace('h', ''))
        return (24 / hours) * 365.25
    elif 'd' in timeframe:
        days = int(timeframe.replace('d', ''))
        return 365.25 / days
    else:
        # Default to daily if not specified
        return 365.25

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
