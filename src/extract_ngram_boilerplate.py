"""
Extract Boilerplate Phrases from N-gram Frequency Files
Uses your actual corpus data to identify high-frequency boilerplate
"""

import pandas as pd
import json
import re
from pathlib import Path
from typing import List, Dict, Set


class NgramBoilerplateExtractor:
    """Extract boilerplate phrases from n-gram frequency CSVs"""

    def __init__(self, ngram_dir: str):
        """
        Initialize with directory containing frequency CSV files

        Args:
            ngram_dir: Path to directory with frequency_*grams.csv files
        """
        self.ngram_dir = Path(ngram_dir)
        self.boilerplate_categories = {
            'formatting': [],
            'administrative': [],
            'procedural': [],
            'ceremonial': [],
            'entity_names': [],
            'metadata': []
        }

    def is_formatting_artifact(self, phrase: str) -> bool:
        """Check if phrase is just formatting (dots, dashes, numbers, etc.)"""
        # Remove spaces and check what's left
        clean = phrase.replace(' ', '')

        # Patterns that are pure formatting
        formatting_patterns = [
            r'^[.\-–—•]+$',  # dots, dashes, bullets
            r'^[0-9\s]+$',   # just numbers and spaces
            r'^[a-z\s]+$' if len(clean) <= 3 else None,  # single letters spaced
            r'^[–\-\s]+$',   # just dashes
            r'^[•\s]+$',     # just bullets
            r'^[·\s]+$',     # middle dots
        ]

        for pattern in formatting_patterns:
            if pattern and re.match(pattern, phrase):
                return True

        return False

    def is_administrative(self, phrase: str) -> bool:
        """Check if phrase is administrative boilerplate"""
        admin_keywords = [
            'status:', 'priority:', 'target date:', 'quarter',
            'thousand', 'dollars', 'budget', 'expenditure',
            'appropriation', 'adjustment', 'recosting',
            'financial resources', 'post resources',
            'board\'s recommendation', 'agreed with',
            'enquiry', 'informed that'
        ]
        phrase_lower = phrase.lower()
        return any(keyword in phrase_lower for keyword in admin_keywords)

    def is_procedural(self, phrase: str) -> bool:
        """Check if phrase is procedural/reference boilerplate"""
        procedural_keywords = [
            'official records', 'report of the secretary',
            'general assembly', 'economic and social council',
            'resolution', 'session', 'committee',
            'upon enquiry', 'by the general assembly in'
        ]
        phrase_lower = phrase.lower()
        return any(keyword in phrase_lower for keyword in procedural_keywords)

    def is_ceremonial(self, phrase: str) -> bool:
        """Check if phrase is ceremonial boilerplate"""
        ceremonial_keywords = [
            'his excellency', 'her excellency',
            'on behalf of', 'i would like to',
            'allow me to', 'congratulate',
            'thank', 'honour', 'privilege'
        ]
        phrase_lower = phrase.lower()
        return any(keyword in phrase_lower for keyword in ceremonial_keywords)

    def is_entity_name(self, phrase: str) -> bool:
        """Check if phrase is a standard entity name"""
        entity_keywords = [
            'united kingdom of great britain',
            'latin america and the caribbean',
            'least developed countries',
            'small island developing',
            'landlocked developing countries',
            'office of the united nations',
            'department of',
            'high commissioner for'
        ]
        phrase_lower = phrase.lower()
        return any(keyword in phrase_lower for keyword in entity_keywords)

    def is_metadata(self, phrase: str) -> bool:
        """Check if phrase is document metadata"""
        metadata_patterns = [
            r'volume [ivx]+',
            r'page \d+',
            r'paragraph \d+',
            r'section [a-z0-9]+',
            r'annex [ivx]+',
            r'appendix [a-z]+'
        ]
        phrase_lower = phrase.lower()
        return any(re.search(pattern, phrase_lower) for pattern in metadata_patterns)

    def categorize_phrase(self, phrase: str) -> str:
        """Categorize a phrase into boilerplate type"""
        if self.is_formatting_artifact(phrase):
            return 'formatting'
        elif self.is_administrative(phrase):
            return 'administrative'
        elif self.is_procedural(phrase):
            return 'procedural'
        elif self.is_ceremonial(phrase):
            return 'ceremonial'
        elif self.is_entity_name(phrase):
            return 'entity_names'
        elif self.is_metadata(phrase):
            return 'metadata'
        else:
            return None  # Not identified as boilerplate

    def extract_from_file(self, filepath: Path, min_frequency: int = 50) -> Dict[str, List[str]]:
        """
        Extract boilerplate phrases from a single n-gram file

        Args:
            filepath: Path to frequency CSV file
            min_frequency: Minimum frequency to consider (default 50)

        Returns:
            Dictionary of categorized phrases
        """
        print(f"Processing {filepath.name}...")

        try:
            df = pd.read_csv(filepath)

            # Filter by frequency
            df_filtered = df[df['Frequency'] >= min_frequency].copy()

            print(f"  Found {len(df_filtered)} phrases with freq >= {min_frequency}")

            categorized = {cat: [] for cat in self.boilerplate_categories.keys()}
            skipped = 0

            for _, row in df_filtered.iterrows():
                phrase = str(row['Phrase']).strip()
                category = self.categorize_phrase(phrase)

                if category:
                    categorized[category].append({
                        'phrase': phrase,
                        'frequency': int(row['Frequency']),
                        'ngram_size': filepath.stem.split('_')[1].replace('grams', '')
                    })
                else:
                    skipped += 1

            print(f"  Categorized: {sum(len(v) for v in categorized.values())}, Skipped: {skipped}")

            return categorized

        except Exception as e:
            print(f"  Error processing {filepath.name}: {e}")
            return {cat: [] for cat in self.boilerplate_categories.keys()}

    def extract_all(self, min_frequency: int = 50, output_json: str = None) -> Dict:
        """
        Extract boilerplate from all n-gram files

        Args:
            min_frequency: Minimum frequency threshold
            output_json: Optional path to save results as JSON

        Returns:
            Dictionary with all categorized boilerplate phrases
        """
        print(f"\n{'='*60}")
        print("N-GRAM BOILERPLATE EXTRACTION")
        print(f"{'='*60}")
        print(f"Directory: {self.ngram_dir}")
        print(f"Min frequency: {min_frequency}\n")

        # Find all n-gram frequency files
        ngram_files = sorted(self.ngram_dir.glob('frequency_*grams.csv'))

        if not ngram_files:
            print(f"No n-gram files found in {self.ngram_dir}")
            return self.boilerplate_categories

        print(f"Found {len(ngram_files)} n-gram files\n")

        # Process each file
        for ngram_file in ngram_files:
            categorized = self.extract_from_file(ngram_file, min_frequency)

            # Merge into main categories
            for category, phrases in categorized.items():
                self.boilerplate_categories[category].extend(phrases)

        # Sort each category by frequency (highest first)
        for category in self.boilerplate_categories:
            self.boilerplate_categories[category].sort(
                key=lambda x: x['frequency'],
                reverse=True
            )

        # Print summary
        print(f"\n{'='*60}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*60}")
        for category, phrases in self.boilerplate_categories.items():
            print(f"{category.upper():20s}: {len(phrases):5d} phrases")
        print(f"{'='*60}")
        print(f"TOTAL:               {sum(len(v) for v in self.boilerplate_categories.values()):5d} phrases\n")

        # Save to JSON if requested
        if output_json:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(self.boilerplate_categories, f, indent=2, ensure_ascii=False)
            print(f"Saved to: {output_json}\n")

        return self.boilerplate_categories

    def create_removal_list(self,
                           categories: List[str] = None,
                           min_frequency: int = 100,
                           max_phrases: int = None) -> List[str]:
        """
        Create a flat list of phrases for removal

        Args:
            categories: List of categories to include (None = all)
            min_frequency: Only include phrases with freq >= this
            max_phrases: Maximum number of phrases to return

        Returns:
            List of phrases sorted by length (longest first)
        """
        if categories is None:
            categories = list(self.boilerplate_categories.keys())

        phrases = []
        for category in categories:
            if category in self.boilerplate_categories:
                for item in self.boilerplate_categories[category]:
                    if item['frequency'] >= min_frequency:
                        phrases.append(item['phrase'])

        # Sort by length (longest first) to avoid partial replacements
        phrases = sorted(set(phrases), key=len, reverse=True)

        if max_phrases:
            phrases = phrases[:max_phrases]

        return phrases


