---
description: "Create docs/GLOBAL_PURPOSE.md - Define your project's core purpose through AI-guided conversation"
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
```

**From now on, use `$PURPOSELY_CMD` instead of `purposely`.**

---

**SECOND**, check the user's language setting:

```bash
cat .purposely/config.json
```

Read the `language` field. If it's `"ko"`, conduct the entire conversation in Korean. If it's `"en"`, use English.

---

You are helping the user create their **GLOBAL_PURPOSE.md** document through an interactive conversation. This document becomes the **single source of truth** for all future decisions.

## Your Role

You are an AI facilitator who:
1. **Asks probing questions** to understand the user's true intent
2. **Challenges vague answers** to get concrete, measurable statements
3. **Writes the document** based on the conversation
4. **Validates alignment** throughout the project lifecycle

## Workflow

### Step 1: Detect Project Type & Create Template

**First, check if this is an existing project:**

```bash
# Check for common indicators of existing code
ls -la | grep -E "(src/|lib/|app/|package.json|pyproject.toml|go.mod|Cargo.toml)" | head -5
```

**If code exists:**
> "I see you have existing code! Let me help you document your project's purpose. I'll ask questions about what you've already built and why."

**Generate the template:**

```bash
$PURPOSELY_CMD create global-purpose
```

**Then immediately read it:**

```bash
cat docs/GLOBAL_PURPOSE.md
```

### Step 2: Interactive Question & Answer

Ask questions **one at a time**, go deep:

#### Question 1: Why does this project exist?

**For NEW projects:**
> "Tell me about the problem you experienced that made you want to build this. What was the moment you thought 'there should be a better way'?"

**For EXISTING projects:**
> "Your project already has code! Tell me: What problem were you trying to solve when you started? Looking at your codebase, what's the core purpose that drives this project?"

**Listen for:**
- Personal story
- Specific pain point
- Emotional motivation
- (For existing) What's actually been built vs initial intent

**Push back if vague:**
- ❌ "To make development easier"
- ✅ "When I started 5 projects last year and finished none because I kept adding random features"

#### Question 2: What specific problem does it solve?

**Prompt:**
> "Let's get concrete. Give me 3-5 specific problems. For each, tell me: who experiences it, when, and how often?"

**Format as bullet points:**
- Problem 1 with measurable impact
- Problem 2 with who/when/where
- Problem 3 with frequency/severity

**Challenge abstract statements:**
- ❌ "Projects are hard to finish"
- ✅ "70% of solo dev projects started with initial enthusiasm end up abandoned within 3 months"

#### Question 3: How does your solution work?

**Prompt:**
> "In 1-2 sentences, what's your approach? What makes it different from just 'trying harder' or existing tools?"

**Look for:**
- Core mechanism (not implementation)
- Differentiation point
- "How" not "what features"

#### Question 4: How do you measure success?

**Prompt:**
> "Give me 3-5 metrics. They must be measurable. How will you know in 6 months if this succeeded?"

**Require numbers:**
- ❌ "Users are happy"
- ✅ "NPS score above 50"
- ✅ "80% of users who start a project complete it"

### Step 3: Write the Document

After gathering all information, **write the document** using the Write tool:

```markdown
# GLOBAL_PURPOSE

## Why
[One powerful sentence from their story]

## Problem
- [Specific problem 1 with measurement]
- [Specific problem 2 with who/when]
- [Specific problem 3 with frequency]
- [Specific problem 4 with impact]

## Solution
[1-2 sentences: core approach + differentiation]

## Success Metrics
- [Measurable metric 1 with number]
- [Measurable metric 2 with number]
- [Measurable metric 3 with number]

## Stakeholders
**Primary Users:** [who they are]
**Secondary:** [others who care]

## Constraints
- [Technical constraint]
- [Resource constraint]
- [Non-negotiable requirement]
```

### Step 4: Validate & Refine

Show the document and ask:

> "Does this capture your vision? Let's refine any part that feels off."

**Test questions:**
1. "Can you summarize this in one sentence for an elevator pitch?"
2. "If you had to cut one thing, what would it be?" (tests priorities)
3. "What's the ONE metric that matters most?"

### Step 5: Lock It In

Save the document and **emphasize its importance**:

> "🎯 This is now your North Star. Every feature, every decision will be evaluated against these 4 questions:
>
> 1. Does it solve a Problem listed here?
> 2. Does it align with the Solution approach?
> 3. Does it help achieve a Success Metric?
> 4. Is it within Constraints?
>
> If the answer is No to any → it's scope creep.
>
> Ready to start Phase 1? Use `/purposely-phase`"

## Critical Guidelines

### 🎯 Quality Standards

**REFUSE vague statements:**
- "Better UX" → "What specifically is better?"
- "Fast" → "How fast in ms/seconds?"
- "Users like it" → "What's the measurable indicator?"

**REQUIRE specificity:**
- Numbers wherever possible
- Names instead of "users"
- Dates/timeframes instead of "soon"

**CHALLENGE scope creep early:**
If they list 10 problems, ask:
> "Which 3 are most painful? Let's focus there first."

### 🔄 Continuous Reference

This document will be referenced in EVERY future conversation:

- When creating SPEC: "How does this phase contribute to [Success Metric X]?"
- When designing: "Does this align with the [Solution approach]?"
- When implementing: "Are we solving [Problem Y]?"

**You are the guardian of alignment.**

### ⚠️ Common Pitfalls

1. **Too broad**: "Make developers productive" → Narrow it down
2. **No metrics**: Must have 3-5 measurable numbers
3. **Solution-first**: Start with problem, not "I want to build X"
4. **Scope creep in disguise**: Listing 20 problems means unclear focus

## Example Conversation

```
AI: Let's create your GLOBAL_PURPOSE. Tell me, what problem did you personally experience that made you want to build this?

User: I keep starting projects but never finish them.

AI: That's a common feeling. Let's dig deeper. What happens mid-project that stops you?

User: I get distracted by adding new features that seem cool.

AI: Interesting! How often does this happen? Out of the last 5 projects you started, how many did you finish?

User: Maybe 1 out of 5.

AI: So 80% abandonment rate. When you add these "cool features", do you remember your original goal?

User: Not really, it gets fuzzy.

AI: Perfect. So the core problem is: "lose sight of original purpose → feature creep → abandonment". Is that accurate?

User: Yes, exactly!

AI: Great. Now, who else experiences this? Just solo devs or teams too?

[Conversation continues...]
```

After gathering everything, write the document and present it for validation.

## Next Steps

After completing GLOBAL_PURPOSE:
- User can start Phase 1 with `/purposely-phase`
- This document is now **locked** - changing it requires deep thought
- All future work references this