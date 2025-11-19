# Phase 9 — RLang → BoR Runtime Bridge

## Overview

Implemented the RLang → BoR runtime bridge, mapping StepTemplateIR and PipelineIR into executable BoR pipelines with mock and real function support. This phase transforms the compiler from a "static IR generator" into a running, verifiable reasoning pipeline backed by BoR's hashing and proof system.

## Implementation Details

### Files Created

1. **`rlang/bor/bridge.py`** (243 lines)
   - `BoRStepMapping`: Dataclass mapping StepTemplateIR to BoR StepDefinition
     - Fields: template, step_def, fn_impl
   - `BoRPipelineInstance`: Complete BoR pipeline instance
     - Fields: ir, bor_pipeline, step_map
   - `RLangBoRBridge`: Main bridge class
     - `__init__()`: Initialize with PrimaryProgramIR and optional function registry
       - Validates registry function names exist in IR templates
     - `_build_step_definitions()`: Build BoR StepDefinition objects from templates
       - Creates StepDefinition with name, version, rule_repr
       - Maps to function implementation (registry or mock)
     - `_build_pipeline()`: Build BoR Pipeline from entry PipelineIR
       - Finds entry pipeline by name
       - Constructs Pipeline with StepDefinitions
     - `build()`: Build complete BoRPipelineInstance
     - `run()`: Execute pipeline with given input value
       - Returns ExecutionResult with output and proof bundle
   - Mock BoR SDK implementations when SDK not installed
     - `StepDefinition`: Mock dataclass
     - `ExecutionResult`: Mock dataclass with output and proof_bundle
     - `BorPipeline`: Mock class with `run()` method
   - Full `__all__` export list

2. **`rlang/bor/__init__.py`** (12 lines)
   - Public API exports: RLangBoRBridge, BoRStepMapping, BoRPipelineInstance

3. **`tests/test_bor_bridge.py`** (372 lines)
   - Comprehensive test suite with 15 test cases covering:
     - Simple mock execution
     - Real function registry execution
     - Multiple-step pipeline execution
     - Mixed mock and real functions
     - Incorrect registry function type (arity mismatch)
     - Missing function implementation (uses mocks)
     - Build returns proper pipeline instance
     - Step mapping structure validation
     - Invalid registry function name validation
     - No entry pipeline error handling
     - Entry pipeline not found error handling
     - Complex multi-step pipeline execution
     - Pipeline with string types
     - Step definitions have correct attributes
     - Multiple templates in single pipeline

## Key Features

- **BoR SDK Integration**: Maps RLang IR to BoR StepDefinition and Pipeline objects
- **Function Registry**: Supports providing Python implementations for RLang functions
- **Mock Functions**: Automatically creates mock implementations for missing functions
- **Error Handling**: Validates registry function names and entry pipeline existence
- **Pure Execution**: Pipeline execution is pure (no I/O) except for BoR hashing
- **Deterministic**: All mappings and executions are deterministic

## Bridge Architecture

### Step Mapping Flow

1. **StepTemplateIR** → **StepDefinition**
   - Extracts: name, version, rule_repr
   - Maps to function implementation (registry or mock)

2. **PipelineIR** → **BorPipeline**
   - Finds entry pipeline by name
   - Maps PipelineStepIR → StepDefinition via template_id
   - Constructs Pipeline with ordered StepDefinitions

3. **Execution**
   - Pipeline.run() executes steps sequentially
   - Each step receives output of previous step
   - Final output wrapped in ExecutionResult

### Function Implementation Strategy

- **Registry Functions**: User-provided Python implementations
  - Validated to exist in IR templates
  - Called directly during execution
- **Mock Functions**: Auto-generated for missing implementations
  - Returns `{"mock": template_name, "input": x}`
  - Allows testing without full implementations

## Usage Examples

### Simple Execution with Mock

```python
from rlang.emitter import compile_source_to_ir
from rlang.bor import RLangBoRBridge

source = """
fn step1(x: Int) -> Int;
pipeline main(Int) -> Int { step1 }
"""

result = compile_source_to_ir(source)
bridge = RLangBoRBridge(result.program_ir)
execution_result = bridge.run(10)
# Returns: {"mock": "step1", "input": 10}
```

### Execution with Real Functions

```python
def mul2(x):
    return x * 2

source = """
fn mul2(x: Int) -> Int;
pipeline main(Int) -> Int { mul2 }
"""

result = compile_source_to_ir(source)
bridge = RLangBoRBridge(result.program_ir, fn_registry={"mul2": mul2})
execution_result = bridge.run(21)
# Returns: 42
```

### Multi-Step Pipeline

```python
def inc(x):
    return x + 1

def double(x):
    return x * 2

source = """
fn inc(x: Int) -> Int;
fn double(x: Int) -> Int;
pipeline main(Int) -> Int { inc -> double }
"""

result = compile_source_to_ir(source)
bridge = RLangBoRBridge(
    result.program_ir,
    fn_registry={"inc": inc, "double": double}
)
execution_result = bridge.run(5)
# Returns: 12 (5 + 1) * 2
```

## Error Handling

- **Invalid Registry Function**: Raises ValueError if function name doesn't exist in IR
- **Missing Entry Pipeline**: Raises ValueError if entry_pipeline is None
- **Entry Pipeline Not Found**: Raises ValueError if entry pipeline name doesn't exist
- **Function Execution Errors**: Propagates TypeError/ValueError from function calls

## BoR SDK Compatibility

The bridge includes mock implementations of BoR SDK classes when the SDK is not installed:
- Falls back to mocks automatically via try/except ImportError
- Mock implementations match expected BoR SDK interface
- Allows testing without requiring BoR SDK installation

## Testing

All bridge functionality is thoroughly tested:
- ✅ Simple mock execution
- ✅ Real function registry execution
- ✅ Multiple-step execution
- ✅ Mixed mock and real functions
- ✅ Error handling (invalid registry, missing entry, etc.)
- ✅ Complex pipeline execution
- ✅ Type handling (Int, String)
- ✅ Step mapping structure validation

## Integration

- Uses existing PrimaryProgramIR from canonical module
- Integrates with emitter for end-to-end compilation
- Ready for BoR SDK integration (with fallback mocks)
- Follows project invariants (no empty files, deterministic, testable)

## Next Steps

Phase 9 complete. The compiler now bridges RLang IR to executable BoR pipelines:
- ✅ StepTemplateIR → StepDefinition mapping
- ✅ PipelineIR → BorPipeline construction
- ✅ Function registry support
- ✅ Mock function fallback
- ✅ Pipeline execution with input/output

Ready for Phase 10 — Step Execution Proof Generation (BoR Proof Bundles) where we incorporate hash-chain verification and fully integrate RLang pipelines into BoR consensus.

