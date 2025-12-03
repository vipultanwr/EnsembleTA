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
    """Scans the results directory and generates a JSON file with the data."""
    results_dir = "results"
    results_data = []
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

    with open("results_data.json", "w") as f:
        json.dump(results_data, f, indent=4)

if __name__ == "__main__":
    scan_results()
