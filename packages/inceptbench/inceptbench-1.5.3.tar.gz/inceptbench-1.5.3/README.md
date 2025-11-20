# InceptBench

[![PyPI version](https://badge.fury.io/py/inceptbench.svg)](https://badge.fury.io/py/inceptbench)
[![Python Version](https://img.shields.io/pypi/pyversions/inceptbench.svg)](https://pypi.org/project/inceptbench/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

Educational content evaluation framework with multiple AI-powered assessment modules.

## 📖 Documentation

### Official Sites
[Website](https://bench.inceptapi.com/) • [Benchmarks](https://bench.inceptapi.com/benchmarks/) • [Glossary](https://bench.inceptapi.com/glossary/) • [Docs](https://bench.inceptapi.com/inceptbench-docs/) • [API Endpoint](https://uae-poc.inceptapi.com/evaluate) • [API Docs](https://uae-poc.inceptapi.com/docs)

### User Guides
- **[USAGE.md](./docs/USAGE.md)** - Installation, configuration, CLI & Python API
- **[INPUT_OUTPUT.md](./docs/INPUT_OUTPUT.md)** - Input schemas and output formats
- **[EVALUATORS.md](./docs/EVALUATORS.md)** - Complete evaluator reference

### Developer Guides
- **[WIKI.md](./docs/WIKI.md)** - Documentation hub and workflows
- **[MAINTAINERS.md](./docs/MAINTAINERS.md)** - Submodule maintainer guide
- **[PUBLISHING.md](./docs/PUBLISHING.md)** - Package publishing workflow
- **[VERSION_LOCATIONS.md](./docs/VERSION_LOCATIONS.md)** - Version file reference

### Resources
- **[Google Drive](https://drive.google.com/drive/folders/1dFdMj70HgYZCtrMG3W1_3lVyi8Kmyz_V)** - Test data and examples
- **[GitHub Repo](https://github.com/trilogy-group/inceptbench)** - Source code

## 🚀 Quick Start

```bash
# Install from PyPI (latest published release)
pip install inceptbench

# Or install from source (current repo snapshot)
git clone https://github.com/incept-ai/inceptbench.git
cd inceptbench
python3 -m venv venv && source venv/bin/activate
pip install -e .

# Create .env file (optional - for API-based evaluation)
echo "OPENAI_API_KEY=your_key" >> .env
echo "ANTHROPIC_API_KEY=your_key" >> .env

# Generate example
inceptbench example

# Run evaluation via CLI
inceptbench evaluate qs.json --full

# Or call the CLI module directly (no install needed)
PYTHONPATH="$(pwd)/src:$PYTHONPATH" python -m inceptbench.cli evaluate qs.json --full
```

## ✨ Features

- **6 Specialized Evaluators** - Quality assessment across multiple dimensions
- **Automatic Image Evaluation** - Context-aware DI rubric scoring
- **Parallel Processing** - 47+ tasks running concurrently
- **Multi-language Support** - Evaluate content in any language
- **Dual Content Types** - Questions (MCQ/fill-in) and text content (passages/explanations)
- **Production-Ready** - Full demo in `qs.json` (~3-4 minutes)

## 📊 Evaluators

| Evaluator | Type | Auto |
|-----------|------|------|
| ti_question_qa | Question quality (10 dimensions) | Yes |
| answer_verification | Answer correctness | Yes |
| reading_question_qc | MCQ distractor analysis | Yes |
| math_content_evaluator | Content quality (9 criteria) | Yes |
| text_content_evaluator | Pedagogical text assessment | Yes |
| image_quality_di_evaluator | DI rubric image quality | **Auto** |
| external_edubench | Educational benchmark (6 tasks) | No |

See [EVALUATORS.md](./docs/EVALUATORS.md) for details.

## 📦 Architecture

```
inceptbench/
├── src/inceptbench/          # Unified package (src/ layout)
│   ├── orchestrator.py        # Main evaluation orchestrator
│   ├── cli.py                 # Command-line interface
│   ├── core/                  # Core evaluators and utilities
│   ├── agents/                # Agent-based evaluators
│   ├── qc/                    # Quality control modules
│   ├── evaluation/            # Evaluation templates
│   └── image/                 # Image quality evaluation
├── submodules/                # External dependencies
│   ├── reading-question-qc/
│   ├── EduBench/
│   ├── agentic-incept-reasoning/
│   └── image_generation_package/
└── pyproject.toml             # Package configuration
```

## 🎯 Demo

The `qs.json` file demonstrates all capabilities:
- 8 questions (MCQ/fill-in, Arabic/English)
- 4 text content items
- 7 images (auto-evaluated)
- All 6 evaluators active
- ~3-4 minute runtime

## ✅ Local Smoke Test

Use the bundled demo file to validate your environment before making changes:

```bash
# Using CLI (recommended)
inceptbench evaluate qs.json --full

# Or run locally without installing the package
PYTHONPATH="$(pwd)/src:$PYTHONPATH" python -m inceptbench.cli evaluate qs.json --full

# Or using Python API
python -c "from inceptbench import universal_unified_benchmark, UniversalEvaluationRequest; import json; data = json.load(open('qs.json')); request = UniversalEvaluationRequest(**data); result = universal_unified_benchmark(request); print(result.model_dump_json(indent=2))"
```

These commands exercise every evaluator (including localization + DI image checks) and report per-item scores plus the combined `inceptbench_version`. Sample data leaves some `image_url` fields set to `null`, so the DI image checker will log `FileNotFoundError: 'null'` entries—those are expected for the placeholders and can be ignored during the smoke test.

## 🌐 Locale-Aware Localization

`UniversalEvaluationRequest` now accepts a `locale` such as `ar-AE`, `en-AE`, or `en-IN`. The format is:

- **First segment** (`ar`, `en`, etc.): language of the text
- **Second segment** (`AE`, `IN`, etc.): cultural/regional guardrails to apply

When `locale` is provided, all localization checks use the corresponding language + cultural context. If it is omitted, we fall back to the legacy `language` field and heuristics (auto-detecting non-ASCII text when necessary).

Localized prompts now run through a dedicated `localization_evaluator`, making cultural QA a first-class signal rather than a side-effect of other evaluators. Technical checks (schema fidelity, grammar, etc.) live in other modules—this evaluator focuses only on cultural neutrality and regional appropriateness.

**Rule-based regionalization checks (ITD guidance):**
- Familiarity & relevance: keep contexts understandable for the target region/grade (no “filing taxes” for Grade 3, no hyper-local fruit for remote regions).
- Regional reference limit: at most one explicit local prop—multiple props often create caricatures.
- Instruction-aligned language: only switch languages when the student’s classroom instruction uses that language (respect bilingual/international settings).
- Respectful tone & content: references must not mock, stereotype, or oversimplify cultures; neutral fallbacks beat risky flair.
- Rule-first transparency: every failure cites the violated rule, favoring deterministic guardrails over fuzzy similarity scores.

All localization guardrails live in `src/inceptbench/agents/localization_guidelines.json`, so future tweaks are data-only—add new cultural rules/prompts in JSON and the evaluator automatically picks them up without code changes.

Each rule is scored via its own compact prompt that returns `0` (fail) or `1` (pass); section and overall scores are simply the percentage of guardrail rules satisfied, so localization quality is now a transparent, deterministic checklist.

## 📝 Example Usage

### CLI
```bash
inceptbench evaluate qs.json --full
inceptbench evaluate qs.json -o results.json
```

### Python API
```python
from inceptbench import universal_unified_benchmark, UniversalEvaluationRequest

request = UniversalEvaluationRequest(
    submodules_to_run=["ti_question_qa", "answer_verification"],
    generated_questions=[{
        "id": "q1",
        "type": "mcq",
        "question": "What is 2+2?",
        "answer": "4",
        "answer_options": {"A": "3", "B": "4", "C": "5"},
        "answer_explanation": "2+2 equals 4",
        "skill": {
            "title": "Basic Addition",
            "grade": "1",
            "subject": "mathematics",
            "difficulty": "easy"
        }
    }]
)

response = universal_unified_benchmark(request)
print(response.evaluations["q1"].score)
```

See [USAGE.md](./docs/USAGE.md) for complete examples.

## 🖼️ Image Evaluation

Add `image_url` to any question or content:
```json
{
  "id": "q1",
  "question": "How many apples?",
  "image_url": "https://example.com/apples.png"
}
```

The `image_quality_di_evaluator` runs automatically with:
- Context-aware evaluation (accompaniment vs standalone)
- DI rubric scoring (0-100, normalized to 0-1)
- Hard-fail gates (answer leakage, wrong representations)
- Canonical DI representation checks

## 📥 Input Format

**Questions**:
```json
{
  "submodules_to_run": ["ti_question_qa"],
  "generated_questions": [{
    "id": "q1",
    "type": "mcq",
    "question": "...",
    "answer": "...",
    "image_url": "..."  // Optional
  }]
}
```

**Text Content**:
```json
{
  "submodules_to_run": ["text_content_evaluator"],
  "generated_content": [{
    "id": "text1",
    "type": "text",
    "content": "...",
    "image_url": "..."  // Optional
  }]
}
```

See [INPUT_OUTPUT.md](./docs/INPUT_OUTPUT.md) for complete schema.

## 📤 Output Format

**Simplified** (default):
```json
{
  "evaluations": {
    "q1": {"score": 0.89}
  }
}
```

**Full** (verbose=True):
```json
{
  "evaluations": {
    "q1": {
      "ti_question_qa": {
        "overall": 0.95,
        "scores": {...},
        "issues": [...],
        "strengths": [...]
      },
      "score": 0.89
    }
  }
}
```

## 🔄 Module Selection

**Automatic** (if `submodules_to_run` not specified):
- Questions → `ti_question_qa`, `answer_verification`, `math_content_evaluator`, `reading_question_qc`
- Text → `text_content_evaluator`, `math_content_evaluator`
- Images → `image_quality_di_evaluator` (auto-added)
- Localization → `localization_evaluator` (auto when `locale`/`language` ≠ English or non-ASCII text is detected)

**Manual**:
```python
request = UniversalEvaluationRequest(
    submodules_to_run=["ti_question_qa", "answer_verification"],  # Only these
    generated_questions=[...]
)
```

## 📜 License

Proprietary - Copyright Trilogy Education Services
