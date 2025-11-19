# semantic-compiler-core

**Deterministic Reasoning Compiler for Verifiable AI Systems**

A production-grade compiler that transforms structured decision logic (SIR) into cryptographically verifiable proof bundles. Designed for enterprise compliance, rule engines, and provable AI pipelines where reproducibility and auditability are critical.

---

## Overview

`semantic-compiler-core` is a deterministic reasoning compiler that converts Semantic Intermediate Representation (SIR) into RLang source code, then compiles and executes it to produce stable, hash-verified proof bundles. The compiler guarantees:

- **Deterministic execution**: Same input → same output, every time
- **Cryptographic verification**: Stable hashing (HMASTER, H_IR, HRICH) ensures reproducibility
- **Zero nondeterministic IO**: Pure deterministic compilation pipeline
- **Clean architecture**: Separation of stochastic (LLM) and deterministic layers

The compiler operates entirely offline and requires no API keys or external services. LLM frontend functionality is available separately in the `nl_frontend` package.

---

## Why This Matters

### Deterministic Execution in AI Pipelines

Traditional AI systems suffer from nondeterminism, making it impossible to verify decisions or reproduce results. `semantic-compiler-core` provides a deterministic foundation for:

- **Verifiable decision-making**: Every decision produces a cryptographic proof
- **Enterprise compliance**: Full audit trail with traceable reasoning
- **Reproducible AI**: Same logic + same input = same output, guaranteed
- **Anti-hallucination pipelines**: LLM proposes, deterministic logic disposes

### Unique Proof Bundle Hashing

The compiler generates three cryptographic hashes:

- **HMASTER**: Program IR hash (proves the logic itself)
- **H_IR**: Intermediate representation hash
- **HRICH**: Execution trace hash (proves the execution path)

These hashes enable:
- Cryptographic verification of decision logic
- Blockchain-compatible proof generation (BoR - Blockchain of Reasoning)
- Tamper-proof audit logs
- Cross-system reproducibility verification

### Clear Separation of Concerns

```
┌─────────────────────────────────────┐
│  Stochastic Layer (Optional)        │
│  nl_frontend/ (LLM → SIR)           │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Deterministic Layer (Core)          │
│  SIR → RLang → IR → ProofBundle      │
│  Zero nondeterminism                │
└─────────────────────────────────────┘
```

---

## Architecture Overview

The compiler follows a clean, layered architecture with clear separation between stochastic (LLM) and deterministic (compilation) layers.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STOCHASTIC LAYER (Optional)                      │
│                         nl_frontend/ Package                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐         │
│  │ init_llm.py  │ ───▶ │ llm_bridge.py│ ───▶ │semantic_agent│         │
│  │              │      │              │      │     .py       │         │
│  │ LLM Config   │      │ API Wrapper  │      │ NL → SIR     │         │
│  │ Management   │      │ Error Handle │      │ Translation  │         │
│  └──────────────┘      └──────────────┘      └──────┬───────┘         │
│                                                      │                  │
└──────────────────────────────────────────────────────┼──────────────────┘
                                                       │
                                                       │ SIR Dict/JSON
                                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC COMPILATION LAYER                       │
