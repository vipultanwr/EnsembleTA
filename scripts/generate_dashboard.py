import pandas as pd
import os
import re
import argparse
import yaml

#Created by Claude

def extract_readme_sections():
    """
    Extracts key sections from README.md for display on the dashboard.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    readme_file = os.path.join(project_root, 'README.md')
    
    sections = {
        'overview': '',
        'methodology': '',
        'project_structure': ''
    }
    
    if not os.path.exists(readme_file):
        print(f"Warning: README.md not found at '{readme_file}'.")
        return sections
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract Project Overview
    overview_match = re.search(r'## Project Overview\s+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if overview_match:
        sections['overview'] = overview_match.group(1).strip()
    
    # Extract methodology points
    methodology_match = re.search(r'The methodology is divided into two main phases:(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if methodology_match:
        sections['methodology'] = methodology_match.group(1).strip()
    
    return sections

def create_dashboard(results_path, output_path, config_path):
    """
    Generates an interactive HTML dashboard from the master results CSV file.
    """
    if not os.path.exists(results_path):
        print(f"Error: Results file not found at '{results_path}'.")
        print("Please run 'run_orchestrator.py' first to generate results.")
        return

    print(f"Reading results from '{results_path}'...")
    df = pd.read_csv(results_path)

    # --- Read Config Parameters ---
    config_params_html = "<h3>Parameters from config file could not be loaded.</h3>"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Format fixed parameters
        fixed_params = {k: v for k, v in config.items() if k != 'param_grid'}
        config_params_html = "<h4>Fixed Parameters</h4><ul>"
        for key, value in fixed_params.items():
            config_params_html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        config_params_html += "</ul>"

        # Format tunable parameters (param_grid)
        param_grid = config.get('param_grid', {})
        config_params_html += "<h4>Tunable Parameters (Hyperparameter Grid)</h4><ul>"
        for key, value in param_grid.items():
            config_params_html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {', '.join(map(str, value))}</li>"
        config_params_html += "</ul>"
    else:
        print(f"Warning: Config file not found at '{config_path}'. Parameter section will not be populated.")


    # Convert float columns to a more readable format
    for col in ['Sharpe Ratio', 'Profit Factor', 'Average Win', 'Average Loss']:
        if col in df.columns:
            df[col] = df[col].round(2)

    # Convert dataframe to JSON for embedding in HTML
    data_json = df.to_json(orient='records')
    
    # Extract README sections
    readme_sections = extract_readme_sections()

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EnsembleTA Strategy</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
                background-attachment: fixed;
                min-height: 100vh;
                padding: 2rem;
                overflow-x: hidden;
                position: relative;
            }}
            
            body::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: inherit;
                filter: blur(80px);
                z-index: -1;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            /* --- REFINED GLASS CLASS --- */
            .glass {{
                /* Lighter, cleaner background tint */
                background: rgba(255, 255, 255, 0.15);
                
                /* KEY CHANGE: Added saturate(180%) to make colors pop */
                backdrop-filter: blur(25px) saturate(180%);
                -webkit-backdrop-filter: blur(25px) saturate(180%);
                
                border-radius: 24px;
                
                /* Cleaner border */
                border: 1px solid rgba(255, 255, 255, 0.25);
                
                /* Softer shadow + distinct inner highlight */
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15),
                            inset 0 1px 1px 0 rgba(255, 255, 255, 0.6);
            }}
            
            .header {{
                padding: 3rem 2.5rem;
                margin-bottom: 2rem;
                text-align: center;
            }}
            
            h1 {{
                font-size: 3.5rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
                letter-spacing: -0.02em;
            }}
            
            .subtitle {{
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.9);
                font-weight: 400;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            
            .info-card {{
                padding: 2rem;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .info-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 12px 48px 0 rgba(0, 0, 0, 0.15),
                            inset 0 1px 1px 0 rgba(255, 255, 255, 0.7);
            }}
            
            .info-card h2 {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .info-card .icon {{
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }}
            
            /* Info cards keep the light text, as it's sparse and legible */
            .info-card p, .info-card ul {{
                color: rgba(255, 255, 255, 0.95);
                line-height: 1.8;
                font-size: 1rem;
                font-weight: 400;
                text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            
            .info-card ul {{
                list-style: none;
                padding-left: 0;
            }}
            
            .info-card li {{
                margin-bottom: 1.2rem;
                padding-left: 1.8rem;
                position: relative;
                color: rgba(255, 255, 255, 0.95);
            }}
            
            .info-card li::before {{
                content: "→";
                position: absolute;
                left: 0;
                color: #ffffff;
                font-weight: 700;
                font-size: 1.2rem;
            }}
            
            .info-card strong {{
                color: #ffffff;
                font-weight: 600;
                font-size: 1.05rem;
            }}
            
            .results-section {{
                padding: 2.5rem;
                margin-top: 2rem;
            }}
            
            .results-section h2 {{
                font-size: 2rem;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 1.5rem;
                text-align: center;
                text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            }}
            
            .table-wrapper {{
                background: transparent; /* Let the parent glass show through */
                border-radius: 16px;
                padding: 1.5rem;
                overflow: hidden;
            }}
            
            table.dataTable {{
                border-collapse: collapse !important;
                width: 100%;
                background-color: transparent;
            }}
            
            table.dataTable thead th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff;
                font-weight: 600;
                padding: 1rem;
                border: none;
                text-transform: uppercase;
                font-size: 0.8rem;
                letter-spacing: 0.05em;
            }}
            
            table.dataTable tbody tr {{
                cursor: pointer;
                /* Darker border for better contrast on light blur */
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
            }}
            
            table.dataTable tbody tr:hover {{
                /* Lighter background hover */
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.01);
            }}
            
            /* --- KEY LEGIBILITY FIX: DARK TABLE TEXT --- */
            table.dataTable tbody td {{
                padding: 1rem;
                color: #222222; /* High-contrast dark text */
                font-size: 0.9rem;
                font-weight: 500;
                text-shadow: none; /* Remove shadow */
            }}
            
            /* --- KEY LEGIBILITY FIX: DARK CONTROLS --- */
            
            /* "Search" and "Show" labels */
            .dataTables_wrapper .dataTables_filter label,
            .dataTables_wrapper .dataTables_length label {{
                color: #333333; /* Dark text */
                font-weight: 500;
                text-shadow: none; /* Remove shadow */
            }}

            .dataTables_wrapper .dataTables_filter input {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                padding: 0.6rem 1rem;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                color: #1a1a1a; /* Keep input text dark */
            }}
            
            .dataTables_wrapper .dataTables_filter input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .dataTables_wrapper .dataTables_length select {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                padding: 0.5rem 2rem 0.5rem 0.8rem;
                font-size: 0.9rem;
                cursor: pointer;
                color: #1a1a1a; /* Keep select text dark */
            }}
            
            /* "Showing 1 of..." and Pagination text */
            .dataTables_wrapper .dataTables_info,
            .dataTables_wrapper .dataTables_paginate {{
                color: #333333; /* Dark text */
                margin-top: 1rem;
                font-weight: 500;
                text-shadow: none; /* Remove shadow */
            }}
            
            .dataTables_wrapper .dataTables_paginate .paginate_button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                margin: 0 0.2rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .dataTables_wrapper .dataTables_paginate .paginate_button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
            
            .dataTables_wrapper .dataTables_paginate .paginate_button.disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            @media (max-width: 768px) {{
                h1 {{
                    font-size: 2.5rem;
                }}
                
                .info-grid {{
                    grid-template-columns: 1fr;
                }}
                
                body {{
                    padding: 1rem;
                }}
            }}
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {{
                width: 10px;
                height: 10px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="glass header">
                <h1>📊 EnsembleTA Dashboard</h1>
                <p class="subtitle">Advanced Technical Analysis Ensemble Strategy Performance</p>
            </div>
            
            <div class="info-grid">
                <div class="glass info-card">
                    <h2><span class="icon">🎯</span> Strategy Overview</h2>
                    <p>EnsembleTA implements an ensemble trading strategy based on a large set of technical indicators from the TA-Lib library. The system identifies the best-performing indicators and combines them into a unified strategy validated on out-of-sample cryptocurrency data.</p>
                </div>
                
                <div class="glass info-card">
                    <h2><span class="icon">🔬</span> Methodology</h2>
                    <ul>
                        <li><strong>Ranking Phase (In-Sample):</strong> Evaluates a wide range of individual technical analysis strategies over a historical period, testing both long and short versions. Top performers are selected based on metrics like final return and Sharpe ratio.</li>
                        <li><strong>Ensemble Backtesting (Out-of-Sample):</strong> Top-ranked strategies are combined using a voting system. The ensemble is then rigorously backtested on unseen data to validate effectiveness and robustness.</li>
                    </ul>
                </div>

                <div class="glass info-card">
                    <h2><span class="icon">⚙️</span> Backtest Parameters</h2>
                    <div>{config_params_html}</div>
                </div>
            </div>
            
            <div class="glass results-section">
                <h2>📈 Backtest Results</h2>
                <div class="table-wrapper">
                    <table id="results-table" class="display" style="width:100%"></table>
                </div>
            </div>

            <div class="glass results-section">
                <h2>📝 Project Report</h2>
                <h3>Project Report: Performance Analysis of the EnsembleTA Trading Strategy</h3>
                <p><strong>Date:</strong> November 20, 2025</p>
                <p><strong>Author:</strong> Gemini AI Agent</p>
                <h4>1.0 Executive Summary</h4>
                <p>This report details the performance of the EnsembleTA trading strategy following a comprehensive backtesting process across a diverse range of asset classes and timeframes. Despite extensive testing and debugging of the backtesting engine, the results conclusively demonstrate that the current strategy is not profitable and carries a high risk of significant capital loss. Out of 450 unique backtests, only a single combination showed a positive return, which is statistically insignificant and likely attributable to random chance rather than a robust strategic edge. The consistent negative performance across all other tests points to fundamental flaws in the strategy's design, specifically in its signal generation and risk management protocols. Immediate and substantial redevelopment of the core strategy is recommended before any further testing or consideration of live deployment.</p>
                <h4>2.0 Backtesting Methodology</h4>
                <p>To evaluate the strategy's effectiveness, a series of backtests were conducted using the orchestration script (<code>run_orchestrator.py</code>) and a diverse configuration (<code>config_diverse_assets.yaml</code>).</p>
                <ul>
                    <li><strong>Asset Classes:</strong> Cryptocurrencies (BTC/USDT, ETH/USDT), US Stocks (AAPL, GOOG), Indian Stocks (RELIANCE.NS, TCS.NS), Forex (EURUSD=X, GBPJPY=X), and Commodities (GC=F, SI=F).</li>
                    <li><strong>Timeframes:</strong> Daily (1d), Weekly (1wk), and Monthly (1mo).</li>
                    <li><strong>Hyperparameters:</strong>
                        <ul>
                            <li><code>n_top_strategies</code>: 3, 5, 7</li>
                            <li><code>signal_shifts</code>: [0], [1], [2], [0, 1], [0, 1, 2]</li>
                        </ul>
                    </li>
                </ul>
                <p>A total of 450 unique combinations were tested, with detailed performance metrics and equity curves generated for each run. Initial runs were plagued by runtime errors related to data fetching and processing, which were systematically debugged and resolved. The final, complete backtest provides the basis for this report.</p>
                <h4>3.0 Performance Analysis</h4>
                <p>The results of the backtesting, as aggregated in <code>master_results.csv</code> and detailed in individual HTML reports, are overwhelmingly negative.</p>
                <ul>
                    <li><strong>Overall Profitability:</strong> The vast majority of tests resulted in significant losses, with total returns frequently falling between -50% and -90%. The Sharpe Ratios, a measure of risk-adjusted return, were consistently negative, indicating that the strategies failed to generate returns sufficient to justify the risks taken.</li>
                    <li><strong>Positive Outlier:</strong> A single test combination showed a positive return:
                        <ul>
                            <li><strong>Asset:</strong> GOOG</li>
                            <li><strong>Timeframe:</strong> 1wk</li>
                            <li><strong>Parameters:</strong> <code>n_top_strategies</code>=5, <code>signal_shifts</code>=[2]</li>
                            <li><strong>Sharpe Ratio:</strong> 1.15</li>
                            <li><strong>Total Return:</strong> 5.13%</li>
                        </ul>
                        While positive, this result is statistically insignificant when viewed in the context of 449 failed tests. Further analysis of the corresponding HTML report revealed that this profit was the result of a single, long-held trade. This suggests a lucky entry rather than a repeatable strategic edge.
                    </li>
                    <li><strong>Consistent Failure Across Asset Classes:</strong> The strategy's failure was not isolated to any single market. It performed poorly across cryptocurrencies, US and Indian equities, forex, and commodities, indicating the underlying logic is not adapted to any specific market behavior.</li>
                    <li><strong>Low Win Rates:</strong> The <code>Win Rate</code> for most tests was below 20%, a clear indicator of a failing strategy. Without a reasonable probability of winning trades, long-term profitability is impossible.</li>
                </ul>
                <h4>4.0 Root Cause of Failure</h4>
                <p>The investigation into the strategy's poor performance points to two critical flaws in the design:</p>
                <ol>
                    <li><strong>Lack of Effective Signal Generation:</strong> The strategy relies on an ensemble of over 100 technical indicators, each with hardcoded, generic thresholds. This "one-size-fits-all" approach fails to adapt to the unique characteristics of different assets and market conditions. The "voting" mechanism, which aggregates these weak signals, results in a final signal with no discernible predictive power.</li>
                    <li><strong>Absence of Risk Management:</strong> The backtesting engine (<code>backtester.py</code>) and the strategy itself lack any form of risk management. There are no stop-loss orders to cap losses on individual trades, nor are there take-profit orders to secure gains. This means that a few losing trades can, and did, wipe out any small profits and lead to catastrophic drawdowns.</li>
                </ol>
                <h4>5.0 Recommendations</h4>
                <p>Based on this analysis, the EnsembleTA strategy in its current form is not viable. The following recommendations are made for future development:</p>
                <ol>
                    <li><strong>Abandon the Current Ensemble Method:</strong> The "more is better" approach to indicators has proven ineffective. It is recommended to pivot to a strategy based on a small number of well-understood, configurable indicators (e.g., RSI, MACD, Bollinger Bands).</li>
                    <li><strong>Prioritize Risk Management:</strong> Immediately implement stop-loss and take-profit functionality within the backtesting engine. This is a non-negotiable feature of any trading strategy and is essential to preserve capital. It is recommended to add <code>stop_loss_pct</code> and <code>take_profit_pct</code> as tunable hyperparameters in the configuration.</li>
                    <li><strong>Adopt a "Simple First" Development Approach:</strong> Begin with a simple, classic strategy, such as a moving average crossover, and ensure it can be backtested and optimized correctly. Once a baseline is established, complexity can be gradually added.</li>
                    <li><strong>Further Investigation of the GOOG Outlier (with caution):</strong> The single profitable test case for GOOG should be examined as a learning opportunity, but not as a sign of a successful strategy. It may provide insight into which <em>type</em> of indicator (if any) showed promise on that specific asset and timeframe. This investigation should be secondary to the redevelopment of the core strategy.</li>
                </ol>
            </div>
        </div>

        <script type(text/javascript) charset="utf8" src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script type(text/javascript) charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>

        <script>
            // Embed the data from the pandas DataFrame
            const data = {data_json};

            $(document).ready(function() {{
                const table = $('#results-table').DataTable({{
                    data: data,
                    columns: [
                        {{ "title": "Asset", "data": "asset" }},
                        {{ "title": "Timeframe", "data": "timeframe" }},
                        {{ "title": "N Top Strategies", "data": "n_top_strategies" }},
                        {{ "title": "Signal Shifts", "data": "signal_shifts" }},
                        {{ "title": "Total Return", "data": "Total Return" }},
                        {{ "title": "Annualized Return", "data": "Annualized Return" }},
                        {{ "title": "Sharpe Ratio", "data": "Sharpe Ratio" }},
                        {{ "title": "Max Drawdown", "data": "Maximum Drawdown" }},
                        {{ "title": "Win Rate", "data": "Win Rate" }},
                        {{ "title": "Profit Factor", "data": "Profit Factor" }},
                        // Hidden column for the report URL
                        {{ "title": "Report URL", "data": "report_url", "visible": false }}
                    ],
                    pageLength: 10,
                    order: [[4, 'desc']], // Sort by Total Return descending
                    // Add a click event to rows
                    "createdRow": function(row, data, dataIndex) {{
                        $(row).on('click', function() {{
                            window.open(data.report_url, '_blank');
                        }});
                    }}
                }});
            }});
        </script>

    </body>
    </html>
    """

    print(f"Generating dashboard HTML file: '{output_path}'...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Dashboard generated successfully.")
    print(f"Open '{output_path}' in your browser to view the dashboard.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a dashboard from backtest results.')
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    parser.add_argument('--results', type=str, default=os.path.join(project_root, 'results', 'master_results.csv'),
                        help='Path to the master results CSV file.')
    parser.add_argument('--output', type=str, default=os.path.join(project_root, 'index.html'),
                        help='Path to the output HTML dashboard file.')
    parser.add_argument('--config', type=str, default=os.path.join(project_root, 'config_diverse_assets.yaml'),
                        help='Path to the config file.')
    args = parser.parse_args()
    create_dashboard(args.results, args.output, args.config)