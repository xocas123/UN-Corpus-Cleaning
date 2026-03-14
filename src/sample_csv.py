"""
Sample CSV Reader for Large UN Documents Dataset
Efficiently reads and displays sample rows from the large gate_mwe.csv file
"""

import pandas as pd
import sys
from pathlib import Path


def sample_csv(csv_path, n_rows=5, output_columns=None):
    """
    Read and display sample rows from CSV file.
    
    Args:
        csv_path: Path to CSV file
        n_rows: Number of sample rows to display
        output_columns: List of specific columns to show (if None, shows key columns)
    """
    
    try:
        # Define key columns we care about
        key_columns = ['Country', 'Date', 'Forum', 'Title', 'Text', 'Source', 'doc_id']
        
        # Read CSV with specific columns to reduce memory
        print(f"Reading CSV file: {csv_path}")
        print(f"This may take a moment for large files...\n")
        
        # Read just the columns we need
        df = pd.read_csv(csv_path, usecols=key_columns, nrows=n_rows)
        
        print(f"Successfully loaded {len(df)} rows\n")
        print("=" * 100)
        
        for idx, row in df.iterrows():
            print(f"\nRow {idx + 1}:")
            print(f"  Country: {row['Country']}")
            print(f"  Date: {row['Date']}")
            print(f"  Forum: {row['Forum']}")
            print(f"  Source: {row['Source']}")
            print(f"  Doc ID: {row['doc_id']}")
            print(f"\n  Text Preview (first 500 chars):")
            text = str(row['Text'])[:500]
            print(f"  {text}...")
            print("\n" + "-" * 100)
        
        print(f"\n✓ Total rows in file: {pd.read_csv(csv_path, usecols=['doc_id']).shape[0]}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        sys.exit(1)


def get_file_info(csv_path):
    """Get basic info about the CSV file"""
    try:
        # Just read first row to get column names
        df = pd.read_csv(csv_path, nrows=1)
        print(f"CSV Columns ({len(df.columns)} total):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:3d}. {col}")
        print()
    except Exception as e:
        print(f"Error reading file info: {str(e)}")


if __name__ == "__main__":
    # Path to the CSV file
    csv_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\gate_mwe.csv"
    
    print("UN Documents CSV Sample Viewer\n")
    
    # Show file info
    get_file_info(csv_path)
    
    # Show sample rows
    print("=" * 100)
    print("SAMPLE DATA (first 3 rows with text)\n")
    sample_csv(csv_path, n_rows=3)
