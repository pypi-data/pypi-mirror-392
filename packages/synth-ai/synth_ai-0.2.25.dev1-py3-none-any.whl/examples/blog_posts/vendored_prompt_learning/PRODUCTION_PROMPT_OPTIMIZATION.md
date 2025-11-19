# Production Prompt Optimization with Synth AI

## Overview

The `vendored_prompt_learning` directory provides **production-ready examples** for optimizing prompts on the fly using Synth AI's GEPA and MIPRO algorithms. These examples demonstrate how to integrate prompt optimization directly into your production workflows.

## Use Case: Prompt Optimization on the Fly

### What It's For

**Optimize prompts dynamically in production** without manual intervention:

- **A/B Testing**: Automatically find better prompts for your use case
- **Performance Tuning**: Continuously improve prompt performance as your data changes
- **Multi-Tenant Optimization**: Optimize prompts per customer or use case
- **Rapid Iteration**: Test and deploy better prompts faster than manual tuning

### Key Benefits

✅ **Automated**: No manual prompt engineering required  
✅ **Production-Ready**: In-process task apps with automatic tunnel management  
✅ **Fast**: Minimal budgets for quick testing (~1 minute)  
✅ **Complete Pipeline**: Baseline → Optimization → Final Evaluation  
✅ **Self-Contained**: Everything in one script, no external dependencies  

## Quick Start

### Prerequisites

```bash
# Environment variables (.env file)
GROQ_API_KEY=your_groq_key          # For policy model
OPENAI_API_KEY=your_openai_key      # For meta-model (MIPRO) and mutation LLM (GEPA)
SYNTH_API_KEY=your_synth_key        # Backend API key
ENVIRONMENT_API_KEY=your_env_key    # Task app authentication
BACKEND_BASE_URL=http://localhost:8000  # Backend URL
```

### Example 1: GEPA Optimization

```bash
cd examples/blog_posts/vendored_prompt_learning
uv run run_gepa_example.py
```

**What it does:**
1. Evaluates baseline prompt performance
2. Starts task app in-process (automatic Cloudflare tunnel)
3. Runs GEPA optimization with programmatic polling
4. Retrieves best prompts
5. Evaluates final performance

**Output:**
```
Baseline Accuracy: 54.00%
Final Accuracy:    75.00%
Improvement:       +21.00%
```

### Example 2: MIPRO Optimization

```bash
cd examples/blog_posts/vendored_prompt_learning
uv run run_mipro_example.py
```

**What it does:**
1. Evaluates baseline prompt performance
2. Starts task app in-process (automatic Cloudflare tunnel)
3. Runs MIPRO optimization with programmatic polling
4. Retrieves best prompts
5. Evaluates final performance

## Architecture

### In-Process Task App

The examples use `InProcessTaskApp` which automatically:

- Starts FastAPI server in background thread
- Opens Cloudflare tunnel (production) or uses localhost (dev)
- Provides tunnel URL for optimization jobs
- Cleans up everything on exit

```python
from synth_ai.task import InProcessTaskApp
from task_app import build_config

async with InProcessTaskApp(
    config_factory=build_config,
    port=8114,
    tunnel_mode="quick",  # or "local" for dev
) as task_app:
    # Use task_app.url for your optimization jobs
    print(f"Task app running at: {task_app.url}")
```

### Optimization Flow

```
Your Script
    ↓
1. Evaluate Baseline
    ↓
2. Start Task App (In-Process)
    ↓
3. Submit Optimization Job
    ↓
4. Poll for Completion
    ↓
5. Retrieve Best Prompts
    ↓
6. Evaluate Final Performance
```

## Production Integration

### Step 1: Define Your Task App

Create a task app that evaluates prompts on your data:

```python
# task_app.py
from synth_ai.task.apps import TaskAppConfig

def build_config() -> TaskAppConfig:
    # Your task app configuration
    return TaskAppConfig(
        app_id="your_task",
        rollout=your_rollout_executor,
        # ... other config
    )
```

### Step 2: Run Optimization

```python
# optimize_prompts.py
from synth_ai.task import InProcessTaskApp
from synth_ai.api.train.prompt_learning import PromptLearningJob
from task_app import build_config

async def optimize_prompts():
    async with InProcessTaskApp(
        config_factory=build_config,
        port=8114,
    ) as task_app:
        # Create optimization job
        job = PromptLearningJob.from_config(
            config_path="configs/your_task_gepa.toml",
            backend_url="http://localhost:8000",
            api_key=os.getenv("SYNTH_API_KEY"),
            task_app_api_key=os.getenv("ENVIRONMENT_API_KEY"),
        )
        
        # Submit and wait for completion
        job_id = job.submit()
        result = job.poll_until_complete(timeout=3600.0)
        
        # Get best prompts
        from synth_ai.learning.prompt_learning_client import PromptLearningClient
        client = PromptLearningClient(backend_url, api_key)
        prompts = await client.get_prompts(job_id)
        
        print(f"Best score: {prompts.best_score:.2%}")
        return prompts.best_prompt
```

