# {{ t.research.title.replace('{phase_number}', phase_number).replace('{topic}', 'Overview') }}

> **{{ t.research.subtitle }}**
>
> **{{ t.research.sections.global_contribution }}:**
> {{ t.research.prompts.global_contribution }}

---

## {{ t.research.sections.overview }}

{{ t.research.prompts.overview }}

**{{ t.common.status }}:** {{ t.common.tbd }}

<!-- Describe the overall research strategy for this phase -->

---

## {{ t.research.sections.questions }}

{{ t.research.prompts.questions }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - Related to SPEC objective: {{ t.common.tbd }}
   - Research doc: `01_XX_RESEARCH_*.md`

<!-- List all research areas needed for this phase -->

---

## Research Documents

{{ t.research.prompts.documents }}

### Completed

- [ ] `01_01_RESEARCH_{{ t.common.tbd }}.md` - {{ t.common.tbd }}

### Planned

- [ ] `01_02_RESEARCH_{{ t.common.tbd }}.md` - {{ t.common.tbd }}

---

## Key Findings Summary

{{ t.research.prompts.findings }}

### {{ t.common.status }}: {{ t.common.tbd }}

<!-- Summarize findings from all research documents -->

### From Research 01: {{ t.common.tbd }}

- {{ t.common.tbd }}

---

## {{ t.research.sections.recommendations }}

{{ t.research.prompts.recommendations }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - {{ t.common.tbd }}

---

## Impact on Design

{{ t.research.prompts.impact }}

### {{ t.common.status }}: {{ t.common.tbd }}

<!-- How do these findings influence the design phase? -->

- {{ t.common.tbd }}

---

## {{ t.research.sections.notes }}

<!-- Add any additional notes -->

---

## {{ t.research.sections.version_history }}

### v1.0 ({{ ''|now('utc', '%Y-%m-%d') }})
- {{ t.common.status }}: {{ t.common.draft }}
