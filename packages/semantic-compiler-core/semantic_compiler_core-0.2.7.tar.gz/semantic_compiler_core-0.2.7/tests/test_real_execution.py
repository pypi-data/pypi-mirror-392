"""
Test real RLang execution backend (no mocks).

These tests verify that semantic-compiler-core uses the REAL
rlang-compiler backend and produces deterministic proof bundles.
"""

import pytest
from semantic_compiler_core import compile_sir_to_proof, run_with_proof
from semantic_compiler_core.rlang_runtime import is_backend_available


@pytest.mark.skipif(
    not is_backend_available(),
    reason="RLang backend not available - install rlang-compiler>=0.2.4"
)
class TestRealExecution:
    """Test real execution with RLang backend."""
    
    def test_compile_sir_to_proof_produces_real_bundle(self):
        """Test that compile_sir_to_proof produces real proof bundle (no mock)."""
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
        
        # Verify NO mock keys
        assert "mock" not in result, "Result must NOT contain 'mock' key - real backend required"
        assert "mock" not in str(result), "Result must NOT contain 'mock' anywhere"
        
        # Verify real bundle structure
        assert "bundle" in result
        bundle = result["bundle"]
        assert isinstance(bundle, dict)
        
        # Verify bundle has real execution data (not mock)
        # Bundle should have output_value or output
        assert "output_value" in bundle or "output" in bundle, \
            "Bundle must have output_value or output (real execution)"
        
        # Verify hashes are real (not None, not "mock")
        assert "hashes" in result
        hashes = result["hashes"]
        assert "HMASTER" in hashes
        assert "H_IR" in hashes
        assert "HRICH" in hashes
        
        # Hashes should be real strings (64 hex chars) or None
        # But NOT "mock" strings
        if hashes["HMASTER"] is not None:
            assert isinstance(hashes["HMASTER"], str)
            assert len(hashes["HMASTER"]) == 64
            assert hashes["HMASTER"] != "mock"
            assert "mock" not in hashes["HMASTER"].lower()
        
        if hashes["HRICH"] is not None:
            assert isinstance(hashes["HRICH"], str)
            assert len(hashes["HRICH"]) == 64
            assert hashes["HRICH"] != "mock"
            assert "mock" not in hashes["HRICH"].lower()
    
    def test_run_with_proof_uses_real_backend(self):
        """Test that run_with_proof uses real RLang backend."""
        rlang_source = """
pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
"""
        
        result = run_with_proof(rlang_source, input_value=15)
        
        # Verify NO mock
        assert "mock" not in result
        assert "mock" not in str(result)
        
        # Verify real bundle
        assert "bundle" in result
        bundle = result["bundle"]
        assert isinstance(bundle, dict)
        
        # Verify real execution output
        assert "output_value" in bundle or "output" in bundle
        
        # Verify real hashes
        assert "hashes" in result
        hashes = result["hashes"]
        assert "HMASTER" in hashes
        assert "H_IR" in hashes
        assert "HRICH" in hashes
    
    def test_execution_output_is_correct(self):
        """Test that execution produces correct output values."""
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
        
        # Test with value > 10
        result1 = compile_sir_to_proof(sir, input_value=15)
        bundle1 = result1["bundle"]
        output1 = bundle1.get("output_value") or bundle1.get("output")
        assert output1 == 1, f"Expected output 1 for input 15, got {output1}"
        
        # Test with value <= 10
        result2 = compile_sir_to_proof(sir, input_value=5)
        bundle2 = result2["bundle"]
        output2 = bundle2.get("output_value") or bundle2.get("output")
        assert output2 == 0, f"Expected output 0 for input 5, got {output2}"
    
    def test_bundle_contains_ir_and_trp(self):
        """Test that bundle contains IR and TRP (real execution trace)."""
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
        bundle = result["bundle"]
        
        # Bundle should have IR (intermediate representation) or TRP (trace)
        # These are proof of real execution
        has_ir = "ir" in bundle or "program_ir" in bundle
        has_trp = "trp" in bundle or "steps" in bundle or "branches" in bundle
        
        assert has_ir or has_trp, \
            "Bundle must contain IR or TRP (proof of real execution)"
    
    def test_backend_error_on_invalid_source(self):
        """Test that invalid RLang source raises proper backend error."""
        invalid_source = "this is not valid RLang code"
        
        with pytest.raises(RuntimeError, match="execution failed|compilation failed"):
            run_with_proof(invalid_source, input_value=10)

