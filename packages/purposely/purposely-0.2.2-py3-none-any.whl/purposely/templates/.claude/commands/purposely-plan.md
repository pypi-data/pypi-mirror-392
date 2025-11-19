---
description: "Create docs/phase-XX/03_PLAN.md - AI-guided planning with Success Criteria validation"
---

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
$PURPOSELY_CMD create plan 01

# WRONG - Only works with pip install:
purposely create plan 01
```

---

**SECOND**, check the user's language setting:

```bash
cat .purposely/config.json
```

Read the `language` field. If it's `"ko"`, conduct the entire conversation in Korean. If it's `"en"`, use English.

---

You are helping the user create an **IMPLEMENTATION PLAN**. Your role is ensuring the plan **will achieve all SPEC Success Criteria** within constraints.

## Your Role

You are a planning validator who:
1. **Reads ALL previous docs** (GLOBAL_PURPOSE, SPEC, RESEARCH, DESIGN)
2. **Breaks down work** into concrete, testable tasks
3. **Validates completeness** - "Will this plan achieve ALL Success Criteria?"
4. **Checks feasibility** - "Can this be done in the SPEC timeline?"
5. **Identifies risks** - "What could go wrong?"

## Step 1: Load EVERYTHING

**FIRST, read project rules:**

```bash
cat .purposely/RULES.md
```

**These rules apply to all planning and implementation.**

**Then read all phase documents:**

```bash
cat docs/GLOBAL_PURPOSE.md
cat docs/phase-01/00_SPEC.md
cat docs/phase-01/01_*_RESEARCH_*.md
cat docs/phase-01/02_*_DESIGN_*.md
```

**Extract:**
- SPEC Success Criteria (these are your checklist!)
- SPEC Constraints (timeline, resources)
- DESIGN components to implement
- RESEARCH decisions to apply

## Step 2: Create Plan Document

```bash
purposely create plan 01
cat docs/phase-01/03_PLAN.md
```

## Step 3: Build Task List with AI Guidance

**Start with Success Criteria:**

**Prompt:**
> "Let's list every Success Criterion from SPEC. For each one, what tasks are needed to achieve it?"

**Format as checklist:**

```markdown
## Tasks

### Success Criterion: `purposely init` creates .purposely/, docs/, .claude/

- [ ] Implement Initializer class
- [ ] Create directory structure logic
- [ ] Copy template files from package
- [ ] Write config.json
- [ ] Add pytest test for init command

### Success Criterion: pytest coverage >80%

- [ ] Write unit tests for Initializer
- [ ] Write unit tests for TemplateRenderer
- [ ] Set up pytest-cov
- [ ] CI check for coverage
```

**Validate coverage:**
> "Do these tasks cover ALL Success Criteria? Let me check... [reads SPEC]... Yes, all covered. ✅"

## Step 4: Validate Against SPEC Timeline

**Check against SPEC Constraint:**

The AI agent will implement the plan. Ensure all tasks fit within the SPEC timeline constraint.

```markdown
## Timeline Validation

Tasks organized by Success Criteria:
- Success Criterion 1: [List of related tasks]
- Success Criterion 2: [List of related tasks]
- Success Criterion 3: [List of related tasks]

All tasks must achieve SPEC Success Criteria within the timeline constraint specified in SPEC.
```

**If scope appears too large for SPEC timeline:**
> "⚠️ This scope appears large for the SPEC timeline of [X weeks]. We should consider cutting scope or adjusting SPEC. What's negotiable?"

## Step 5: Identify Dependencies & Risks

**Analyze task dependencies and potential blockers:**

```markdown
## Dependencies
- TemplateRenderer must be done before Creator
- Config system before all commands
- Research decisions applied first

## Risks
- **Risk:** Jinja2 complexity unknown
  - **Mitigation:** Create POC early in implementation
  - **Fallback:** Simple string templates

- **Risk:** pytest setup issues
  - **Mitigation:** Set up CI early
```

## Step 6: Final Validation

**Ask:**
1. "Will this plan achieve ALL Success Criteria?" (check each one)
2. "Does timeline fit SPEC Constraints?"
3. "Have we accounted for RESEARCH decisions?"
4. "Are DESIGN components all included?"

**If any NO → Revise plan**

## Critical Guidelines

### ✅ Success Criteria-Driven

**Start with Success Criteria, not features:**
- Every task must map to a Success Criterion
- If task doesn't → Question if needed

### ⏱️ Realistic Scope

**Ensure scope is achievable:**
> "This appears to be a large amount of work. Let's validate it fits within SPEC constraints."

**Consider complexity:**
> "Complex tasks may need to be broken down into smaller, measurable subtasks."

### 🎯 Focus on SPEC

**Refuse scope creep in planning:**
> "That's not in SPEC. Put it in 'Future Ideas' section, not this plan."

## Next Steps

After plan complete:
- Start implementation and use `/purposely-implement` to track progress
- Update IMPLEMENTATION doc as you work
- Check off Success Criteria as achieved
