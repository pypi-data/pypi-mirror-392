# Scripts Directory Structure

## Overview

The `scripts/` directory mirrors the `docs/` structure, organizing automation scripts by phase.

## Structure

```
scripts/
├── phase-01/
│   ├── build.sh           # Build automation for phase 1
│   ├── deploy.sh          # Deployment script
│   ├── migrate_data.py    # Data migration
│   └── test_runner.sh     # Custom test utilities
├── phase-02/
│   ├── setup_env.sh
│   └── benchmark.py
└── shared/                # Optional: Shared utilities across phases
    └── common.sh
```

## When to Use scripts/phase-XX/

Place scripts in phase-specific directories when they are:

1. **Build automation** - Compiling, bundling, packaging
2. **Deployment** - CI/CD, infrastructure setup
3. **Data operations** - Migrations, seeding, backups
4. **Testing utilities** - Custom test runners, fixtures generation
5. **Development tools** - Code generation, scaffolding

## Guidelines

### ✅ DO
- Place phase-specific automation in `scripts/phase-XX/`
- Keep scripts executable (`chmod +x`)
- Add shebang lines (`#!/bin/bash`, `#!/usr/bin/env python3`)
- Document script purpose and usage in comments
- Reference scripts in IMPLEMENTATION.md

### ❌ DON'T
- Don't put application code here (that goes in `src/`, `lib/`, etc.)
- Don't mix scripts from different phases
- Don't commit secrets or credentials

## Example: Phase 1 Build Script

```bash
# scripts/phase-01/build.sh
#!/bin/bash
# Build script for Phase 1: CLI Tool
# Purpose: Build and package Purposely CLI

set -e

echo "Building Purposely CLI..."
python -m build
echo "✅ Build complete"
```

## Integration with PLAN

When creating PLAN (03_PLAN.md), include scripts as tasks:

```markdown
## Tasks

### Success Criterion: Package is installable via pip

- [ ] Create build script in scripts/phase-01/build.sh
- [ ] Test build script in clean environment
- [ ] Add CI job to run build script
```

## Integration with IMPLEMENTATION

Document scripts in IMPLEMENTATION (04_IMPLEMENTATION.md):

```markdown
### Task: Create build automation

- **Status:** ✅ Complete
- **Files changed:** scripts/phase-01/build.sh
- **Purpose:** Automate Python package building
- **Usage:** `./scripts/phase-01/build.sh`
- **CI Integration:** Added to .github/workflows/build.yml
```

## Phase Directory Created Automatically

When you run:
```bash
purposely create spec 01
```

Both directories are created:
- `docs/phase-01/`
- `scripts/phase-01/`

This ensures scripts and documentation stay organized together.
