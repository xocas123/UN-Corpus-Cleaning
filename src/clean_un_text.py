"""
UN Documents Boilerplate Text Cleaner
Removes ceremonial, procedural, and repetitive boilerplate from UN resolutions and speeches
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


class UNTextCleaner:
    """Clean boilerplate text from UN documents"""
    
    def __init__(self, config_path: str):
        """
        Initialize cleaner with config file
        
        Args:
            config_path: Path to config_boilerplate.json
        """
        self.config = self._load_config(config_path)
        self.patterns = self._compile_patterns()
    
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
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile all regex patterns from config"""
        compiled = {}
        
        for category, config_data in self.config['boilerplate_patterns'].items():
            if not config_data.get('enabled', True):
                continue
            
            compiled[category] = []
            for pattern_str in config_data.get('patterns', []):
                try:
                    # Compile with MULTILINE and DOTALL flags
                    pattern = re.compile(
                        pattern_str,
                        re.MULTILINE | re.DOTALL | re.IGNORECASE
                    )
                    compiled[category].append(pattern)
                except re.error as e:
                    print(f"Warning: Invalid regex pattern in {category}: {e}")
        
        return compiled
    
    def clean_text(self, text: str, verbose: bool = False) -> Tuple[str, Dict]:
        """
        Clean boilerplate from text
        
        Args:
            text: Raw UN document text
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
            "patterns_removed": {}
        }
        
        # Apply each boilerplate pattern
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches_before = len(pattern.findall(cleaned))
                if matches_before > 0:
                    cleaned = pattern.sub('', cleaned)
                    stats["patterns_removed"][category] = matches_before
                    if verbose:
                        print(f"  Removed {matches_before} instances of {category}")
        
        # Clean up extra whitespace
        if self.config['text_cleaning'].get('remove_extra_whitespace', True):
            # Remove multiple spaces
            cleaned = re.sub(r' +', ' ', cleaned)
            # Remove multiple newlines (keep max 2)
            cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
            # Strip leading/trailing whitespace per line
            cleaned = '\n'.join(line.strip() for line in cleaned.split('\n'))
        
        # Filter out short paragraphs if configured
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
        Clean text in CSV file

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

                # Create a list of records with Country and BLOC memberships
                bloc_data = []
                for idx, row in df.iterrows():
                    country = row.get('Country', f'Row_{idx}')
                    bloc_memberships = {}
                    for col in bloc_columns:
                        # Store only non-zero values
                        if pd.notna(row[col]) and row[col] != 0.0:
                            # Remove 'BLOC_' prefix for cleaner JSON
                            org_name = col.replace('BLOC_', '')
                            bloc_memberships[org_name] = row[col]

                    if bloc_memberships:  # Only add if country has memberships
                        bloc_data.append({
                            'country': country,
                            'organizations': bloc_memberships
                        })

                # Save to JSON file
                with open(bloc_json_output, 'w', encoding='utf-8') as f:
                    json.dump(bloc_data, f, indent=2, ensure_ascii=False)
                print(f"Saved BLOC data to: {bloc_json_output}")

                # Remove BLOC_ columns from dataframe
                df = df.drop(columns=bloc_columns)
                print(f"Removed {len(bloc_columns)} BLOC_ columns from output CSV")

            print(f"Cleaning '{text_column}' column...")

            # Track statistics
            total_stats = {
                "total_rows": len(df),
                "total_original_chars": 0,
                "total_cleaned_chars": 0,
                "avg_reduction_percent": 0
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
                reductions.append(stats["reduction_percent"])

                if verbose and (idx + 1) % 100 == 0:
                    print(f"  Processed {idx + 1}/{len(df)} rows")

            # Add cleaned text to dataframe
            df[f'{text_column}_cleaned'] = cleaned_texts

            # Save output
            print(f"Writing output to: {output_csv}")
            df.to_csv(output_csv, index=False)

            total_stats["avg_reduction_percent"] = round(
                sum(reductions) / len(reductions), 2
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


def print_comparison(original: str, cleaned: str, max_chars: int = 300):
    """Pretty print before/after comparison"""
    print("\n" + "=" * 80)
    print("BEFORE CLEANING:")
    print("-" * 80)
    print(original[:max_chars] + ("..." if len(original) > max_chars else ""))
    print("\n" + "=" * 80)
    print("AFTER CLEANING:")
    print("-" * 80)
    print(cleaned[:max_chars] + ("..." if len(cleaned) > max_chars else ""))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Configuration
    config_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\n-grams and cleaning data\config_boilerplate.json"
    
    # Example 1: Clean a single text
    print("UN Document Boilerplate Cleaner\n")
    print("Initializing cleaner...")
    
    cleaner = UNTextCleaner(config_path)
    
    # Test with a sample text
    sample_text = """
    The President: On behalf of the General Assembly, I have the honour to welcome 
    to the United Nations His Excellency Mr. John Smith, President of the 
    Republic of Example, and to invite him to address the Assembly.
    
    President Smith (spoke in English): Allow me at the outset to congratulate 
    His Excellency Mr. Peter Thomson, Permanent Representative of Fiji, who has 
    been elected President of the General Assembly at its seventy-first session.
    
    I would also like to congratulate and thank His Excellency Mr. Mogens Lykketoft, 
    outgoing President of the General Assembly, for his dedication and his many 
    initiatives to strengthen the role of the Assembly.
    
    The real substance of our statement concerns the pressing issue of climate change.
    We must take immediate action to reduce carbon emissions and protect our planet.
    The future of our children depends on the decisions we make today.
    
    In conclusion, we reaffirm our commitment to the ideals of the United Nations
    and our belief that international cooperation is the path to peace.
    """
    
    print("\nExample 1: Single Text Cleaning")
    cleaned, stats = cleaner.clean_text(sample_text, verbose=True)
    
    print(f"\nStatistics:")
    print(f"  Original length: {stats['original_length']} chars")
    print(f"  Cleaned length: {stats['cleaned_length']} chars")
    print(f"  Reduction: {stats['reduction_percent']}%")
    
    print_comparison(sample_text, cleaned)
    
    # Example 2: Process CSV (small sample)
    print("\nExample 2: CSV Processing (first 10 rows)")
    print("Note: Specify your CSV path and run with sample_size parameter")
    
    csv_input = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe.csv"
    csv_output = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\gate_mwe_cleaned.csv"
    
    if Path(csv_input).exists():
        print(f"\nProcessing CSV with sample of 10 rows...")

        # Define path for BLOC organizations JSON output
        bloc_json_path = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\Inputs\international_organizations.json"

        df, total_stats = cleaner.clean_csv(
            csv_input,
            csv_output,
            text_column='Text',
            sample_size=10,
            verbose=True,
            bloc_json_output=bloc_json_path
        )

        print(f"\nCSV Cleaning Results:")
        print(f"  Total rows processed: {total_stats['total_rows']}")
        print(f"  Total original chars: {total_stats['total_original_chars']:,}")
        print(f"  Total cleaned chars: {total_stats['total_cleaned_chars']:,}")
        print(f"  Average reduction: {total_stats['avg_reduction_percent']}%")
        print(f"\nOutput saved to: {csv_output}")
        print(f"BLOC organizations saved to: {bloc_json_path}")
    else:
        print(f"CSV file not found at {csv_input}")
        print("Update the csv_input path to process your data")
