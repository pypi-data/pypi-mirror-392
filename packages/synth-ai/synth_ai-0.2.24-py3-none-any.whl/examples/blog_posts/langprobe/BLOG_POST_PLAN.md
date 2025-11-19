# Blog Post Plan: Comparing Prompt Optimization Frameworks

## Title

**"Benchmarking Prompt Optimization: Synth AI vs GEPA-AI vs DSPy"**

Alternative titles:
- "A Comprehensive Comparison of Prompt Optimization Frameworks"
- "Which Prompt Optimizer Works Best? Data-Driven Analysis Across 4 Benchmarks"
- "Prompt Optimization Showdown: Synth AI, GEPA-AI, and DSPy Head-to-Head"

## Target Audience

- ML engineers evaluating prompt optimization tools
- Researchers comparing optimization algorithms
- Practitioners looking for production-ready solutions

## Structure

### 1. Introduction (300 words)

**Hook**: With multiple prompt optimization frameworks available, which one should you use?

**Key Points**:
- Prompt optimization is critical for LLM applications
- Multiple frameworks exist: Synth AI (GEPA/MIPRO), GEPA-AI, DSPy
- Need data-driven comparison across real benchmarks
- This post provides comprehensive evaluation

**Value Proposition**:
- Empirical results from 4 diverse benchmarks
- Fair comparison with same prompts, models, and budgets
- Clear recommendations based on performance
- Production-ready examples

### 2. The LangProbe Benchmark Suite (500 words)

#### 2.1 What is LangProbe?

LangProbe is a standardized benchmark suite for evaluating prompt optimization algorithms across diverse task types.

**Design Philosophy**:
- **Unified Interface**: Each benchmark has adapters for all frameworks
- **Fair Comparison**: Same prompts, models, and evaluation metrics
- **Diverse Tasks**: Classification, QA, reasoning, multi-step
- **Production-Ready**: Real-world task apps with proper evaluation

#### 2.2 Benchmark Tasks

**Banking77** (Intent Classification)
- **Task**: Classify customer queries into 77 banking intents
- **Dataset**: HuggingFace Banking77
- **Baseline**: ~49-87% accuracy (varies by model)
- **Why it matters**: Real-world customer service use case
- **Complexity**: High (77 classes, nuanced intents)

**HeartDisease** (Medical Classification)
- **Task**: Classify patients as having heart disease (1) or not (0)
- **Dataset**: `buio/heart-disease` from HuggingFace
- **Baseline**: ~48-54% accuracy
- **Why it matters**: Medical decision-making, high-stakes classification
- **Complexity**: Medium (binary classification, structured features)

**HotpotQA** (Multi-hop Question Answering)
- **Task**: Answer questions requiring reasoning across multiple documents
- **Dataset**: HotpotQA
- **Baseline**: ~0-79% accuracy (varies by model)
- **Why it matters**: Tests reasoning and information synthesis
- **Complexity**: High (multi-step reasoning, document retrieval)

**Pupa** (Privacy-aware Task Delegation)
- **Task**: Delegate tasks while preserving privacy constraints
- **Dataset**: PUPA benchmark
- **Baseline**: ~35-56% accuracy
- **Why it matters**: Privacy-preserving AI applications
- **Complexity**: High (constraint satisfaction, privacy rules)

#### 2.3 Benchmark Setup Architecture

**Unified Adapter Pattern**:
```
Benchmark Task
    ↓
Task App (FastAPI)
    ↓
Adapter Layer
    ├── DSPy Adapter (dspy_banking77_adapter.py)
    ├── GEPA-AI Adapter (gepa_ai_banking77_adapter.py)
    └── Synth Adapter (synth_banking77_adapter.py)
    ↓
Optimizer
    ├── DSPy GEPA/MIPRO
    ├── GEPA-AI Library
    └── Synth AI (GEPA/MIPRO)
```

**Key Components**:
- **Task Apps**: FastAPI apps that evaluate prompts on real data
- **Adapters**: Framework-specific wrappers that convert between formats
- **Configs**: YAML/TOML files defining optimization parameters
- **Evaluation**: Standardized metrics (accuracy, F1, etc.)

### 3. The Frameworks Compared (400 words)

#### 3.1 Synth AI

**GEPA (Genetic Evolution for Prompt Architectures)**:
- Population-based genetic algorithm
- LLM-guided mutations and crossovers
- Pareto optimization (performance vs. prompt length)
- Pattern transformations

**MIPRO (Meta-Instruction PROposer)**:
- Meta-LLM generates instruction variants
- TPE (Tree-structured Parzen Estimator) guides search
- Few-shot learning for demonstrations
- Multi-stage pipeline support

**Key Features**:
- Production-ready backend API
- In-process task apps with Cloudflare tunnels
- Programmatic polling and progress tracking
- Interceptor pattern (no prompts sent to task apps)

#### 3.2 GEPA-AI

**Library**: Python package for genetic prompt optimization

