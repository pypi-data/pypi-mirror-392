"""
Test the public API of semantic-compiler-core.

These tests verify that the deterministic core API works correctly
without any LLM dependencies.
"""

import pytest
from semantic_compiler_core import sir_to_rlang, compile_sir_to_proof, run_with_proof


def test_basic_sir_to_rlang():
    """Test that sir_to_rlang converts SIR dict to RLang source."""
    sir = {
        "type": "DecisionPipeline",
        "name": "main",
        "input_name": "value",
        "steps": [
            {
                "type": "Decision",
                "id": "value_gt_10",
                "condition": {"op": "gt", "args": ["value", 10]},
                "then_steps": [{"type": "SetOutput", "value": 1}],
                "else_steps": [{"type": "SetOutput", "value": 0}],
            }
        ],
    }
    
    rlang_source = sir_to_rlang(sir)
    assert isinstance(rlang_source, str)
    assert "pipeline main(Int)" in rlang_source
    assert "ret_1" in rlang_source
    assert "ret_0" in rlang_source


def test_compile_sir_to_proof():
    """Test the convenience function that compiles SIR all the way to proof."""
    sir = {
        "type": "DecisionPipeline",
        "name": "main",
        "input_name": "value",
        "steps": [
            {
                "type": "Decision",
                "id": "value_gt_10",
                "condition": {"op": "gt", "args": ["value", 10]},
                "then_steps": [{"type": "SetOutput", "value": 1}],
                "else_steps": [{"type": "SetOutput", "value": 0}],
            }
        ],
    }
    
    bundle = compile_sir_to_proof(sir, input_value=15)
    
    # Verify structure
    assert "source" in bundle
    assert "sir" in bundle
    assert "bundle" in bundle
    assert "hashes" in bundle
    
    # Verify source is RLang code
    assert isinstance(bundle["source"], str)
    assert "pipeline main(Int)" in bundle["source"]
    
    # Verify proof bundle structure (legacy structure used by semantic-compiler-core)
    # semantic-compiler-core uses legacy keys: program, steps, branches
    # NOT the rich structure: ir, trp
    assert "program" in bundle["bundle"] or "steps" in bundle["bundle"] or "branches" in bundle["bundle"], \
        "bundle must contain legacy keys: 'program' or 'steps'/'branches'"
    
    # Verify hashes exist (v0.2.4+ guarantees these exist)
    assert "hashes" in bundle
    assert "HMASTER" in bundle["hashes"]
    assert bundle["hashes"]["HMASTER"] is not None, "HMASTER must exist (proof engine v0.2.4+)"
    assert "H_IR" in bundle["hashes"]
    assert "HRICH" in bundle["hashes"]
    assert bundle["hashes"]["HRICH"] is not None, "HRICH must exist (proof engine v0.2.4+)"
    
    # Verify hash format (64 hex characters)
    assert len(bundle["hashes"]["HMASTER"]) == 64
    assert len(bundle["hashes"]["HRICH"]) == 64


def test_run_with_proof():
    """Test run_with_proof with RLang source directly."""
    rlang_source = """
fn ret_1(x: Int) -> Int;
fn ret_0(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
"""
    
    result = run_with_proof(rlang_source, input_value=15)
    
    assert "bundle" in result
    assert "hashes" in result
    assert "HMASTER" in result["hashes"]
    
    # Verify proof bundle structure (legacy structure used by semantic-compiler-core)
    # semantic-compiler-core uses legacy keys: program, steps, branches
    assert "program" in result["bundle"] or "steps" in result["bundle"] or "branches" in result["bundle"], \
        "bundle must contain legacy keys: 'program' or 'steps'/'branches'"
    # Hashes may be None if backend doesn't provide them
    # But if they exist, they should be valid
    if result["hashes"]["HMASTER"] is not None:
        assert len(result["hashes"]["HMASTER"]) == 64, "HMASTER must be 64 hex characters if present"
    if result["hashes"]["HRICH"] is not None:
        assert len(result["hashes"]["HRICH"]) == 64, "HRICH must be 64 hex characters if present"


def test_deterministic_output():
    """Test that same SIR produces same RLang output."""
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
    
    # Compile twice
    source1 = sir_to_rlang(sir)
    source2 = sir_to_rlang(sir)
    
    # Should be byte-for-byte identical
    assert source1 == source2


def test_invalid_sir_raises_error():
    """Test that invalid SIR raises appropriate errors."""
    # Missing required fields
    invalid_sir = {
        "type": "DecisionPipeline",
        # Missing "name", "input_name", "steps"
    }
    
    with pytest.raises((ValueError, TypeError)):
        sir_to_rlang(invalid_sir)

