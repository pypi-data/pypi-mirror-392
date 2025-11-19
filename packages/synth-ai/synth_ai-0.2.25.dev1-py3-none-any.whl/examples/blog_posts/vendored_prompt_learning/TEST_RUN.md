# Test Run Instructions

Both scripts are ready to run with small budgets for quick testing.

## Prerequisites

Make sure you have these environment variables set in `.env`:

```bash
GROQ_API_KEY=your_groq_key          # Required for both
OPENAI_API_KEY=your_openai_key      # Required for MIPRO (meta-model)
SYNTH_API_KEY=test                  # Backend API key
ENVIRONMENT_API_KEY=test            # Task app authentication
BACKEND_BASE_URL=http://localhost:8000  # Backend URL
```

Also ensure the backend is running:
```bash
# In another terminal
cd /path/to/monorepo/backend
# Start backend (depends on your setup)
```

## Test Run 1: MIPRO Banking77

**Small Budget**: 2 iterations × 2 evaluations = ~4-8 rollouts

```bash
cd examples/blog_posts/vendored_prompt_learning
uv run scripts/run_mipro_in_process.py
```

**What it does**:
- Starts Banking77 task app in-process with Cloudflare tunnel
- Runs MIPRO optimization with reduced budget (2 iterations)
- Polls for completion
- Shows results

**Expected time**: ~5-10 minutes with small budget

## Test Run 2: GEPA Banking77

**Small Budget**: 20 rollouts, population size 3, 2 generations

```bash
cd examples/blog_posts/vendored_prompt_learning
uv run scripts/run_gepa_banking77_in_process.py
```

**What it does**:
- Starts Banking77 task app in-process with Cloudflare tunnel
- Runs GEPA optimization with reduced budget (20 rollouts)
- Polls for completion
- Shows results

**Expected time**: ~5-15 minutes with small budget

## What to Expect

Both scripts will:
1. ✅ Check for required environment variables
2. ✅ Start task app in-process (with Cloudflare tunnel)
3. ✅ Load and modify config (reducing budgets)
4. ✅ Submit optimization job to backend
5. ✅ Poll for completion with progress updates
6. ✅ Display final results (best score, candidates evaluated)

## Troubleshooting

### "GROQ_API_KEY required"
- Add `GROQ_API_KEY=your_key` to `.env` file in repo root

### "OPENAI_API_KEY required" (MIPRO only)
- Add `OPENAI_API_KEY=your_key` to `.env` file

### "Backend connection error"
- Make sure backend is running on `localhost:8000`
- Check `BACKEND_BASE_URL` environment variable

### "Task app not found"
- Make sure `examples/task_apps/banking77/banking77_task_app.py` exists
- Check that you're running from the correct directory

### "Config file not found"
- Make sure you're running from `vendored_prompt_learning/` directory
- Check that `configs/banking77_*.toml` files exist

## Success Indicators

You'll know it's working when you see:
- ✅ Task app running at: `https://...trycloudflare.com`
- ✅ Job submitted: `job_...`
- Status updates every 10 seconds showing progress
- Final results with best score

## Next Steps

Once these work, you can:
- Increase budgets in the scripts for full runs
- Try other benchmarks (HeartDisease, HotpotQA, etc.)
- Use the complete pipeline scripts (`run_gepa_example.py`, `run_mipro_example.py`)

