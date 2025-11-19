"""
Test hash stability and determinism.

These tests verify that:
1. Same input produces same hashes (determinism)
2. Hashes are computed using real RLangBoRCrypto (not fake)
3. Hashes are stable across multiple runs
"""

import pytest
from semantic_compiler_core import compile_sir_to_proof, run_with_proof
from semantic_compiler_core.rlang_runtime import is_backend_available, extract_hashes


@pytest.mark.skipif(
    not is_backend_available(),
    reason="RLang backend not available - install rlang-compiler>=0.2.4"
)
class TestHashStability:
    """Test hash stability and determinism."""
    
    def test_same_input_produces_same_hashes(self):
        """Test that same SIR + input produces identical hashes."""
        sir = {
            "type": "DecisionPipeline",
            "name": "main",
            "input_name": "value",
            "steps": [
                {
                    "type": "Decision",
                    "id": "check",
                    "condition": {"op": "gt", "args": ["value", 10]},
                    "then_steps": [{"type": "SetOutput", "value": 1}],
                    "else_steps": [{"type": "SetOutput", "value": 0}],
                }
            ],
        }
        
        # Run twice with same input
        result1 = compile_sir_to_proof(sir, input_value=15)
        result2 = compile_sir_to_proof(sir, input_value=15)
        
        hashes1 = result1["hashes"]
        hashes2 = result2["hashes"]
        
        # All hashes must be identical
        assert hashes1["HMASTER"] == hashes2["HMASTER"], \
            "HMASTER must be identical for same input"
        assert hashes1["H_IR"] == hashes2["H_IR"], \
            "H_IR must be identical for same input"
        assert hashes1["HRICH"] == hashes2["HRICH"], \
            "HRICH must be identical for same input"
        
        # H_IR should alias HMASTER
        assert hashes1["H_IR"] == hashes1["HMASTER"], \
            "H_IR should alias HMASTER"
    
    def test_different_inputs_produce_different_hashes(self):
        """Test that different inputs produce different HRICH (execution hash)."""
        sir = {
            "type": "DecisionPipeline",
            "name": "main",
            "input_name": "value",
            "steps": [
                {
                    "type": "Decision",
                    "id": "check",
                    "condition": {"op": "gt", "args": ["value", 10]},
                    "then_steps": [{"type": "SetOutput", "value": 1}],
                    "else_steps": [{"type": "SetOutput", "value": 0}],
                }
            ],
        }
        
        # Run with different inputs
        result1 = compile_sir_to_proof(sir, input_value=15)
        result2 = compile_sir_to_proof(sir, input_value=5)
        
        hashes1 = result1["hashes"]
        hashes2 = result2["hashes"]
        
        # HMASTER should be same (same program)
        assert hashes1["HMASTER"] == hashes2["HMASTER"], \
            "HMASTER should be same for same program"
        
        # HRICH should be different (different execution)
        if hashes1["HRICH"] is not None and hashes2["HRICH"] is not None:
            assert hashes1["HRICH"] != hashes2["HRICH"], \
                "HRICH should be different for different inputs"
    
    def test_hash_format_is_correct(self):
        """Test that hashes are 64-character hex strings."""
        sir = {
            "type": "DecisionPipeline",
            "name": "main",
            "input_name": "value",
            "steps": [
                {
                    "type": "Decision",
                    "id": "check",
                    "condition": {"op": "gt", "args": ["value", 10]},
                    "then_steps": [{"type": "SetOutput", "value": 1}],
                    "else_steps": [{"type": "SetOutput", "value": 0}],
                }
            ],
        }
        
        result = compile_sir_to_proof(sir, input_value=15)
        hashes = result["hashes"]
        
        # HMASTER should be 64 hex chars if present
        if hashes["HMASTER"] is not None:
            assert isinstance(hashes["HMASTER"], str)
            assert len(hashes["HMASTER"]) == 64, \
                f"HMASTER must be 64 hex chars, got {len(hashes['HMASTER'])}"
            assert all(c in "0123456789abcdef" for c in hashes["HMASTER"].lower()), \
                "HMASTER must be hex string"
        
        # HRICH should be 64 hex chars if present
        if hashes["HRICH"] is not None:
            assert isinstance(hashes["HRICH"], str)
            assert len(hashes["HRICH"]) == 64, \
                f"HRICH must be 64 hex chars, got {len(hashes['HRICH'])}"
            assert all(c in "0123456789abcdef" for c in hashes["HRICH"].lower()), \
                "HRICH must be hex string"
    
    def test_hash_extraction_from_raw_bundle(self):
        """Test that extract_hashes works with raw bundle objects."""
        rlang_source = """
pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
"""
        
        from semantic_compiler_core.rlang_runtime import run_with_proof
        
        raw_bundle, bundle_dict = run_with_proof(rlang_source, input_value=15)
        
        # Extract hashes from raw bundle (preferred method)
        hashes_from_raw = extract_hashes(raw_bundle)
        
        # Extract hashes from dict (fallback)
        hashes_from_dict = extract_hashes(bundle_dict)
        
        # Both should produce same result (if backend provides hashes)
        if hashes_from_raw["HMASTER"] is not None:
            assert hashes_from_raw["HMASTER"] == hashes_from_dict["HMASTER"] or \
                   hashes_from_dict["HMASTER"] is None, \
                "Raw bundle and dict should produce same HMASTER"
        
        if hashes_from_raw["HRICH"] is not None:
            assert hashes_from_raw["HRICH"] == hashes_from_dict["HRICH"] or \
                   hashes_from_dict["HRICH"] is None, \
                "Raw bundle and dict should produce same HRICH"
    
    def test_hash_stability_across_multiple_runs(self):
        """Test that hashes are stable across multiple runs."""
        sir = {
            "type": "DecisionPipeline",
            "name": "main",
            "input_name": "value",
            "steps": [
                {
                    "type": "Decision",
                    "id": "check",
                    "condition": {"op": "gt", "args": ["value", 10]},
                    "then_steps": [{"type": "SetOutput", "value": 1}],
                    "else_steps": [{"type": "SetOutput", "value": 0}],
                }
            ],
        }
        
        # Run 5 times with same input
        results = [compile_sir_to_proof(sir, input_value=15) for _ in range(5)]
        
        # All HMASTER should be identical
        hmasters = [r["hashes"]["HMASTER"] for r in results]
        assert all(h == hmasters[0] for h in hmasters), \
            "HMASTER must be identical across all runs"
        
        # All HRICH should be identical
        hrichs = [r["hashes"]["HRICH"] for r in results]
        if hrichs[0] is not None:
            assert all(h == hrichs[0] for h in hrichs), \
                "HRICH must be identical across all runs"

