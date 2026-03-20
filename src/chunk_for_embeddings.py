"""
Paragraph Chunker for Embedding Generation

Chunks cleaned UN speeches by paragraph, enriches with country group
memberships, and outputs CSV + JSONL for downstream embedding pipelines.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE / "lawsec_v1.18i_cluster_cleaned.csv"
OUTPUT_CSV = BASE / "lawsec_v1.18i_chunked.csv"
OUTPUT_JSONL = BASE / "lawsec_v1.18i_chunked.jsonl"
COUNTRY_GROUPS = Path(
    r"c:\Users\joaqu\OneDrive\Desktop\Remote Systems Project"
    r"\arms-control-nlp\data\raw\country_groups.json"
)

TEXT_COL = "Text_cleaned_ngram"
MAX_CHUNK_CHARS = 1500
MIN_CHUNK_CHARS = 50

METADATA_COLS = [
    "Date", "Year", "Title", "Country", "Forum",
    "Submission_Type", "Actor_Type", "Attribution",
    "Session", "Cluster",
]

GROUP_NAMES = [
    "p5", "de_facto_nuclear", "nato", "nam", "nac",
    "tpnw_parties", "att_parties", "major_exporters",
    "major_importers", "gulf_states", "eu", "brics",
]

SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')


# ---------------------------------------------------------------------------
# ParagraphChunker
# ---------------------------------------------------------------------------
class ParagraphChunker:

    def __init__(self, input_csv: Path, country_groups_path: Path):
        # Load country groups
        self.name_to_iso3: Dict[str, str] = {}
        self.name_to_groups: Dict[str, Dict[str, bool]] = {}
        self.unmapped_countries: Counter = Counter()
        self._load_country_groups(country_groups_path)

        # Load and filter CSV
        print(f"Reading {input_csv} ...")
        self.df = pd.read_csv(input_csv, low_memory=False)
        before = len(self.df)
        self.df = self.df[
            (self.df["Flag_Cleaned"] == "cleaned")
            & self.df[TEXT_COL].notna()
            & (self.df[TEXT_COL].str.strip().str.len() > 0)
        ].copy()
        print(f"  {before} total rows -> {len(self.df)} valid for chunking")

    # ---- country groups ---------------------------------------------------

    def _load_country_groups(self, path: Path):
        if not path.exists():
            print(f"[WARN] Country groups not found at {path}, skipping enrichment")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Reverse the iso3-to-name mapping
        iso3_to_name = data.get("country_iso3_to_name", {})
        self.name_to_iso3 = {
            name.strip().lower(): code for code, name in iso3_to_name.items()
        }

        # Collect group membership lists (exclude the mapping dict itself)
        group_lists: Dict[str, set] = {}
        for g in GROUP_NAMES:
            members = data.get(g, [])
            group_lists[g] = set(members)

        # Pre-compute group booleans per country name
        for name_lower, iso3 in self.name_to_iso3.items():
            self.name_to_groups[name_lower] = {
                g: iso3 in members for g, members in group_lists.items()
            }

        print(f"  Loaded {len(self.name_to_iso3)} country mappings, "
              f"{len(GROUP_NAMES)} groups")

    def resolve_country(self, country_name) -> Tuple[Optional[str], Dict[str, bool]]:
        empty_groups = {g: False for g in GROUP_NAMES}

        if pd.isna(country_name) or not str(country_name).strip():
            return None, empty_groups

        key = str(country_name).strip().lower()
        iso3 = self.name_to_iso3.get(key)

        if iso3 is None:
            self.unmapped_countries[str(country_name).strip()] += 1
            return None, empty_groups

        groups = self.name_to_groups.get(key, empty_groups)
        return iso3, groups

    # ---- chunking ---------------------------------------------------------

    def chunk_text(self, text: str) -> List[Tuple[str, str]]:
        text = text.strip()
        if not text:
            return []

        # Short text: keep as single chunk
        if len(text) <= MAX_CHUNK_CHARS:
            return [(text, "no_split")]

        # Level 1: double newline (real paragraph breaks)
        if "\n\n" in text:
            paras = [c.strip() for c in text.split("\n\n")
                     if len(c.strip()) >= MIN_CHUNK_CHARS]
            if len(paras) > 1:
                # Sub-chunk any oversized paragraphs via sentence splitting
                result = []
                for p in paras:
                    if len(p) > MAX_CHUNK_CHARS:
                        sub = self._split_sentences_greedy(p)
                        result.extend((s, "paragraph") for s in sub)
                    else:
                        result.append((p, "paragraph"))
                return result if result else [(text, "no_split")]

        # Level 2: sentence boundaries with greedy grouping
        # (skip single \n — it's usually PDF line wrapping, not paragraphs)
        sentence_chunks = self._split_sentences_greedy(text)
        if len(sentence_chunks) > 1:
            return [(c, "sentence") for c in sentence_chunks]

        # Fallback: can't split meaningfully
        return [(text, "no_split")]

    def _split_sentences_greedy(self, text: str) -> List[str]:
        sentences = SENTENCE_SPLIT_RE.split(text)
        if len(sentences) <= 1:
            return [text] if len(text) >= MIN_CHUNK_CHARS else []

        chunks: List[str] = []
        buffer = ""

        for sentence in sentences:
            if buffer and len(buffer) + len(sentence) + 1 > MAX_CHUNK_CHARS:
                chunks.append(buffer.strip())
                buffer = sentence
            else:
                buffer = f"{buffer} {sentence}".strip() if buffer else sentence

        if buffer.strip():
            chunks.append(buffer.strip())

        return [c for c in chunks if len(c) >= MIN_CHUNK_CHARS]

    # ---- main processing --------------------------------------------------

    def process(self) -> Tuple[pd.DataFrame, Counter]:
        rows_out: List[dict] = []
        stats: Counter = Counter()
        skipped = 0

        total = len(self.df)
        for i, (_, row) in enumerate(self.df.iterrows()):
            if (i + 1) % 10000 == 0:
                print(f"  Chunked {i + 1}/{total} docs ...")

            text = str(row[TEXT_COL])
            chunks = self.chunk_text(text)

            if not chunks:
                skipped += 1
                continue

            iso3, groups = self.resolve_country(row.get("Country"))

            for ci, (chunk_text, method) in enumerate(chunks):
                stats[method] += 1
                out = {
                    "chunk_id": f"{row['doc_id']}_chunk{ci:03d}",
                    "doc_id": row["doc_id"],
                    "chunk_index": ci,
                    "chunk_total": len(chunks),
                    "chunk_text": chunk_text,
                    "split_method": method,
                    "country_iso3": iso3,
                }
                for col in METADATA_COLS:
                    out[col] = row.get(col)
                for g in GROUP_NAMES:
                    out[g] = groups[g]
                rows_out.append(out)

        if skipped:
            print(f"  Skipped {skipped} docs (empty after chunking)")

        df_out = pd.DataFrame(rows_out)
        return df_out, stats

    # ---- output -----------------------------------------------------------

    def save_csv(self, df: pd.DataFrame, path: Path):
        df.to_csv(path, index=False, encoding="utf-8-sig")
        size_mb = path.stat().st_size / 1024 / 1024
        print(f"  CSV: {path.name} ({len(df)} rows, {size_mb:.1f} MB)")

    def save_jsonl(self, df: pd.DataFrame, path: Path):
        with open(path, "w", encoding="utf-8") as f:
            for _, row in df.iterrows():
                f.write(json.dumps(row.to_dict(), ensure_ascii=False, default=str) + "\n")
        size_mb = path.stat().st_size / 1024 / 1024
        print(f"  JSONL: {path.name} ({len(df)} rows, {size_mb:.1f} MB)")

    def print_summary(self, df: pd.DataFrame, stats: Counter):
        print("\n=== Chunking Summary ===")
        print(f"Input docs:   {len(self.df)}")
        print(f"Output chunks: {len(df)}")
        print(f"Avg chunks/doc: {len(df) / max(len(self.df), 1):.2f}")

        print("\nSplit method distribution:")
        for method, count in stats.most_common():
            pct = count / len(df) * 100
            print(f"  {method:12s}: {count:>8,} ({pct:.1f}%)")

        # Country coverage
        has_iso3 = df["country_iso3"].notna().sum()
        print(f"\nCountry coverage: {has_iso3:,}/{len(df):,} chunks "
              f"({has_iso3 / len(df) * 100:.1f}%) have resolved ISO-3")

        if self.unmapped_countries:
            top = self.unmapped_countries.most_common(10)
            print(f"Unmapped countries ({len(self.unmapped_countries)} unique):")
            for name, cnt in top:
                print(f"  {name}: {cnt}")

        # Group coverage
        print("\nGroup membership (chunks with True):")
        for g in GROUP_NAMES:
            if g in df.columns:
                n = df[g].sum()
                print(f"  {g:20s}: {n:>8,} ({n / len(df) * 100:.1f}%)")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    groups_path = Path(sys.argv[1]) if len(sys.argv) > 1 else COUNTRY_GROUPS

    chunker = ParagraphChunker(INPUT_CSV, groups_path)
    df_out, stats = chunker.process()
    chunker.save_csv(df_out, OUTPUT_CSV)
    chunker.save_jsonl(df_out, OUTPUT_JSONL)
    chunker.print_summary(df_out, stats)


if __name__ == "__main__":
    main()
