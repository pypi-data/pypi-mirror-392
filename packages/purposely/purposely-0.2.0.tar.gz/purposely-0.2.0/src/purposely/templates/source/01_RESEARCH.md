# {{ t.research.title.replace('{phase_number}', phase_number).replace('{topic}', topic) }}

> **{{ t.research.subtitle }}**
>
> **{{ t.research.sections.global_contribution }}:**
> {{ t.research.prompts.global_contribution }}

---

## {{ t.research.sections.overview }}

{{ t.research.prompts.overview }}

**{{ t.common.status }}:** {{ t.common.tbd }}

<!-- Describe what you're researching and why -->

---

## {{ t.research.sections.questions }}

{{ t.research.prompts.questions }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - {{ t.common.tbd }}

<!-- Add more research questions -->

---

## {{ t.research.sections.findings }}

{{ t.research.prompts.findings }}

### {{ t.common.status }}: {{ t.common.tbd }}

### Finding 1: {{ t.common.tbd }}

<!-- Describe key findings -->

---

## {{ t.research.sections.analysis }}

{{ t.research.prompts.analysis }}

### {{ t.common.status }}: {{ t.common.tbd }}

<!-- Analyze what the findings mean -->

---

## {{ t.research.sections.recommendations }}

{{ t.research.prompts.recommendations }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - {{ t.common.tbd }}

---

## {{ t.research.sections.references }}

{{ t.research.prompts.references }}

- [{{ t.common.tbd }}]({{ t.common.tbd }})

---

## {{ t.research.sections.notes }}

<!-- Add any additional notes -->

---

## {{ t.research.sections.version_history }}

### v1.0 ({{ ''|now('utc', '%Y-%m-%d') }})
- {{ t.common.status }}: {{ t.common.draft }}
