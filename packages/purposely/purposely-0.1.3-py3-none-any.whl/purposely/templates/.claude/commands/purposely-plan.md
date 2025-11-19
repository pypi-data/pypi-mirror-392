---
description: "Create docs/phase-XX/03_PLAN.md - AI-guided planning with Success Criteria validation"
---

**FIRST**, check the user's language setting:

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

**Read all phase documents:**

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

## Step 4: Estimate Timeline

**Prompt:**
> "Your SPEC says [X weeks]. For each task group, how long?"

**Check against SPEC Constraint:**

```markdown
## Timeline

Week 1:
- Initializer implementation (2 days)
- TemplateRenderer (2 days)
- Tests (1 day)

Week 2:
- Integration (2 days)
- Documentation (1 day)
- Buffer (2 days)

Total: 10 days (fits 2-week constraint ✅)
```

**If timeline exceeds SPEC:**
> "⚠️ This plan is 3 weeks but SPEC says 2 weeks. We need to cut scope or adjust SPEC. What's negotiable?"

## Step 5: Identify Dependencies & Risks

**Prompt:**
> "What must be done first? What could block you?"

**Format:**

```markdown
## Dependencies
- TemplateRenderer must be done before Creator
- Config system before all commands
- Research decisions applied first

## Risks
- **Risk:** Jinja2 complexity unknown
  - **Mitigation:** 1-day POC in week 1
  - **Fallback:** Simple string templates

- **Risk:** pytest setup issues
  - **Mitigation:** Set up CI early (day 2)
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

### ⏱️ Realistic Timeline

**Push back on over-optimism:**
> "You estimated 1 day for 5 components. Your last similar project took how long? Let's be realistic."

**Add buffer:**
> "Always add 20-30% buffer. Things go wrong."

### 🎯 Focus on SPEC

**Refuse scope creep in planning:**
> "That's not in SPEC. Put it in 'Future Ideas' section, not this plan."

## Next Steps

After plan complete:
- Start implementation and use `/purposely-implement` to track progress
- Update IMPLEMENTATION doc as you work
- Check off Success Criteria as achieved
