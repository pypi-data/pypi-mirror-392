# {{ t.rules.title }}

{{ t.rules.description }}

## {{ t.rules.sections.purpose }}

{{ t.rules.purpose_text }}

## {{ t.rules.sections.how_to_use }}

1. {{ t.rules.how_to_use.step1 }}
2. {{ t.rules.how_to_use.step2 }}
3. {{ t.rules.how_to_use.step3 }}

---

## {{ t.rules.sections.code_quality }}

### {{ t.rules.naming.title }}

**❌ {{ t.rules.naming.dont }}**
- {{ t.rules.naming.bad1 }}
- {{ t.rules.naming.bad2 }}
- {{ t.rules.naming.bad3 }}

**✅ {{ t.rules.naming.do }}**
- {{ t.rules.naming.good1 }}
- {{ t.rules.naming.good2 }}
- {{ t.rules.naming.good3 }}

### {{ t.rules.duplication.title }}

**❌ {{ t.rules.duplication.dont }}**
- {{ t.rules.duplication.bad1 }}
- {{ t.rules.duplication.bad2 }}
- {{ t.rules.duplication.bad3 }}

**✅ {{ t.rules.duplication.do }}**
- {{ t.rules.duplication.good1 }}
- {{ t.rules.duplication.good2 }}
- {{ t.rules.duplication.good3 }}

### {{ t.rules.file_org.title }}

**❌ {{ t.rules.file_org.dont }}**
- {{ t.rules.file_org.bad1 }}
- {{ t.rules.file_org.bad2 }}

**✅ {{ t.rules.file_org.do }}**
- {{ t.rules.file_org.good1 }}
- {{ t.rules.file_org.good2 }}
- {{ t.rules.file_org.good3 }}

### {{ t.rules.ai_watermarks.title }}

**❌ {{ t.rules.ai_watermarks.dont }}**
- {{ t.rules.ai_watermarks.bad1 }}
- {{ t.rules.ai_watermarks.bad2 }}
- {{ t.rules.ai_watermarks.bad3 }}
- {{ t.rules.ai_watermarks.bad4 }}
- {{ t.rules.ai_watermarks.bad5 }}

**✅ {{ t.rules.ai_watermarks.do }}**
- {{ t.rules.ai_watermarks.good1 }}
- {{ t.rules.ai_watermarks.good2 }}
- {{ t.rules.ai_watermarks.good3 }}
- {{ t.rules.ai_watermarks.good4 }}

**{{ t.rules.ai_watermarks.exception }}** {{ t.rules.ai_watermarks.exception_text }}

### {{ t.rules.diagrams.title }}

**❌ {{ t.rules.diagrams.dont }}**
- {{ t.rules.diagrams.bad1 }}
- {{ t.rules.diagrams.bad2 }}
- {{ t.rules.diagrams.bad3 }}

**✅ {{ t.rules.diagrams.do }}**
- {{ t.rules.diagrams.good1 }}
- {{ t.rules.diagrams.good2 }}
- {{ t.rules.diagrams.good3 }}
- {{ t.rules.diagrams.good4 }}

---

## {{ t.rules.sections.project_specific }}

<!-- {{ t.rules.project_specific_hint }} -->

### {{ t.rules.examples.db.title }}

**{{ t.rules.examples.db.rule }}** {{ t.rules.examples.db.description }}
- ❌ {{ t.rules.examples.db.bad }}
- ✅ {{ t.rules.examples.db.good }}

### {{ t.rules.examples.api.title }}

**{{ t.rules.examples.api.rule }}** {{ t.rules.examples.api.description }}
```typescript
{
  success: boolean,
  data?: any,
  error?: { code: string, message: string }
}
```

---

## {{ t.rules.sections.enforcement }}

{{ t.rules.enforcement.intro }}
- {{ t.rules.enforcement.implement }}
- {{ t.rules.enforcement.plan }}
- {{ t.rules.enforcement.design }}

**{{ t.rules.enforcement.violation_title }}**
1. {{ t.rules.enforcement.violation1 }}
2. {{ t.rules.enforcement.violation2 }}
3. {{ t.rules.enforcement.violation3 }}
