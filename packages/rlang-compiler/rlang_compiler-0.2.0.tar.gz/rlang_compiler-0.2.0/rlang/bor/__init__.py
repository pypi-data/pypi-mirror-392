"""RLang → BoR Runtime Bridge module.

Provides bridge functionality to convert RLang IR into executable BoR pipelines,
generate execution proof bundles, and apply BoR cryptographic hashing.
"""

from rlang.bor.bridge import BoRPipelineInstance, BoRStepMapping, RLangBoRBridge
from rlang.bor.crypto import HashedProgram, RLangBoRCrypto, StepHashRecord
from rlang.bor.proofs import BranchExecutionRecord, PipelineProofBundle, StepExecutionRecord, run_program_with_proof

__all__ = [
    "RLangBoRBridge",
    "BoRStepMapping",
    "BoRPipelineInstance",
    "StepExecutionRecord",
    "BranchExecutionRecord",
    "PipelineProofBundle",
    "run_program_with_proof",
    "StepHashRecord",
    "HashedProgram",
    "RLangBoRCrypto",
]

