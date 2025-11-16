import quantstats as qs
import matplotlib.pyplot as plt
import sys
import os

def generate_quantstats_report(returns, title, output_filename):
    """
    Generates and saves a comprehensive QuantStats HTML report.
    """
    print(f"Generating QuantStats report: {output_filename}", file=sys.stderr)
    # Ensure the directory exists
    output_dir = os.path.dirname(output_filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    qs.reports.html(returns, title=title, output=output_filename, download_filename=output_filename)
    print(f"Successfully saved report to {output_filename}", file=sys.stderr)

