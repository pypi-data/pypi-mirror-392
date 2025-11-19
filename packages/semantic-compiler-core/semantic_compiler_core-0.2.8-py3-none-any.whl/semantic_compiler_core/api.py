"""
Public API for semantic-compiler-core.

This module provides a clean, stable API for deterministic compilation:
SIR → RLang → ProofBundle → Hashes

No LLM dependencies, no API keys required.
"""

from typing import Any, Dict, Tuple

# Import deterministic functions from existing modules
from semantic_compiler_core.sir_model import DecisionPipeline, sir_from_dict
from semantic_compiler_core.sir_to_rlang import sir_to_rlang as _sir_to_rlang_impl
from semantic_compiler_core.rlang_runtime import (
    run_with_proof as _run_with_proof_impl,
    extract_hashes,
    bundle_to_dict,
)


def sir_to_rlang(sir: Dict[str, Any]) -> str:
    """
    Deterministically compile a canonical SIR dict into RLang source code.
    
    Args:
        sir: SIR dictionary (must have "type": "DecisionPipeline", "name", "input_name", "steps")
        
    Returns:
        RLang source code string (deterministic, canonical)
        
    Raises:
        ValueError: If SIR is invalid or contains unsupported constructs
        TypeError: If SIR structure is invalid
        
    Example:
        >>> sir = {
        ...     "type": "DecisionPipeline",
        ...     "name": "main",
        ...     "input_name": "value",
        ...     "steps": [
        ...         {
        ...             "type": "Decision",
        ...             "id": "check",
        ...             "condition": {"op": "gt", "args": ["value", 10]},
        ...             "then_steps": [{"type": "SetOutput", "value": 1}],
        ...             "else_steps": [{"type": "SetOutput", "value": 0}],
        ...         }
        ...     ],
        ... }
        >>> rlang_source = sir_to_rlang(sir)
        >>> assert "pipeline main(Int)" in rlang_source
    """
    # Convert dict to DecisionPipeline object
    if isinstance(sir, dict):
        pipeline = sir_from_dict(sir)
    elif isinstance(sir, DecisionPipeline):
        pipeline = sir
    else:
        raise TypeError(f"Expected dict or DecisionPipeline, got {type(sir).__name__}")
    
    # Call implementation with strict=True for deterministic compilation
    return _sir_to_rlang_impl(pipeline, strict=True)


def run_with_proof(
    rlang_source: str,
    input_value: Any,
    fn_registry: Dict[str, Any] = None,
    sir: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run RLang source through the deterministic backend, returning a proof bundle dict.
    
    Args:
        rlang_source: RLang source code string
        input_value: Input value for pipeline execution
        fn_registry: Optional function registry (dict mapping function names to callables).
                    If None and sir is provided, will be auto-generated from SIR.
        sir: Optional SIR dictionary. If fn_registry is None, will be used to auto-generate
             function registry for SetOutput steps.
        
    Returns:
        Dict containing:
        - 'bundle': Proof bundle dict
        - 'hashes': Dict with 'HMASTER', 'H_IR', 'HRICH' keys
        
    Raises:
        RuntimeError: If backend is unavailable or execution fails
        
    Example:
        >>> rlang_source = "pipeline main(Int) -> Int { if (__value > 10) { ret_1 } else { ret_0 } }"
        >>> result = run_with_proof(rlang_source, input_value=15)
        >>> assert 'bundle' in result
        >>> assert 'hashes' in result
        >>> assert 'HMASTER' in result['hashes']
    """
    # Call implementation
    raw_bundle, bundle_dict = _run_with_proof_impl(
        source=rlang_source,
        input_value=input_value,
        fn_registry=fn_registry,
        sir=sir,
    )
    
    # Extract hashes using raw bundle (preferred) or bundle_dict (fallback)
    try:
        hashes = extract_hashes(raw_bundle)
    except Exception:
        # Fallback to dict-based extraction if raw bundle fails
        hashes = extract_hashes(bundle_dict)
    
    return {
        'bundle': bundle_dict,
        'hashes': hashes,
    }


def compile_sir_to_proof(sir: Dict[str, Any], input_value: Any, fn_registry: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function: SIR → RLang → ProofBundle (all deterministic).
    
    This is a one-shot function that compiles SIR to RLang and executes it,
    returning the complete proof bundle with hashes.
    
    Args:
        sir: SIR dictionary (must have "type": "DecisionPipeline", "name", "input_name", "steps")
        input_value: Input value for pipeline execution
        fn_registry: Optional function registry (dict mapping function names to callables)
        
    Returns:
        Dict containing:
        - 'source': RLang source code string
        - 'sir': SIR dict (normalized)
        - 'bundle': Proof bundle dict
        - 'hashes': Dict with 'HMASTER', 'H_IR', 'HRICH' keys
        
    Raises:
        ValueError: If SIR is invalid or contains unsupported constructs
        RuntimeError: If backend is unavailable or execution fails
        
    Example:
        >>> sir = {
        ...     "type": "DecisionPipeline",
        ...     "name": "main",
        ...     "input_name": "value",
        ...     "steps": [
        ...         {
        ...             "type": "Decision",
        ...             "id": "check",
        ...             "condition": {"op": "gt", "args": ["value", 10]},
        ...             "then_steps": [{"type": "SetOutput", "value": 1}],
        ...             "else_steps": [{"type": "SetOutput", "value": 0}],
        ...         }
        ...     ],
        ... }
        >>> result = compile_sir_to_proof(sir, input_value=15)
        >>> assert 'source' in result
        >>> assert 'sir' in result
        >>> assert 'bundle' in result
        >>> assert 'hashes' in result
        >>> assert 'HMASTER' in result['hashes']
    """
    # Step 1: SIR → RLang
    rlang_source = sir_to_rlang(sir)
    
    # Step 2: RLang → ProofBundle (pass SIR for auto fn_registry generation)
    # Normalize SIR to dict if needed
    if isinstance(sir, dict):
        sir_dict = sir
    elif isinstance(sir, DecisionPipeline):
        from semantic_compiler_core.sir_model import sir_to_dict
        sir_dict = sir_to_dict(sir)
    else:
        sir_dict = None
    
    proof_result = run_with_proof(rlang_source, input_value, fn_registry=fn_registry, sir=sir_dict)
    
    # Step 3: Normalize SIR dict
    if isinstance(sir, dict):
        from semantic_compiler_core.sir_model import sir_from_dict, sir_to_dict
        sir_obj = sir_from_dict(sir)
        sir_dict = sir_to_dict(sir_obj)
    elif isinstance(sir, DecisionPipeline):
        from semantic_compiler_core.sir_model import sir_to_dict
        sir_dict = sir_to_dict(sir)
    else:
        raise TypeError(f"Expected dict or DecisionPipeline, got {type(sir).__name__}")
    
    # Return complete result
    return {
        'source': rlang_source,
        'sir': sir_dict,
        'bundle': proof_result['bundle'],
        'hashes': proof_result['hashes'],
    }

