# Data Extraction Issues - Root Cause Analysis

## Overview
This document breaks down the core issues preventing proper extraction of:
- Artifacts (prompt variants/snapshots)
- Trials/Tokens counts
- Eval details (Eval N, Trial N)
- Variants/prompts evaluated

## Issue 1: Missing Artifacts

### Problem
- Backend API returns `has best_snapshot=False, artifacts=0` or `artifacts=1` but no actual snapshot data
- Script shows "No variants found in results" for all tasks
- Debug output: `has best_snapshot=False, artifacts=0` or `artifacts=1` (but no content)

### Root Causes

#### 1.1 Backend Not Storing Snapshots
**Location**: `monorepo/backend/app/routes/prompt_learning/online_jobs.py`

**Issue**: The backend may not be creating/storing snapshots properly:
- `best_snapshot_id` may not be set in job metadata
- Snapshots may not be saved to `prompt_learning_snapshots` table
- Artifacts may not be linked to jobs in `prompt_learning_artifacts` table

**Evidence**:
- Debug output: `has best_snapshot=False`
- Backend job data shows `artifacts=1` but no snapshot content

**Investigation Needed**:
- Check if `job_service.create_snapshot()` is being called
- Verify snapshot is saved with correct `job_id`
- Check if `best_snapshot_id` is set in job metadata after optimization completes

#### 1.2 Artifacts API Endpoint Not Returning Data
**Location**: `monorepo/backend/app/routes/prompt_learning/routes_online.py`

**Issue**: The `/api/prompt-learning/online/jobs/{job_id}/artifacts` endpoint may:
- Not be querying the correct tables
- Not be joining snapshots with artifacts correctly
- Returning empty arrays even when data exists

**Investigation Needed**:
- Verify artifacts endpoint queries `prompt_learning_artifacts` table
- Check if artifacts are linked to snapshots via `snapshot_id`
- Verify PostgREST permissions allow reading artifacts

#### 1.3 Script Not Fetching Snapshot Details
**Location**: `synth-ai/examples/blog_posts/langprobe/comparisons/run_gepa_parallel_experiments.py`

**Issue**: `fetch_backend_job_details()` gets `best_snapshot_id` but doesn't fetch the actual snapshot:
- Only gets `best_snapshot` from job metadata (may be None)
- Doesn't fetch snapshot details from `/api/prompt-learning/online/jobs/{job_id}/snapshots/{snapshot_id}`
- Doesn't fetch all snapshots for the job

**Investigation Needed**:
- Check if snapshot endpoint exists: `/api/prompt-learning/online/jobs/{job_id}/snapshots/{snapshot_id}`
- Verify snapshot payload includes `messages` array with prompt content
- Add logic to fetch snapshot details when `best_snapshot_id` is present
- Check `job_service.get_prompt_snapshot()` implementation
- Verify snapshot is saved with correct `job_id` foreign key

---

## Issue 2: Missing Trials/Tokens

### Problem
- `Trials: N/A` in aggregate table
- `Tokens: N/A` in aggregate table
- Script shows `TOTAL: 0 trials, 0 tokens`

### Root Causes

#### 2.1 Status JSON Not Populated
**Location**: `synth-ai/synth_ai/experiment_queue/status.py`

**Issue**: `ExperimentStatusTracker.update()` may not be storing:
- `trials_tried` count
- `total_tokens` or `rollout_tokens_used`
- Token breakdowns

**Evidence**:
- `status_json` may only have `rollouts_completed` but not `trials_tried`
- Token counts may not be tracked at all

**Investigation Needed**:
- Check what `status_tracker.update()` accepts and stores
- Verify tokens are tracked during rollouts
- Check if trial counts are incremented correctly

#### 2.2 Backend Not Emitting Trial/Token Metrics
**Location**: `monorepo/backend/app/routes/prompt_learning/online_jobs.py`

**Issue**: Progress events may not include:
- `trials_tried` in progress event data
- `total_tokens` or `rollout_tokens_used` in progress event data
- Token tracking may not be implemented

**Evidence**:
- Progress events show `rollouts_total` but not `trials_tried`
- Token fields may be missing from progress event `data` dict

**Investigation Needed**:
- Check `_emit_metric()` callback for GEPA
- Verify token tracking in `GEPAOptimizer._track_rollout_cost()`
- Check if trial counts are tracked in optimizer state

#### 2.3 Result Summary Not Including Stats
**Location**: `synth-ai/synth_ai/experiment_queue/tasks.py`

**Issue**: `ResultSummary` may not be populated with:
- `stats.trials_tried`
- `stats.total_tokens`
- Token breakdowns

**Evidence**:
- `job.result` may be empty or missing `stats` dict
- Stats may not be extracted from optimizer state

**Investigation Needed**:
- Check how `ResultSummary` is created from optimizer results
- Verify optimizer exposes trial/token counts
- Check if stats are serialized correctly

