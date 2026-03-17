"""
Full cleaning pipeline for lawsec_v1.18i_cluster.csv
Steps:
  1. N-gram frequency analysis (sample)
  2. Boilerplate extraction from frequency CSVs
  3. Cleaning with n-gram + pattern removal
"""

import sys
import os
import csv
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE        = Path(r"c:\Users\joaqu\OneDrive\Desktop\UN-Corpus-Cleaning")
SRC         = BASE / "src"
NGRAM_DIR   = BASE / "n-grams and cleaning data" / "frequency csv"
CONFIG      = BASE / "n-grams and cleaning data" / "config_boilerplate.json"
NGRAM_JSON  = BASE / "ngram_boilerplate_aggressive.json"

INPUT_CSV   = BASE / "lawsec_v1.18i_cluster.csv"
OUTPUT_CSV  = BASE / "lawsec_v1.18i_cluster_cleaned.csv"

TEXT_COLUMN = "Text"
FLAG_COLUMN = "Flag_Valid"   # rows where Flag_Valid != 1 skip cleaning
SAMPLE_SIZE = 20000  # rows for n-gram frequency analysis (random sample)
TOP_N       = 500    # top n-grams to keep per size
MIN_FREQ    = 15     # minimum frequency to flag as boilerplate

sys.path.insert(0, str(SRC))

# ── Step 1: N-gram frequency analysis ─────────────────────────────────────────
print("=" * 70)
print("STEP 1: N-GRAM FREQUENCY ANALYSIS")
print(f"  Input : {INPUT_CSV}")
print(f"  Sample: {SAMPLE_SIZE:,} rows (random, stratified)")
print("=" * 70)

from analyze_frequencies import FrequencyAnalyzer

os.makedirs(NGRAM_DIR, exist_ok=True)

analyzer = FrequencyAnalyzer(str(INPUT_CSV), TEXT_COLUMN)
analyzer.load_data(sample_size=SAMPLE_SIZE)

# Words
word_freq = analyzer.analyze_word_frequency(TOP_N)
analyzer.print_top_frequencies(word_freq, "WORDS", show_top=20)
word_out = NGRAM_DIR / "frequency_words.csv"
analyzer.save_frequency_report(word_freq, str(word_out), "word")

# N-grams 4–10
for n in range(4, 11):
    ngram_freq = analyzer.analyze_ngram_frequency(n, TOP_N)
    analyzer.print_top_frequencies(ngram_freq, f"{n}-GRAMS", show_top=10)
    out = NGRAM_DIR / f"frequency_{n}grams.csv"
    analyzer.save_frequency_report(ngram_freq, str(out), f"{n}-gram")

print(f"\n[OK] Frequency CSVs saved to: {NGRAM_DIR}")

# ── Step 2: Boilerplate extraction ────────────────────────────────────────────
print()
print("=" * 70)
print("STEP 2: BOILERPLATE EXTRACTION")
print(f"  Source  : {NGRAM_DIR}")
print(f"  Min freq: {MIN_FREQ}")
print("=" * 70)

from extract_ngram_boilerplate import NgramBoilerplateExtractor

extractor = NgramBoilerplateExtractor(str(NGRAM_DIR))
extractor.extract_all(min_frequency=MIN_FREQ, output_json=str(NGRAM_JSON))
print(f"[OK] Boilerplate JSON saved to: {NGRAM_JSON}")

# ── Step 3: Cleaning ──────────────────────────────────────────────────────────
print()
print("=" * 70)
print("STEP 3: CLEANING")
print(f"  Input : {INPUT_CSV}")
print(f"  Output: {OUTPUT_CSV}")
print("=" * 70)

from clean_un_text_ngram import EnhancedUNTextCleaner

if not CONFIG.exists():
    print(f"ERROR: Config not found at {CONFIG}")
    sys.exit(1)

cleaner = EnhancedUNTextCleaner(str(CONFIG), str(NGRAM_JSON))

df, stats = cleaner.clean_csv(
    str(INPUT_CSV),
    str(OUTPUT_CSV),
    text_column=TEXT_COLUMN,
    flag_column=FLAG_COLUMN,
    flag_valid_value=1,
    sample_size=None,   # clean ALL rows
    verbose=True,
)

print()
print("=" * 70)
print("PIPELINE COMPLETE")
print("=" * 70)
print(f"  Rows processed  : {stats['total_rows']:,}")
print(f"  Skipped invalid : {stats['skipped_invalid_rows']:,}")
print(f"  OCR fixed rows  : {stats['total_ocr_fixed_rows']:,}")
print(f"  Original chars  : {stats['total_original_chars']:,}")
print(f"  Cleaned chars   : {stats['total_cleaned_chars']:,}")
print(f"  Avg reduction   : {stats['avg_reduction_percent']}%")
print(f"  N-grams removed : {stats['total_ngrams_removed']:,}")
print(f"  Pattern matches : {stats['total_patterns_removed']:,}")
print(f"\n  Output: {OUTPUT_CSV}")
