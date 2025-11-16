import pandas as pd
import os
import re

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

def create_dashboard():
    """
    Generates an interactive HTML dashboard from the master results CSV file.
    """
    # Build absolute paths from the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    results_file = os.path.join(project_root, 'results', 'master_results.csv')
    dashboard_file = os.path.join(project_root, 'index.html')

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
    
    # Extract README sections
    readme_sections = extract_readme_sections()

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EnsembleTA Dashboard</title>
        <!-- DataTables CSS -->
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
            
            .glass {{
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(20px) saturate(180%);
                -webkit-backdrop-filter: blur(20px) saturate(180%);
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.4);
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2),
                            inset 0 1px 0 0 rgba(255, 255, 255, 0.5);
            }}
            
            .header {{
                padding: 3rem 2.5rem;
                margin-bottom: 2rem;
                text-align: center;
                position: relative;
            }}
            
            .theme-toggle {{
                position: absolute;
                top: 2rem;
                right: 2rem;
                width: 60px;
                height: 32px;
                background: rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.4);
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                padding: 0 4px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .theme-toggle-slider {{
                width: 24px;
                height: 24px;
                background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
                border-radius: 50%;
                transition: transform 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.75rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }}
            
            .theme-toggle.dark .theme-toggle-slider {{
                transform: translateX(28px);
            }}
            
            h1 {{
                font-size: 3.5rem;
                font-weight: 700;
                color: #1d1d1f;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                letter-spacing: -0.02em;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode h1 {{
                color: #f5f5f7;
            }}
            
            .subtitle {{
                font-size: 1.1rem;
                color: #6e6e73;
                font-weight: 400;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .subtitle {{
                color: #a1a1a6;
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
                box-shadow: 
                    0 12px 48px 0 rgba(31, 38, 135, 0.2),
                    0 4px 16px 0 rgba(31, 38, 135, 0.15),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.9),
                    inset 0 1px 0 0 rgba(255, 255, 255, 1);
            }}
            
            .info-card h2 {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #1d1d1f;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .info-card h2 {{
                color: #f5f5f7;
            }}
            
            .info-card .icon {{
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                border: 1px solid rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
            }}
            
            body.dark-mode .info-card .icon {{
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
                border: 1px solid rgba(102, 126, 234, 0.4);
            }}
            
            .info-card p, .info-card ul {{
                color: #1d1d1f;
                line-height: 1.8;
                font-size: 1rem;
                font-weight: 400;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .info-card p,
            body.dark-mode .info-card ul {{
                color: #f5f5f7;
            }}
            
            .info-card ul {{
                list-style: none;
                padding-left: 0;
            }}
            
            .info-card li {{
                margin-bottom: 1.2rem;
                padding-left: 1.8rem;
                position: relative;
                color: #1d1d1f;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .info-card li {{
                color: #f5f5f7;
            }}
            
            .info-card li::before {{
                content: "→";
                position: absolute;
                left: 0;
                color: #667eea;
                font-weight: 700;
                font-size: 1.2rem;
            }}
            
            .info-card strong {{
                color: #1d1d1f;
                font-weight: 600;
                font-size: 1.05rem;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .info-card strong {{
                color: #f5f5f7;
            }}
            
            .results-section {{
                padding: 2.5rem;
                margin-top: 2rem;
            }}
            
            .results-section h2 {{
                font-size: 2rem;
                font-weight: 600;
                color: #1d1d1f;
                margin-bottom: 1.5rem;
                text-align: center;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .results-section h2 {{
                color: #f5f5f7;
            }}
            
            .table-wrapper {{
                background: rgba(255, 255, 255, 0.5);
                backdrop-filter: blur(20px) saturate(180%);
                -webkit-backdrop-filter: blur(20px) saturate(180%);
                border-radius: 16px;
                padding: 1.5rem;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.6);
                box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.8);
                transition: all 0.3s ease;
            }}
            
            body.dark-mode .table-wrapper {{
                background: rgba(30, 30, 30, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
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
                border-bottom: 1px solid rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease;
            }}
            
            table.dataTable tbody tr:hover {{
                background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
                transform: scale(1.01);
            }}
            
            table.dataTable tbody td {{
                padding: 1rem;
                color: #1a1a1a;
                font-size: 0.9rem;
                font-weight: 500;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode table.dataTable tbody td {{
                color: #f5f5f7;
            }}
            
            .dataTables_wrapper .dataTables_filter input {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                padding: 0.6rem 1rem;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                color: #1a1a1a;
            }}
            
            body.dark-mode .dataTables_wrapper .dataTables_filter input {{
                background-color: rgba(50, 50, 50, 0.8);
                border: 2px solid rgba(102, 126, 234, 0.4);
                color: #f5f5f7;
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
                transition: all 0.3s ease;
                color: #1a1a1a;
            }}
            
            body.dark-mode .dataTables_wrapper .dataTables_length select {{
                background-color: rgba(50, 50, 50, 0.8);
                border: 2px solid rgba(102, 126, 234, 0.4);
                color: #f5f5f7;
            }}
            
            .dataTables_wrapper .dataTables_info,
            .dataTables_wrapper .dataTables_paginate {{
                color: #1a1a1a;
                margin-top: 1rem;
                font-weight: 500;
                transition: color 0.3s ease;
            }}
            
            body.dark-mode .dataTables_wrapper .dataTables_info,
            body.dark-mode .dataTables_wrapper .dataTables_paginate {{
                color: #f5f5f7;
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
            <!-- Header -->
            <div class="glass header">
                <div class="theme-toggle" id="themeToggle">
                    <div class="theme-toggle-slider">☀️</div>
                </div>
                <h1>📊 EnsembleTA Dashboard</h1>
                <p class="subtitle">Advanced Technical Analysis Ensemble Strategy Performance</p>
            </div>
            
            <!-- Info Cards -->
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
                    <h2><span class="icon">💡</span> Key Features</h2>
                    <ul>
                        <li><strong>Multi-Strategy Ensemble:</strong> Combines signals from multiple technical indicators for robust decision-making</li>
                        <li><strong>Rigorous Validation:</strong> Separate in-sample and out-of-sample testing periods ensure strategy robustness</li>
                        <li><strong>Flexible Architecture:</strong> Easily extensible framework for adding new strategies</li>
                        <li><strong>Comprehensive Metrics:</strong> Tracks Sharpe ratio, profit factor, win rate, and drawdown metrics</li>
                    </ul>
                </div>
            </div>
            
            <!-- Results Table -->
            <div class="glass results-section">
                <h2>📈 Backtest Results</h2>
                <div class="table-wrapper">
                    <table id="results-table" class="display" style="width:100%"></table>
                </div>
            </div>
        </div>

        <!-- jQuery and DataTables JS -->
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>

        <script>
            // Embed the data from the pandas DataFrame
            const data = {data_json};
            
            // Theme toggle functionality
            const themeToggle = document.getElementById('themeToggle');
            const themeSlider = themeToggle.querySelector('.theme-toggle-slider');
            const body = document.body;
            
            // Check for saved theme preference or default to light mode
            const currentTheme = localStorage.getItem('theme') || 'light';
            if (currentTheme === 'dark') {{
                body.classList.add('dark-mode');
                themeToggle.classList.add('dark');
                themeSlider.textContent = '🌙';
            }}
            
            themeToggle.addEventListener('click', function() {{
                body.classList.toggle('dark-mode');
                themeToggle.classList.toggle('dark');
                
                if (body.classList.contains('dark-mode')) {{
                    themeSlider.textContent = '🌙';
                    localStorage.setItem('theme', 'dark');
                }} else {{
                    themeSlider.textContent = '☀️';
                    localStorage.setItem('theme', 'light');
                }}
            }});

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

    print(f"Generating dashboard HTML file: '{dashboard_file}'...")
    with open(dashboard_file, 'w') as f:
        f.write(html_template)
    print("Dashboard generated successfully.")
    print(f"Open '{dashboard_file}' in your browser to view the dashboard.")

if __name__ == '__main__':
    create_dashboard()