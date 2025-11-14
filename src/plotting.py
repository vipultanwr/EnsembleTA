import quantstats as qs
import os

def generate_quantstats_report(returns, title='Ensemble Strategy Report', output_filename="tearsheet.html"):
    """
    Generates a full QuantStats HTML report for a given returns series.

    Args:
        returns (pd.Series): A pandas Series of portfolio returns.
        title (str): The title for the report.
        output_filename (str): The name of the output HTML file.
    """
    print(f"\nGenerating QuantStats report: {output_filename}...")
    
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        qs.reports.html(returns, output=output_filename, title=title)
        print(f"Successfully saved report to {output_filename}")
    except Exception as e:
        print(f"Could not generate QuantStats report. Error: {e}")

