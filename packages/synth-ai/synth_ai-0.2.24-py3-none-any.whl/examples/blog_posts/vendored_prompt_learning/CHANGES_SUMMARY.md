# Changes Summary: high-fidelity-gepa-dspy vs dev

## Major Changes

### 🎯 New Directory: `vendored_prompt_learning/`
- **Consolidated all GEPA and MIPRO examples** from `blog_posts/gepa/` and `blog_posts/mipro/`
- **54+ files** organized into unified structure:
  - `configs/` - 31 configuration files (all benchmarks)
  - `scripts/` - 22 Python/shell scripts
  - `docs/` - 7 documentation files
  - `results/` - Historical results
- **Two complete pipeline examples**:
  - `run_gepa_example.py` - Full GEPA pipeline (baseline → optimization → final eval)
  - `run_mipro_example.py` - Full MIPRO pipeline (baseline → optimization → final eval)
- **In-process task app scripts** for Banking77:
  - `scripts/run_mipro_in_process.py` - MIPRO with minimal budgets
  - `scripts/run_gepa_banking77_in_process.py` - GEPA with minimal budgets

### 📊 MIPRO Improvements
- **Standardized MIPRO configs** - Consistent structure across all benchmarks
- **Progress streaming** - Real-time status updates during optimization
- **Debug logging** - Enhanced logging for meta_model overrides and rollout extraction
- **Status display improvements**:
  - Better config extraction
  - Recalculated progress_pct
  - Prevent division by tiny elapsed time
- **Config fixes**:
  - Fixed `banking77_mipro_local.toml` to use `llama-3.3-70b-versatile` with Groq
  - Added `val_seeds` to match `reference_pool`

### 🔧 GEPA Improvements
- **HeartDisease benchmarks** - Multiple config variants (dspy, gepa_ai, synth, local)
- **Standalone scripts** - `heartdisease_gepa_standalone.py` for direct execution
- **Baseline evaluation** - `heartdisease_baseline.py` for performance measurement

### 📝 Documentation
- **New docs**:
  - `PROMPT_LEARNING_SDK_CLI.md` - SDK/CLI documentation
  - `SDK_CLI_SUMMARY.md` - Summary of SDK/CLI features
  - `SDK_CLI_TESTING.md` - Testing guide
  - `SUPPORTED_MODELS_PROMPT_LEARNING.md` - Model support matrix
- **Consolidation docs**:
  - `CONSOLIDATION.md` - What was consolidated and why
  - `TEST_RUN.md` - Test run instructions
  - `issues.md` - Known issues and workarounds

### 🧪 Testing & Validation
- **New test files**:
  - `tests/unit/learning/test_gepa_mipro_file_validation.py` (800+ lines)
  - `tests/unit/task/test_in_process.py` (382 lines)
  - Various tunnel and CLI tests
- **Test improvements**:
  - Better validation for GEPA/MIPRO configs
  - In-process task app testing
  - Tunnel health checks

### 🛠️ Infrastructure
- **CI/CD updates** - `.github/workflows/ci.yml` improvements
- **Dependencies** - `uv.lock` updated (922+ changes)
- **Configuration** - `ty.toml` environment section added
- **Utilities** - `cancel_stuck_jobs.py` script added

### 📈 Results & Benchmarks
- **HeartDisease results** - Learning curves and stats for GEPA/MIPRO comparisons
- **Banking77 results** - Updated results with new configs
- **DSPy comparisons** - Detailed results comparing DSPy vs Synth implementations

## Key Features

### Complete Pipeline Examples
- ✅ Baseline evaluation before optimization
- ✅ In-process task app management (automatic Cloudflare tunnels)
- ✅ Programmatic polling with progress updates
- ✅ Final evaluation with optimized prompts
- ✅ All in one script, no external dependencies

### Path Fixes
- ✅ Fixed `.env` loading (uses `parents[4]` to reach repo root)
- ✅ Fixed task app paths (removed duplicate "examples")
- ✅ Fixed config paths (all scripts use `vendored_prompt_learning/configs/`)

### Budget Controls
- ✅ Minimal budget modes for quick testing (~1 minute)
- ✅ Configurable rollout budgets
- ✅ Population size and generation controls

## Statistics

- **Files changed**: 769 files
- **Lines added**: 4,426,155+ (includes large test files and results)
- **Lines removed**: 7,141
- **New directory**: `vendored_prompt_learning/` with 54+ files
- **Commits**: 20+ commits ahead of dev

## Notable Commits

1. `c8decf8` - save
2. `45cd615` - Standardize MIPRO configs and add progress streaming
3. `31df691` - Add debug logging for meta_model overrides
4. `077ba38` - Fix banking77_mipro_local.toml
5. `2c577cd` - Improve MIPRO status display
6. `4d56217` - Fix status display progress calculation
7. `6902591` - Add debug logging for MIPRO rollout extraction

## Breaking Changes

None - all changes are additive or improvements to existing functionality.

## Migration Notes

- Old scripts in `blog_posts/gepa/` and `blog_posts/mipro/` still work
- New consolidated scripts in `vendored_prompt_learning/` are recommended
- All paths updated to use new consolidated structure
- See `CONSOLIDATION.md` for detailed migration guide

