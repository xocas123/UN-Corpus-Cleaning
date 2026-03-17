"""
UN Document N-gram Frequency Analyzer

This script analyzes word and n-gram frequencies in UN documents to identify
common boilerplate phrases that can be targeted for removal.

Focus: 4-10 word n-grams (phrases) to capture longer boilerplate patterns
"""

import pandas as pd
from collections import Counter
import re
from typing import List, Dict, Tuple
import csv


class FrequencyAnalyzer:
    """Analyze word and n-gram frequencies in UN documents"""

    def __init__(self, csv_path: str, text_column: str = 'Text'):
        """
        Initialize the analyzer

        Args:
            csv_path: Path to the CSV file
            text_column: Name of the column containing text
        """
        self.csv_path = csv_path
        self.text_column = text_column
        self.df = None

    def load_data(self, sample_size: int = None):
        """
        Load data from CSV

        Args:
            sample_size: Number of rows to sample (None = load all)
        """
        print(f"Loading data from {self.csv_path}...")

        if sample_size:
            # Load full CSV then draw a stratified random sample (avoids
            # temporal bias that sequential nrows would introduce)
            print(f"Loading full CSV for random sampling ({sample_size} rows)...")
            self.df = pd.read_csv(self.csv_path, low_memory=False)
            self.df = self.df[self.df[self.text_column].notna()]
            self.df = self.df.sample(
                n=min(sample_size, len(self.df)), random_state=42
            )
            print(f"Sampled {len(self.df)} documents (random, seed=42)")
        else:
            print("Loading full dataset (this may take a while)...")
            self.df = pd.read_csv(self.csv_path, low_memory=False)
            # Remove NaN values
            self.df = self.df[self.df[self.text_column].notna()]
            print(f"Loaded {len(self.df)} documents")

    def preprocess_text(self, text: str) -> str:
        """
        Basic text preprocessing

        Args:
            text: Input text

        Returns:
            Preprocessed text
        """
        if not isinstance(text, str):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def extract_ngrams(self, text: str, n: int) -> List[str]:
        """
        Extract n-grams from text

        Args:
            text: Input text
            n: N-gram size (number of words)

        Returns:
            List of n-grams
        """
        # Split into words (keeping basic punctuation for context)
        words = text.split()

        # Generate n-grams
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)

        return ngrams

    def analyze_word_frequency(self, top_n: int = 100) -> List[Tuple[str, int]]:
        """
        Analyze individual word frequencies

        Args:
            top_n: Number of top words to return

        Returns:
            List of (word, count) tuples
        """
        print("\nAnalyzing word frequencies...")
        word_counter = Counter()

        for text in self.df[self.text_column]:
            processed = self.preprocess_text(text)
            words = processed.split()
            word_counter.update(words)

        return word_counter.most_common(top_n)

    def analyze_ngram_frequency(self, n: int, top_n: int = 100) -> List[Tuple[str, int]]:
        """
        Analyze n-gram frequencies

        Args:
            n: N-gram size (4-10)
            top_n: Number of top n-grams to return

        Returns:
            List of (n-gram, count) tuples
        """
        print(f"\nAnalyzing {n}-gram frequencies...")
        ngram_counter = Counter()

        for idx, text in enumerate(self.df[self.text_column]):
            if idx % 100 == 0 and idx > 0:
                print(f"  Processed {idx}/{len(self.df)} documents...")

            processed = self.preprocess_text(text)
            ngrams = self.extract_ngrams(processed, n)
            ngram_counter.update(ngrams)

        print(f"  Found {len(ngram_counter)} unique {n}-grams")
        return ngram_counter.most_common(top_n)

    def save_frequency_report(self, frequencies: List[Tuple[str, int]],
                             output_file: str, label: str):
        """
        Save frequency analysis to CSV

        Args:
            frequencies: List of (phrase, count) tuples
            output_file: Output CSV file path
            label: Label for the type of analysis
        """
        print(f"\nSaving {label} to {output_file}...")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Rank', 'Phrase', 'Frequency', 'Type'])

            for rank, (phrase, count) in enumerate(frequencies, 1):
                writer.writerow([rank, phrase, count, label])

        print(f"  Saved {len(frequencies)} entries")

    def print_top_frequencies(self, frequencies: List[Tuple[str, int]],
                             label: str, show_top: int = 20):
        """
        Print top frequencies to console

        Args:
            frequencies: List of (phrase, count) tuples
            label: Label for the type of analysis
            show_top: Number of top items to display
        """
        print(f"\n{'='*80}")
        print(f"TOP {show_top} {label}")
        print(f"{'='*80}")
        print(f"{'Rank':<6} {'Frequency':<12} {'Phrase'}")
        print(f"{'-'*80}")

        for rank, (phrase, count) in enumerate(frequencies[:show_top], 1):
            # Truncate long phrases for display
            display_phrase = phrase[:100] + '...' if len(phrase) > 100 else phrase
            print(f"{rank:<6} {count:<12} {display_phrase}")

    def run_full_analysis(self, sample_size: int = None,
                         ngram_range: Tuple[int, int] = (4, 10),
                         top_n: int = 100,
                         save_to_csv: bool = True):
        """
        Run complete frequency analysis

        Args:
            sample_size: Number of documents to sample (None = all)
            ngram_range: Range of n-gram sizes to analyze (min, max)
            top_n: Number of top items to extract
            save_to_csv: Whether to save results to CSV files
        """
        # Load data
        self.load_data(sample_size)

        # Analyze word frequencies
        word_freq = self.analyze_word_frequency(top_n)
        self.print_top_frequencies(word_freq, "WORDS", show_top=30)

        if save_to_csv:
            self.save_frequency_report(word_freq,
                                      'frequency_words.csv',
                                      'word')

        # Analyze n-grams
        min_n, max_n = ngram_range
        for n in range(min_n, max_n + 1):
            ngram_freq = self.analyze_ngram_frequency(n, top_n)
            self.print_top_frequencies(ngram_freq, f"{n}-GRAMS", show_top=20)

            if save_to_csv:
                self.save_frequency_report(ngram_freq,
                                          f'frequency_{n}grams.csv',
                                          f'{n}-gram')

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)

        if save_to_csv:
            print("\nResults saved to:")
            print(f"  - frequency_words.csv")
            for n in range(min_n, max_n + 1):
                print(f"  - frequency_{n}grams.csv")