#### 2.4 Database Trials Not Counted Correctly
**Location**: `synth-ai/examples/blog_posts/langprobe/comparisons/run_gepa_parallel_experiments.py`

**Issue**: Script tries to count trials from DB but:
- Trials may not have `phase` metadata to distinguish eval vs optimization
- Trial counting logic may be incorrect
- Token summing from trial metadata may fail

**Evidence**:
- Debug output shows trial counting attempts but results in `N/A`
- Trial metadata may not have `tokens` field

**Investigation Needed**:
- Query DB to see actual trial structure
- Check if trials have `metadata_json` with `phase` and `tokens`
- Verify trial counting logic matches actual data structure

---

## Issue 3: Missing Eval Details (Eval N, Trial N)

### Problem
- `Eval N: N/A` in aggregate table
- `Trials: N/A` in aggregate table
- Cannot distinguish between optimization trials and evaluation runs

### Root Causes

#### 3.1 No Phase Metadata in Trials
**Location**: `monorepo/backend/app/routes/prompt_learning/core/evaluation.py`

**Issue**: Trials may not be tagged with `phase` metadata:
- Optimization rollouts don't set `phase="optimization"`
- Evaluation rollouts don't set `phase="validation_baseline"` or `phase="eval"`
- Script can't distinguish eval vs optimization from DB alone

**Evidence**:
- Debug output: `Sample trial metadata phase: None` or missing
- Script tries to filter by phase but finds none

**Investigation Needed**:
- Check where trials are created in evaluation layer
- Verify `extra_metadata` includes `phase` field
- Check if `register_trial_with_metadata()` sets phase correctly

#### 3.2 Backend Not Tracking Eval vs Optimization Separately
**Location**: `monorepo/backend/app/routes/prompt_learning/online_jobs.py`

**Issue**: Backend may not distinguish:
- Optimization trials (pattern evaluations during search)
- Evaluation runs (final validation on best candidates)
- Both may be counted as "rollouts" but serve different purposes

**Evidence**:
- Progress events show `rollouts_total` but not `eval_n` or `trials_tried`
- Backend metadata may not have `stats.eval_n` or `stats.trials_tried`

**Investigation Needed**:
- Check if backend tracks eval runs separately from optimization rollouts
- Verify optimizer exposes eval vs optimization counts
- Check if final evaluation runs are tracked differently

#### 3.3 Script Can't Infer Eval N from Config
**Location**: `synth-ai/examples/blog_posts/langprobe/comparisons/run_gepa_parallel_experiments.py`

**Issue**: Script tries to get `eval_seeds_n` from config but:
- Config may not have `gepa.evaluation.seeds` or `gepa.evaluation.validation_seeds`
- Config structure may be different than expected
- Overrides may have changed config structure

**Evidence**:
- Script attempts config parsing but may fail silently
- Config may use different field names

**Investigation Needed**:
- Verify config structure matches script expectations
- Check if overrides affect config parsing
- Add better error handling for config parsing

---

## Issue 4: No Variants/Prompts Extracted

### Problem
- "No variants found in results" for all tasks
- Cannot see what prompts were actually evaluated
- Cannot sort variants by score

### Root Causes

#### 4.1 Backend Not Returning Snapshot Content
**Location**: `monorepo/backend/app/routes/prompt_learning/routes_online.py`

**Issue**: Snapshot endpoints may not return:
- `messages` array with prompt content
- Full prompt template/pattern structure
- Score information linked to snapshots

**Evidence**:
- `best_snapshot` from job metadata may be None or empty
- Snapshot API may not include `messages` field

**Investigation Needed**:
- Check snapshot schema in `prompt_learning_snapshots` table
- Verify snapshot payload includes `messages` or `payload.messages`
- Check if snapshot includes score/token_count

#### 4.2 Learning Curve Not Storing Prompt Content
**Location**: `monorepo/backend/app/routes/prompt_learning/online_jobs.py`

**Issue**: Learning curve points may not include:
- Full prompt template/transformation in metadata
- Only scores, not the actual prompts evaluated
- Metadata may be truncated or missing

**Evidence**:
- Script tries to extract from `learning_curve[].metadata.template` but finds nothing
- Learning curve may only store scores, not prompts

**Investigation Needed**:
- Check what `learning_curve` actually contains
- Verify if prompts are stored in curve metadata
- Check if metadata is being serialized correctly

#### 4.3 Archive Not Exposed via API
**Location**: `monorepo/backend/app/routes/prompt_learning/algorithm/gepa/optimizer.py`

**Issue**: GEPA optimizer has `archive` with best candidates but:
- Archive may not be exposed via API endpoints
- Archive items may not be saved as snapshots
- Archive may only exist in memory during optimization

**Evidence**:
- Optimizer has `self.archive` with Pareto-optimal solutions
- But archive may not be persisted or exposed

**Investigation Needed**:
- Check if archive is saved to database
- Verify if archive items are converted to snapshots
- Check if archive endpoint exists

---

## Issue 5: Model Override Not Reflected

