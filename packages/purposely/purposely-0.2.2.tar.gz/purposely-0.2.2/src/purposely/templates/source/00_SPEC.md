# {{ t.spec.title.replace('{phase_number}', phase_number).replace('{phase_name}', phase_name) }}

> **{{ t.spec.subtitle }}**
>
> **{{ t.spec.sections.global_contribution }}:**
> {{ t.spec.prompts.global_contribution }}

---

## {{ t.spec.sections.overview }}

{{ t.spec.prompts.overview }}

**{{ t.common.status }}:** {{ t.common.tbd }}

<!-- Describe the phase overview -->

---

## {{ t.spec.sections.objectives }}

{{ t.spec.prompts.objectives }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - {{ t.spec.sections.scope }}: {{ t.common.tbd }}
   - {{ t.spec.sections.success_indicators }}: {{ t.common.tbd }}

<!-- Add more objectives -->

---

## {{ t.spec.sections.tasks }}

{{ t.spec.prompts.tasks }}

### {{ t.common.status }}: {{ t.common.tbd }}

1. **{{ t.common.tbd }}**
   - {{ t.common.tbd }}

<!-- Add more tasks -->

---

## {{ t.spec.sections.data_sources }}

{{ t.spec.prompts.data_sources }}

### {{ t.common.status }}: {{ t.common.tbd }}

- {{ t.common.tbd }}

---

## {{ t.spec.sections.constraints }}

{{ t.spec.prompts.constraints }}

### {{ t.common.status }}: {{ t.common.tbd }}

- **{{ t.common.tbd }}**: {{ t.common.tbd }}

---

## {{ t.spec.sections.success_indicators }}

{{ t.spec.prompts.success_indicators }}

### {{ t.common.status }}: {{ t.common.tbd }}

- ✅ {{ t.common.tbd }}

---

## {{ t.spec.sections.scope }}

### {{ t.spec.sections.scope_in }}

{{ t.spec.prompts.scope_in }}

- ✅ {{ t.common.tbd }}

### {{ t.spec.sections.scope_out }}

{{ t.spec.prompts.scope_out }}

- ❌ {{ t.common.tbd }}

### {{ t.spec.sections.future }}

{{ t.spec.prompts.future }}

- {{ t.common.tbd }}

---

## {{ t.spec.sections.next_steps }}

{{ t.spec.prompts.next_steps }}

1. {{ t.common.tbd }}

---

## {{ t.spec.sections.notes }}

<!-- Add any additional notes -->

---

## {{ t.spec.sections.version_history }}

### v1.0 ({{ ''|now('utc', '%Y-%m-%d') }})
- {{ t.common.status }}: {{ t.common.draft }}
