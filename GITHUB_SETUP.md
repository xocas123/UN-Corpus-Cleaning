# GitHub Setup Instructions

Follow these steps to push your repository to GitHub.

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `un-speech-cleaner` (or your preferred name)
3. Description: "Data-driven tool for removing boilerplate text from UN speeches using n-gram analysis"
4. Choose: **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Connect Your Local Repository to GitHub

In your terminal, run these commands:

```bash
# Navigate to your project
cd "c:\Users\xocas\OneDrive\Desktop\un-cleaning"

# Add the remote (replace USERNAME and REPO_NAME with yours)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Verify the remote was added
git remote -v
```

**Example:**
```bash
git remote add origin https://github.com/yourusername/un-speech-cleaner.git
```

## Step 3: Push to GitHub

```bash
# Push your code to GitHub
git branch -M main
git push -u origin main
```

If you get an authentication error, you may need to:
1. Use a Personal Access Token instead of password
2. Or configure SSH keys (recommended)

### Option A: Using Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Generate and **copy the token**
5. When pushing, use the token as your password

### Option B: Using SSH (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy the public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

Then use SSH URL instead:
```bash
git remote set-url origin git@github.com:USERNAME/REPO_NAME.git
git push -u origin main
```

## Step 4: Verify on GitHub

1. Go to your repository: `https://github.com/USERNAME/REPO_NAME`
2. Verify all files are there
3. Check that README.md displays nicely

## Step 5: Add Repository Topics (Optional)

On your GitHub repo page:
1. Click "⚙️ Settings" → About section → "Add topics"
2. Suggested topics:
   - `nlp`
   - `text-processing`
   - `united-nations`
   - `boilerplate-removal`
   - `n-gram-analysis`
   - `data-cleaning`
   - `python`

## What's Included

Your repository now contains:

✅ **Code**
- `src/clean_un_text_ngram.py` - Enhanced cleaner
- `src/extract_ngram_boilerplate.py` - N-gram extractor
- `src/clean_un_text.py` - Original pattern-based cleaner
- Supporting analysis scripts

✅ **Data**
- `ngram_boilerplate_aggressive.json` - 567 extracted phrases
- `n-grams and cleaning data/` - Frequency CSVs and config
- N-gram frequency files (4-10 grams)

✅ **Documentation**
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- `CONTRIBUTING.md` - Contribution guidelines
- `BOILERPLATE_ANALYSIS_AND_RECOMMENDATIONS.md` - Detailed analysis
- `LICENSE` - MIT License

✅ **Configuration**
- `.gitignore` - Git ignore rules (excludes large CSV files)
- `requirements.txt` - Python dependencies

## What's NOT Included (by design)

❌ Large CSV input/output files (`.gitignore`d)
❌ Temporary processing files
❌ IDE configuration files

This keeps your repository clean and focused on the code and methodology.

## Updating Your Repository

After making changes:

```bash
# Check what changed
git status

# Add changed files
git add .

# Commit with a message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Collaborating

### Clone on another machine

```bash
git clone https://github.com/USERNAME/REPO_NAME.git
cd REPO_NAME
pip install -r requirements.txt
```

### Pull latest changes

```bash
git pull origin main
```

## Making it Public/Private

You can change repository visibility anytime:
1. Go to Settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility"

## Adding a Badge

Add this to your README.md to show a GitHub star badge:

```markdown
![GitHub stars](https://img.shields.io/github/stars/USERNAME/REPO_NAME?style=social)
```

## Next Steps

1. ✅ Push to GitHub (done!)
2. Share with collaborators
3. Submit to research communities
4. Add to your CV/portfolio
5. Consider publishing on PyPI (optional)

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/REPO_NAME.git
```

### "Permission denied"
- Check your GitHub username/token
- Verify repository URL is correct
- Try SSH instead of HTTPS

### "Large files detected"
- Check `.gitignore` is working
- Remove large files: `git rm --cached filename`
- Use Git LFS for large files (optional)

## Resources

- GitHub Docs: https://docs.github.com/
- Git Basics: https://git-scm.com/book/en/v2
- GitHub Desktop (GUI): https://desktop.github.com/

---

**Congratulations!** Your UN Speech Boilerplate Cleaner is now on GitHub! 🎉