│                    semantic_compiler/ Package                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                    sir_model.py                              │       │
│  │  ┌────────────────────────────────────────────────────────┐  │       │
│  │  │ DecisionPipeline (dataclass)                          │  │       │
│  │  │   ├── name: str                                       │  │       │
│  │  │   ├── input_name: str                                │  │       │
│  │  │   ├── input_type: InputType                          │  │       │
│  │  │   └── steps: List[Step]                              │  │       │
│  │  │                                                       │  │       │
│  │  │ Step Types:                                          │  │       │
│  │  │   ├── DecisionStep (condition + branches)            │  │       │
│  │  │   ├── SetOutputStep (output assignment)              │  │       │
│  │  │   └── Predicate (operators: gt, lt, eq, etc.)        │  │       │
│  │  └────────────────────────────────────────────────────────┘  │       │
│  │                                                              │       │
│  │  Functions:                                                  │       │
│  │   • sir_from_dict() → DecisionPipeline                      │       │
│  │   • sir_to_dict() → Dict[str, Any]                          │       │
│  └──────────────────────┬───────────────────────────────────────┘       │
│                         │                                                │
│                         │ Validated SIR Object                           │
│                         ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                 sir_validator.py                            │       │
│  │  ┌────────────────────────────────────────────────────────┐  │       │
│  │  │ Validation Functions:                                  │  │       │
│  │  │   • validate_pipeline() → bool                         │  │       │
│  │  │   • validate_step() → bool                             │  │       │
│  │  │   • validate_predicate() → bool                        │  │       │
│  │  │                                                         │  │       │
│  │  │ Checks:                                                 │  │       │
│  │  │   • Type safety (Int, Float, String, Bool)             │  │       │
│  │  │   • Operator compatibility                              │  │       │
│  │  │   • Reference validity (input_name exists)              │  │       │
│  │  │   • Semantic constraints                                │  │       │
│  │  └────────────────────────────────────────────────────────┘  │       │
│  └──────────────────────┬───────────────────────────────────────┘       │
│                         │                                                │
│                         │ Validated SIR                                  │
│                         ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                sir_to_rlang.py                              │       │
│  │  ┌────────────────────────────────────────────────────────┐  │       │
│  │  │ Compilation Functions:                                  │  │       │
│  │  │   • sir_to_rlang(pipeline, strict=True) → str          │  │       │
│  │  │                                                         │  │       │
│  │  │ Translation Rules:                                      │  │       │
│  │  │   • DecisionPipeline → "pipeline name(type) -> type"   │  │       │
│  │  │   • DecisionStep → "if (condition) { then } else { }"  │  │       │
│  │  │   • Predicate → "arg1 op arg2" (e.g., "value > 10")    │  │       │
│  │  │   • SetOutputStep → "ret_value"                        │  │       │
│  │  │                                                         │  │       │
│  │  │ Deterministic Guarantees:                               │  │       │
│  │  │   • 4-space indentation (canonical)                    │  │       │
│  │  │   • Stable operator ordering                            │  │       │
│  │  │   • No trailing whitespace                              │  │       │
│  │  │   • Byte-for-byte identical output                     │  │       │
│  │  └────────────────────────────────────────────────────────┘  │       │
│  └──────────────────────┬───────────────────────────────────────┘       │
│                         │                                                │
│                         │ RLang Source Code (string)                     │
│                         ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │              rlang_runtime.py                                │       │
│  │  ┌────────────────────────────────────────────────────────┐  │       │
│  │  │ Runtime Functions:                                      │  │       │
│  │  │   • run_with_proof(source, input_value) → Bundle       │  │       │
│  │  │   • extract_hashes(bundle) → Dict[str, str]            │  │       │
│  │  │   • bundle_to_dict(bundle) → Dict[str, Any]            │  │       │
│  │  │                                                         │  │       │
│  │  │ Backend Integration:                                    │  │       │
│  │  │   • Imports: rlang.bor.run_program_with_proof()        │  │       │
│  │  │   • Delegates to rlang-compiler PyPI package           │  │       │
│  │  │   • No re-implementation of IR/hashing                 │  │       │
│  │  │                                                         │  │       │
│  │  │ Execution Flow:                                        │  │       │
│  │  │   1. RLang source → IR (canonical)                    │  │       │
│  │  │   2. IR + input → Execution trace (TRP)               │  │       │
│  │  │   3. TRP → Proof bundle (JSON)                        │  │       │
│  │  │   4. Extract hashes: HMASTER, H_IR, HRICH              │  │       │
│  │  └────────────────────────────────────────────────────────┘  │       │
│  └──────────────────────┬───────────────────────────────────────┘       │
│                         │                                                │
└─────────────────────────┼────────────────────────────────────────────────┘
                          │
                          │ Proof Bundle + Hashes
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PUBLIC API LAYER                                    │
│                      semantic_compiler_core/ Package                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                        api.py                                │       │
│  │  ┌────────────────────────────────────────────────────────┐  │       │
│  │  │ Public Functions:                                      │  │       │
│  │  │                                                         │  │       │
│  │  │ 1. compile_sir_to_proof(sir, input_value)             │  │       │
│  │  │    → Dict[str, Any]                                    │  │       │
│  │  │    • One-shot: SIR → RLang → ProofBundle              │  │       │
│  │  │    • Returns: source, sir, bundle, hashes              │  │       │
│  │  │                                                         │  │       │
│  │  │ 2. sir_to_rlang(sir)                                   │  │       │
│  │  │    → str                                                │  │       │
│  │  │    • Compiles SIR dict to RLang source                 │  │       │
│  │  │    • Deterministic output                              │  │       │
│  │  │                                                         │  │       │
│  │  │ 3. run_with_proof(rlang_source, input_value)          │  │       │
│  │  │    → Dict[str, Any]                                    │  │       │
│  │  │    • Executes RLang and generates proof bundle         │  │       │
│  │  │    • Returns: bundle, hashes                           │  │       │
│  │  └────────────────────────────────────────────────────────┘  │       │
│  │                                                              │       │
│  │  ┌────────────────────────────────────────────────────────┐  │       │
│  │  │                   version.py                           │  │       │
│  │  │   • __version__ = "0.2.2"                             │  │       │
│  │  └────────────────────────────────────────────────────────┘  │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC PROOF LAYER                             │
│                    (Generated by rlang-compiler backend)                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Proof Bundle Structure:                                                  │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   "ir": {...},           ← Canonical Intermediate Rep        │       │
│  │   "trp": {...},          ← Trace of Reasoning Process        │       │
│  │   "output": <value>,     ← Execution result                  │       │
│  │   "metadata": {...}      ← Compilation metadata              │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  Cryptographic Hashes:                                                    │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  • HMASTER: Hash of program IR (proves logic itself)         │       │
│  │  • H_IR:    Hash of intermediate representation              │       │
│  │  • HRICH:   Hash of execution trace (proves execution path)  │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  Deterministic Guarantees:                                                │
│  • Same SIR + same input → same HMASTER, H_IR, HRICH                     │
│  • Cryptographic verification of decision logic                           │
│  • Blockchain-compatible proof generation (BoR)                          │
│  • Tamper-proof audit logs                                                │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Input (SIR Dict/JSON)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. SIR Parsing & Validation                                 │
│    sir_model.sir_from_dict()                                │
│    → DecisionPipeline (dataclass)                           │
│    sir_validator.validate_pipeline()                        │
│    → Validated SIR Object                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SIR → RLang Compilation                                  │
│    sir_to_rlang.sir_to_rlang(pipeline, strict=True)        │
│    → RLang Source Code (string)                            │
│    • Deterministic formatting                               │
│    • Canonical operator ordering                            │
│    • Byte-for-byte identical output                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. RLang Execution                                          │
│    rlang_runtime.run_with_proof(source, input_value)        │
│    │                                                         │
│    ├─→ Backend: rlang.bor.run_program_with_proof()         │
│    │   │                                                     │
│    │   ├─→ RLang Source → IR (canonical)                   │
│    │   ├─→ IR + Input → Execution Trace (TRP)              │
│    │   └─→ TRP → Proof Bundle (JSON)                       │
│    │                                                         │
│    └─→ Extract Hashes: extract_hashes(bundle)              │
│        → {HMASTER, H_IR, HRICH}                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Proof Bundle Return                                      │
│    {                                                         │
│      "source": <rlang_source>,                              │
│      "sir": <normalized_sir_dict>,                          │
│      "bundle": <proof_bundle_dict>,                          │
│      "hashes": {                                            │
│        "HMASTER": "...",                                    │
│        "H_IR": "...",                                       │
│        "HRICH": "..."                                       │
│      }                                                       │
│    }                                                         │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Diagram

