# {{ t.design.title.replace('{phase_number}', phase_number).replace('{topic}', topic) }}

> **{{ t.design.subtitle }}**
>
> **{{ t.design.sections.global_contribution }}:**
> {{ t.design.prompts.global_contribution }}

---

## {{ t.design.sections.overview }}

{{ t.design.prompts.overview }}

**{{ t.common.status }}:** {{ t.common.tbd }}

<!-- Describe what specific aspect you're designing -->

---

## {{ t.design.sections.requirements }}

{{ t.design.prompts.requirements }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - {{ t.common.tbd }}

---

## {{ t.design.sections.architecture }}

{{ t.design.prompts.architecture }}

### {{ t.common.status }}: {{ t.common.tbd }}

```
[Add detailed architecture or design]
```

---

## {{ t.design.sections.components }}

{{ t.design.prompts.components }}

### {{ t.common.status }}: {{ t.common.tbd }}

### Component 1: {{ t.common.tbd }}

**{{ t.design.sections.overview }}:** {{ t.common.tbd }}

**Responsibilities:**
- {{ t.common.tbd }}

**{{ t.design.sections.interfaces }}:**
```
[Add interface details]
```

---

## {{ t.design.sections.data_flow }}

{{ t.design.prompts.data_flow }}

### {{ t.common.status }}: {{ t.common.tbd }}

```
[Add data flow for this specific design]
```

---

## {{ t.design.sections.decisions }}

{{ t.design.prompts.decisions }}

### {{ t.common.status }}: {{ t.common.tbd }}

### Decision 1: {{ t.common.tbd }}

**Rationale:** {{ t.common.tbd }}

---

## {{ t.design.sections.alternatives }}

{{ t.design.prompts.alternatives }}

### {{ t.common.status }}: {{ t.common.tbd }}

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| {{ t.common.tbd }} | {{ t.common.tbd }} | {{ t.common.tbd }} | {{ t.common.tbd }} |

---

## {{ t.design.sections.risks }}

{{ t.design.prompts.risks }}

### {{ t.common.status }}: {{ t.common.tbd }}

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {{ t.common.tbd }} | {{ t.common.tbd }} | {{ t.common.tbd }} | {{ t.common.tbd }} |

---

## {{ t.design.sections.validation }}

{{ t.design.prompts.validation }}

### {{ t.common.status }}: {{ t.common.tbd }}

- {{ t.common.tbd }}

---

## {{ t.design.sections.notes }}

<!-- Add any additional notes specific to this design -->

---

## {{ t.design.sections.version_history }}

### v1.0 ({{ ''|now('utc', '%Y-%m-%d') }})
- {{ t.common.status }}: {{ t.common.draft }}