**Approach**:
- Genetic algorithm similar to Synth GEPA
- Local execution (no backend)
- Direct integration with task code

**Use Cases**:
- Research and experimentation
- Local development
- Custom optimization pipelines

#### 3.3 DSPy

**Framework**: Stanford's framework for building LLM applications

**Optimizers**:
- **GEPA**: Genetic evolution optimizer
- **MIPROv2**: Meta-learning optimizer

**Approach**:
- Module-based architecture
- Reflection and self-improvement
- Few-shot learning

**Use Cases**:
- Research and prototyping
- Academic comparisons
- Module-based LLM applications

### 4. Experimental Setup (300 words)

#### 4.1 Fair Comparison Methodology

**Controlled Variables**:
- ✅ Same initial prompts (baseline)
- ✅ Same models (Groq/OpenAI)
- ✅ Same evaluation seeds
- ✅ Same rollout budgets
- ✅ Same task apps

**Varied Variables**:
- Optimization algorithm (GEPA vs MIPRO)
- Framework implementation (Synth vs GEPA-AI vs DSPy)
- Proposer mode (DSPy vs GEPA-AI vs Synth)

#### 4.2 Configuration

**Rollout Budgets**:
- Banking77: 500 rollouts
- HeartDisease: 500 rollouts
- HotpotQA: 100 rollouts
- Pupa: 300 rollouts

**Models**:
- Banking77: `llama-3.1-8b-instant` (Groq)
- HeartDisease: `openai/gpt-oss-20b` (Groq)
- HotpotQA: `llama-3.3-70b-versatile` (Groq)
- Pupa: `openai/gpt-oss-120b` (Groq)

**Evaluation**:
- Training seeds: Task-specific (20-30 examples)
- Validation seeds: Held-out sets (50-200 examples)
- Metrics: Accuracy, F1 score, task-specific metrics

### 5. Results Analysis (800 words)

#### 5.1 Overall Performance

**Library Reference Experiments** (GEPA-AI vs DSPy):

```
Optimizer            Avg Gain (Δ)       Avg Final Score    Count     
--------------------------------------------------------------------
GEPA-AI              +0.1461           0.7550           4         
DSPy                 +0.2394           0.4742           4         
```

**Key Findings**:
- GEPA-AI achieves higher final scores (75.5% vs 47.4%)
- DSPy shows larger average gains but from lower baselines
- GEPA-AI more consistent across benchmarks

#### 5.2 Benchmark-by-Benchmark Results

**Banking77**:
- **Baseline**: 49-87% (varies by model)
- **GEPA-AI**: 95% (+26.7% lift)
- **DSPy**: 49% (+0% lift)
- **Synth GEPA**: 100% (+13% lift)
- **Winner**: Synth GEPA (perfect score!)

**HeartDisease**:
- **Baseline**: 48-54%
- **GEPA-AI**: 76% (+58.3% lift)
- **DSPy**: 38% (+38% lift)
- **Synth GEPA**: 75% (+21% lift)
- **Synth MIPRO**: 75% (+21% lift)
- **Winner**: GEPA-AI (highest absolute score)

**HotpotQA**:
- **Baseline**: 0-79%
- **GEPA-AI**: 75% (+15.4% lift)
- **DSPy**: 52% (+52% lift from 0% baseline)
- **Synth GEPA**: 89% (+11% lift)
- **Winner**: Synth GEPA (highest final score)

**Pupa**:
- **Baseline**: 35-56%
- **GEPA-AI**: 56% (+0.8% lift)
- **DSPy**: 51% (+13.6% lift)
- **Synth MIPRO**: 56% (+21% lift)
- **Winner**: Synth MIPRO (best improvement)

#### 5.3 Synth AI Performance

**GEPA Results**:
- Average lift: +7.34% across benchmarks
- Best performance: Banking77 (100% accuracy)
- Consistent improvements across all tasks

**MIPRO Results**:
- Average lift: +11.30% across benchmarks
- Best improvement: Pupa (+21.22%)
- 75% of experiments show positive lift
- Average time: 51 seconds (very fast!)

**Key Advantages**:
- ✅ Production-ready (backend API, task apps)
- ✅ Fast optimization (minutes vs hours)
- ✅ Consistent improvements
- ✅ Easy integration

#### 5.4 Framework Comparison

**Synth AI vs GEPA-AI**:
- **Performance**: Comparable (Synth slightly better on some tasks)
- **Production**: Synth AI wins (backend, APIs, task apps)
- **Ease of Use**: Synth AI wins (in-process task apps, automatic tunnels)
- **Speed**: Synth AI wins (optimized backend)

**Synth AI vs DSPy**:
- **Performance**: Synth AI wins (higher final scores)
- **Production**: Synth AI wins (production-ready infrastructure)
- **Research**: DSPy wins (more flexible, module-based)
- **Speed**: Synth AI wins (faster optimization)

### 6. Key Insights (400 words)

#### 6.1 When to Use Each Framework

