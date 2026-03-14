"""
View random samples of cleaned vs original text to evaluate cleaning quality
"""

import pandas as pd
import random

def print_comparison(original, cleaned, index, doc_id=""):
    """Print a before/after comparison"""
    print("\n" + "="*100)
    print(f"SAMPLE #{index}" + (f" (doc_id: {doc_id})" if doc_id else ""))
    print("="*100)

    # Calculate stats
    orig_len = len(original) if isinstance(original, str) else 0
    clean_len = len(cleaned) if isinstance(cleaned, str) else 0
    reduction = round((1 - clean_len / orig_len) * 100, 2) if orig_len > 0 else 0

    print(f"\nStats: Original: {orig_len:,} chars | Cleaned: {clean_len:,} chars | Reduction: {reduction}%")

    print("\n" + "-"*100)
    print("ORIGINAL TEXT:")
    print("-"*100)
    print(original[:2000] + ("..." if len(str(original)) > 2000 else ""))

    print("\n" + "-"*100)
    print("CLEANED TEXT:")
    print("-"*100)
    print(cleaned[:2000] + ("..." if len(str(cleaned)) > 2000 else ""))
    print("="*100)


if __name__ == "__main__":
    # Load the cleaned dataset
    csv_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe_v2_cleaned.csv"

    print("Loading cleaned dataset...")
    df = pd.read_csv(csv_path, low_memory=False)

    print(f"Loaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")

    # Check if we have both original and cleaned text
    if 'Text' not in df.columns or 'Text_cleaned' not in df.columns:
        print("\nError: Expected 'Text' and 'Text_cleaned' columns")
        print(f"Available columns: {list(df.columns)}")
        exit(1)

    # Filter to rows with non-empty text
    df_valid = df[(df['Text'].notna()) & (df['Text_cleaned'].notna())].copy()
    print(f"\nRows with valid text: {len(df_valid)}")

    # Calculate reduction for each row
    df_valid['reduction'] = df_valid.apply(
        lambda row: round((1 - len(str(row['Text_cleaned'])) / len(str(row['Text']))) * 100, 2)
        if len(str(row['Text'])) > 0 else 0,
        axis=1
    )

    # Show overall stats
    print("\n" + "="*100)
    print("OVERALL CLEANING STATISTICS")
    print("="*100)
    print(f"Average reduction: {df_valid['reduction'].mean():.2f}%")
    print(f"Median reduction: {df_valid['reduction'].median():.2f}%")
    print(f"Min reduction: {df_valid['reduction'].min():.2f}%")
    print(f"Max reduction: {df_valid['reduction'].max():.2f}%")

    # Show distribution
    print("\nReduction distribution:")
    print(f"  0-10%:   {len(df_valid[df_valid['reduction'] < 10])} docs ({len(df_valid[df_valid['reduction'] < 10])/len(df_valid)*100:.1f}%)")
    print(f"  10-25%:  {len(df_valid[(df_valid['reduction'] >= 10) & (df_valid['reduction'] < 25)])} docs ({len(df_valid[(df_valid['reduction'] >= 10) & (df_valid['reduction'] < 25)])/len(df_valid)*100:.1f}%)")
    print(f"  25-50%:  {len(df_valid[(df_valid['reduction'] >= 25) & (df_valid['reduction'] < 50)])} docs ({len(df_valid[(df_valid['reduction'] >= 25) & (df_valid['reduction'] < 50)])/len(df_valid)*100:.1f}%)")
    print(f"  50-75%:  {len(df_valid[(df_valid['reduction'] >= 50) & (df_valid['reduction'] < 75)])} docs ({len(df_valid[(df_valid['reduction'] >= 50) & (df_valid['reduction'] < 75)])/len(df_valid)*100:.1f}%)")
    print(f"  75-100%: {len(df_valid[df_valid['reduction'] >= 75])} docs ({len(df_valid[df_valid['reduction'] >= 75]/len(df_valid)*100:.1f}%)")

    # Show samples from different reduction levels
    print("\n" + "="*100)
    print("SAMPLE COMPARISONS")
    print("="*100)

    # Sample 1: Low reduction (< 10%)
    low_reduction = df_valid[df_valid['reduction'] < 10]
    if len(low_reduction) > 0:
        sample = low_reduction.sample(1).iloc[0]
        doc_id = sample.get('doc_id', '')
        print_comparison(sample['Text'], sample['Text_cleaned'], 1, doc_id)
        print(f"\n>>> LOW REDUCTION EXAMPLE ({sample['reduction']}%) - Mostly substantive content")

    # Sample 2: Medium reduction (25-50%)
    med_reduction = df_valid[(df_valid['reduction'] >= 25) & (df_valid['reduction'] < 50)]
    if len(med_reduction) > 0:
        sample = med_reduction.sample(1).iloc[0]
        doc_id = sample.get('doc_id', '')
        print_comparison(sample['Text'], sample['Text_cleaned'], 2, doc_id)
        print(f"\n>>> MEDIUM REDUCTION EXAMPLE ({sample['reduction']}%) - Mix of content and boilerplate")

    # Sample 3: High reduction (> 50%)
    high_reduction = df_valid[df_valid['reduction'] >= 50]
    if len(high_reduction) > 0:
        sample = high_reduction.sample(1).iloc[0]
        doc_id = sample.get('doc_id', '')
        print_comparison(sample['Text'], sample['Text_cleaned'], 3, doc_id)
        print(f"\n>>> HIGH REDUCTION EXAMPLE ({sample['reduction']}%) - Heavy boilerplate removed")

    # Sample 4: Random sample
    sample = df_valid.sample(1).iloc[0]
    doc_id = sample.get('doc_id', '')
    print_comparison(sample['Text'], sample['Text_cleaned'], 4, doc_id)
    print(f"\n>>> RANDOM SAMPLE ({sample['reduction']}%)")

    print("\n" + "="*100)
    print("EVALUATION COMPLETE")
    print("="*100)
    print("\nReview the samples above to assess:")
    print("  1. Is important content being preserved?")
    print("  2. Is boilerplate being effectively removed?")
    print("  3. Are there patterns we're missing that should be cleaned?")
