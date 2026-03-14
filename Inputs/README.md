# Inputs Directory

Place your input CSV files here.

## Expected Format

Your CSV should contain at least:
- A `Text` column with UN speech/document text
- Optional: `Country` column for identifying speakers
- Optional: `BLOC_*` columns for international organization memberships

## Example

```csv
Country,Text,BLOC_AfrGroup,BLOC_G77,...
Chad,"The President: On behalf of...",1.0,1.0,...
South Africa,"Mabhongo (South Africa): My delegation...",1.0,1.0,...
```

## Data Sources

- **UN General Debate Corpus**: https://github.com/sjankin/UnitedNations
- **UN Official Documents**: https://documents.un.org/
- **UN Speeches**: https://speechbank.un.org/

## Note

Large CSV files are gitignored by default to keep the repository size manageable.
