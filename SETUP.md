# Project Setup with `uv`

## Quick Start (5 minutes)

### 1. Add `uv` to PATH (one-time)
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add to `~/.zshrc` or `~/.bash_profile` to make it permanent:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Verify `uv` is installed
```bash
uv --version
# Expected: uv 0.11.28 (or newer)
```

### 3. Add your OpenAI API key
```bash
# Edit .env and replace with your real key
open .env
# Or use your editor:
# OPENAI_API_KEY=sk-proj-xxxxx...
```

Get your key from: https://platform.openai.com/api-keys

### 4. Verify everything works
```bash
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Ready!' if os.getenv('OPENAI_API_KEY') else '✗ Missing API key')"
```

---

## Common `uv` Commands

### Running Python code
```bash
# Run a script
uv run python script.py

# Run a Python command
uv run python -c "print('hello')"

# Run an installed CLI tool
uv run jupytext --help
```

### Working with notebooks
```bash
# Convert markdown notebook to .ipynb (if needed)
uv run jupytext --to notebook learning/week\ 1/01_intro.md

# Start Jupyter Lab to edit notebooks
uv run jupyter lab
```

### Managing dependencies
```bash
# Install new package (updates pyproject.toml and uv.lock)
uv add requests

# Add dev-only dependency
uv add --dev pytest

# Sync environment (install from uv.lock)
uv sync

# Sync with dev dependencies
uv sync --dev
```

### Virtual environment
```bash
# Activate the virtual environment
source .venv/bin/activate

# Or run commands with uv run (don't need to activate)
uv run python my_script.py

# Show environment info
uv env show
```

---

## File Structure

```
.
├── pyproject.toml         # ← Project metadata + dependencies (managed by uv)
├── uv.lock                # ← Locked dependency versions (reproducible installs)
├── .venv/                 # ← Virtual environment (created by uv sync)
├── .env                   # ← Your secrets (add to .gitignore ✓)
├── .env.example           # ← Template for .env
├── SETUP.md               # ← You're reading this
├── LEARNING_GUIDE.md      # ← Learning path
└── learning/week 1/       # ← Lesson notebooks
    ├── requirements.txt   # ← (legacy, not needed with uv)
    └── *.md              # ← Jupytext markdown notebooks
```

---

## Next Steps

1. ✅ Install `uv` (done!)
2. ✅ Setup virtual environment (done!)
3. ✅ Create `.env` with your API key (just do this now)
4. → Run `00_setup_overview.md` to verify
5. → Start Lesson 1!

---

## Troubleshooting

**`uv: command not found`**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
# Then reload shell
source ~/.zshrc
```

**`OPENAI_API_KEY` still missing**
```bash
# Check .env exists and has your key
cat .env

# Verify it's readable by Python
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:20])"
```

**Want to uninstall `uv`?**
```bash
rm -rf $HOME/.local/bin/uv $HOME/.local/bin/uvx
```

---

Ready? Let's start learning! 🚀
