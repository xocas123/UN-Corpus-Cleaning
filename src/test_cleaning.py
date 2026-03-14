"""Test script to process CSV with 100 row sample"""
from clean_un_text import UNTextCleaner
import pandas as pd

cleaner = UNTextCleaner('config_boilerplate.json')
print('Processing 100 rows from CSV...\n')

df, stats = cleaner.clean_csv(
    'gate_mwe.csv',
    'gate_mwe_cleaned_sample.csv',
    text_column='Text',
    sample_size=100,
    verbose=True
)

print('\n' + '='*70)
print('CLEANING RESULTS (100 rows sample)')
print('='*70)
print(f'Rows processed: {stats["total_rows"]}')
print(f'Original characters: {stats["total_original_chars"]:,}')
print(f'Cleaned characters: {stats["total_cleaned_chars"]:,}')
print(f'Average reduction: {stats["avg_reduction_percent"]}%')
print(f'Characters removed: {stats["total_original_chars"] - stats["total_cleaned_chars"]:,}')
print('='*70)

# Show sample comparison
print('\nSample comparison (first row):')
print('-'*70)
print('ORIGINAL TEXT (first 300 chars):')
print(df['Text'].iloc[0][:300])
print('\nCLEANED TEXT (first 300 chars):')
print(df['Text_cleaned'].iloc[0][:300])
