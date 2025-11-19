"""
Deterministic RLang Runtime Adapter

This module provides a clean, deterministic interface to the RLang compiler backend
(PyPI rlang-compiler package). It respects all Physics-layer invariants:

- Deterministic Semantics Invariant
- Deterministic Proof Shape Invariant  
- Single-Source Canonical Representation Invariant

The adapter NEVER re-implements IR, canonicalization, proofs, or hashing.
It delegates all physics-layer operations to the backend compiler.

Physics-Layer Constraints:
- Same (source, input) → same bundle dict (byte-for-byte identical)
- No time, random, UUIDs, or non-deterministic ordering
- dict outputs are stable JSON-safe structures
- bundle_to_dict uses backend's canonicalization if present
"""

import json
from typing import Any, Dict, Optional, Union, Tuple

# Import real RLang backend - REQUIRED dependency
try:
    from rlang.bor import run_program_with_proof, RLangBoRCrypto
    _BACKEND_AVAILABLE = True
except ImportError:
    _BACKEND_AVAILABLE = False
    run_program_with_proof = None
    RLangBoRCrypto = None


def is_backend_available() -> bool:
    """
    Return True iff the RLang compiler backend is importable.
    
    This function is deterministic: same environment → same result.
    """
    return _BACKEND_AVAILABLE


def run_with_proof(
    source: str,
    input_value: Any,
    fn_registry: Optional[Dict[str, Any]] = None
) -> Tuple[Any, Dict[str, Any]]:
    """
    Compile & execute RLang source with deterministic execution,
    returning both the raw bundle object and its dict representation.
    
    Physics-Layer Guarantees:
    - Same (source, input_value, fn_registry) → same bundle
    - Bundle contains deterministic TRP traces
    - No time, random, or non-deterministic metadata
    
    Args:
        source: RLang source code string
        input_value: Input value for pipeline execution
        fn_registry: Optional function registry (dict mapping function names to callables)
        
    Returns:
        Tuple of (raw_bundle, bundle_dict) where:
        - raw_bundle: Original proof bundle object (for hash extraction)
        - bundle_dict: Dict representation of proof bundle
        
    Raises:
        RuntimeError: If backend is unavailable or execution fails
    """
    if not _BACKEND_AVAILABLE:
        raise RuntimeError(
            "RLang compiler backend is not available. "
            "Install with: pip install rlang-compiler>=0.2.4"
        )
    
    if run_program_with_proof is None:
        raise RuntimeError(
            "Backend does not support run_program_with_proof. "
            "Backend may not be properly installed."
        )
    
    # Normalize fn_registry to ensure deterministic behavior
    if fn_registry is None:
        fn_registry = {}
    
    try:
        # Call real RLang backend - NO MOCK, NO FALLBACK
        raw_bundle = run_program_with_proof(
            source=source,
            input_value=input_value,
            fn_registry=fn_registry
        )
        
        # Convert to dict for return
        bundle_dict = bundle_to_dict(raw_bundle)
        return (raw_bundle, bundle_dict)
    except Exception as e:
        raise RuntimeError(f"RLang execution failed: {e}") from e


