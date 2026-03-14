# Quick Start Guide

Get up and running with UN Speech Boilerplate Cleaner in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/un-speech-cleaner.git
cd un-speech-cleaner

# Install dependencies
pip install -r requirements.txt
```

## Step 1: Prepare Your Data

Place your UN speech CSV in the `Inputs/` directory. Your CSV should have:
- A `Text` column with speech content
- Optional: `Country` column
- Optional: `BLOC_*` columns for organization memberships

## Step 2: Run Basic Cleaning

```python
from src.clean_un_text_ngram import EnhancedUNTextCleaner

# Initialize the cleaner
cleaner = EnhancedUNTextCleaner(
    config_path="n-grams and cleaning data/config_boilerplate.json",
    ngram_boilerplate_path="ngram_boilerplate_aggressive.json"
)

# Process your CSV
df, stats = cleaner.clean_csv(
    input_csv="Inputs/your_speeches.csv",
    output_csv="Outputs/cleaned_speeches.csv",
    text_column='Text'  # Name of your text column
)

# View results
print(f"Average reduction: {stats['avg_reduction_percent']}%")
print(f"N-grams removed: {stats['total_ngrams_removed']}")
```

## Step 3: Extract International Organizations (Optional)

If your CSV has BLOC_ columns:

```python
df, stats = cleaner.clean_csv(
    input_csv="Inputs/your_speeches.csv",
    output_csv="Outputs/cleaned_speeches.csv",
    text_column='Text',
    bloc_json_output="Outputs/organizations.json"  # Export BLOC data
)
```

This creates a JSON file with country-organization mappings.

## Step 4: Customize (Optional)

### Make It More Aggressive

Edit `src/extract_ngram_boilerplate.py`:

```python
# Change this line (around line 279)
min_frequency=20,  # Lower number = more aggressive (e.g., 10)
```

Then regenerate:

```bash
python src/extract_ngram_boilerplate.py
```

### Add Custom Patterns

Edit `n-grams and cleaning data/config_boilerplate.json`:

```json
{
  "boilerplate_patterns": {
    "your_custom_category": {
      "enabled": true,
      "description": "Your custom boilerplate",
      "patterns": [
        "(?i)pattern_to_remove"
      ]
    }
  }
}
```

## Common Use Cases

### Single Text Cleaning

```python
text = "The President: On behalf of the General Assembly..."
cleaned, stats = cleaner.clean_text(text)
print(cleaned)
```

### Batch Processing

```python
# Process first 100 rows for testing
df, stats = cleaner.clean_csv(
    input_csv="Inputs/large_dataset.csv",
    output_csv="Outputs/test_output.csv",
    sample_size=100
)

# Then process all
df, stats = cleaner.clean_csv(
    input_csv="Inputs/large_dataset.csv",
    output_csv="Outputs/full_output.csv"
)
```

### Comparison

```python
# Run both methods for comparison
from src.clean_un_text import UNTextCleaner

# Old method (patterns only)
old_cleaner = UNTextCleaner(config_path)
old_cleaned, old_stats = old_cleaner.clean_text(text)

# New method (n-grams + patterns)
new_cleaned, new_stats = cleaner.clean_text(text)

print(f"Old: {old_stats['reduction_percent']}%")
print(f"New: {new_stats['reduction_percent']}%")
```

## Example Output

**Before:**
```
The President: On behalf of the General Assembly, I have the honour to
welcome to the United Nations His Excellency Mr. John Smith, President
of the Republic of Example, and to invite him to address the Assembly.

President Smith (spoke in English): Allow me at the outset to congratulate
His Excellency Mr. Peter Thomson on his election as President...

[1500 words of actual speech content]

In conclusion, we reaffirm our commitment to the ideals of the United Nations.
```

**After:**
```
[1500 words of actual speech content - boilerplate removed]
```

**Statistics:**
- Original: 12,236 characters
- Cleaned: 11,744 characters
- Reduction: 4.0%
- N-grams removed: 3 instances
- Pattern matches: 2 instances

## Troubleshooting

### "No such file or directory"
- Check that your paths are correct
- Use absolute paths if relative paths fail

### "Column 'Text' not found"
- Verify your CSV has the correct column name
- Use the `text_column` parameter to specify: `text_column='YourColumnName'`

### Low reduction percentage (<5%)
- Your speeches may already be cleaned
- Try lowering the n-gram frequency threshold
- Check if boilerplate is in a different language

### High reduction percentage (>50%)
- Verify substantive content is preserved
- May be removing too much - increase frequency threshold
- Check output manually

## Next Steps

1. Review cleaned output manually
2. Adjust parameters based on your needs
3. Process full dataset
4. Share your results!

## Need Help?

- Check [README.md](README.md) for detailed documentation
- See [BOILERPLATE_ANALYSIS_AND_RECOMMENDATIONS.md](BOILERPLATE_ANALYSIS_AND_RECOMMENDATIONS.md) for methodology
- Open an issue on GitHub
