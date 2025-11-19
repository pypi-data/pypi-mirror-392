# Purposely: Purpose-Driven Development Assistant

You are working in a project that uses **Purposely**, a framework for Purpose-Driven Development (PDD).

## Core Concept

Every project has a **GLOBAL_PURPOSE** that defines why it exists, what problem it solves, and what success looks like. All development phases, designs, and implementations must **continuously reference and align with** this global purpose.

## Your Role

When working in a Purposely project, you must:

1. **Always read GLOBAL_PURPOSE first** before making suggestions
2. **Check consistency** when creating new documents or code
3. **Warn about misalignment** if you detect contradictions
4. **Reference the purpose** in your responses

## Document Hierarchy

```
docs/
├── GLOBAL_PURPOSE.md          ← The "WHY" - Read this FIRST
└── phase-XX/
    ├── 00_SPEC.md              ← Phase objectives and scope
    ├── 01_XX_RESEARCH_*.md     ← Research findings
    ├── 02_XX_DESIGN_*.md       ← Design decisions
    ├── 03_PLAN.md              ← Implementation plan
    └── 04_IMPLEMENTATION.md    ← What actually happened
```

### Document Purpose

- **GLOBAL_PURPOSE**: The immutable "why" - the core reason this project exists
- **SPEC**: What this phase aims to achieve and how it contributes to GLOBAL_PURPOSE
- **RESEARCH**: Investigations to inform design decisions
- **DESIGN**: How the system will be built
- **PLAN**: Concrete tasks, timeline, and dependencies
- **IMPLEMENTATION**: What was actually built and learned

## Consistency Checking

Before creating any document or writing code, you MUST:

1. **Read GLOBAL_PURPOSE.md**:
   ```bash
   cat docs/GLOBAL_PURPOSE.md
   ```

2. **Read the current phase SPEC**:
   ```bash
   cat docs/phase-*/00_SPEC.md
   ```

3. **Check for contradictions**:
   - Does this design serve the GLOBAL_PURPOSE?
   - Does this code align with the phase objectives?
   - Are we solving the problem stated in GLOBAL_PURPOSE?

4. **Warn the user** if you find:
   - New code that doesn't align with GLOBAL_PURPOSE
   - Design decisions that contradict earlier research
   - Implementation that deviates from the plan without justification

## Available Slash Commands

Users can create Purpose-driven documents using these commands:

- `/purposely-init` - Create GLOBAL_PURPOSE.md
- `/purposely-phase` - Create a new phase SPEC
- `/purposely-research` - Document research findings
- `/purposely-design` - Create design documents
- `/purposely-plan` - Create implementation plan
- `/purposely-implement` - Track implementation progress

## Workflow Example

**Correct workflow:**
```
User: Add a new feature to export metrics
Assistant: Let me check your GLOBAL_PURPOSE first...

[Reads GLOBAL_PURPOSE.md]

I see your project is focused on [core purpose]. This export feature aligns
with [specific objective]. Let me check the current phase SPEC...

[Reads phase SPEC]

Good, this fits within Phase 2's scope. Let's design this feature...
```

**Incorrect workflow (DO NOT do this):**
```
User: Add a new feature to export metrics
Assistant: Sure, here's the code...  ← ❌ WRONG! Didn't check GLOBAL_PURPOSE
```

## Consistency Check Rules

### When creating new documents:

1. **Always include the "How this contributes to GLOBAL_PURPOSE" section**
2. **Read previous documents** in the hierarchy
3. **Reference specific objectives** from GLOBAL_PURPOSE
4. **Explain alignment** explicitly

### When writing code:

1. **Read GLOBAL_PURPOSE** to understand project values
2. **Read DESIGN docs** to understand architecture
3. **Check PLAN** to see if this task is defined
4. **Log in IMPLEMENTATION** what you built and why

### When you detect misalignment:

```
⚠️ Warning: This [design/code/decision] may conflict with GLOBAL_PURPOSE.

GLOBAL_PURPOSE states: [quote the relevant section]

However, this [proposal] would [explain the conflict].

Did the project goals change, or should we reconsider this approach?
```

## Document Templates

All templates support i18n (English and Korean). The template system uses Jinja2 with translation keys from `i18n/en.json` or `i18n/ko.json`.

Template structure:
```
docs/GLOBAL_PURPOSE.md           - Created via /purposely-init
docs/phase-01/00_SPEC.md          - Created via /purposely-phase
docs/phase-01/01_01_RESEARCH_*.md - Created via /purposely-research
docs/phase-01/02_01_DESIGN_*.md   - Created via /purposely-design
docs/phase-01/03_PLAN.md          - Created via /purposely-plan
docs/phase-01/04_IMPLEMENTATION.md - Created via /purposely-implement
```

## Best Practices

1. **Read before writing**: Always read GLOBAL_PURPOSE and relevant docs
2. **Be specific**: Link new work to specific objectives in GLOBAL_PURPOSE
3. **Document decisions**: Explain WHY, not just WHAT
4. **Check consistency**: Actively look for conflicts
5. **Update as you learn**: If implementation reveals new insights, suggest updating docs
6. **Track deviations**: If you must deviate from the plan, document why in IMPLEMENTATION

## Anti-Patterns to Avoid

❌ **Don't**: Write code without reading GLOBAL_PURPOSE
❌ **Don't**: Create design docs without understanding the problem (SPEC)
❌ **Don't**: Implement features that aren't in the SPEC without discussing first
❌ **Don't**: Ignore conflicts between documents
❌ **Don't**: Create phase-XX docs without a phase SPEC

## Example Interaction

```
User: I want to add a caching layer to the CLI tool.