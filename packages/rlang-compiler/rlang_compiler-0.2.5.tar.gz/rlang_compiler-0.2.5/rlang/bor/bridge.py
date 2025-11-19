"""RLang → BoR Runtime Bridge.

Maps StepTemplateIR and PipelineIR into executable BoR pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from rlang.canonical import PrimaryProgramIR
from rlang.ir import PipelineIR, PipelineStepIR, StepTemplateIR

# Try to import BoR SDK, fall back to mocks if not available
try:
    from bor.core import ExecutionResult, Pipeline as BorPipeline, StepDefinition
except ImportError:
    # Mock implementations for testing when BoR SDK is not installed
    @dataclass
    class StepDefinition:
        """Mock StepDefinition for testing."""

        name: str
        version: str
        rule_repr: str

    @dataclass
    class ExecutionResult:
        """Mock ExecutionResult for testing."""

        output: Any
        proof_bundle: Optional[Dict[str, Any]] = None

    class BorPipeline:
        """Mock Pipeline for testing."""

        def __init__(self, name: str, steps: list[StepDefinition]):
            self.name = name
            self.steps = steps

        def run(self, input_value: Any, fn_registry: Dict[str, Callable]) -> ExecutionResult:
            """Execute pipeline with given input and function registry."""
            current_value = input_value
            for step_def in self.steps:
                if step_def.name not in fn_registry:
                    raise ValueError(f"Function '{step_def.name}' not found in registry")
                fn = fn_registry[step_def.name]
                current_value = fn(current_value)
            return ExecutionResult(output=current_value)


@dataclass
class BoRStepMapping:
    """Mapping between RLang StepTemplateIR and BoR StepDefinition.

    Attributes:
        template: The original StepTemplateIR
        step_def: The BoR StepDefinition
        fn_impl: The Python function implementation (placeholder or real)
    """

    template: StepTemplateIR
    step_def: StepDefinition
    fn_impl: Callable[[Any], Any]


@dataclass
class BoRPipelineInstance:
    """Complete BoR pipeline instance built from PrimaryProgramIR.

    Attributes:
        ir: The original PrimaryProgramIR
        bor_pipeline: The constructed BoR Pipeline
        step_map: Mapping from template_id to BoRStepMapping
    """

    ir: PrimaryProgramIR
    bor_pipeline: BorPipeline
    step_map: Dict[str, BoRStepMapping]


class RLangBoRBridge:
    """Bridge from RLang PrimaryProgramIR to BoR executable pipelines.

    Converts RLang IR structures into BoR Pipeline and StepDefinition objects,
    allowing execution of RLang programs within the BoR runtime.
    """

    def __init__(self, ir: PrimaryProgramIR, fn_registry: Dict[str, Callable] | None = None):
        """Initialize bridge with PrimaryProgramIR and optional function registry.

        Args:
            ir: The PrimaryProgramIR to bridge
            fn_registry: Optional dictionary mapping function names to Python implementations.
                        If a function is not in the registry, a mock implementation will be used.

        Raises:
            ValueError: If fn_registry contains a function name that doesn't exist in IR templates
        """
        self.ir = ir
        self.fn_registry = fn_registry or {}

        # Validate registry: all function names must exist in IR templates
        template_names = {template.name for template in ir.step_templates}
        for fn_name in self.fn_registry.keys():
            if fn_name not in template_names:
                raise ValueError(
                    f"Function '{fn_name}' in registry does not exist in IR templates. "
                    f"Available templates: {sorted(template_names)}"
                )

    def _build_step_definitions(self) -> Dict[str, BoRStepMapping]:
        """Build BoR StepDefinition objects from StepTemplateIR templates.

        Returns:
            Dictionary mapping template_id to BoRStepMapping
        """
        mapping: Dict[str, BoRStepMapping] = {}

        for template in self.ir.step_templates:
            # Create StepDefinition
            step_def = StepDefinition(
                name=template.name,
                version=template.version,
                rule_repr=template.rule_repr,
            )

            # Get function implementation
            if template.name in self.fn_registry:
                fn_impl = self.fn_registry[template.name]
            else:
                # Create mock function with proper closure capture
                template_name = template.name  # Capture in closure

                def _mock_fn(x: Any) -> Dict[str, Any]:
                    return {"mock": template_name, "input": x}

                fn_impl = _mock_fn

            mapping[template.id] = BoRStepMapping(
                template=template,
                step_def=step_def,
                fn_impl=fn_impl,
            )

        return mapping

    def _build_pipeline(self, step_map: Dict[str, BoRStepMapping]) -> BorPipeline:
        """Build BoR Pipeline from entry PipelineIR.

        Args:
            step_map: Mapping from template_id to BoRStepMapping

        Returns:
            Constructed BoR Pipeline

        Raises:
            ValueError: If entry_pipeline is None or not found in IR pipelines
        """
        if self.ir.entry_pipeline is None:
            raise ValueError("Cannot build pipeline: entry_pipeline is None")

        # Find the entry pipeline
        pipeline_ir: Optional[PipelineIR] = None
        for pipeline in self.ir.pipelines:
            if pipeline.name == self.ir.entry_pipeline:
                pipeline_ir = pipeline
                break

        if pipeline_ir is None:
            raise ValueError(
                f"Entry pipeline '{self.ir.entry_pipeline}' not found in IR pipelines. "
                f"Available pipelines: {[p.name for p in self.ir.pipelines]}"
            )

        # Build list of StepDefinitions for pipeline steps
        step_defs: list[StepDefinition] = []
        for step in pipeline_ir.steps:
            if step.template_id not in step_map:
                raise ValueError(
                    f"Template ID '{step.template_id}' referenced in pipeline "
                    f"but not found in step mappings"
                )
            step_defs.append(step_map[step.template_id].step_def)

        # Construct BoR Pipeline
        pipeline = BorPipeline(
            name=pipeline_ir.name,
            steps=step_defs,
        )

        return pipeline

    def build(self) -> BoRPipelineInstance:
        """Build complete BoR pipeline instance from IR.

        Returns:
            BoRPipelineInstance containing IR, pipeline, and step mappings

        Raises:
            ValueError: If entry_pipeline is None or not found
        """
        step_map = self._build_step_definitions()
        bor_pipeline = self._build_pipeline(step_map)

        return BoRPipelineInstance(
            ir=self.ir,
            bor_pipeline=bor_pipeline,
            step_map=step_map,
        )

    def run(self, input_value: Any) -> ExecutionResult:
        """Execute the pipeline with given input value.

        Args:
            input_value: Input value to pass to the pipeline

        Returns:
            ExecutionResult containing output and proof bundle

        Raises:
            ValueError: If entry_pipeline is None or not found
            ValueError: If a function is missing from registry during execution
        """
        instance = self.build()

        # Build function registry for execution
        fn_registry: Dict[str, Callable] = {}
        for template_id, mapping in instance.step_map.items():
            fn_registry[mapping.step_def.name] = mapping.fn_impl

        # Execute pipeline
        return instance.bor_pipeline.run(
            input_value=input_value,
            fn_registry=fn_registry,
        )


__all__ = [
    "RLangBoRBridge",
    "BoRStepMapping",
    "BoRPipelineInstance",
]

