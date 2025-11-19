"""
Semantic Compiler: Deterministic Core - SIR → RLang → IR + Proof

This package provides the deterministic core functionality.
LLM-based modules (text → SIR) are in the nl_frontend package.
"""

__version__ = "0.0.1"

import logging

logger = logging.getLogger("semantic_compiler")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

# LLM-related modules are in nl_frontend package, not here
__all__ = ['logger']