```
┌──────────────┐
│   User Code  │
└──────┬───────┘
       │
       │ compile_sir_to_proof(sir_dict, input_value)
       ▼
┌──────────────────────────────────────────────────────────────┐
│           semantic_compiler_core.api                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ compile_sir_to_proof()                                 │  │
│  │   │                                                     │  │
│  │   ├─→ sir_to_rlang(sir)                                │  │
│  │   │     │                                               │  │
│  │   │     ├─→ semantic_compiler.sir_model               │  │
│  │   │     │     sir_from_dict() → DecisionPipeline       │  │
│  │   │     │                                               │  │
│  │   │     ├─→ semantic_compiler.sir_validator           │  │
│  │   │     │     validate_pipeline() → bool               │  │
│  │   │     │                                               │  │
│  │   │     └─→ semantic_compiler.sir_to_rlang           │  │
│  │   │           sir_to_rlang() → RLang string            │  │
│  │   │                                                     │  │
│  │   └─→ run_with_proof(rlang_source, input_value)        │  │
│  │         │                                               │  │
│  │         └─→ semantic_compiler.rlang_runtime            │  │
│  │               run_with_proof()                          │  │
│  │               │                                         │  │
│  │               ├─→ rlang.bor.run_program_with_proof()   │  │
│  │               │   (external: rlang-compiler package)   │  │
│  │               │                                         │  │
│  │               └─→ extract_hashes() → Dict[str, str]    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
       │
       │ Returns: {source, sir, bundle, hashes}
       ▼
┌──────────────┐
│   User Code  │
└──────────────┘
```

### Layer Descriptions

1. **SIR Model** (`sir_model.py`): Defines the Semantic Intermediate Representation as strongly-typed Python dataclasses. SIR v0.1 supports scalar integer decision pipelines with comparison operators and Boolean combiners.

2. **SIR Validator** (`sir_validator.py`): Validates SIR structure and enforces semantic constraints. Ensures type safety and rejects invalid constructs.

3. **SIR → RLang Compiler** (`sir_to_rlang.py`): Deterministically compiles SIR to RLang source code. Guarantees byte-for-byte identical output for identical input.

4. **RLang Runtime** (`rlang_runtime.py`): Wraps the `rlang-compiler` PyPI package to execute RLang code and generate proof bundles. Handles IR canonicalization and hash extraction.