def bundle_to_dict(bundle: Any) -> Dict[str, Any]:
    """
    Convert backend proof bundle to deterministic dict form.
    
    Physics-Layer Guarantees:
    - Same bundle → same dict (byte-for-byte identical)
    - Dict is JSON-safe (no non-serializable objects)
    - Uses backend's canonicalization if present
    - No timestamps, UUIDs, or non-deterministic metadata
    
    Args:
        bundle: Backend proof bundle object
        
    Returns:
        Deterministic dict representation of proof bundle
        
    Raises:
        RuntimeError: If bundle cannot be converted
        ValueError: If bundle structure is invalid
    """
    if bundle is None:
        raise ValueError("Bundle cannot be None")
    
    # Try to get dict representation from bundle
    # Backend bundles may have to_dict(), to_json(), or dict() conversion
    
    # First, try to get rich bundle structure if available
    rich_bundle_data = None
    if RLangBoRCrypto is not None:
        try:
            crypto = RLangBoRCrypto(bundle)
            rich = crypto.to_rich_bundle()
            if hasattr(rich, 'rich') and isinstance(rich.rich, dict):
                rich_bundle_data = rich.rich
            # Also check if bundle has ir/trp directly
            if hasattr(bundle, 'ir') or hasattr(bundle, 'trp'):
                if rich_bundle_data is None:
                    rich_bundle_data = {}
                if hasattr(bundle, 'ir'):
                    rich_bundle_data['ir'] = _normalize_value(bundle.ir)
                if hasattr(bundle, 'trp'):
                    rich_bundle_data['trp'] = _normalize_value(bundle.trp)
        except Exception:
            pass
    
    # Method 1: Check for to_dict() method
    if hasattr(bundle, 'to_dict'):
        try:
            result = bundle.to_dict()
            if isinstance(result, dict):
                # Merge rich bundle data if available (ir, trp, etc.)
                if rich_bundle_data is not None:
                    result.update(rich_bundle_data)
                # RICH MERGE FIX: If bundle has rich attribute, merge it
                if hasattr(bundle, "rich") and bundle.rich:
                    rich_data = bundle.rich
                    if isinstance(rich_data, dict):
                        result.update(rich_data)  # MUST merge ir, trp, primary, etc.
                return result
        except Exception:
            pass
    
    # Method 2: Check for to_json() method (returns string)
    if hasattr(bundle, 'to_json'):
        try:
            json_str = bundle.to_json()
            if isinstance(json_str, str):
                return json.loads(json_str)
        except Exception:
            pass
    
    # Method 3: Check if bundle is already a dict
    if isinstance(bundle, dict):
        return bundle
    
    # Method 4: Try dict() conversion
    try:
        result = dict(bundle)
        if isinstance(result, dict):
            return result
    except (TypeError, ValueError):
        pass
    
    # Method 5: Try accessing common attributes and building dict
    # This is backend-specific but common patterns
    result = {}
    
    # RICH MERGE FIX: If bundle has rich attribute, merge it first
    if hasattr(bundle, "rich") and bundle.rich:
        rich_data = bundle.rich
        if isinstance(rich_data, dict):
            result.update(rich_data)  # MUST merge ir, trp, primary, etc.
        else:
            # If rich is not a dict, try to normalize it
            result["rich"] = _normalize_value(rich_data)
    
    # Common bundle attributes (from Physics spec and README)
    common_attrs = [
        'output_value',
        'output',
        'input_value',
        'input',
        'steps',
        'branches',
        'program_ir',
        'ir',  # IR from rich bundle
        'trp',  # TRP from rich bundle
        'version',
        'language',
        'entry_pipeline',
        'primary',  # Primary proof data
        'H_RICH',  # Rich hash
        'metadata',
    ]
    
    for attr in common_attrs:
        if hasattr(bundle, attr):
            value = getattr(bundle, attr)
            # Recursively convert nested objects
            result[attr] = _normalize_value(value)
    
    # Merge rich bundle data if we got it earlier (ensures ir, trp are included)
    if rich_bundle_data is not None:
        result.update(rich_bundle_data)
    
    if not result:
        raise RuntimeError(
            f"Cannot convert bundle to dict. "
            f"Bundle type: {type(bundle).__name__}, "
            f"Available methods: {[m for m in dir(bundle) if not m.startswith('_')]}"
        )
    
    return result


