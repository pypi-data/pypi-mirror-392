# Project Rules System

## Overview

The `.purposely/RULES.md` file is your project's **custom coding standards enforcer**. All AI agents automatically read and enforce these rules during implementation.

## Why This Exists

**Problem:** Telling AI not to create `UserManager_V2` or `utils_new/` folder every single session is exhausting.

**Solution:** Write the rule once in RULES.md. AI reads it automatically in every slash command.

## How It Works

### 1. Rules Are Auto-Loaded

Every slash command reads RULES.md FIRST:
- `/purposely-implement` - Reads before writing any code
- `/purposely-plan` - Reads before creating task breakdown
- `/purposely-design` - Reads before designing architecture

### 2. Rules Are Non-Negotiable

AI agents treat RULES.md as **hard constraints**, just like SPEC Success Criteria.

If a rule is violated:
- AI should catch it during implementation
- Human reviewer catches it during code review
- Document the exception in IMPLEMENTATION.md if unavoidable

### 3. Rules Evolve with Project

Update RULES.md when:
- You notice repeated bad patterns
- Team adopts new coding standards
- Technology stack changes (e.g., migrating to TypeScript)

## Example Rules

### Prevent Version Suffixes

```markdown
### Naming Conventions

**❌ DON'T create duplicate code with version suffixes:**
- Bad: `class UserManager` and `class UserManager_V2`
- Bad: `function parseData()` and `function parseData2()`

**✅ DO refactor or replace existing code:**
- Refactor the original if behavior needs to change
- Use git history to track old versions
```

**Before this rule:** AI would create `parseData2()` when improving the function.

**After this rule:** AI refactors `parseData()` in place or uses a better name.

### Enforce Architecture Patterns

```markdown
### Database Access

**Rule:** All database queries MUST go through Repository classes.

❌ Bad:
```python
# In controller
users = db.session.query(User).filter(User.active == True).all()
```

✅ Good:
```python
# In controller
users = user_repository.get_active_users()
```
```

**Before this rule:** AI might write ORM queries anywhere.

**After this rule:** AI creates/uses Repository methods.

### Project-Specific Patterns

```markdown
### API Response Format

**Rule:** All API endpoints MUST return this structure:

```typescript
{
  success: boolean,
  data?: T,
  error?: {
    code: string,
    message: string,
    details?: any
  }
}
```

No other response formats allowed.
```

**Before this rule:** Inconsistent API responses.

**After this rule:** Every endpoint follows the standard.

## Best Practices

### ✅ DO

1. **Be specific:** "Use Repository pattern" > "Write clean code"
2. **Show examples:** Code snippets clarify intent
3. **Explain why:** Context helps AI make better decisions
4. **Update regularly:** Add rules when you find patterns

### ❌ DON'T

1. **Don't write vague rules:** "Code should be good" (too vague)
2. **Don't contradict SPEC:** Rules support SPEC, not override it
3. **Don't overload:** 50 rules = AI won't remember them all
4. **Don't skip examples:** Abstract rules are hard to apply

## Rules vs SPEC vs DESIGN

| Document | Purpose | Scope |
|----------|---------|-------|
| RULES.md | Coding standards, patterns to avoid | **All phases** |
| SPEC | What to build, success criteria | **One phase** |
| DESIGN | How to build it, architecture | **One phase** |

**Example:**
- RULES.md: "Never create _V2 suffixes"
- SPEC: "Build user authentication system"
- DESIGN: "Use JWT tokens with Redis session store"

All three work together to guide implementation.

## Common Rules to Add

### 1. Prevent Duplicate Code

```markdown
❌ No version suffixes: _V2, _new, _old, _backup
❌ No copy-paste with minor changes
✅ Refactor existing code
✅ Extract shared logic into utilities
```

### 2. Enforce Testing

```markdown
Every new function/class MUST have:
- Unit tests in tests/ directory
- Test coverage >80%
- Edge case tests
```

### 3. Dependency Management

```markdown
Before adding a new npm/pip package:
1. Check if existing package can do it
2. Verify license compatibility
3. Check bundle size impact (npm only)
```

### 4. Error Handling

```markdown
Never use generic `except Exception` or `catch (e)`
- Python: Use specific exception types
- TypeScript: Use discriminated unions for errors
```

### 5. Documentation

```markdown
Every public function MUST have:
- Docstring/JSDoc with parameters
- Return type documentation
- Example usage (for complex functions)
```

## Enforcement Workflow

```
User adds rule to RULES.md
         ↓
AI agent starts /purposely-implement
         ↓
Reads .purposely/RULES.md FIRST
         ↓
Internalizes rules as constraints
         ↓
Writes code following rules
         ↓
If violation detected → Refactor immediately
```

## Migration from Comments to Rules

**Old way (every session):**
```
User: "Don't create UserManager_V2, refactor the original"
AI: "Got it!"
[Next session]
User: "Again, no _V2 suffix!"
```

**New way (once):**
```
User: [Adds to RULES.md]
"❌ No version suffixes"

AI: [Reads RULES.md every session]
"I see the rule. Will refactor in place."
```

## Location

RULES.md lives in `.purposely/` because:
- It's project configuration (like config.json)
- It's version controlled with the project
- It's easily accessible to all slash commands

## Integration Points

RULES.md is read by:
1. `/purposely-implement` - Before writing any code
2. `/purposely-plan` - When breaking down tasks
3. `/purposely-design` - When designing architecture

RULES.md is referenced in:
- IMPLEMENTATION.md - "Followed rules: X, Y, Z"
- Code review - "Violates RULE: No version suffixes"

## Summary

**The plugin-like system you wanted:**

1. Write rule once → `.purposely/RULES.md`
2. AI enforces automatically → Every slash command
3. Update as needed → Rules evolve with project
4. No repetition → Stop explaining the same thing every session

**This transforms "that thing I keep telling the AI" into "the rule the AI always follows".**