5. **Public API** (`api.py`): Clean, stable API surface:
   - `compile_sir_to_proof()`: One-shot SIR → ProofBundle compilation
   - `sir_to_rlang()`: SIR → RLang source code
   - `run_with_proof()`: RLang → ProofBundle execution

---

## Key Features

- **Pure deterministic compiler core**: Zero external dependencies beyond deterministic modules
- **Strict validation mode**: Enforces type safety and semantic correctness
- **Stable hashing**: HMASTER, H_IR, HRICH guarantee reproducibility
- **Strong typing**: Canonical JSON with dataclass validation
- **Works offline**: No API keys, no network calls, no nondeterministic IO
- **Production-grade packaging**: Proper PyPI distribution with CI/CD
- **Clean separation**: LLM frontend is optional and separated

---

## Installation

```bash
pip install semantic-compiler-core
```

### Requirements

- Python >= 3.9
- `rlang-compiler >= 0.2.4` (automatically installed)

---

## Quick Start

### Minimal Example

```python
from semantic_compiler_core import compile_sir_to_proof

# Define a simple decision pipeline in SIR format
sir = {
    "type": "DecisionPipeline",
    "name": "main",
    "input_name": "value",
    "steps": [
        {
            "type": "Decision",
            "condition": {"op": "gt", "args": ["value", 10]},
            "then_steps": [{"type": "SetOutput", "value": 1}],
            "else_steps": [{"type": "SetOutput", "value": 0}],
        }
    ]
}

# Compile SIR to proof bundle
bundle = compile_sir_to_proof(sir, input_value=15)

# Access cryptographic hashes
print(f"HMASTER: {bundle['hashes']['HMASTER']}")
print(f"HRICH: {bundle['hashes']['HRICH']}")

# Access execution result
print(f"Output: {bundle['bundle']['output']}")
```

### Step-by-Step API Usage

```python
from semantic_compiler_core import sir_to_rlang, run_with_proof

# Step 1: SIR → RLang source code
rlang_source = sir_to_rlang(sir)
print(rlang_source)

# Step 2: Execute RLang and generate proof bundle
result = run_with_proof(rlang_source, input_value=15)
print(result['hashes']['HMASTER'])
```

---

## Use Cases

### For Investors

- **Verified AI decision systems**: Cryptographically provable AI logic
- **Compliance automation**: Regulatory-compliant rule engines with audit trails
- **Blockchain integration**: BoR-compatible proof generation for on-chain verification
- **Enterprise AI governance**: Transparent, auditable decision-making systems

### For Enterprises

- **Rule engines with cryptographic proofs**: Financial compliance, healthcare regulations
- **Deterministic workflow automation**: Reproducible business logic execution
- **Audit trail generation**: Tamper-proof logs with cryptographic verification
- **Anti-hallucination LLM pipelines**: "AI proposes, Logic disposes" architectures

### For Developers

- **Provable AI systems**: Build verifiable machine learning pipelines
- **Deterministic testing**: Reproducible test execution with proof generation
- **Reasoning engines**: Structured decision logic with cryptographic guarantees
- **Compliance tooling**: Regulatory logic with full traceability

---

## Current Scope (SIR v0.1)

The compiler currently supports:

- **Input**: Single scalar integer (`Int`)
- **Operators**: `gt`, `ge`, `lt`, `le`, `eq`, `neq`
- **Boolean combiners**: `all()`, `any()`, `not()`
- **Output**: Scalar constant integers

### Deterministic Guarantees

For any valid SIR v0.1 pipeline and input value:

- Same input → same SIR representation
- Same SIR → same RLang source code (byte-for-byte identical)
- Same RLang → same canonical IR
- Same IR → same execution trace (TRP)
- Same execution → same proof bundle (HMASTER, HRICH)

---

## Roadmap (v0.3 and Beyond)

- **Records**: Multi-field input types (`{income: Int, age: Int}`)
- **Lists**: Array/vector operations
- **Pattern Matching**: Advanced control flow constructs
- **Modules**: Code organization and reuse
- **Deterministic Arithmetic Engine**: Extended mathematical operations
- **Decision DAGs**: Graph-based execution models
- **Graph Execution**: Parallel decision path evaluation

---

## Development

### Local Installation

```bash
git clone <repository-url>
cd Verifiable_agent
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

### Building Distribution

```bash
python -m build
```

---

## License

This project is licensed under the MIT License.

---

## Authors

**Kushagra Bhatnagar**

- GitHub: [kushagrab21](https://github.com/kushagrab21)
- Project: [Compiler_new](https://github.com/kushagrab21/Compiler_new)

---

## Contributing

Contributions welcome! Please ensure all tests pass and deterministic guarantees are maintained.

---

## Links

- **PyPI**: https://pypi.org/project/semantic-compiler-core/
- **Source**: https://github.com/kushagrab21/Compiler_new
- **Issues**: https://github.com/kushagrab21/Compiler_new/issues
