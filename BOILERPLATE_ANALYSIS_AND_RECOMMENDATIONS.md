# UN Boilerplate Removal: Analysis & Recommendations

## Current Performance
**Overall Effectiveness: POOR (12.9% average reduction, 0.5% median)**

- 67.8% of speeches: <5% reduction (essentially unchanged)
- 11.7% of speeches: 5-20% reduction (minimal cleaning)
- 9.4% of speeches: 20-50% reduction (moderate cleaning)
- 11.0% of speeches: >50% reduction (heavy cleaning)

## Key Findings from Your N-Grams

### High-Frequency Boilerplate Patterns Found:

**Administrative/Procedural (Top offenders):**
- `. . . . . . . . . .` (63,002 occurrences) - formatting artifact
- `status: in progress priority: medium target date: fourth quarter of` (332×)
- `agreed with the board's recommendation that it` (559×)
- `(thousands of united states dollars)` (1,163×)
- `upon enquiry, the advisory committee was informed` (240×)

**Ceremonial/Standard Phrases:**
- `report of the secretary-general on the work of the organization` (213×)
- `official records of the general assembly` (567×)
- `advisory committee on administrative and budgetary questions` (246×)
- `by the general assembly in its resolution` (415×)

**Standard Entity Names:**
- `united kingdom of great britain and northern` (328×)
- `office of the united nations high commissioner` (286×)
- `economic and social development in latin america and the caribbean` (152×)
- `least developed countries, landlocked developing countries and small island developing` (138×)

## Recommendations

### 1. **USE YOUR N-GRAMS FOR BOILERPLATE REMOVAL ✓ RECOMMENDED**

Your frequency CSVs are perfect for this! Here's the strategy:

**Step 1: Extract high-frequency n-grams**
- Filter n-grams with frequency > threshold (e.g., 100+ occurrences)
- Exclude substantive phrases (manual review or keyword filtering)
- Create removal lists by n-gram size (4-10 grams)

**Step 2: Implement frequency-based removal**
- Remove exact matches first (faster)
- Use simple string replacement, not regex
- Process longer n-grams first (10→4) to avoid partial matches

**Benefits:**
- Data-driven (from your actual corpus)
- Fast (string matching vs regex)
- Comprehensive (captures variations you have)
- Already categorized by frequency

### 2. **Existing Libraries & Tools**

**Best Options:**

1. **BoilerNet** (Deep Learning Approach)
   - GitHub: https://github.com/mrjleo/boilernet
   - Uses neural sequence labeling
   - PRO: State-of-the-art accuracy
   - CON: Requires training data, computational overhead
   - **Verdict:** Worth trying if you have GPUs

2. **TextPrettifier** (General NLP Preprocessing)
   - Python library for text cleaning
   - PRO: Easy to use, well-maintained
   - CON: Not UN-specific
   - **Verdict:** Good for post-processing after boilerplate removal

3. **UNGDC Preprocessing (Baturo et al. 2017/2025)**
   - Standard approach: tokenization, stopwords, stemming
   - No specific boilerplate removal mentioned
   - **Verdict:** Not helpful for boilerplate

**None of the existing tools are specifically designed for UN boilerplate removal.**

### 3. **Hybrid Approach (BEST SOLUTION)**

Combine multiple methods for maximum effectiveness:

```python
# Step 1: N-gram based removal (fast, catches most)
- Load high-frequency n-grams (freq > 50)
- Remove exact matches

# Step 2: Pattern-based removal (regex for variations)
- Improved regex patterns (broader, more flexible)
- Multi-pass cleaning

# Step 3: TF-IDF based filtering
- Calculate TF-IDF across corpus
- Remove sentences with very low TF-IDF (likely boilerplate)

# Step 4: Manual review & iteration
- Sample check 100 speeches
- Identify missed patterns
- Add to removal list
```

## Implementation Plan

### Phase 1: Leverage Your N-Grams (Quick Win)

1. **Create boilerplate lists from n-grams:**
   ```python
   # Filter high-frequency administrative phrases
   - Load all n-gram files
   - Keep phrases with freq > 100
   - Categorize: formatting, procedural, ceremonial
   - Export to JSON for easy loading
   ```

2. **Implement n-gram remover:**
   ```python
   - Load boilerplate lists
   - Remove matches (exact string replacement)
   - Process 10-grams first, then 9, 8, etc.
   ```

**Expected improvement: 30-50% reduction** (vs current 12.9%)

### Phase 2: Enhanced Pattern Matching

1. **Fix existing regex patterns:**
   - Current patterns too specific
   - Add fuzzy matching for variations
   - Use word boundaries, not exact phrases

2. **Add new pattern categories:**
   - Speaker introductions
   - Country delegations
   - Document references
   - Session markers

**Expected improvement: 50-70% reduction**

### Phase 3: Machine Learning (Advanced)

1. **Train a binary classifier:**
   - Label sentences: boilerplate vs substantive
   - Use TF-IDF or BERT embeddings
   - Classify each sentence, remove boilerplate

2. **Or use BoilerNet:**
   - Adapt for UN documents
   - Fine-tune on sample data

**Expected improvement: 70-85% reduction**

## Immediate Next Steps

**I can create for you:**

1. ✅ **N-gram boilerplate extractor** - Parse your frequency CSVs, extract high-frequency phrases
2. ✅ **Enhanced cleaner** - Combine n-gram removal + improved regex
3. ✅ **Evaluation script** - Compare before/after, measure effectiveness
4. ✅ **Interactive review tool** - Manually review samples, add patterns

**Which would you like me to implement first?**

## Sample Code Preview

```python
# Example: Using n-grams for removal
def load_ngram_boilerplate(frequency_files, min_freq=100):
    """Extract high-frequency phrases from your n-gram CSVs"""
    boilerplate = []
    for file in frequency_files:
        df = pd.read_csv(file)
        # Filter by frequency and type
        filtered = df[df['Frequency'] >= min_freq]
        # Exclude formatting artifacts (dots, dashes)
        filtered = filtered[~filtered['Phrase'].str.match(r'^[.\-–•\s]+$')]
        boilerplate.extend(filtered['Phrase'].tolist())
    return sorted(boilerplate, key=len, reverse=True)  # Longest first

def remove_ngram_boilerplate(text, boilerplate_list):
    """Remove boilerplate phrases from text"""
    cleaned = text
    for phrase in boilerplate_list:
        cleaned = cleaned.replace(phrase, '')
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()
```

## Resources Found

**GitHub Repositories:**
- https://github.com/sjankin/UnitedNations (UNGDC corpus)
- https://github.com/jradius/un-general-debates (transformation scripts)
- https://github.com/mrjleo/boilernet (deep learning approach)

**Academic Papers:**
- Baturo et al. (2017) "Understanding State Preferences With Text As Data"
- Baturo et al. (2025) "Words to Unite Nations: The Complete UNGDC, 1946–present"

**None provide UN-specific boilerplate removal - you'd be pioneering this!**
