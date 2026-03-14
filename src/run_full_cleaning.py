"""
Run full dataset cleaning with updated config v2.0
Creates a new cleaned file while preserving the original
"""

from clean_un_text import UNTextCleaner
from pathlib import Path

if __name__ == "__main__":
    print("="*80)
    print("UN DOCUMENT CLEANING - FULL DATASET")
    print("="*80)

    # Configuration
    config_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\n-grams and cleaning data\config_boilerplate.json"
    csv_input = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe.csv"
    csv_output = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe_v2_cleaned.csv"

    print(f"\nInput file: {csv_input}")
    print(f"Output file: {csv_output}")
    print(f"Config: {config_path}")

    # Check if input exists
    if not Path(csv_input).exists():
        print(f"\nError: Input file not found at {csv_input}")
        exit(1)

    # Warn if output exists
    if Path(csv_output).exists():
        print(f"\nWarning: Output file already exists and will be overwritten: {csv_output}")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            exit(0)

    # Initialize cleaner
    print("\nInitializing cleaner with config v2.0...")
    cleaner = UNTextCleaner(config_path)

    print("\nProcessing full dataset (this may take several minutes)...")
    print("Progress will be shown every 100 rows...")

    # Process full CSV (sample_size=None means process all)
    df, total_stats = cleaner.clean_csv(
        csv_input,
        csv_output,
        text_column='Text',
        sample_size=None,  # Process ALL rows
        verbose=True
    )

    print("\n" + "="*80)
    print("CLEANING COMPLETE!")
    print("="*80)
    print(f"\nFinal Statistics:")
    print(f"  Total rows processed: {total_stats['total_rows']:,}")
    print(f"  Total original chars: {total_stats['total_original_chars']:,}")
    print(f"  Total cleaned chars: {total_stats['total_cleaned_chars']:,}")
    print(f"  Average reduction: {total_stats['avg_reduction_percent']}%")
    print(f"\nOutput saved to: {csv_output}")
    print("\nOriginal file preserved at: {csv_input}")
