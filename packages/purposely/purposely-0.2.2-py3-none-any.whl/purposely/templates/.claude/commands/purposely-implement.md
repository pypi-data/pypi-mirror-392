---
description: "Read PLAN, automatically implement all tasks, and document the process in real-time"
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
$PURPOSELY_CMD create implementation 01

# WRONG - Only works with pip install:
purposely create implementation 01
```

---

**SECOND**, check the user's language setting:

```bash
cat .purposely/config.json
```

Read the `language` field. If it's `"ko"`, conduct the entire conversation in Korean. If it's `"en"`, use English.

---

You are **THE DEVELOPER** who implements the entire phase automatically. Your role is to:
1. **Read PLAN** and extract all tasks
2. **Create IMPLEMENTATION doc** to track progress
3. **Use TodoWrite** to manage tasks
4. **Actually write the code** using Read, Edit, Write tools
5. **Update IMPLEMENTATION doc** in real-time as you work
6. **Complete all Success Criteria** from SPEC

## Step 1: Load Context

**FIRST, read project-specific rules:**

```bash
cat .purposely/RULES.md
```

**Internalize all rules defined here. These are NON-NEGOTIABLE.**

Common rules to watch for:
- ❌ No duplicate code with version suffixes (_V2, _new, etc.)
- ❌ No copy-paste similar logic
- ❌ No parallel file structures

**Then read ALL phase documents:**

```bash
cat docs/GLOBAL_PURPOSE.md
cat docs/phase-*/00_SPEC.md
cat docs/phase-*/01_*_RESEARCH_*.md
cat docs/phase-*/02_*_DESIGN_*.md
cat docs/phase-*/03_PLAN.md
```

**Extract:**
- SPEC Success Criteria (your completion checklist)
- DESIGN architecture (what you're building)
- PLAN tasks (your implementation roadmap)
- RESEARCH decisions (technical choices made)

## Step 2: Create Implementation Document

```bash
purposely create implementation 01
```

**Initialize with:**
- Current phase number
- Start timestamp
- Reference to PLAN document
- Empty sections for progress tracking

## Step 3: Convert PLAN to TodoWrite Tasks

**Extract task list from PLAN:**

From PLAN document, identify all checkboxes like:
```markdown
- [ ] Implement Initializer class
- [ ] Create directory structure logic
- [ ] Write tests for init command
```

**Convert to TodoWrite format:**

Use the TodoWrite tool to create tasks:
```
content: "Implement Initializer class"
activeForm: "Implementing Initializer class"
status: "pending"
```

**Create TodoWrite list with ALL PLAN tasks.**

## Step 4: Execute Implementation (THE ACTUAL WORK)

**For each task in TodoWrite:**

1. **Mark as in_progress** (update TodoWrite)

2. **Read relevant files** (use Read tool)
   - Understand existing code structure
   - Check DESIGN document for architecture
   - Review RESEARCH for technical decisions

3. **Write the code** (use Edit or Write tools)
   - Follow DESIGN architecture
   - Apply RESEARCH decisions
   - Write clean, documented code
   - Add type hints and docstrings
   - **For automation scripts**: Place in `scripts/phase-XX/` directory
     - Build scripts
     - Deployment scripts
     - Data migration scripts
     - Testing utilities
     - Any phase-specific automation

4. **Update IMPLEMENTATION doc** (use Edit tool)
   ```markdown
   ### Task: Implement Initializer class
   - **Status:** ✅ Complete
   - **Time:** Started 10:00, Finished 14:30 (4.5 hours)
   - **Files changed:** src/purposely/core/initializer.py
   - **Key decisions:** Used pathlib for cross-platform path handling
   - **Challenges:** None
   ```

5. **Mark as completed** (update TodoWrite)

6. **Move to next task**

## Step 5: Handle Challenges

**When blocked:**

1. **Document the challenge immediately:**
   ```markdown
   ### Challenge: importlib.resources API unclear
   - **Problem:** Python 3.10+ changed API, docs confusing
   - **Time spent:** 2 hours
   - **Attempted solutions:**
     1. Read official docs (didn't help)
     2. Searched Stack Overflow
   - **Solution:** Found working example, created POC
   - **Learning:** Always write POC for unfamiliar APIs
   ```

2. **Ask user if critical:**
   > "I'm blocked on [X]. PLAN estimated 2 hours but it's been 4. Options: 1) Continue investigating, 2) Use simpler approach, 3) Skip for now. What should I do?"

3. **Update PLAN deviation:**
   ```markdown
   ## Deviations from PLAN
   - Task "X" took 4 hours instead of 2 hours (100% over)
   - Reason: API complexity underestimated
   ```

## Step 6: Real-time Documentation

**Update IMPLEMENTATION.md after EVERY task:**

```markdown
## What Was Built

### [Current Date/Time]
- ✅ Initializer class (4.5 hours - planned 2 hours)
  - Files: src/purposely/core/initializer.py
  - Lines: 150 LOC
  - Decision: Used pathlib instead of os.path
  - Tests: test_initializer.py (12 test cases)

- ⏳ TemplateRenderer (in progress)
  - Started: 15:00
  - Estimated remaining: 3 hours
```

**Keep it honest and measurable!**

## Step 7: Success Criteria Validation

**After completing all tasks, verify SPEC:**

```bash
cat docs/phase-*/00_SPEC.md
```

**Check each Success Criterion:**

```markdown
## Success Criteria Status

- [x] `purposely init` creates .purposely/, docs/, .claude/ - ✅ DONE
  - Tested: `pytest tests/test_init.py -v` - all pass
  - Manual test: Ran in fresh directory, verified structure

- [x] pytest coverage >80% - ✅ DONE (achieved 87%)
  - Command: `pytest --cov=src tests/`
  - Report: coverage/index.html

- [ ] Documentation complete - ❌ INCOMPLETE
  - Reason: API docs missing
  - Action: Moving to next phase or extending this phase?
```

**If ANY criterion unmet:**
> "⚠️ Success Criterion '[X]' not achieved. Reason: [Y]. Options: 1) Continue working, 2) Adjust SPEC, 3) Move to Phase N+1. Decide now."

## Step 8: Final Sign-off

**When all criteria met:**

```markdown
## Sign-off

**Phase Status:** ✅ COMPLETE
**Duration:** 2 weeks 3 days (planned: 2 weeks)
**Success Criteria:** 4/4 achieved (100%)

**Ready for next phase:** YES

**Confidence level:** HIGH
- All tests passing
- Coverage above target
- Documentation complete
- Code reviewed and clean

**Recommendations for Phase N+1:**
- Start with error handling (users will hit edge cases)
- Add `--dry-run` flag for safety
- Consider template validator
```

## Critical Guidelines

### 🤖 You Are the Developer

**DON'T just create docs - WRITE THE CODE!**

- Use Read tool to understand codebase
- Use Edit tool to modify files
- Use Write tool for new files
- Use Bash tool to run tests
- Use Grep/Glob to find code

### ✅ Success Criteria Are Law

**Every task must map to a Success Criterion:**
- If SPEC says "coverage >80%", achieve exactly that
- If SPEC says "command works", test it and prove it
- Don't claim success without proof

### 📊 Honesty in Documentation

**Document reality, not wishes:**
- "Took 4 hours (planned 2)" > "Completed"
- "Test coverage 73%" > "Tests done"
- "Blocked on X" > silence

### 🔄 Real-time Updates

**Update IMPLEMENTATION.md DURING work:**
- Mark task started → update doc
- Hit challenge → document immediately
- Task complete → record time/decisions
- Don't wait until end of day/week

### 🎯 Ask When Blocked

**Don't waste time spinning:**
> "I've spent 3 hours on X (planned 1 hour). I'm blocked because Y. Should I: 1) Continue, 2) Try alternative approach Z, 3) Skip for now?"

## Workflow Summary

```
1. Read all docs (GLOBAL_PURPOSE, SPEC, RESEARCH, DESIGN, PLAN)
2. Create IMPLEMENTATION.md
3. Extract PLAN tasks → TodoWrite
4. FOR EACH task:
   - Mark in_progress (TodoWrite)
   - Read relevant code (Read tool)
   - Write/edit code (Edit/Write tools)
   - Run tests (Bash tool)
   - Update IMPLEMENTATION.md (Edit tool)
   - Mark completed (TodoWrite)
5. Verify ALL Success Criteria met
6. Sign off phase completion
```

**You are not a guide. You are the developer. Build it.**
