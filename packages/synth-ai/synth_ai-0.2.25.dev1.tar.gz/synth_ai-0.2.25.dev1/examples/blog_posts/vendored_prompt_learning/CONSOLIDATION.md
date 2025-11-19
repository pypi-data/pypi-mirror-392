# Consolidation Notes

This directory consolidates **ALL** prompt learning examples from `blog_posts/gepa/` and `blog_posts/mipro/` into a unified format.

## What Was Consolidated

### From `blog_posts/gepa/`:
- ✅ **All Python scripts** (15 files) → `scripts/`
  - `run_fully_in_process.py`
  - `run_dspy_gepa_heartdisease.py`
  - `run_synth_gepa_heartdisease.py`
  - `heartdisease_gepa_standalone.py`
  - `gepa_baseline.py`
  - `heartdisease_baseline.py`
  - `query_prompts_example.py`
  - `test_proposer_modes.py`
  - `test_proposer_modes_local.py`
  - `check_backend_route.py`
  - `task_apps.py`
  - And more...

- ✅ **All shell scripts** (5 files) → `scripts/`
  - `run_gepa_banking77.sh`
  - `run_gepa_banking77_pipeline.sh`
  - `test_gepa_local.sh`
  - `deploy_banking77_task_app.sh`
  - `verify_banking77_setup.sh`

- ✅ **All configs** (23 files) → `configs/`
  - Banking77 configs (gepa, mipro, pipeline variants)
  - HeartDisease configs (gepa, mipro, dspy, synth variants)
  - HotpotQA configs
  - HoVer configs
  - IFBench configs
  - PUPA configs

- ✅ **All documentation** (5 files) → `docs/`
  - `README.md` (original GEPA README)
  - `HEARTDISEASE_DEMO.md`
  - `PROPOSER_MODES_TEST.md`
  - `RESULTS_SUMMARY.md`

- ✅ **Results** → `results/`
  - Historical results from GEPA experiments

### From `blog_posts/mipro/`:
- ✅ **All Python scripts** (1 file) → `scripts/`
  - `run_mipro_in_process.py`

- ✅ **All shell scripts** (5 files) → `scripts/`
  - `run_mipro_banking77.sh`
  - `run_mipro_banking77_pipeline.sh`
  - `run_mipro_banking77_pipeline_gemini_flash_lite.sh`
  - `run_mipro_banking77_pipeline_gpt41mini.sh`
  - `deploy_banking77_task_app.sh`
  - `deploy_banking77_pipeline_task_app.sh`
  - `verify_banking77_setup.sh`

- ✅ **All configs** (8 files) → `configs/`
  - Banking77 configs (mipro, pipeline variants)
  - `banking77_spec.json`

- ✅ **All documentation** (2 files) → `docs/`
  - `README.md` (original MIPRO README)
  - `multi_step.md`

## Path Updates

All scripts have been updated to use paths relative to `vendored_prompt_learning/`:

- ✅ Config paths: `examples/blog_posts/vendored_prompt_learning/configs/`
- ✅ Script paths: `examples/blog_posts/vendored_prompt_learning/scripts/`
- ✅ Python imports: Updated to use `Path(__file__).parent.parent / "configs"`

## Key Improvements

The new consolidated structure includes:

1. **Complete Pipeline Scripts** (`run_gepa_example.py`, `run_mipro_example.py`):
   - Baseline evaluation
   - In-process task app management
   - Full optimization with polling
   - Final evaluation
   - Everything in one script

2. **Organized Structure**:
   - `configs/` - All configuration files
   - `scripts/` - All Python and shell scripts
   - `docs/` - All documentation
   - `results/` - Historical results

3. **Unified Format**: Both GEPA and MIPRO examples use consistent structure

4. **Updated Paths**: All scripts work from `vendored_prompt_learning/` directory

## Migration Guide

### Old GEPA Scripts:
```bash
cd examples/blog_posts/gepa
python run_fully_in_process.py
```

### New GEPA Scripts:
```bash
cd examples/blog_posts/vendored_prompt_learning
uv run run_gepa_example.py  # Recommended: complete pipeline
# OR
uv run scripts/run_fully_in_process.py  # Original script
```

### Old MIPRO Scripts:
```bash
cd examples/blog_posts/mipro
uv run python run_mipro_in_process.py
```

### New MIPRO Scripts:
```bash
cd examples/blog_posts/vendored_prompt_learning
uv run run_mipro_example.py  # Recommended: complete pipeline
# OR
uv run scripts/run_mipro_in_process.py  # Original script
```

### Config Paths:

**Old:**
```python
config_path = Path(__file__).parent / "configs" / "heartdisease_gepa_local.toml"
```

**New:**
```python
config_path = Path(__file__).parent.parent / "configs" / "heartdisease_gepa_local.toml"
```

## Statistics

- **Total Files Consolidated**: ~70+ files
- **Configs**: 31 files
- **Python Scripts**: 15 files
- **Shell Scripts**: 10 files
- **Documentation**: 7 files
- **Results**: Preserved in `results/`

## What Wasn't Consolidated

The following remain in their original locations (if they exist):
- **Traces**: Database files (`gepa/traces/`) - too large, not needed for examples
- **Backup Files**: `.bak` files - not needed

## Future Work

Consider:
- Adding more benchmark examples
- Creating unified test suite
- Adding CI/CD for example scripts
- Creating video tutorials