### Step 3: Use Optimized Prompts

```python
# Use the optimized prompt in your application
best_prompt = await optimize_prompts()

# Apply to your LLM calls
messages = best_prompt.to_messages(your_data)
response = await llm.chat(messages)
```

## Configuration

### Minimal Budget (Quick Testing)

For fast testing (~1 minute):

```toml
[prompt_learning.gepa.rollout]
budget = 5  # Minimal rollouts

[prompt_learning.gepa.population]
initial_size = 2
num_generations = 1
```

```toml
[prompt_learning.mipro]
num_iterations = 1
num_evaluations_per_iteration = 1
```

### Production Budget

For real optimization:

```toml
[prompt_learning.gepa.rollout]
budget = 200  # More rollouts for better results

[prompt_learning.gepa.population]
initial_size = 10
num_generations = 10
```

```toml
[prompt_learning.mipro]
num_iterations = 10
num_evaluations_per_iteration = 4
```

## Available Examples

### Complete Pipeline Examples

- **`run_gepa_example.py`** - Full GEPA pipeline (recommended)
- **`run_mipro_example.py`** - Full MIPRO pipeline (recommended)

### In-Process Scripts

- **`scripts/run_mipro_in_process.py`** - MIPRO Banking77 (minimal budget)
- **`scripts/run_gepa_banking77_in_process.py`** - GEPA Banking77 (minimal budget)

### Other Scripts

All original scripts from `blog_posts/gepa/` and `blog_posts/mipro/` are available in `scripts/`:
- Baseline evaluation scripts
- Deployment scripts
- Test scripts
- Benchmark-specific scripts

## Benchmarks

### HeartDisease (Medical Classification)
- **Task**: Classify patients as having heart disease (1) or not (0)
- **Baseline**: ~54% accuracy
- **Optimized**: ~75% accuracy (+21% improvement)
- **Configs**: `configs/heartdisease_*.toml`

### Banking77 (Intent Classification)
- **Task**: Classify customer queries into 77 banking intents
- **Configs**: `configs/banking77_*.toml`
- **Scripts**: `scripts/run_*banking77*.py`

### Other Benchmarks
- HotpotQA (Multi-hop QA)
- IFBench (Instruction following)
- HoVer (Claim verification)
- PUPA (Privacy-aware delegation)

See `configs/` for all available benchmark configurations.

## Production Considerations

### Tunnel Management

**Production:**
```python
tunnel_mode="quick"  # Cloudflare tunnel (default)
```

**Development:**
```python
tunnel_mode="local"  # Localhost only
SYNTH_TUNNEL_MODE=local uv run run_gepa_example.py
```

### Error Handling

```python
try:
    result = job.poll_until_complete(timeout=3600.0)
except Exception as e:
    # Handle errors
    logger.error(f"Optimization failed: {e}")
    # Fall back to baseline prompt
```

### Monitoring

```python
def on_status(status):
    # Log progress
    logger.info(f"Status: {status['status']}, Progress: {status.get('progress', {})}")
    # Send metrics to your monitoring system
    metrics.gauge("prompt_optimization.progress", status.get("progress_pct", 0))

job.poll_until_complete(
    timeout=3600.0,
    interval=5.0,
    on_status=on_status,  # Progress callback
)
```

### Cost Management

- **Minimal budgets** for testing: 5-20 rollouts
- **Production budgets**: 200-400 rollouts
- **Monitor costs** via backend API
- **Set timeouts** to prevent runaway jobs

## Troubleshooting

See `issues.md` for known issues and solutions.

### Common Issues

1. **Backend not accessible**
   - Ensure backend is running on `localhost:8000`
   - Or set `BACKEND_BASE_URL` environment variable

2. **Task app not starting**
   - Check port availability (default: 8114)
   - Verify `ENVIRONMENT_API_KEY` is set

3. **Tunnel issues**
   - Use `SYNTH_TUNNEL_MODE=local` for development
   - Check firewall/network settings for production

## Next Steps

1. **Try the examples**: Run `run_gepa_example.py` or `run_mipro_example.py`
2. **Customize for your task**: Create your own task app and config
3. **Integrate into production**: Use the patterns in your application
4. **Monitor results**: Track improvements over time

## References

- [README.md](README.md) - Complete guide
- [CONSOLIDATION.md](CONSOLIDATION.md) - What was consolidated
- [TEST_RUN.md](TEST_RUN.md) - Test run instructions
- [issues.md](issues.md) - Known issues

