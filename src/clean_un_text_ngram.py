"""
Enhanced UN Document Cleaner with N-gram Based Boilerplate Removal
Combines regex patterns with data-driven n-gram removal
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


class EnhancedUNTextCleaner:
    """Clean boilerplate text from UN documents using n-grams + patterns"""

    def __init__(self, config_path: str, ngram_boilerplate_path: str = None):
        """
        Initialize cleaner with config and n-gram boilerplate

        Args:
            config_path: Path to config_boilerplate.json
            ngram_boilerplate_path: Path to ngram_boilerplate.json (optional)
        """
        self.config = self._load_config(config_path)
        self.patterns = self._compile_patterns()
        self.ngram_boilerplate = self._load_ngram_boilerplate(ngram_boilerplate_path)

    def _load_config(self, config_path: str) -> Dict:
        """Load and validate configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[OK] Loaded config from {config_path}")
            return config
        except FileNotFoundError:
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            sys.exit(1)

    def _load_ngram_boilerplate(self, ngram_path: str = None) -> Dict[str, List[str]]:
        """Load n-gram boilerplate phrases"""
        if not ngram_path or not Path(ngram_path).exists():
            print("[INFO] No n-gram boilerplate file provided, using patterns only")
            return {}

        try:
            with open(ngram_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert to flat lists sorted by length (longest first)
            boilerplate = {}
            for category, phrases in data.items():
                if phrases:
                    # Extract just the phrase strings
                    phrase_list = [item['phrase'] for item in phrases]
                    # Sort by length (longest first) to avoid partial matches
                    phrase_list = sorted(phrase_list, key=len, reverse=True)
                    boilerplate[category] = phrase_list

            total = sum(len(v) for v in boilerplate.values())
            print(f"[OK] Loaded {total} n-gram boilerplate phrases from {ngram_path}")

            return boilerplate

        except Exception as e:
            print(f"[WARN] Failed to load n-gram boilerplate: {e}")
            return {}

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile all regex patterns from config"""
        compiled = {}

        for category, config_data in self.config['boilerplate_patterns'].items():
            if not config_data.get('enabled', True):
                continue

            compiled[category] = []
            for pattern_str in config_data.get('patterns', []):
                try:
                    pattern = re.compile(
                        pattern_str,
                        re.MULTILINE | re.DOTALL | re.IGNORECASE
                    )
                    compiled[category].append(pattern)
                except re.error as e:
                    print(f"Warning: Invalid regex pattern in {category}: {e}")

        return compiled

    def remove_ngram_boilerplate(self, text: str,
                                  categories: List[str] = None,
                                  min_frequency: int = 50,
                                  verbose: bool = False) -> Tuple[str, Dict]:
        """
        Remove n-gram boilerplate from text

        Args:
            text: Input text
            categories: List of categories to remove (None = ALL categories)
            min_frequency: Minimum frequency threshold (not used yet, for future)
            verbose: Print removal stats

        Returns:
            Tuple of (cleaned_text, stats)
        """
        if not self.ngram_boilerplate:
            return text, {"ngrams_removed": 0}

        # Default: AGGRESSIVE - remove ALL categories including ceremonial
        if categories is None:
            categories = ['formatting', 'administrative', 'procedural', 'metadata', 'entity_names', 'ceremonial']

        cleaned = text
        removals = {}
        total_removed = 0

        for category in categories:
            if category not in self.ngram_boilerplate:
                continue

            phrases = self.ngram_boilerplate[category]
            category_removed = 0

            for phrase in phrases:
                if phrase in cleaned:
                    count = cleaned.count(phrase)
                    cleaned = cleaned.replace(phrase, ' ')
                    category_removed += count
                    total_removed += count

            if category_removed > 0:
                removals[category] = category_removed
                if verbose:
                    print(f"  Removed {category_removed} n-gram instances from category: {category}")

        return cleaned, {"ngrams_removed": total_removed, "by_category": removals}

    def clean_text(self, text: str,
                   use_ngrams: bool = True,
                   use_patterns: bool = True,
                   verbose: bool = False) -> Tuple[str, Dict]:
        """
        Clean boilerplate from text using n-grams and/or patterns

        Args:
            text: Raw UN document text
            use_ngrams: Apply n-gram based removal
            use_patterns: Apply regex pattern removal
            verbose: Print which patterns matched

        Returns:
            Tuple of (cleaned_text, statistics)
        """
        if not isinstance(text, str):
            return "", {"error": "Input text must be string"}

        original_length = len(text)
        cleaned = text
        stats = {
            "original_length": original_length,
            "ngram_stats": {},
            "pattern_stats": {}
        }

        # Step 1: Remove n-gram boilerplate (high-frequency exact matches)
        if use_ngrams and self.ngram_boilerplate:
            cleaned, ngram_stats = self.remove_ngram_boilerplate(cleaned, verbose=verbose)
            stats["ngram_stats"] = ngram_stats

        # Step 2: Apply regex pattern removal
        if use_patterns:
            for category, patterns in self.patterns.items():
                for pattern in patterns:
                    matches_before = len(pattern.findall(cleaned))
                    if matches_before > 0:
                        cleaned = pattern.sub('', cleaned)
                        stats["pattern_stats"][category] = matches_before
                        if verbose:
                            print(f"  Removed {matches_before} instances of {category} (regex)")

        # Step 3: Clean up extra whitespace
        if self.config['text_cleaning'].get('remove_extra_whitespace', True):
            # Remove multiple spaces
            cleaned = re.sub(r' +', ' ', cleaned)
            # Remove multiple newlines (keep max 2)
            cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
            # Strip leading/trailing whitespace per line
            cleaned = '\n'.join(line.strip() for line in cleaned.split('\n'))

        # Step 4: Filter out short paragraphs if configured
        min_length = self.config['output_options'].get('min_paragraph_length', 50)
        paragraphs = cleaned.split('\n\n')
        paragraphs = [p for p in paragraphs if len(p.strip()) >= min_length]
        cleaned = '\n\n'.join(paragraphs)

        stats["cleaned_length"] = len(cleaned)
        stats["reduction_percent"] = round(
            (1 - len(cleaned) / max(original_length, 1)) * 100, 2
        )

        return cleaned.strip(), stats

    def clean_csv(self,
                  input_csv: str,
                  output_csv: str,
                  text_column: str = 'Text',
                  sample_size: int = None,
                  verbose: bool = False,
                  bloc_json_output: str = None):
        """
        Clean text in CSV file with n-gram + pattern removal

        Args:
            input_csv: Path to input CSV
            output_csv: Path to output CSV
            text_column: Name of text column to clean
            sample_size: Process only first N rows (None = all)
            verbose: Print progress
            bloc_json_output: Path to save BLOC_ columns as JSON (optional)
        """
        try:
            print(f"Reading CSV: {input_csv}")

            # Read CSV
            if sample_size:
                df = pd.read_csv(input_csv, nrows=sample_size)
            else:
                df = pd.read_csv(input_csv)

            print(f"Loaded {len(df)} rows")

            # Extract BLOC_ columns to JSON if output path provided
            bloc_columns = [col for col in df.columns if col.startswith('BLOC_')]
            if bloc_columns and bloc_json_output:
                print(f"Extracting {len(bloc_columns)} BLOC_ columns to JSON...")

                bloc_data = []
                for idx, row in df.iterrows():
                    country = row.get('Country', f'Row_{idx}')
                    bloc_memberships = {}
                    for col in bloc_columns:
                        if pd.notna(row[col]) and row[col] != 0.0:
                            org_name = col.replace('BLOC_', '')
                            bloc_memberships[org_name] = row[col]

                    if bloc_memberships:
                        bloc_data.append({
                            'country': country,
                            'organizations': bloc_memberships
                        })

                with open(bloc_json_output, 'w', encoding='utf-8') as f:
                    json.dump(bloc_data, f, indent=2, ensure_ascii=False)
                print(f"Saved BLOC data to: {bloc_json_output}")

                df = df.drop(columns=bloc_columns)
                print(f"Removed {len(bloc_columns)} BLOC_ columns from output CSV")

            print(f"Cleaning '{text_column}' column with N-GRAM + PATTERN removal...")

            # Track statistics
            total_stats = {
                "total_rows": len(df),
                "total_original_chars": 0,
                "total_cleaned_chars": 0,
                "avg_reduction_percent": 0,
                "total_ngrams_removed": 0,
                "total_patterns_removed": 0
            }

            # Clean text column
            cleaned_texts = []
            reductions = []

            for idx, text in enumerate(df[text_column]):
                if pd.isna(text):
                    cleaned_texts.append("")
                    continue

                cleaned, stats = self.clean_text(str(text), verbose=False)
                cleaned_texts.append(cleaned)

                total_stats["total_original_chars"] += stats["original_length"]
                total_stats["total_cleaned_chars"] += stats["cleaned_length"]
                total_stats["total_ngrams_removed"] += stats.get("ngram_stats", {}).get("ngrams_removed", 0)
                total_stats["total_patterns_removed"] += sum(stats.get("pattern_stats", {}).values())
                reductions.append(stats["reduction_percent"])

                if verbose and (idx + 1) % 100 == 0:
                    print(f"  Processed {idx + 1}/{len(df)} rows")

            # Add cleaned text to dataframe
            df[f'{text_column}_cleaned_ngram'] = cleaned_texts

            # Save output
            print(f"Writing output to: {output_csv}")
            df.to_csv(output_csv, index=False)

            total_stats["avg_reduction_percent"] = round(
                sum(reductions) / len(reductions) if reductions else 0, 2
            )

            return df, total_stats

        except FileNotFoundError:
            print(f"Error: CSV file not found at {input_csv}")
            sys.exit(1)
        except KeyError:
            print(f"Error: Column '{text_column}' not found in CSV")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing CSV: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    # Configuration
    config_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\n-grams and cleaning data\config_boilerplate.json"
    ngram_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\ngram_boilerplate_aggressive.json"

    print("="*80)
    print("AGGRESSIVE UN DOCUMENT CLEANER (N-GRAMS + PATTERNS)")
    print("="*80 + "\n")

    cleaner = EnhancedUNTextCleaner(config_path, ngram_path)

    # Test with ORIGINAL data (not the already-cleaned version!)
    csv_input = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe.csv"
    csv_output = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe_NGRAM_AGGRESSIVE.csv"
    bloc_json_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\international_organizations_ngram.json"

    if Path(csv_input).exists():
        print(f"\nProcessing ORIGINAL CSV (first 100 rows for testing)...")

        df, total_stats = cleaner.clean_csv(
            csv_input,
            csv_output,
            text_column='Text',
            sample_size=100,
            verbose=True,
            bloc_json_output=bloc_json_path
        )

        print(f"\n{'='*80}")
        print("CLEANING RESULTS (N-GRAM + PATTERN)")
        print(f"{'='*80}")
        print(f"  Total rows processed: {total_stats['total_rows']}")
        print(f"  Total original chars: {total_stats['total_original_chars']:,}")
        print(f"  Total cleaned chars: {total_stats['total_cleaned_chars']:,}")
        print(f"  Average reduction: {total_stats['avg_reduction_percent']}%")
        print(f"  N-grams removed: {total_stats['total_ngrams_removed']:,}")
        print(f"  Pattern matches removed: {total_stats['total_patterns_removed']:,}")
        print(f"\nOutput saved to: {csv_output}")
        print(f"{'='*80}\n")
    else:
        print(f"CSV file not found at {csv_input}")