### Problem
- Heart Disease shows `llama-3.1-8b-instant` instead of `openai/gpt-oss-20b`
- Policy model in results doesn't match override

### Root Causes

#### 5.1 Status JSON Uses Wrong Model
**Location**: `synth-ai/synth_ai/experiment_queue/status.py`

**Issue**: `status_tracker.update(policy=...)` may be:
- Called with wrong model (from config, not override)
- Called before override is applied
- Not updated when override changes

**Evidence**:
- Status shows `Policy: llama-3.1-8b-instant` for Heart Disease
- But override specifies `openai/gpt-oss-20b`

**Investigation Needed**:
- Check when `status_tracker.update(policy=...)` is called
- Verify policy is extracted from prepared config (with overrides)
- Check if policy is updated correctly

#### 5.2 Result Extraction Uses Wrong Source
**Location**: `synth-ai/examples/blog_posts/langprobe/comparisons/run_gepa_parallel_experiments.py`

**Issue**: Script extracts policy_model from:
- Stats/artifacts (may be wrong or missing)
- Config file (original, not overridden) - **THIS IS THE PROBLEM**
- **NOT from `config_overrides`** - override is stored in DB but ignored

**Evidence**:
- Aggregate table shows wrong model (Heart Disease shows `llama-3.1-8b-instant` instead of `openai/gpt-oss-20b`)
- But override was set correctly in `job.config_overrides`
- Script reads from original config file, ignoring override

**Fix Applied**:
- ✅ Added logic to check `job.config_overrides.get("prompt_learning.policy.model")` FIRST
- ✅ Fallback to config file only if override not found
- ✅ Added debug logging to show which source was used

**Investigation Needed**:
- Verify fix works correctly
- Check if status_json should also be updated with override value
- Consider storing override value in status_json when job starts

---

## Database Schema Analysis

### Experiment Queue DB (SQLite)
**Table: `experiment_jobs`**
- `status_json`: TEXT (JSON) - Stores progress updates
- `result`: JSON - Stores final result summary
- `backend_job_id`: VARCHAR(128) - Links to backend job

**Table: `trials`**
- `metadata_json`: JSON - Stores trial metadata (may be empty `{}`)
- `status`: VARCHAR - Trial status (completed, failed, etc.)
- No `phase` field - Must be in `metadata_json`

### Backend DB (Postgres)
**Table: `prompt_learning_online_jobs`**
- `best_snapshot_id`: UUID - Reference to best snapshot
- `metadata`: JSONB - Job metadata including stats

**Table: `prompt_learning_snapshots`**
- `payload`: JSONB - Snapshot payload (should contain `messages`)
- `score`: FLOAT - Snapshot score
- `job_id`: UUID - Foreign key to job

**Table: `prompt_learning_artifacts`**
- `snapshot_id`: UUID - Reference to snapshot
- `label`: TEXT - Artifact label
- `job_id`: UUID - Foreign key to job

## Summary of Required Fixes

**See `DATA_FLOW_ANALYSIS.md` for detailed implementation proposals.**

### High Priority (Direct Fixes - No Fallbacks)
1. **Add `messages` to snapshot payload** (`online_jobs.py:_run_gepa`):
   - Add `best_prompt_messages` field to snapshot payload
   - Add `messages` array to archive items

2. **Expose trials/tokens in snapshot payload** (`online_jobs.py:_run_gepa`):
   - Add `trials_tried`, `total_trials_evaluated`, `total_tokens` to payload

3. **Store stats in job_metadata** (`online_jobs.py:run_job`):
   - Add `metadata["stats"]` dict with trials/tokens/rollouts

4. **Tag trials with phase** (`evaluation.py`):
   - Set `phase="optimization"` for optimization trials
   - Set `phase="validation"` for validation trials

5. **Update status_json with final stats** (`synth_ai/experiment_queue/tasks.py`):
   - Update `status_json` with stats from backend job metadata after completion

### Medium Priority
6. **Use override model in status tracker** (`synth_ai/experiment_queue/tasks.py`):
   - Pass override model to `status_tracker.update()` instead of original config

7. **Track eval counts separately** (`optimizer.py`):
   - Add `_optimization_trials_evaluated` and `_validation_trials_evaluated`
   - Expose in snapshot payload

### Implementation Notes
- **No fallbacks**: All fixes are direct data flow improvements
- **Single source of truth**: Optimizer → snapshot_payload → job_metadata → status_json
- **Explicit tagging**: Trials tagged with `phase`, not inferred
- **Complete payloads**: Snapshot payloads include all needed fields (messages, stats, etc.)

---

## Next Steps

1. **Query Backend DB**: Directly query Postgres to see what's actually stored
2. **Add Debug Logging**: Add extensive logging to trace data flow
3. **Fix One Issue at a Time**: Start with snapshots (most critical)
4. **Add Integration Tests**: Test data extraction end-to-end
5. **Update Script**: Fix extraction logic once backend issues are resolved

