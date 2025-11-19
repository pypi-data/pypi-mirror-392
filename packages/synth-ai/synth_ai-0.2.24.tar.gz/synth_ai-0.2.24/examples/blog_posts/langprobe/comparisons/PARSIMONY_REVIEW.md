# Parsimony Review: Complex Fixes That Need Simplification

## Issues That Need Review

### ⚠️ Issue 1: Missing Variants - `best_prompt.render({})` Problem

**Proposed Fix**:
```python
payload = {
    "best_prompt_messages": best_prompt.render({}),  # ❌ Will fail if template has required variables
}
```

**Problem**: `render()` raises `ValueError` if template has required variables and they're not provided.

**Simpler Alternative**: Use existing helper function `_render_template_messages()`:
```python
# In online_jobs.py, import or reuse the helper:
from .core.evaluation import _render_template_messages

payload = {
    "best_prompt": _serialize_prompt_template(best_prompt),
    "best_prompt_messages": _render_template_messages(best_prompt),  # ✅ Handles variables gracefully
}
```

**Why Simpler**:
- Already exists and handles edge cases
- Provides empty strings for required variables
- Falls back to sections if rendering fails
- No need to handle exceptions

---

### ⚠️ Issue 5: Archive Items - Complex Type Handling

**Proposed Fix**:
```python
# Convert archive items to messages format
archive_items_with_messages = []
for item in archive_summary.get("items", []):
    payload = item.get("payload", {})
    obj = payload.get("object")
    
    # Convert to messages if template
    if isinstance(obj, PromptTemplate):
        messages = obj.render({})  # ❌ Same variable problem
    elif isinstance(obj, dict) and obj.get("kind") == "template":
        template = PromptTemplate.from_dict(obj)  # ❌ Complex deserialization
        messages = template.render({})
    else:
        messages = None
```

**Problem**: 
1. Same `render({})` variable issue
2. Archive items are already serialized (not `PromptTemplate` instances)
3. Need to handle multiple object types (template, transformation, pattern)

**Simpler Alternative**: Use existing `_summarise_archive()` and add messages to summary:
```python
# Archive is already summarized by _summarise_archive()
archive_summary = optimizer.archive.to_summary()  # Returns list of dicts

# Add messages to each item using helper
from .core.evaluation import _render_template_messages

archive_items_with_messages = []
for item in archive_summary:
    obj_repr = item.get("object", {})
    
    # Extract template from serialized representation
    if obj_repr.get("type") == "template":
        template_data = obj_repr.get("data", {})
        # Deserialize template
        template = PromptTemplate.from_dict(template_data)
        # Render messages using helper
        messages = _render_template_messages(template)
    else:
        # For transformations/patterns, messages may not be applicable
        messages = None
    
    archive_items_with_messages.append({
        **item,
        "messages": messages,
    })

payload = {
    "archive": archive_items_with_messages,
}
```

**Even Simpler**: Just add messages to `_summarise_archive()` itself:
```python
# Modify _summarise_archive() to include messages:
def _summarise_archive(archive: Optional[ParetoArchive]) -> List[Dict[str, Any]]:
    if archive is None:
        return []
    from .core.evaluation import _render_template_messages
    
    out: List[Dict[str, Any]] = []
    for item in archive.items:
        payload = item.get("payload", {})
        obj = payload.get("object")
        
        # ... existing serialization code ...
        
        # Add messages if template
        messages = None
        if isinstance(obj, PromptTemplate):
            messages = _render_template_messages(obj)
        elif isinstance(obj_repr, dict) and obj_repr.get("type") == "template":
            template_data = obj_repr.get("data", {})
            template = PromptTemplate.from_dict(template_data)
            messages = _render_template_messages(template)
        
        out.append({
            **existing_fields,
            "messages": messages,  # ✅ ADD
        })
    return out
```

**Why Simpler**:
- Reuses existing serialization logic
- Uses helper function for rendering
- Single place to modify (not scattered)
- Handles all edge cases already

---

### ✅ Issue 3: Validation Trial Registration - May Be Complex

**Proposed Fix**:
```python
# During validation (lines 1663-1900), register validation trials:
for val_result in validation_results:
    val_trial_id = encode_trial_id(job_id, iteration=0, trial_index=val_result.get("rank", 0), seed=val_seed)
    val_trial_key = TrialKey(job_id=job_id, trial_id=val_trial_id, seed=val_seed)
    
    await register_trial_with_metadata(
        trial_key=val_trial_key,
        deltas={},  # No deltas for validation
        baseline_messages=baseline_messages,
        job_id=job_id,
        org_id=org_id,
        provider_config=provider_config,
        phase="validation",
        validation_rank=val_result.get("rank"),
        validation_score=val_result.get("accuracy"),
    )
```

**Potential Issues**:
1. Need to understand validation flow (lines 1663-1900)
2. May need to fetch `baseline_messages` and `provider_config`
3. May need `org_id` which might not be available in that scope

**Simpler Alternative**: Just track validation counts, don't register trials:
```python
# In optimizer, track validation separately:
self._validation_rollouts_executed: int = 0

# During validation:
self._validation_rollouts_executed += len(validation_seeds)

# Expose in snapshot_payload:
payload = {
    "validation_rollouts_executed": int(getattr(optimizer, "_validation_rollouts_executed", 0) or 0),
    "optimization_rollouts_executed": int(getattr(optimizer, "_total_rollouts_executed", 0) or 0),
}
```

**Why Simpler**:
- No trial registration needed
- Just count rollouts (simpler than tracking individual trials)
- Script can distinguish by rollout count, not trial metadata

---

## Summary: Recommended Simplifications

1. **Issue 1**: Use `_render_template_messages()` helper instead of `render({})`
2. **Issue 5**: Modify `_summarise_archive()` to include messages, reuse existing logic
3. **Issue 3**: Track validation rollouts separately instead of registering validation trials

All other fixes (Issue 2, Issue 4) are straightforward and don't need simplification.