def main():
    """Main execution function"""

    # Configuration
    CSV_FILE = 'gate_mwe.csv'
    TEXT_COLUMN = 'Text'

    # Sample size (set to None to analyze full dataset)
    # Use smaller sample for quick testing, None for comprehensive analysis
    SAMPLE_SIZE = 1000  # Set to None for full dataset

    # N-gram range (4-10 words as requested)
    NGRAM_MIN = 4
    NGRAM_MAX = 10

    # Number of top items to extract and save
    TOP_N = 200

    # Whether to save results to CSV
    SAVE_TO_CSV = True

    print("="*80)
    print("UN DOCUMENT N-GRAM FREQUENCY ANALYZER")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Input file: {CSV_FILE}")
    print(f"  Sample size: {SAMPLE_SIZE if SAMPLE_SIZE else 'Full dataset'}")
    print(f"  N-gram range: {NGRAM_MIN}-{NGRAM_MAX} words")
    print(f"  Top N results: {TOP_N}")
    print(f"  Save to CSV: {SAVE_TO_CSV}")
    print()

    # Create analyzer
    analyzer = FrequencyAnalyzer(CSV_FILE, TEXT_COLUMN)

    # Run analysis
    analyzer.run_full_analysis(
        sample_size=SAMPLE_SIZE,
        ngram_range=(NGRAM_MIN, NGRAM_MAX),
        top_n=TOP_N,
        save_to_csv=SAVE_TO_CSV
    )


if __name__ == '__main__':
    main()
