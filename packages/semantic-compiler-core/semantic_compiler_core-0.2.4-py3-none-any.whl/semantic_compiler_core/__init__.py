"""
Semantic Compiler Core - Deterministic Compiler Library

This package provides the deterministic core of the semantic compiler:
SIR → RLang → ProofBundle → Hashes

No LLM dependencies, no API keys required.
"""

from .version import __version__
from .api import (
    sir_to_rlang,
    run_with_proof,
    compile_sir_to_proof,
)

__all__ = [
    '__version__',
    'sir_to_rlang',
    'run_with_proof',
    'compile_sir_to_proof',
]