**Use Synth AI When**:
- ✅ You need production-ready optimization
- ✅ You want fast results (minutes, not hours)
- ✅ You need automatic task app management
- ✅ You want consistent improvements
- ✅ You're building production LLM applications

**Use GEPA-AI When**:
- ✅ You're doing research/experimentation
- ✅ You need local execution
- ✅ You want direct code integration
- ✅ You're prototyping

**Use DSPy When**:
- ✅ You're doing academic research
- ✅ You need module-based architecture
- ✅ You want reflection/self-improvement
- ✅ You're building complex multi-step pipelines

#### 6.2 Performance Patterns

**GEPA vs MIPRO**:
- MIPRO: Faster convergence, better for structured tasks
- GEPA: More exploration, better for complex tasks
- Both achieve similar final performance

**Proposer Modes**:
- DSPy proposer: Good for multi-step reasoning
- GEPA-AI proposer: Good for instruction optimization
- Synth proposer: Balanced performance

#### 6.3 Production Considerations

**Synth AI Advantages**:
- Automatic Cloudflare tunnel management
- In-process task apps (no manual deployment)
- Programmatic polling and progress tracking
- Backend API for integration
- Interceptor pattern (secure prompt injection)

**Cost & Time**:
- Synth AI: Fastest (minutes)
- GEPA-AI: Moderate (tens of minutes)
- DSPy: Slowest (hours for some tasks)

### 7. Code Examples (400 words)

#### 7.1 Running a Benchmark with Synth AI

```python
from synth_ai.task import InProcessTaskApp
from synth_ai.api.train.prompt_learning import PromptLearningJob

async with InProcessTaskApp(
    config_factory=build_banking77_config,
    port=8102,
) as task_app:
    job = PromptLearningJob.from_config(
        config_path="configs/banking77_gepa.toml",
        backend_url="http://localhost:8000",
        api_key=os.getenv("SYNTH_API_KEY"),
    )
    
    job_id = job.submit()
    result = job.poll_until_complete(timeout=3600.0)
    
    print(f"Best score: {result['best_score']:.2%}")
```

#### 7.2 Running with GEPA-AI

```python
from gepa_ai import GEPAOptimizer

optimizer = GEPAOptimizer(
    initial_prompt=baseline_prompt,
    rollout_budget=500,
)

best_prompt = optimizer.optimize()
```

#### 7.3 Running with DSPy

```python
import dspy
from dspy.teleprompt import GEPA

optimizer = GEPA(
    metric=banking77_metric,
    num_candidates=20,
)

best_module = optimizer.compile(
    student=Banking77Classifier(),
    trainset=trainset,
)
```

### 8. Conclusion (200 words)

**Summary**:
- Synth AI provides production-ready prompt optimization
- Comparable or better performance than alternatives
- Significantly faster optimization times
- Easy integration with automatic task app management

**Recommendations**:
- **Production**: Use Synth AI (GEPA or MIPRO)
- **Research**: Use GEPA-AI or DSPy for flexibility
- **Quick Testing**: Use Synth AI with minimal budgets

**Future Work**:
- More benchmarks (agentic tasks, multi-modal)
- Advanced proposer modes
- Cost optimization
- Real-time optimization

### 9. Appendix: Reproducing Results

#### 9.1 Setup

```bash
# Install dependencies
uv pip install -e .

# Set environment variables
export GROQ_API_KEY=your_key
export OPENAI_API_KEY=your_key
export SYNTH_API_KEY=your_key

# Run library reference experiments
uv run python examples/blog_posts/langprobe/comparisons/run_library_reference_experiments.py

# Run Synth GEPA experiments
uv run python examples/blog_posts/langprobe/comparisons/run_gepa_parallel_experiments.py

# Run Synth MIPRO experiments
uv run python examples/blog_posts/langprobe/comparisons/run_mipro_parallel_experiments.py
```

#### 9.2 Results Files

- Library reference: `comparisons/library_reference_results_*.json`
- Synth GEPA: `comparisons/synth_gepa_comparison_results_*.json`
- Synth MIPRO: `comparisons/mipro_comparison_readout_*.txt`

## Visualizations Needed

1. **Performance Comparison Chart**: Bar chart showing final scores across frameworks
2. **Lift Comparison**: Bar chart showing improvements over baseline
3. **Time Comparison**: Bar chart showing optimization time
4. **Learning Curves**: Line charts showing optimization progress over time
5. **Benchmark Heatmap**: Heatmap showing performance across benchmarks and frameworks

## Key Statistics to Highlight

- **Synth MIPRO**: +11.30% average lift, 51s average time
- **Synth GEPA**: +7.34% average lift, consistent improvements
- **GEPA-AI**: 75.5% average final score, +14.61% average lift
- **DSPy**: 47.4% average final score, +23.94% average lift (from lower baselines)

## Call to Action

- Try Synth AI: `examples/blog_posts/vendored_prompt_learning/`
- Run benchmarks: `examples/blog_posts/langprobe/comparisons/`
- Read docs: Production optimization guide
- Get started: Quick start examples

