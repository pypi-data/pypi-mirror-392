# Determinism Guarantees

## Overview

The RLang compiler provides **bit-for-bit deterministic execution**, meaning identical inputs always produce identical outputs, down to the byte level. This determinism is essential for cryptographic verification and trustless execution.

## Exact Hashing Invariants

The following invariants are guaranteed: source code invariance, input invariance, hash invariance, and serialization invariance. Same source code produces same IR, same input produces same execution trace, same proof bundle produces same HMASTER and HRICH.

## Why Results are Bit-for-Bit Identical

Determinism is achieved through pure functions, no randomness, no I/O, canonical serialization, fixed evaluation order, deterministic hashing, and deterministic branch decisions (v0.2). Conditions are evaluated by pure expressions with no randomness, time, or I/O.

## Branch Decision Determinism

Branch decisions in `if/else` expressions are deterministic because conditions are evaluated by pure expressions. For the same input and same function registry, the same branch is always taken. HRICH changes when the branch path changes, and branch metadata tampering is detected during verification.

## Cross-Machine Reproducibility

The compiler produces identical results across different operating systems, Python versions, hardware architectures, and execution environments. This is verified through automated testing on multiple platforms, SHA256 hash comparison, and canonical JSON comparison.

## Tamper Detection

Any modification to a proof bundle is detected through HRICH mismatch or subproof hash mismatch. The verification process recomputes HRICH and detects any tampering with the execution trace or branch metadata.

