# [Workbook Name]

**Category:** [Category Name] (e.g., AI Agents, Workflows, RAG & Retrieval)
**Difficulty:** ⭐ Beginner | ⭐⭐ Intermediate | ⭐⭐⭐ Advanced | ⭐⭐⭐⭐ Production
**Lines of Code:** ~[XXX] lines ([main.py] + [other files])

**One-line description:** [Brief description of what this workbook demonstrates]

---

## What You'll Learn

- [Key concept 1]
- [Key concept 2]
- [Key concept 3]

---

## What This Example Does

[2-3 paragraph explanation of the workflow, what problem it solves, and how it works]

**Flow diagram:**
```
[Node1] → [Node2] → [Node3]
            ↓
        [Branch]
```

---

## Quick Start

### Prerequisites

```bash
# Required dependencies (if any)
pip install [package1] [package2]

# Or
pip install -r requirements.txt
```

### Run It

```bash
cd workbooks/[##-category-name]/[workbook-name]
python main.py
```

**Expected output:**
```
[Show what users should see when they run it]
```

---

## File Structure

```
[workbook-name]/
├── main.py                 # Main entry point
├── [other files].py        # [Description]
├── README.md               # This file
└── requirements.txt        # Optional dependencies (if any)
```

---

## Key Components

### 1. [Component Name] (`[file.py]:[line]`)

**Purpose:** [What this component does]

```python
class [NodeName](Node):
    def prep(self, shared):
        # [Explanation]
        return data

    def exec(self, prep_res):
        # [Explanation]
        return result

    def post(self, shared, prep_res, exec_res):
        # [Explanation]
        shared["result"] = exec_res
        return "action"  # or None
```

**Why this matters:** [Explanation of the pattern or technique]

### 2. [Another Component]

[Similar structure]

---

## Customization

**To adapt this for your use case:**

1. **[Customization point 1]**
   - Modify: `[file]:[line]`
   - Change: [What to change]
   - Example: [Quick example]

2. **[Customization point 2]**
   - [Similar structure]

3. **[Customization point 3]**
   - [Similar structure]

---

## Common Use Cases

This pattern is useful for:

- ✅ [Use case 1]
- ✅ [Use case 2]
- ✅ [Use case 3]

Not suitable for:

- ❌ [Anti-use case 1]
- ❌ [Anti-use case 2]

---

## Related Workbooks

**Build on this:**
- 📚 [Next-level workbook] - [Why to check it out]
- 📚 [Related workbook] - [How it's related]

**Prerequisites (if you're new):**
- 📖 [Simpler workbook] - [What foundational concept it teaches]
- 📖 [Basic workbook] - [Another prerequisite]

**Combine with:**
- 🔧 [Complementary workbook] - [How they work together]

---

## Production Checklist

Before using this in production:

- [ ] Replace mock/placeholder implementations with real services
- [ ] Add proper error handling (see `kaygraph-fault-tolerant-workflow`)
- [ ] Add validation (see `kaygraph-validated-pipeline`)
- [ ] Add metrics and monitoring (see `kaygraph-metrics-dashboard`)
- [ ] Add logging throughout (see `COMMON_PATTERNS_AND_ERRORS.md`)
- [ ] Add tests (unit + integration)
- [ ] Configure secrets management (environment variables)
- [ ] Add rate limiting for external APIs
- [ ] Review security considerations
- [ ] Document deployment requirements

---

## Common Issues

### Issue 1: [Common problem]

**Symptom:** [What users see]

**Cause:** [Why it happens]

**Fix:**
```python
# [Code showing the fix]
```

### Issue 2: [Another common problem]

[Similar structure]

---

## Learn More

- 📘 [Main README](../../README.md) - Complete KayGraph overview
- 🤖 [DSL Reference](../../LLM_CONTEXT_KAYGRAPH_DSL.md) - For AI coding agents
- ⚠️ [Common Patterns & Errors](../../COMMON_PATTERNS_AND_ERRORS.md) - Avoid mistakes
- 🎯 [Task Finder](../QUICK_FINDER.md) - Find workbooks by use case
- 📚 [All Workbooks](../WORKBOOK_INDEX_CONSOLIDATED.md) - Complete catalog

---

## Design Decisions

**Why we built it this way:**

1. **[Design decision 1]**
   - Rationale: [Why this approach]
   - Trade-offs: [What we gave up]
   - Alternatives: [Other approaches considered]

2. **[Design decision 2]**
   - [Similar structure]

---

## Next Steps

After mastering this workbook:

1. **Modify the example** - Change [something specific] to match your use case
2. **Combine patterns** - Try integrating with [related workbook]
3. **Add production features** - Implement [specific production feature]
4. **Build something new** - Use this as a template for [application type]

---

## Contributing

Found an issue or have an improvement?

1. Check [COMMON_PATTERNS_AND_ERRORS.md](../../COMMON_PATTERNS_AND_ERRORS.md)
2. Open an issue on [GitHub](https://github.com/KayOS-AI/KayGraph/issues)
3. Submit a PR with your improvements

---

**Last Updated:** [Date]
**Tested with:** KayGraph v[version], Python 3.[minor]+
