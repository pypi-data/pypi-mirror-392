# Data Flow Analysis: GEPA/MIPRO → Backend → DB → API

## Overview
This document traces the data flow from optimizer to final API response, identifying gaps and proposing **direct, parsimonious fixes** (no fallbacks).

---

## Issue 1: Missing Artifacts / No Variants Extracted

### Data Flow Trace

**1. Optimizer (`optimizer.py`)**:
- `best_prompt` is a `PromptTemplate` object
- Returned as `(best_prompt, best_score, snapshot_payload)` from `optimizer.optimize()`

**2. Backend (`online_jobs.py:_run_gepa`)**:
```python
payload = {
    "best_prompt": _serialize_prompt_template(best_prompt),  # Line 1624
    "best_score": best_score,
    "total_rollouts": int(getattr(optimizer, "_total_rollouts_executed", 0) or 0),
    # ... tokens, archive, etc.
}
return best_prompt, best_score, payload
```

**3. Serialization (`online_jobs.py:_serialize_prompt_template`)**:
```python
def _serialize_prompt_template(template: PromptTemplate) -> Dict[str, Any]:
    return template.to_dict()  # Returns sections, NOT messages
```

**4. `PromptTemplate.to_dict()` (`core/prompt.py`)**:
```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "prompt_template_id": self.id,
        "prompt_template_name": self.name,
        "prompt_sections": [...],  # Sections with name/content/role/order
        "prompt_variables": self.variables,
        "prompt_metadata": self.metadata,
    }
    # ❌ NO messages array!
```

**5. Snapshot Storage (`online_jobs.py:run_job`)**:
```python
snapshot = await self.repo.create_prompt_snapshot(
    job_id=job_id,
    payload=snapshot_payload,  # Contains best_prompt (sections), NOT messages
    tag="best_prompt",
    score=best_score,
)
snapshot_id = snapshot["id"]
metadata["prompt_best_snapshot_id"] = snapshot_id  # ✅ Stored
metadata["prompt_best_snapshot"] = snapshot_payload  # ✅ Also stored in metadata
```

**6. API Response (`routes_online.py:get_prompt_learning_online_job`)**:
```python
best_snapshot_id = job_row.get("prompt_best_snapshot_id")
if best_snapshot_id:
    snapshot_row = await job_service.get_prompt_snapshot(best_snapshot_id)
    best_snapshot_payload = snapshot_row.get("payload")  # Contains best_prompt (sections)
```

