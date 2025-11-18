# Proof System Integration

## Overview

The compiler integrates with the BoR (Blockchain of Reasoning) proof system to generate cryptographic proof bundles. These bundles enable trustless verification of program execution.

## PipelineProofBundle

A `PipelineProofBundle` contains the raw execution trace including steps, branches (v0.2), input/output values, and metadata. Each step execution record captures the step index, template ID, input snapshot, and output snapshot. Branch execution records (v0.2) capture the index, path ("then" or "else"), and condition value.

## Subproofs

The BoR system includes eight cryptographic subproof types: DIP (Data Integrity Proof), DP (Deterministic Proof), PEP (Program Execution Proof), PoPI (Proof of Pipeline Integrity), CCP (Cryptographic Computation Proof), CMIP (Cryptographic Memory Integrity Proof), PP (Program Proof), and TRP (Trace Record Proof). In v0.2, TRP includes both step trace and branch trace, making the entire control-flow path cryptographically verifiable.

## HMASTER vs HRICH

HMASTER aggregates all step execution hashes, providing execution integrity, ordering guarantees, and input/output binding. HRICH is computed from subproof hashes, providing subproof integrity, completeness, and enabling independent verification.

## Verification Process

Proof bundles are verified using the `borp` CLI tool, which checks H_RICH match, subproof hash matches, structure validity, and type correctness. Successful verification confirms cryptographic integrity of the execution trace.

