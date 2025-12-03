import os
import json
import re

def parse_dirname(dirname):
    """Parses a directory name to extract parameters."""
    match = re.match(r"ensemble_strategy_(?P<asset>.*?)_(?P<timeframe>.*?)_top(?P<top_n>.*?)_shifts(?P<shifts>.*?)_assets", dirname)
    if match:
        return match.groupdict()
    return None

def scan_results():
    """Scans the results directory and returns the data."""
    results_dir = "results"
    results_data = []
    if not os.path.exists(results_dir):
        return results_data
        
    for dirname in os.listdir(results_dir):
        dirpath = os.path.join(results_dir, dirname)
        if os.path.isdir(dirpath):
            params = parse_dirname(dirname)
            if params:
                files = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
                results_data.append({
                    "params": params,
                    "folder": dirname,
                    "files": files
                })
    return results_data

def generate_dashboard_html(results_data):
    """Generates the HTML and JavaScript for the dashboard."""
    
    # The initial population of dropdowns is now handled by the JavaScript
    dropdowns_html = """
        <div id="dashboard" style="display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;">
            <div>
                <label for="asset">Asset:</label>
                <select id="asset"></select>
            </div>
            <div>
                <label for="timeframe">Timeframe:</label>
                <select id="timeframe"></select>
            </div>
            <div>
                <label for="top_n">Top N:</label>
                <select id="top_n"></select>
            </div>
            <div>
                <label for="shifts">Shifts:</label>
                <select id="shifts"></select>
            </div>
        </div>
        <div id="results-content" style="background: #22252a; border: 1px solid #444; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);">
            <!-- Results will be displayed here -->
        </div>
    """

    javascript = f"""
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const allResultsData = {json.dumps(results_data)};
            const selectors = {{
                asset: document.getElementById('asset'),
                timeframe: document.getElementById('timeframe'),
                top_n: document.getElementById('top_n'),
                shifts: document.getElementById('shifts')
            }};
            const resultsContentDiv = document.getElementById('results-content');
            const paramKeys = ['asset', 'timeframe', 'top_n', 'shifts'];

            function populateSelector(selector, values, selectedValue) {{
                const currentValue = selector.value;
                selector.innerHTML = '';
                for (const value of values) {{
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = value;
                    selector.appendChild(option);
                }}
                // Restore previous selection if it's still valid
                if (values.includes(currentValue)) {{
                    selector.value = currentValue;
                }} else if (selectedValue) {{
                    selector.value = selectedValue;
                }}
            }}

            function updateDropdowns() {{
                let filteredData = allResultsData;

                // Sequentially filter and update dropdowns
                paramKeys.forEach(key => {{
                    const selectedValue = selectors[key].value;
                    
                    // Get available options for the current dropdown based on previous selections
                    const availableOptions = [...new Set(filteredData.map(item => item.params[key]))].sort();
                    populateSelector(selectors[key], availableOptions, selectedValue);
                    
                    // Filter data for the next dropdown
                    filteredData = filteredData.filter(item => item.params[key] === selectors[key].value);
                }});
                displayResults();
            }}

            function displayResults() {{
                const selections = {{
                    asset: selectors.asset.value,
                    timeframe: selectors.timeframe.value,
                    top_n: selectors.top_n.value,
                    shifts: selectors.shifts.value
                }};

                const filteredResult = allResultsData.find(item => 
                    item.params.asset === selections.asset &&
                    item.params.timeframe === selections.timeframe &&
                    item.params.top_n === selections.top_n &&
                    item.params.shifts === selections.shifts
                );

                resultsContentDiv.innerHTML = ''; // Clear previous results

                if (filteredResult) {{
                    resultsContentDiv.innerHTML += `<h2>Results for: ${{filteredResult.folder}}</h2>`;
                    filteredResult.files.forEach(file => {{
                        const filePath = `results/${{filteredResult.folder}}/${{file}}`;
                        if (file.endsWith('.png') || file.endsWith('.jpg') || file.endsWith('.jpeg') || file.endsWith('.gif')) {{
                            resultsContentDiv.innerHTML += `<img src="${{filePath}}" alt="${{file}}" style="max-width: 100%; height: auto; margin-bottom: 1rem;">`;
                        }} else if (file.endsWith('.csv')) {{
                            resultsContentDiv.innerHTML += `<p><a href="${{filePath}}" target="_blank">${{file}}</a></p>`;
                        }}
                    }});
                }} else {{
                    resultsContentDiv.innerHTML = '<p>No results found for the selected criteria. Please try another combination.</p>';
                }}
            }}

            // Add event listeners
            paramKeys.forEach(key => {{
                selectors[key].addEventListener('change', updateDropdowns);
            }});

            // Initial population
            updateDropdowns();
        }});
    </script>
    """
    return dropdowns_html + javascript

def main():
    # Scan results
    results_data = scan_results()

    # Generate dashboard HTML and JS
    dashboard_content = generate_dashboard_html(results_data)

    # Read template
    with open("index.template.html", "r") as f:
        template_content = f.read()

    # Replace placeholder
    final_html = template_content.replace("<!-- DASHBOARD_PLACEHOLDER -->", dashboard_content)

    # Write final HTML
    with open("index.html", "w") as f:
        f.write(final_html)

if __name__ == "__main__":
    main()