**7. Script Extraction (`run_gepa_parallel_experiments.py:extract_variants`)**:
- Tries to extract from `best_snapshot.payload.messages` ❌ (doesn't exist)
- Falls back to `best_snapshot.payload.best_prompt.prompt_sections` ✅ (exists but not extracted)

### Root Cause
`best_prompt` is serialized as **sections** (template structure), not **messages** (API-ready format). The script expects `messages` array but it doesn't exist.

### Direct Fix
**Use existing helper function** `_render_template_messages()` to add `messages` array to snapshot payload:
```python
# In online_jobs.py:_run_gepa, after line 1624:
from .core.evaluation import _render_template_messages

payload = {
    "best_prompt": _serialize_prompt_template(best_prompt),
    "best_prompt_messages": _render_template_messages(best_prompt),  # ✅ Add messages array
    # ... rest of payload
}
```

**Why This Approach**: 
- Uses existing helper that handles variables gracefully (provides empty strings for required vars)
- Falls back to sections if rendering fails
- Single source of truth (backend generates messages once)
- No template rendering logic needed in script
- Matches API expectations (`best_snapshot.messages`)

---

## Issue 2: Missing Trials/Tokens in Results

### Data Flow Trace

**1. Optimizer (`optimizer.py`)**:
- `_candidate_counter`: Incremented for each transformation tried
- `_total_trials_evaluated`: Incremented for each trial evaluated
- `_total_rollouts_executed`: Incremented for each rollout
- `rollouts_prompt_tokens`, `rollouts_completion_tokens`, `rollouts_unknown_tokens`: Tracked

**2. Backend (`online_jobs.py:_run_gepa`)**:
```python
payload = {
    "total_rollouts": int(getattr(optimizer, "_total_rollouts_executed", 0) or 0),  # ✅ Exposed
    "rollouts_prompt_tokens": int(getattr(optimizer, "rollouts_prompt_tokens", 0) or 0),  # ✅ Exposed
    "rollouts_completion_tokens": int(getattr(optimizer, "rollouts_completion_tokens", 0) or 0),  # ✅ Exposed
    "rollouts_unknown_tokens": int(getattr(optimizer, "rollouts_unknown_tokens", 0) or 0),  # ✅ Exposed
    # ❌ NO trials_tried or total_trials_evaluated
    # ❌ NO total_tokens (sum of all token types)
}
```

**3. Snapshot Storage**:
- Tokens stored in `snapshot_payload` ✅
- But NOT stored in `job_metadata` ❌

**4. Job Metadata Update (`online_jobs.py:run_job`)**:
```python
metadata["prompt_best_snapshot_id"] = snapshot_id
metadata["prompt_best_train_score"] = best_score_to_store
metadata["prompt_best_snapshot"] = snapshot_payload  # ✅ Contains tokens, but nested
# ❌ NO top-level stats like trials_tried, total_tokens
```

**5. Experiment Queue Status (`synth_ai/experiment_queue/status.py`)**:
- `status_tracker.update()` may update `status_json` with progress
- But tokens/trials may not be persisted to `status_json` ❌

**6. Script Extraction (`run_gepa_parallel_experiments.py:extract_results`)**:
- Tries `job.status_json.get("trials_tried")` ❌ (may not exist)
- Tries `job.status_json.get("total_tokens")` ❌ (may not exist)
- Falls back to counting DB trials ❌ (incomplete)

### Root Cause
1. **Trials**: `_candidate_counter` and `_total_trials_evaluated` are NOT exposed in `snapshot_payload`
2. **Tokens**: Tokens ARE in `snapshot_payload` but NOT in top-level `job_metadata` or `status_json`
3. **Status JSON**: Not updated with final stats when job completes

### Direct Fix

**Fix 1**: Expose trials in `snapshot_payload` (`online_jobs.py:_run_gepa`):
```python
payload = {
    "total_rollouts": int(getattr(optimizer, "_total_rollouts_executed", 0) or 0),
    "trials_tried": int(getattr(optimizer, "_candidate_counter", 0) or 0),  # ✅ ADD
    "total_trials_evaluated": int(getattr(optimizer, "_total_trials_evaluated", 0) or 0),  # ✅ ADD
    "total_tokens": int(
        (getattr(optimizer, "rollouts_prompt_tokens", 0) or 0)
        + (getattr(optimizer, "rollouts_completion_tokens", 0) or 0)
        + (getattr(optimizer, "rollouts_unknown_tokens", 0) or 0)
        + (getattr(optimizer, "mutation_prompt_tokens", 0) or 0)
        + (getattr(optimizer, "mutation_completion_tokens", 0) or 0)
        + (getattr(optimizer, "mutation_unknown_tokens", 0) or 0)
    ),  # ✅ ADD
    # ... existing token fields
}
```

**Fix 2**: Store stats in `job_metadata` (`online_jobs.py:run_job`):
```python
metadata["prompt_best_snapshot_id"] = snapshot_id
metadata["prompt_best_train_score"] = best_score_to_store
metadata["prompt_best_snapshot"] = snapshot_payload

# ✅ ADD: Top-level stats for easy extraction
metadata["stats"] = {
    "trials_tried": snapshot_payload.get("trials_tried", 0),
    "total_trials_evaluated": snapshot_payload.get("total_trials_evaluated", 0),
    "total_rollouts": snapshot_payload.get("total_rollouts", 0),
    "total_tokens": snapshot_payload.get("total_tokens", 0),
    "rollouts_prompt_tokens": snapshot_payload.get("rollouts_prompt_tokens", 0),
    "rollouts_completion_tokens": snapshot_payload.get("rollouts_completion_tokens", 0),
    "rollouts_unknown_tokens": snapshot_payload.get("rollouts_unknown_tokens", 0),
}
```

**Fix 3**: Update `status_json` in experiment queue (`synth_ai/experiment_queue/tasks.py`):
```python
# After job completes, update status_json with final stats
if job.status_json:
    status_json = json.loads(job.status_json) if isinstance(job.status_json, str) else job.status_json
else:
    status_json = {}

# Update with final stats from backend job metadata
backend_job = await fetch_backend_job(job.backend_job_id)
if backend_job:
    backend_metadata = backend_job.get("metadata", {})
    backend_stats = backend_metadata.get("stats", {})
    status_json.update({
        "trials_tried": backend_stats.get("trials_tried"),
        "total_tokens": backend_stats.get("total_tokens"),
        "total_rollouts": backend_stats.get("total_rollouts"),
    })
    # Update job status_json
    await update_job_status_json(job.job_id, status_json)
```

**Why This Approach**:
- Single source of truth: optimizer → snapshot_payload → job_metadata → status_json
- No fallbacks needed: data flows directly
- Easy extraction: script reads from `status_json` or `job_metadata.stats`

---

## Issue 3: Missing Eval Details (Eval N vs Trial N)

### Data Flow Trace

**1. Optimizer (`optimizer.py`)**:
- Optimization rollouts: `_candidate_counter` incremented
- Validation/eval rollouts: No separate counter ❌
- No phase metadata set on rollouts ❌

**2. Evaluation (`core/evaluation.py`)**:
- `evaluate_prompt_template()` / `evaluate_prompt_transformation_with_limits()`:
  - Calls `register_trial_with_metadata()` with `metadata` dict
  - But `metadata` may not include `phase` field ❌

**3. Trial Registration (`core/interceptor_registry.py`)**:
- `register_trial_with_metadata()` accepts `**extra_metadata`
- But `phase` may not be set ❌

**4. Backend (`online_jobs.py:_run_gepa`)**:
- Validation runs happen in `_run_gepa` (lines 1663-1900)
- But validation results stored in `snapshot_payload["validation"]`, NOT tracked as separate trials ❌

**5. Script Extraction (`run_gepa_parallel_experiments.py:extract_results`)**:
- Tries to count trials by `metadata_json.get("phase")` ❌ (phase not set)
- Falls back to backend metadata ❌ (may not exist)

### Root Cause
1. **No phase tagging**: Trials are NOT tagged with `phase` metadata during optimization/evaluation
2. **No separate counters**: No distinction between optimization trials and eval trials in optimizer
3. **Validation not tracked**: Validation runs stored in snapshot but NOT as separate trial records

### Direct Fix

**Fix 1**: Tag trials with phase in `evaluation.py`:
```python
# In evaluate_prompt_template() / evaluate_prompt_transformation_with_limits()
extra_metadata = dict(trial_descriptor.metadata)
extra_metadata.setdefault("iteration", trial_descriptor.iteration)
extra_metadata.setdefault("trial_index", trial_descriptor.trial_index)
extra_metadata["seed"] = seed
extra_metadata["phase"] = "optimization"  # ✅ ADD: Tag optimization trials

await register_trial_with_metadata(
    trial_key=trial_key,
    deltas=trial_descriptor.deltas,
    baseline_messages=trial_descriptor.baselines,
    job_id=trial_descriptor.job_id,
    org_id=org_id,
    provider_config=provider_config,
    **extra_metadata,
)
```

**Fix 2**: Track validation rollouts separately in optimizer (simpler than registering trials):
```python
# In optimizer.py __init__:
self._validation_rollouts_executed: int = 0

# During validation in _run_gepa (lines 1663-1900):
# Track validation rollouts separately
optimizer._validation_rollouts_executed = len(validation_seeds) if validation_seeds else 0

# Expose in snapshot_payload:
payload = {
    "optimization_rollouts_executed": int(getattr(optimizer, "_total_rollouts_executed", 0) or 0),
    "validation_rollouts_executed": int(getattr(optimizer, "_validation_rollouts_executed", 0) or 0),
}
```

**Fix 3**: Track eval counts in optimizer:
```python
# In optimizer.py:
self._optimization_trials_evaluated: int = 0
self._validation_trials_evaluated: int = 0

# During optimization:
self._optimization_trials_evaluated += 1

# During validation:
self._validation_trials_evaluated += 1

# Expose in snapshot_payload:
payload = {
    "optimization_trials_evaluated": self._optimization_trials_evaluated,
    "validation_trials_evaluated": self._validation_trials_evaluated,
}
```

**Why This Approach**:
- Direct tagging: Each trial knows its phase
- Easy counting: Script filters by `phase` field
- No inference needed: Explicit phase, not inferred from context

---

## Issue 4: Model Override Not Reflected in Status JSON

### Data Flow Trace

**1. Script (`run_gepa_parallel_experiments.py:_prepare_experiment_request`)**:
```python
config_overrides["prompt_learning.policy.model"] = model_config["model"]  # ✅ Set correctly
```

**2. Experiment Queue (`synth_ai/experiment_queue/tasks.py`)**:
```python
# Config prepared with overrides ✅
prepared = prepare_config_file(config_path, job.config_overrides)
policy = extract_policy_from_config(prepared.path)  # ✅ Extracted correctly
```

**3. Backend (`online_jobs.py:run_job`)**:
```python
# Policy extracted from prepared config ✅
policy_config = optimizer_config.policy_config
policy_model = policy_config.get("model")  # ✅ Correct
```

**4. Status Tracker (`synth_ai/experiment_queue/status.py`)**:
```python
# status_tracker.update(policy=...) called
# But may use original config, not override ❌
```

**5. Status JSON**:
- May contain wrong model ❌

### Root Cause
`status_tracker.update(policy=...)` is called with model from original config, not from override.

### Direct Fix

**Fix**: Pass override model to status tracker (`synth_ai/experiment_queue/tasks.py`):
```python
# Extract model from override FIRST
model_override = job.config_overrides.get("prompt_learning.policy.model")
provider_override = job.config_overrides.get("prompt_learning.policy.provider")

# Extract from prepared config as fallback
policy = extract_policy_from_config(prepared.path)
provider = extract_provider_from_config(prepared.path)

# Use override if available, otherwise use extracted
final_model = model_override or policy
final_provider = provider_override or provider

# Update status with correct model
status_tracker.update(
    policy=f"{final_provider}/{final_model}",  # ✅ Use override
    # ... other fields
)
```

**Why This Approach**:
- Single source of truth: Override takes precedence
- No config parsing needed: Override already extracted
- Direct: No fallbacks or inference

---

## Issue 5: Archive Items Not Exposed

### Data Flow Trace

**1. Optimizer (`optimizer.py`)**:
- `archive` contains Pareto-optimal solutions
- `archive_summary` created in `_run_gepa` (line 1630)

**2. Backend (`online_jobs.py:_run_gepa`)**:
```python
archive_summary = optimizer.archive.to_summary()  # ✅ Created
payload = {
    "archive": archive_summary,  # ✅ Included in snapshot
}
```

**3. Snapshot Storage**:
- `archive_summary` stored in `snapshot_payload` ✅
- But NOT exposed as separate artifacts ❌

**4. Script Extraction (`run_gepa_parallel_experiments.py:extract_variants`)**:
- Tries to extract from `archive_summary` ✅ (exists)
- But archive items may not have `messages` array ❌

### Root Cause
Archive items are stored as transformations/templates (sections), not messages. Script expects messages.

### Direct Fix

**Fix**: Modify `_summarise_archive()` to include messages (reuses existing serialization logic):
```python
# In online_jobs.py, modify _summarise_archive():
def _summarise_archive(archive: Optional[ParetoArchive]) -> List[Dict[str, Any]]:
    if archive is None:
        return []
    from .core.evaluation import _render_template_messages
    
    out: List[Dict[str, Any]] = []
    for item in archive.items:
        payload = item.get("payload", {})
        obj = payload.get("object")
        
        # Existing serialization logic...
        if isinstance(obj, PromptTemplate):
            obj_repr = {"type": "template", "data": _serialize_prompt_template(obj)}
            # ✅ ADD: Render messages for templates
            messages = _render_template_messages(obj)
        elif isinstance(obj, PromptTransformation):
            obj_repr = {"type": "transformation", "data": _serialize_prompt_transformation(obj)}
            messages = None  # Transformations don't have messages directly
        elif isinstance(obj, PromptPattern):
            obj_repr = {"type": "pattern", "data": _serialize_prompt_pattern(obj)}
            messages = None  # Patterns don't have messages directly
        else:
            obj_repr = {"repr": repr(obj)}
            messages = None
        
        # ... existing trace sanitization ...
        
        out.append({
            "score": item.get("score"),
            "payload_kind": payload.get("kind"),
            "object": obj_repr,
            "trace": safe_trace,
            "instance_scores": payload.get("instance_scores"),
            "messages": messages,  # ✅ ADD: Messages array
        })
    return out
```

**Why This Approach**:
- Reuses existing serialization logic (no duplication)
- Uses `_render_template_messages()` helper (handles variables gracefully)
- Single place to modify (not scattered across codebase)
- Handles all edge cases already (template, transformation, pattern)
- Script can consume messages directly from archive items

---

## Summary of Required Changes

### High Priority (Direct Fixes)

1. **Add `messages` to snapshot payload** (`online_jobs.py:_run_gepa`):
   - Add `best_prompt_messages` field
   - Add `messages` to archive items

2. **Expose trials/tokens in snapshot payload** (`online_jobs.py:_run_gepa`):
   - Add `trials_tried`, `total_trials_evaluated`, `total_tokens` to payload

3. **Store stats in job_metadata** (`online_jobs.py:run_job`):
   - Add `metadata["stats"]` with trials/tokens/rollouts

4. **Tag trials with phase** (`evaluation.py`):
   - Set `phase="optimization"` for optimization trials
   - Track validation rollouts separately (simpler than registering validation trials)

5. **Update status_json with final stats** (`synth_ai/experiment_queue/tasks.py`):
   - Update `status_json` with stats from backend job metadata

### Medium Priority

6. **Use override model in status tracker** (`synth_ai/experiment_queue/tasks.py`):
   - Pass override model to `status_tracker.update()`

7. **Track eval counts separately** (`optimizer.py`):
   - Add `_optimization_trials_evaluated` and `_validation_trials_evaluated`
   - Add `_validation_rollouts_executed` for simpler validation tracking
   - Expose in snapshot payload

---

## Implementation Order

1. **Phase 1**: Fix snapshot payload (messages, trials, tokens)
2. **Phase 2**: Fix job metadata (stats storage)
3. **Phase 3**: Fix trial tagging (phase metadata)
4. **Phase 4**: Fix status_json updates (experiment queue)

---

## Testing Checklist

- [ ] Snapshot payload contains `best_prompt_messages` array
- [ ] Snapshot payload contains `trials_tried`, `total_tokens`
- [ ] Job metadata contains `stats` dict with trials/tokens/rollouts
- [ ] Trials have `phase` field in metadata_json
- [ ] Status JSON contains final stats after job completion
- [ ] Script can extract variants from `best_snapshot.payload.best_prompt_messages`
- [ ] Script can extract variants from archive items with `messages` field
- [ ] Script can extract trials/tokens from `status_json` or `job_metadata.stats`
- [ ] Script can count eval N vs trial N by using `validation_rollouts_executed` vs `optimization_rollouts_executed`

