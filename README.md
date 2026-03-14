# UN Speech Boilerplate Cleaner

A data-driven tool for removing boilerplate text from United Nations speeches and documents using frequency-based n-gram analysis combined with pattern matching.

## 🎯 Overview

This project addresses the challenge of cleaning UN speeches by removing:
- Administrative boilerplate (budget tables, status markers)
- Procedural references (committee citations, document numbers)
- Ceremonial phrases (greetings, congratulations, closing statements)
- Formatting artifacts (repeated punctuation, OCR errors)
- Standard entity names (long-form organization names)
- Document metadata (page numbers, volume references)

### Key Features

- **Data-Driven Approach**: Extracts boilerplate from actual corpus using n-gram frequency analysis
- **Dual Cleaning Methods**: Combines n-gram exact matching with regex pattern matching
- **International Organization Extraction**: Exports BLOC_ membership columns to structured JSON
- **Configurable Aggressiveness**: Adjustable frequency thresholds and category selection
- **Comprehensive Statistics**: Detailed removal metrics and before/after comparisons

## 📊 Performance

**Current Results (100 sample speeches):**
- Average text reduction: **16.9%** (vs 12.9% with patterns only)
- N-gram matches removed: **198 instances**
- Pattern matches removed: **847 instances**
- Extracted **567 unique boilerplate phrases** from corpus

**Boilerplate Categories:**
- Formatting artifacts: 36 phrases
- Administrative text: 288 phrases
- Procedural references: 128 phrases
- Entity names: 97 phrases
- Ceremonial phrases: 2 phrases
- Metadata: 16 phrases

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/un-speech-cleaner.git
cd un-speech-cleaner

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.clean_un_text_ngram import EnhancedUNTextCleaner

# Initialize cleaner
cleaner = EnhancedUNTextCleaner(
    config_path="n-grams and cleaning data/config_boilerplate.json",
    ngram_boilerplate_path="ngram_boilerplate_aggressive.json"
)

# Clean a single text
text = "The President: On behalf of the General Assembly..."
cleaned_text, stats = cleaner.clean_text(text)

print(f"Original: {stats['original_length']} chars")
print(f"Cleaned: {stats['cleaned_length']} chars")
print(f"Reduction: {stats['reduction_percent']}%")
```

### Processing CSV Files

```python
# Process entire CSV dataset
df, stats = cleaner.clean_csv(
    input_csv="Inputs/gate_mwe.csv",
    output_csv="Outputs/cleaned_speeches.csv",
    text_column='Text',
    bloc_json_output="Outputs/international_orgs.json"
)
```

## 📁 Project Structure

```
un-cleaning/
├── src/
│   ├── clean_un_text.py              # Original pattern-based cleaner
│   ├── clean_un_text_ngram.py        # Enhanced n-gram + pattern cleaner
│   ├── extract_ngram_boilerplate.py  # N-gram boilerplate extractor
│   ├── analyze_frequencies.py        # Frequency analysis tools
│   └── run_full_cleaning.py          # Batch processing script
├── n-grams and cleaning data/
│   ├── config_boilerplate.json       # Regex pattern configuration
│   └── frequency csv/                # N-gram frequency data
│       ├── frequency_4grams.csv
│       ├── frequency_5grams.csv
│       ├── ...
│       └── frequency_10grams.csv
├── Inputs/                           # Input data directory
├── ngram_boilerplate_aggressive.json # Extracted boilerplate phrases
├── BOILERPLATE_ANALYSIS_AND_RECOMMENDATIONS.md  # Detailed analysis
└── README.md
```

## 🔧 Advanced Usage

### Extract Boilerplate from Your Corpus

```bash
# Extract boilerplate phrases from n-gram frequency files
python src/extract_ngram_boilerplate.py
```

This generates `ngram_boilerplate_aggressive.json` with categorized phrases.

### Customize Cleaning Aggressiveness

Edit the frequency threshold in `extract_ngram_boilerplate.py`:

```python
boilerplate = extractor.extract_all(
    min_frequency=20,  # Lower = more aggressive (default: 20)
    output_json=output_json
)
```

### Select Removal Categories

```python
# Clean with specific categories only
cleaned_text, stats = cleaner.clean_text(
    text,
    use_ngrams=True,
    use_patterns=True
)

