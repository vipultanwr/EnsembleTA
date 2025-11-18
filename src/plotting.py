import quantstats as qs
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import io
import base64

import quantstats as qs
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import io
import base64

def _plot_to_base64(fig):
    """Converts a matplotlib figure to a base64 encoded string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _create_snapshot_plot(returns: pd.Series, benchmark: pd.Series, trades: pd.DataFrame):
    """
    Creates a custom snapshot plot with strategy returns, benchmark, and trade markers.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot cumulative returns
    (1 + returns).cumprod().plot(ax=ax, label='Strategy', color='royalblue')
    (1 + benchmark).cumprod().plot(ax=ax, label='Buy & Hold', color='gray', linestyle='--')

    # Plot trade markers
    if not trades.empty:
        buys = trades[trades['amount'] > 0]
        sells = trades[trades['amount'] < 0]
        
        # Get the cumulative returns series to plot markers on the line
        cum_returns = (1 + benchmark).cumprod()
        
        # Plot buys
        if not buys.empty:
            buy_dates = buys.index.intersection(cum_returns.index)
            ax.plot(buy_dates, cum_returns.loc[buy_dates], '^', color='green', markersize=8, label='Buys')
        
        # Plot sells
        if not sells.empty:
            sell_dates = sells.index.intersection(cum_returns.index)
            ax.plot(sell_dates, cum_returns.loc[sell_dates], 'v', color='red', markersize=8, label='Sells')

    ax.set_title('Performance Snapshot')
    ax.set_ylabel('Cumulative Returns')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    return fig

def _format_if_number(value, format_str, prefix=''):
    """Safely formats a value with a prefix if it's a number, otherwise returns it as a string."""
    if isinstance(value, (int, float)):
        try:
            return f"{prefix}{format(value, format_str)}"
        except (ValueError, TypeError):
            return str(value)
    return str(value)

