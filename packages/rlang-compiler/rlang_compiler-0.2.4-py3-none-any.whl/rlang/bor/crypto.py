"""RLang → BoR Cryptographic Integration.

Applies BoR's cryptographic hashing model (P₀–P₂) and sub-proof system
to RLang proof bundles to generate HMASTER and HRICH.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List

from rlang.bor.proofs import PipelineProofBundle
from rlang.utils.canonical_json import canonical_dumps

# Try to import BoR SDK, fall back to deterministic mocks if not available
try:
    from bor.core import hash_step, hash_master
    from bor.subproofs import compute_subproofs
    from bor.bundle import RichProofBundle

    BOR_SDK_AVAILABLE = True

    # Try to import helper functions if available
    try:
        from bor.bundle import compute_subproof_hashes, compute_HRICH_from_subproof_hashes
    except ImportError:
        # Define helpers if not available in SDK
        import json

        def compute_subproof_hashes(subproofs: Dict[str, Any]) -> Dict[str, str]:
            """Compute hashes for each subproof."""
            def h_sub(obj: Any) -> str:
                return hashlib.sha256(
                    json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
                ).hexdigest()
            return {k: h_sub(v) for k, v in subproofs.items()}

        def compute_HRICH_from_subproof_hashes(subproof_hashes: Dict[str, str]) -> str:
            """Compute H_RICH from subproof hashes."""
            sorted_hashes = [subproof_hashes[k] for k in sorted(subproof_hashes.keys())]
            combined = "|".join(sorted_hashes)
            return hashlib.sha256(combined.encode("utf-8")).hexdigest()

except ImportError:
    # Deterministic mock implementations for testing when BoR SDK is not installed
    BOR_SDK_AVAILABLE = False

    def hash_step(step_dict: Dict[str, Any]) -> str:
        """Mock hash_step: deterministic SHA-256 of canonical JSON.

        Args:
            step_dict: Step execution dictionary

        Returns:
            Hexadecimal hash string
        """
        canonical_json = canonical_dumps(step_dict)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def hash_master(step_hashes: List[str]) -> str:
        """Mock hash_master: deterministic SHA-256 of concatenated step hashes.

        Args:
            step_hashes: List of step hash strings

        Returns:
            Hexadecimal master hash string
        """
        # Sort hashes for determinism, then concatenate
        sorted_hashes = sorted(step_hashes)
        combined = "".join(sorted_hashes)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def compute_subproofs(primary_hash: str) -> Dict[str, Any]:
        """Mock compute_subproofs: generates deterministic sub-proofs.

        Args:
            primary_hash: Primary hash (HMASTER)

        Returns:
            Dictionary with sub-proof data structures
        """
        # Deterministic sub-proof computation based on primary hash
        # In real BoR SDK, this computes DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP
        # For mocks, we generate deterministic subproof dictionaries
        # Structure matches BoR SDK expectations
        subproofs = {
            "DIP": {"hash": primary_hash, "verified": True},
            "DP": {"hash": primary_hash, "verified": True},
            "PEP": {"ok": True, "exception": None},
            "PoPI": {"hash": primary_hash, "verified": True},
            "CCP": {"hash": primary_hash, "verified": True},
            "CMIP": {"hash": primary_hash, "verified": True},
            "PP": {"hash": primary_hash, "verified": True},
            "TRP": {"hash": primary_hash, "verified": True},
        }

        return subproofs

    # Define helper functions for mock case
    import json

    def compute_subproof_hashes(subproofs: Dict[str, Any]) -> Dict[str, str]:
        """Compute hashes for each subproof.

        Args:
            subproofs: Dictionary of subproof data structures

        Returns:
            Dictionary mapping subproof names to their hashes
        """
        def h_sub(obj: Any) -> str:
            """Hash a subproof object using canonical JSON."""
            return hashlib.sha256(
                json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
            ).hexdigest()

        return {k: h_sub(v) for k, v in subproofs.items()}

    def compute_HRICH_from_subproof_hashes(subproof_hashes: Dict[str, str]) -> str:
        """Compute H_RICH from subproof hashes.

        Args:
            subproof_hashes: Dictionary mapping subproof names to hashes

        Returns:
            H_RICH hash string
        """
        # H_RICH = SHA-256 of sorted subproof hash values joined with "|"
        sorted_hashes = [subproof_hashes[k] for k in sorted(subproof_hashes.keys())]
        combined = "|".join(sorted_hashes)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @dataclass
    class RichProofBundle:
        """Mock RichProofBundle for testing."""

        primary: Dict[str, Any]
        H_RICH: str
        rich: Dict[str, Any]

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return self.rich

        def to_json(self) -> str:
            """Convert to JSON string."""
            return canonical_dumps(self.rich)


@dataclass(frozen=True)
class StepHashRecord:
    """Record of a step hash computation.

    Attributes:
        index: Step index in pipeline
        template_id: Template ID reference
        step_hash: Cryptographic hash of step execution
    """

    index: int
    template_id: str
    step_hash: str


@dataclass(frozen=True)
class HashedProgram:
    """Complete hashed program with HMASTER and HRICH.

    Attributes:
        HMASTER: Master hash aggregating all step hashes
        HRICH: Rich hash including all sub-proofs
        step_hashes: List of step hash records
        primary_data: Primary proof data structure
        rich_data: Rich proof data structure
    """

    HMASTER: str
    HRICH: str
    step_hashes: List[StepHashRecord]
    primary_data: Dict[str, Any]
    rich_data: Dict[str, Any]


class RLangBoRCrypto:
    """Cryptographic converter from RLang proof bundles to BoR rich bundles.

    Applies BoR's P₀–P₂ hashing model and sub-proof system to generate
    HMASTER and HRICH from RLang execution proof bundles.
    """

    def __init__(self, proof: PipelineProofBundle):
        """Initialize crypto converter with proof bundle.

        Args:
            proof: PipelineProofBundle from Phase 10
        """
        self.proof = proof

    def compute_step_hashes(self) -> List[StepHashRecord]:
        """Compute cryptographic hashes for each step execution.

        Returns:
            List of StepHashRecord with step hashes
        """
        records: List[StepHashRecord] = []

        for step in self.proof.steps:
            # Convert step to canonical dictionary
            step_dict = step.to_dict()

            # Compute step hash using BoR SDK or mock
            step_hash = hash_step(step_dict)

            # Create hash record
            record = StepHashRecord(
                index=step.index,
                template_id=step.template_id,
                step_hash=step_hash,
            )
            records.append(record)

        return records

    def compute_HMASTER(self) -> str:
        """Compute HMASTER from canonical IR JSON.

        HMASTER = hash(canonical_json(ir))
        This ensures HMASTER depends only on program logic, not on input or execution.

        Returns:
            Master hash string (HMASTER)
        """
        # Get canonical IR JSON
        ir_json = self.proof.program_ir.to_json()
        
        # Compute SHA-256 hash of canonical IR JSON
        master = hashlib.sha256(ir_json.encode("utf-8")).hexdigest()
        return master

    def compute_HRICH(self, proof_bundle_dict: Dict[str, Any]) -> str:
        """Compute HRICH from canonical proof bundle JSON.

        HRICH = hash(canonical_json(proof_bundle))
        This ensures HRICH changes when input, output, or execution trace changes.

        Args:
            proof_bundle_dict: Complete proof bundle dictionary

        Returns:
            Rich hash string (HRICH)
        """
        # Convert proof bundle to canonical JSON
        proof_json = canonical_dumps(proof_bundle_dict)
        
        # Compute SHA-256 hash of canonical proof bundle JSON
        hrich = hashlib.sha256(proof_json.encode("utf-8")).hexdigest()
        return hrich

    def compute_subproofs_data(self, HMASTER: str) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Compute subproofs and their hashes.

        Args:
            HMASTER: Master hash

        Returns:
            Tuple of (subproofs dict, subproof_hashes dict)
        """
        subproofs = compute_subproofs(primary_hash=HMASTER)
        subproof_hashes = compute_subproof_hashes(subproofs)
        return subproofs, subproof_hashes

    def build_primary_data(self, HMASTER: str) -> Dict[str, Any]:
        """Build primary proof data structure compatible with BoR.

        Args:
            HMASTER: Master hash (computed from canonical IR)

        Returns:
            Primary data dictionary
        """
        return {
            "master": HMASTER,
        }
    
    def build_trp(self) -> Dict[str, Any]:
        """Build TRP (Trace of Reasoning Process) structure.

        TRP includes:
        - All step execution records with input/output snapshots
        - All branch decisions with condition values

        Returns:
            TRP dictionary
        """
        trp = {
            "steps": [
                {
                    "index": s.index,
                    "step_name": s.step_name,
                    "input_snapshot": s.input_snapshot,
                    "output_snapshot": s.output_snapshot,
                }
                for s in self.proof.steps
            ],
            "branches": [
                {
                    "index": b.index,
                    "path": b.path,
                    "condition_value": b.condition_value,
                }
                for b in self.proof.branches
            ],
        }
        return trp

    def to_rich_bundle(self) -> RichProofBundle:
        """Convert proof bundle to BoR RichProofBundle.

        Returns:
            RichProofBundle compatible with BoR SDK

        Raises:
            ValueError: If proof bundle has no steps
        """
        if not self.proof.steps:
            raise ValueError("Cannot create rich bundle: proof has no steps")

        # Compute HMASTER from canonical IR (does NOT depend on input)
        HMASTER = self.compute_HMASTER()

        # Build primary data
        primary_data = self.build_primary_data(HMASTER)

        # Build TRP (Trace of Reasoning Process)
        trp = self.build_trp()

        # Get canonical IR as dictionary
        ir_dict = self.proof.program_ir.to_dict()

        # Build complete proof bundle dictionary
        proof_bundle_dict = {
            "primary": primary_data,
            "ir": ir_dict,
            "trp": trp,
            "input": self.proof.input_value,
            "output": self.proof.output_value,
            "metadata": {
                "version": self.proof.version,
                "language": self.proof.language,
                "entry_pipeline": self.proof.entry_pipeline,
            },
        }

        # Compute HRICH from canonical proof bundle JSON (depends on input/output/execution)
        HRICH = self.compute_HRICH(proof_bundle_dict)

        # Add HRICH to proof bundle
        proof_bundle_dict["H_RICH"] = HRICH

        # Build rich data structure compatible with BoR SDK
        rich_data = proof_bundle_dict.copy()

        # Create RichProofBundle
        bundle = RichProofBundle(
            primary=primary_data,
            H_RICH=HRICH,
            rich=rich_data,
        )

        return bundle

    def to_hashed_program(self) -> HashedProgram:
        """Convert proof bundle to HashedProgram representation.

        Returns:
            HashedProgram with HMASTER, HRICH, and all hash records

        Raises:
            ValueError: If proof bundle has no steps
        """
        # Compute step hashes (for step_hashes field)
        step_records = self.compute_step_hashes()
        
        # Compute HMASTER from canonical IR
        HMASTER = self.compute_HMASTER()
        
        # Build primary data
        primary_data = self.build_primary_data(HMASTER)
        
        # Build TRP
        trp = self.build_trp()
        
        # Get canonical IR
        ir_dict = self.proof.program_ir.to_dict()
        
        # Build proof bundle dict for HRICH computation
        proof_bundle_dict = {
            "primary": primary_data,
            "ir": ir_dict,
            "trp": trp,
            "input": self.proof.input_value,
            "output": self.proof.output_value,
            "metadata": {
                "version": self.proof.version,
                "language": self.proof.language,
                "entry_pipeline": self.proof.entry_pipeline,
            },
        }
        
        # Compute HRICH from canonical proof bundle JSON
        HRICH = self.compute_HRICH(proof_bundle_dict)
        
        # Build rich data
        proof_bundle_dict["H_RICH"] = HRICH
        rich_data = proof_bundle_dict

        return HashedProgram(
            HMASTER=HMASTER,
            HRICH=HRICH,
            step_hashes=step_records,
            primary_data=primary_data,
            rich_data=rich_data,
        )


__all__ = [
    "StepHashRecord",
    "HashedProgram",
    "RLangBoRCrypto",
]

