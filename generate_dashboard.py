import pandas as pd
import os

def create_dashboard():
    """
    Generates an interactive HTML dashboard from the master results CSV file.
    """
    results_file = 'results/master_results.csv'
    dashboard_file = 'results_dashboard.html'

    if not os.path.exists(results_file):
        print(f"Error: Results file not found at '{results_file}'.")
        print("Please run 'run_orchestrator.py' first to generate results.")
        return

    print(f"Reading results from '{results_file}'...")
    df = pd.read_csv(results_file)

    # Convert float columns to a more readable format
    for col in ['Sharpe Ratio', 'Profit Factor', 'Average Win', 'Average Loss']:
        if col in df.columns:
            df[col] = df[col].round(2)

    # Convert dataframe to JSON for embedding in HTML
    data_json = df.to_json(orient='records')

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Backtest Results Dashboard</title>
        <!-- DataTables CSS -->
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background: #f6f8fa;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .dashboard-container {{
                width: 90%;
                max-width: 1200px;
                background: rgba(255, 255, 255, 0.7);
                border-radius: 20px;
                padding: 2em;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }}
            h1 {{
                text-align: center;
                font-size: 2.5em;
                color: #333;
                margin-bottom: 1em;
            }}
            table.dataTable {{
                border-collapse: collapse !important;
                width: 100%;
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 10px;
                overflow: hidden;
            }}
            table.dataTable thead th {{
                background-color: rgba(240, 240, 240, 0.8);
                color: #333;
                font-weight: 600;
                border-bottom: 1px solid #ddd;
            }}
            table.dataTable tbody tr {{
                cursor: pointer;
                border-bottom: 1px solid #eee;
            }}
            table.dataTable tbody tr:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            table.dataTable tbody td {{
                padding: 12px 15px;
            }}
            .dataTables_wrapper .dataTables_filter input,
            .dataTables_wrapper .dataTables_length select {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }}
        </style>
    </head>
    <body>

        <div class="dashboard-container">
            <h1>Ensemble Strategy Backtest Results</h1>
            <table id="results-table" class="display" style="width:100%"></table>
        </div>

        <!-- jQuery and DataTables JS -->
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>

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

    print(f"Generating dashboard HTML file: '{dashboard_file}'...")
    with open(dashboard_file, 'w') as f:
        f.write(html_template)
    print("Dashboard generated successfully.")

if __name__ == '__main__':
    create_dashboard()
