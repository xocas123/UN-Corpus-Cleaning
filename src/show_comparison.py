import pandas as pd

# Load sample data
df = pd.read_csv('gate_mwe_cleaned_sample.csv')

# Show first record comparison
print("="*90)
print("DETAILED BEFORE & AFTER COMPARISON (First Record)")
print("="*90)

row = df.iloc[0]
original = str(row['Text'])
cleaned = str(row['Text_cleaned'])

print("\nBEFORE CLEANING (500 chars):")
print("-"*90)
print(original[:500])

print("\n\nAFTER CLEANING (500 chars):")
print("-"*90)
print(cleaned[:500])

print("\n\nSTATISTICS FOR THIS RECORD:")
print("-"*90)
print(f"Original length: {len(original):,} characters")
print(f"Cleaned length: {len(cleaned):,} characters")
print(f"Reduction: {round((1 - len(cleaned)/len(original))*100, 1)}%")

# Show summary stats across all 100 rows
print("\n\n" + "="*90)
print("SUMMARY STATISTICS (100 rows)")
print("="*90)
total_orig = df['Text'].str.len().sum()
total_clean = df['Text_cleaned'].str.len().sum()
print(f"Total original chars: {total_orig:,}")
print(f"Total cleaned chars: {total_clean:,}")
print(f"Average reduction: {round((1 - total_clean/total_orig)*100, 2)}%")
