"""
End-to-end tests: SIR → RLang → Execution → Proof Bundle.

These tests verify the complete pipeline:
1. SIR dict → RLang source (deterministic)
2. RLang source → Proof bundle (real execution)
3. Proof bundle → Hashes (cryptographic)
"""

import pytest
from semantic_compiler_core import (
    sir_to_rlang,
    run_with_proof,
    compile_sir_to_proof,
)
from semantic_compiler_core.rlang_runtime import is_backend_available


@pytest.mark.skipif(
    not is_backend_available(),
    reason="RLang backend not available - install rlang-compiler>=0.2.4"
)
class TestSIRToRLangAndExecute:
    """Test complete SIR → RLang → Execution pipeline."""
    
    def test_end_to_end_compilation(self):
        """Test complete pipeline: SIR → RLang → Proof."""
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
        
        # Step 1: SIR → RLang
        rlang_source = sir_to_rlang(sir)
        assert isinstance(rlang_source, str)
        assert "pipeline main(Int)" in rlang_source
        
        # Step 2: RLang → Proof Bundle
        result = run_with_proof(rlang_source, input_value=15)
        assert "bundle" in result
        assert "hashes" in result
        
        # Step 3: Verify proof bundle
        bundle = result["bundle"]
        assert isinstance(bundle, dict)
        assert "output_value" in bundle or "output" in bundle
        
        # Step 4: Verify hashes
        hashes = result["hashes"]
        assert "HMASTER" in hashes
        assert "H_IR" in hashes
        assert "HRICH" in hashes
    
    def test_compile_sir_to_proof_complete(self):
        """Test compile_sir_to_proof returns complete result."""
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
        
        # Verify complete structure
        assert "source" in result
        assert "sir" in result
        assert "bundle" in result
        assert "hashes" in result
        
        # Verify source is RLang
        assert isinstance(result["source"], str)
        assert "pipeline main(Int)" in result["source"]
        
        # Verify SIR is normalized dict
        assert isinstance(result["sir"], dict)
        assert result["sir"]["name"] == "main"
        
        # Verify bundle has output
        bundle = result["bundle"]
        assert "output_value" in bundle or "output" in bundle
        
        # Verify hashes are present
        hashes = result["hashes"]
        assert "HMASTER" in hashes
        assert "H_IR" in hashes
        assert "HRICH" in hashes
    
    def test_deterministic_rlang_generation(self):
        """Test that same SIR produces same RLang source."""
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
        
        # Generate RLang twice
        source1 = sir_to_rlang(sir)
        source2 = sir_to_rlang(sir)
        
        # Must be byte-for-byte identical
        assert source1 == source2, "RLang source must be deterministic"
    
    def test_deterministic_execution(self):
        """Test that same RLang + input produces same proof bundle."""
        rlang_source = """
pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
"""
        
        # Execute twice
        result1 = run_with_proof(rlang_source, input_value=15)
        result2 = run_with_proof(rlang_source, input_value=15)
        
        # Bundles should be identical
        bundle1 = result1["bundle"]
        bundle2 = result2["bundle"]
        
        # Output should be same
        output1 = bundle1.get("output_value") or bundle1.get("output")
        output2 = bundle2.get("output_value") or bundle2.get("output")
        assert output1 == output2, "Output must be deterministic"
        
        # Hashes should be identical
        assert result1["hashes"]["HMASTER"] == result2["hashes"]["HMASTER"]
        assert result1["hashes"]["HRICH"] == result2["hashes"]["HRICH"]
    
    def test_multiple_decision_steps(self):
        """Test pipeline with multiple decision steps."""
        sir = {
            "type": "DecisionPipeline",
            "name": "main",
            "input_name": "value",
            "steps": [
                {
                    "type": "Decision",
                    "id": "gt_10",
                    "condition": {"op": "gt", "args": ["value", 10]},
                    "then_steps": [
                        {
                            "type": "Decision",
                            "id": "gt_20",
                            "condition": {"op": "gt", "args": ["value", 20]},
                            "then_steps": [{"type": "SetOutput", "value": 2}],
                            "else_steps": [{"type": "SetOutput", "value": 1}],
                        }
                    ],
                    "else_steps": [{"type": "SetOutput", "value": 0}],
                }
            ],
        }
        
        # Test different inputs
        result1 = compile_sir_to_proof(sir, input_value=25)
        result2 = compile_sir_to_proof(sir, input_value=15)
        result3 = compile_sir_to_proof(sir, input_value=5)
        
        bundle1 = result1["bundle"]
        bundle2 = result2["bundle"]
        bundle3 = result3["bundle"]
        
        output1 = bundle1.get("output_value") or bundle1.get("output")
        output2 = bundle2.get("output_value") or bundle2.get("output")
        output3 = bundle3.get("output_value") or bundle3.get("output")
        
        assert output1 == 2, f"Expected 2 for input 25, got {output1}"
        assert output2 == 1, f"Expected 1 for input 15, got {output2}"
        assert output3 == 0, f"Expected 0 for input 5, got {output3}"
    
    def test_complex_condition_with_and(self):
        """Test pipeline with complex condition using 'all'."""
        sir = {
            "type": "DecisionPipeline",
            "name": "main",
            "input_name": "value",
            "steps": [
                {
                    "type": "Decision",
                    "id": "range_check",
                    "condition": {
                        "op": "all",
                        "args": [
                            {"op": "gt", "args": ["value", 10]},
                            {"op": "lt", "args": ["value", 20]},
                        ]
                    },
                    "then_steps": [{"type": "SetOutput", "value": 1}],
                    "else_steps": [{"type": "SetOutput", "value": 0}],
                }
            ],
        }
        
        # Test in range
        result1 = compile_sir_to_proof(sir, input_value=15)
        bundle1 = result1["bundle"]
        output1 = bundle1.get("output_value") or bundle1.get("output")
        assert output1 == 1, f"Expected 1 for input 15 (in range), got {output1}"
        
        # Test out of range (too low)
        result2 = compile_sir_to_proof(sir, input_value=5)
        bundle2 = result2["bundle"]
        output2 = bundle2.get("output_value") or bundle2.get("output")
        assert output2 == 0, f"Expected 0 for input 5 (too low), got {output2}"
        
        # Test out of range (too high)
        result3 = compile_sir_to_proof(sir, input_value=25)
        bundle3 = result3["bundle"]
        output3 = bundle3.get("output_value") or bundle3.get("output")
        assert output3 == 0, f"Expected 0 for input 25 (too high), got {output3}"