def _normalize_value(value: Any) -> Any:
    """
    Normalize a value to JSON-safe form.
    Recursively converts nested structures.
    
    Deterministic: same value → same normalized output.
    """
    if value is None:
        return None
    elif isinstance(value, (bool, int, float, str)):
        return value
    elif isinstance(value, dict):
        return {k: _normalize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    elif hasattr(value, '__dict__'):
        # Object with __dict__: convert to dict
        return {k: _normalize_value(v) for k, v in value.__dict__.items()}
    elif hasattr(value, 'to_dict'):
        # Object with to_dict method
        return _normalize_value(value.to_dict())
    else:
        # Fallback: convert to string representation
        # This is deterministic but may lose structure
        return str(value)


def extract_hashes(bundle_or_dict: Union[Any, Dict[str, Any]]) -> Dict[str, Optional[str]]:
    """
    Extract physics-layer hashes from proof bundle using RLangBoRCrypto.
    
    This function accepts either:
    1. Raw bundle object (preferred) - uses RLangBoRCrypto for hash extraction
    2. Bundle dict - falls back to dict-based extraction
    
    Physics-Layer Hashes (from Physics spec):
    - HMASTER: Program IR hash (Hash(canonical(program_ir)))
    - H_IR: Alias for HMASTER (program IR hash)
    - HRICH: Execution trace hash (Hash(canonical(proof_bundle)))
    
    Args:
        bundle_or_dict: Either raw proof bundle object or dict representation
    
    Returns:
        Dict with keys: 'HMASTER', 'H_IR', 'HRICH'
        Values are hash strings or None if not found
    """
    result = {
        'HMASTER': None,
        'H_IR': None,
        'HRICH': None,
    }
    
    # If it's already a dict, try dict-based extraction first
    if isinstance(bundle_or_dict, dict):
        # Try to extract from rich bundle structure if present
        if 'rich' in bundle_or_dict:
            rich = bundle_or_dict['rich']
            if isinstance(rich, dict):
                # Extract from rich['primary']['master']
                if 'primary' in rich:
                    primary = rich['primary']
                    if isinstance(primary, dict) and 'master' in primary:
                        master_value = primary['master']
                        if isinstance(master_value, str):
                            result['HMASTER'] = master_value
                            result['H_IR'] = master_value
                
                # Extract from rich['H_RICH']
                if 'H_RICH' in rich:
                    hrich_value = rich['H_RICH']
                    if isinstance(hrich_value, str):
                        result['HRICH'] = hrich_value
        
        # Also check top-level keys for backward compatibility
        if result['HMASTER'] is None and 'HMASTER' in bundle_or_dict:
            value = bundle_or_dict['HMASTER']
            if isinstance(value, str):
                result['HMASTER'] = value
                result['H_IR'] = value
        
        if result['H_IR'] is None and 'H_IR' in bundle_or_dict:
            value = bundle_or_dict['H_IR']
            if isinstance(value, str):
                result['H_IR'] = value
                if result['HMASTER'] is None:
                    result['HMASTER'] = value
        
        if result['HRICH'] is None and 'HRICH' in bundle_or_dict:
            value = bundle_or_dict['HRICH']
            if isinstance(value, str):
                result['HRICH'] = value
        
        return result
    
    # If it's a raw bundle object, use RLangBoRCrypto (REAL BACKEND ONLY)
    if RLangBoRCrypto is not None:
        try:
            crypto = RLangBoRCrypto(bundle_or_dict)
            rich = crypto.to_rich_bundle()
            
            # Extract from rich.rich dict structure
            if hasattr(rich, 'rich') and isinstance(rich.rich, dict):
                rich_dict = rich.rich
                
                # Extract HMASTER from rich['primary']['master']
                if 'primary' in rich_dict:
                    primary = rich_dict['primary']
                    if isinstance(primary, dict) and 'master' in primary:
                        master_value = primary['master']
                        if isinstance(master_value, str):
                            result['HMASTER'] = master_value
                            result['H_IR'] = master_value
                    
                    # Extract H_IR from rich['primary'].get('ir_hash') if available
                    if isinstance(primary, dict) and 'ir_hash' in primary:
                        ir_hash_value = primary['ir_hash']
                        if isinstance(ir_hash_value, str):
                            result['H_IR'] = ir_hash_value
                            if result['HMASTER'] is None:
                                result['HMASTER'] = ir_hash_value
                
                # Extract HRICH from rich['H_RICH']
                if 'H_RICH' in rich_dict:
                    hrich_value = rich_dict['H_RICH']
                    if isinstance(hrich_value, str):
                        result['HRICH'] = hrich_value
            
            return result
        except Exception:
            # If RLangBoRCrypto fails, fall back to dict-based extraction
            # by converting bundle to dict first
            try:
                bundle_dict = bundle_to_dict(bundle_or_dict)
                return extract_hashes(bundle_dict)
            except Exception:
                # If all else fails, return None values
                return result
    
    # If backend crypto is not available, try converting to dict
    try:
        bundle_dict = bundle_to_dict(bundle_or_dict)
        return extract_hashes(bundle_dict)
    except Exception:
        return result


class RLangRuntime:
    """
    Wrapper class for RLang runtime operations.
    
    Provides a clean, deterministic API for:
    - Backend availability checking
    - Execution with proof generation
    - Bundle conversion and hash extraction
    """
    
    def __init__(self):
        """Initialize runtime. Checks backend availability."""
        self._available = is_backend_available()
    
    @property
    def is_available(self) -> bool:
        """Return True if backend is available."""
        return self._available
    
    def run_with_proof(
        self,
        source: str,
        input_value: Any,
        fn_registry: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Compile and execute with proof generation.
        
        Args:
            source: RLang source code string
            input_value: Input value for pipeline
            fn_registry: Optional function registry
            
        Returns:
            Tuple of (raw_bundle, bundle_dict)
        """
        return run_with_proof(source, input_value, fn_registry)
    
    def extract_hashes(self, bundle_or_dict: Union[Any, Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """
        Extract physics-layer hashes from bundle.
        
        Args:
            bundle_or_dict: Either raw bundle object or dict representation
            
        Returns:
            Dict with HMASTER, H_IR, HRICH keys
        """
        return extract_hashes(bundle_or_dict)
    
    def bundle_to_dict(self, bundle: Any) -> Dict[str, Any]:
        """
        Convert bundle to dict.
        
        Args:
            bundle: Proof bundle object
            
        Returns:
            Dict representation
        """
        return bundle_to_dict(bundle)