def generate_curated_report(returns: pd.Series, benchmark_returns: pd.Series, trades: pd.DataFrame, metrics: dict, title: str, output_filename: str):
    """
    Generates a curated, focused HTML report with essential metrics and a comprehensive
    snapshot plot.
    """
    print(f"Generating curated report: {output_filename}...", file=sys.stderr)

    # --- Ensure timezone-naive series for quantstats compatibility ---
    returns = returns.copy()
    returns.index = returns.index.tz_localize(None)
    benchmark_returns = benchmark_returns.copy()
    benchmark_returns.index = benchmark_returns.index.tz_localize(None)
    trades = trades.copy()
    if isinstance(trades.index, pd.DatetimeIndex):
        trades.index = trades.index.tz_localize(None)

    # --- 1. Create a dedicated assets directory for the report's images ---
    assets_dir_name = os.path.splitext(os.path.basename(output_filename))[0] + '_assets'
    assets_dir_path = os.path.join(os.path.dirname(output_filename), assets_dir_name)
    if not os.path.exists(assets_dir_path):
        os.makedirs(assets_dir_path)

    # --- 2. Calculate Key Metrics ---
    # Use the metrics dictionary as the single source of truth and format safely.
    info_ratio = qs.stats.information_ratio(returns, benchmark=benchmark_returns)
    kpis = {
        "Annualized Return": metrics.get("Annualized Return", "N/A"),
        "Sharpe Ratio": _format_if_number(metrics.get('Sharpe Ratio'), ".2f"),
        "Max Drawdown": metrics.get("Maximum Drawdown", "N/A"),
        "Information Ratio": f"{info_ratio:.2f}",
        "Profit Factor": _format_if_number(metrics.get('Profit Factor'), ".2f"),
        "Win Rate": metrics.get("Win Rate", "N/A")
    }

    avg_win_val = metrics.get('Average Win')
    avg_loss_val = metrics.get('Average Loss')

    # Attempt to convert potential string numbers to floats
    try:
        avg_win = float(avg_win_val)
    except (ValueError, TypeError):
        avg_win = avg_win_val
    
    try:
        avg_loss = float(avg_loss_val)
    except (ValueError, TypeError):
        avg_loss = avg_loss_val

    risk_reward_ratio = "N/A"
    if isinstance(avg_win, (int, float)) and isinstance(avg_loss, (int, float)):
        if avg_loss != 0:
            risk_reward_ratio = f"{abs(avg_win / avg_loss):.2f}"
        else:
            risk_reward_ratio = "∞"

    trade_stats = {
        "Total Trades": metrics.get("Total Trades", "N/A"),
        "Average Win": _format_if_number(avg_win, ".2f", prefix='$'),
        "Average Loss": _format_if_number(avg_loss, ".2f", prefix='$'),
        "Risk-Reward Ratio": risk_reward_ratio
    }
    # --- 3. Generate Core Visualizations and Save to Files ---
    plot_paths = {}
    
    # Plot 1: Custom Snapshot Plot
    snapshot_fig = _create_snapshot_plot(returns, benchmark_returns, trades)
    plot_paths['snapshot'] = os.path.join(assets_dir_path, 'snapshot.png')
    snapshot_fig.savefig(plot_paths['snapshot'], bbox_inches='tight')
    plt.close(snapshot_fig)

    # Plot 2: Monthly Returns Heatmap
    plot_paths['monthly_heatmap'] = os.path.join(assets_dir_path, 'monthly_heatmap.png')
    qs.plots.monthly_heatmap(returns, savefig=plot_paths['monthly_heatmap'], show=False)
    plt.close()

    # --- 4. Build HTML Report from Template ---
    kpi_html = "".join([f"<div><h2>{value}</h2><p>{key}</p></div>" for key, value in kpis.items()])
    trade_stats_html = "".join([f"<li><strong>{key}:</strong> {value}</li>" for key, value in trade_stats.items()])

    # Use relative paths for the image sources
    snapshot_img_src = os.path.join(assets_dir_name, 'snapshot.png')
    monthly_heatmap_img_src = os.path.join(assets_dir_name, 'monthly_heatmap.png')

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #333; margin: 0; padding: 2em; }}
            .container {{ max-width: 1000px; margin: auto; background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            h1 {{ text-align: center; color: #1a2b4d; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1.5em; text-align: center; margin: 2em 0; }}
            .kpi-grid h2 {{ margin: 0 0 0.25em 0; font-size: 2em; color: #1a2b4d; }}
            .kpi-grid p {{ margin: 0; font-size: 0.9em; color: #666; }}
            .section {{ margin-top: 3em; }}
            .section h3 {{ border-bottom: 2px solid #eee; padding-bottom: 0.5em; margin-bottom: 1em; color: #1a2b4d; }}
            .plot-container img {{ max-width: 100%; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }}
            .stats-list {{ list-style: none; padding: 0; }}
            .stats-list li {{ background: #f9f9f9; padding: 0.8em 1em; border-radius: 4px; margin-bottom: 0.5em; display: flex; justify-content: space-between; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            
            <div class="section">
                <h3>Key Performance Indicators</h3>
                <div class="kpi-grid">
                    {kpi_html}
                </div>
            </div>

            <div class="section">
                <h3>Performance Snapshot</h3>
                <div class="plot-container">
                    <img src="{snapshot_img_src}" alt="Performance Snapshot">
                </div>
            </div>

            <div class="section">
                <h3>Monthly Performance</h3>
                <div class="plot-container">
                    <img src="{monthly_heatmap_img_src}" alt="Monthly Returns Heatmap">
                </div>
            </div>

            <div class="section">
                <h3>Trade Statistics</h3>
                <ul class="stats-list">
                    {trade_stats_html}
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

    # --- 5. Save Final HTML ---
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"Curated report saved successfully to {output_filename}", file=sys.stderr)


def generate_quantstats_report(returns, title, output_filename):
    """
    Generates and saves a comprehensive QuantStats HTML report.
    """
    print(f"Generating QuantStats report: {output_filename}...", file=sys.stderr)
    # Ensure the directory exists
    output_dir = os.path.dirname(output_filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    qs.reports.html(returns, title=title, output=output_filename, download_filename=output_filename)
    print(f"Successfully saved report to {output_filename}", file=sys.stderr)