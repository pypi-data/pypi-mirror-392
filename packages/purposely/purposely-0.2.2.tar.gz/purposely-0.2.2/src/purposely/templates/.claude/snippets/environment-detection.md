## Environment Detection (DO THIS FIRST!)

**CRITICAL: Detect environment and set up Purposely CLI before running ANY commands.**

Run this detection script:

```bash
# Step 1: Detect Python virtual environment
if [ -d ".venv" ]; then
  source .venv/bin/activate
  echo "✓ Activated Python venv: .venv"
elif [ -d "venv" ]; then
  source venv/bin/activate
  echo "✓ Activated Python venv: venv"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  echo "⚠ Python project detected but no venv found"
fi

# Step 2: Detect how Purposely CLI is available
if command -v purposely >/dev/null 2>&1; then
  echo "✓ Purposely CLI found in PATH"
  PURPOSELY_CMD="purposely"
elif command -v uvx >/dev/null 2>&1; then
  echo "✓ Using uvx to run Purposely"
  PURPOSELY_CMD="uvx --from git+https://github.com/nicered/purposely purposely"
else
  echo "❌ Neither 'purposely' nor 'uvx' found!"
  echo "Install with: pip install git+https://github.com/nicered/purposely"
  echo "Or install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

# Step 3: Detect Node.js environment (if applicable)
if [ -f "package.json" ]; then
  if [ -f "pnpm-lock.yaml" ]; then
    echo "✓ Node.js project: pnpm"
  elif [ -f "yarn.lock" ]; then
    echo "✓ Node.js project: yarn"
  else
    echo "✓ Node.js project: npm"
  fi
fi

# Step 4: Detect other languages (if applicable)
[ -f "go.mod" ] && echo "✓ Go project detected"
[ -f "Cargo.toml" ] && echo "✓ Rust project detected"
[ -f "Gemfile" ] && echo "✓ Ruby project detected"
```

**From now on, use `$PURPOSELY_CMD` instead of `purposely`:**

```bash
# CORRECT - Works with both pip install and uvx:
$PURPOSELY_CMD create spec 01

# WRONG - Only works with pip install:
purposely create spec 01
```

---