if __name__ == "__main__":
    # Configuration
    ngram_dir = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\n-grams and cleaning data\frequency csv"
    output_json = r"c:\Users\xocas\OneDrive\Desktop\un-cleaning\ngram_boilerplate_aggressive.json"

    # Extract boilerplate - AGGRESSIVE MODE: Lower threshold to 20
    extractor = NgramBoilerplateExtractor(ngram_dir)
    boilerplate = extractor.extract_all(
        min_frequency=20,  # AGGRESSIVE: Phrases appearing 20+ times (was 50)
        output_json=output_json
    )

    # Show top phrases per category
    print("\nTOP 10 PHRASES PER CATEGORY:")
    print("="*60)
    for category, phrases in boilerplate.items():
        if phrases:
            print(f"\n{category.upper()}:")
            for i, item in enumerate(phrases[:10], 1):
                print(f"  {i}. [{item['frequency']:4d}×] {item['phrase'][:70]}")

    # Create removal lists with different aggressiveness levels
    print("\n" + "="*60)
    print("REMOVAL LIST SIZES (by frequency threshold):")
    print("="*60)

    for min_freq in [10, 20, 50, 100]:
        removal_list = extractor.create_removal_list(
            categories=['formatting', 'administrative', 'procedural', 'metadata', 'entity_names', 'ceremonial'],
            min_frequency=min_freq
        )
        print(f"  Freq >= {min_freq:3d}: {len(removal_list):4d} phrases")

    print("\n✓ Extraction complete!")