# Categories automatically used: formatting, administrative,
# procedural, metadata, entity_names, ceremonial
```

## 📈 Methodology

### 1. N-gram Frequency Analysis

The system analyzes n-grams (4-10 words) across the entire corpus to identify high-frequency phrases that appear repeatedly across documents but carry little substantive meaning.

**Top Boilerplate Examples:**
- `(thousands of united states dollars)` - 1,163 occurrences
- `official records of the general assembly` - 1,139 occurrences
- `agreed with the board's recommendation` - 785 occurrences
- `report of the secretary-general` - 952 occurrences

### 2. Pattern-Based Removal

Regex patterns target specific boilerplate types:
- Opening ceremonials
- Procedural markers
- Document references
- Closing statements
- Administrative metadata

### 3. Dual-Pass Cleaning

1. **First Pass**: N-gram exact matching (fast, data-driven)
2. **Second Pass**: Regex pattern matching (flexible, catches variations)
3. **Post-processing**: Whitespace normalization, paragraph filtering

## 📊 Comparison with Existing Methods

**Academic Approaches (Baturo et al. 2017, 2025):**
- Basic preprocessing: tokenization, stopwords, stemming
- **No specific boilerplate removal**

**This Project:**
- Data-driven n-gram extraction
- Combined with pattern matching
- **Achieves 16.9% text reduction**
- Preserves substantive content

## 🔍 Data Sources

This project works with UN General Debate speeches and can process:
- UN General Assembly transcripts
- Security Council records
- Committee meeting transcripts
- Any structured UN document corpus

**Format Requirements:**
- CSV file with text column
- Optional: BLOC_ columns for international organization memberships

## 🛠️ Tools & Dependencies

- Python 3.8+
- pandas
- json (standard library)
- re (standard library)
- pathlib (standard library)

## 📝 Configuration Files

### config_boilerplate.json

Defines regex patterns for different boilerplate categories:

```json
{
  "boilerplate_patterns": {
    "procedural_markers": {
      "enabled": true,
      "patterns": [
        "(?:The\\s+)?(?:President|Chair|Chairperson):\\s+.*?(?=\\n[A-Z])"
      ]
    }
  }
}
```

### ngram_boilerplate_aggressive.json

Auto-generated categorized phrases from corpus:

```json
[
  {
    "category": "administrative",
    "phrases": [
      {
        "phrase": "(thousands of united states dollars)",
        "frequency": 1163,
        "ngram_size": "5"
      }
    ]
  }
]
```

## 📚 Documentation

- [BOILERPLATE_ANALYSIS_AND_RECOMMENDATIONS.md](BOILERPLATE_ANALYSIS_AND_RECOMMENDATIONS.md) - Detailed analysis of cleaning effectiveness
- [Comparison Analysis](compare_cleaning_methods.py) - Compare different cleaning approaches

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Machine learning-based boilerplate detection
- Multi-language support
- Additional document types (Security Council, ECOSOC)
- Improved regex patterns
- Performance optimization

## 📄 License

MIT License - feel free to use and modify for your research.

## 🔗 Related Work

- **UN General Debate Corpus (UNGDC)**: Baturo, Dasandi, Mikhaylov (2017, 2025)
- **UN Parallel Corpus**: Official UN multilingual corpus
- **Research**: "Understanding State Preferences With Text As Data" (Research & Politics, 2017)

## 📧 Contact

For questions, issues, or collaboration opportunities, please open an issue on GitHub.

## 🙏 Acknowledgments

- N-gram frequency data extracted from UN document corpus
- Configuration patterns developed through manual analysis of UN speeches
- Inspired by academic work on UN General Debate Corpus

---

**Note**: This tool is designed for research purposes. For production use, please validate outputs and adjust parameters based on your specific corpus characteristics.
