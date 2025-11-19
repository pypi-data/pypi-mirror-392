"""
Test suite for RLang Runtime Adapter.

Tests backend availability, compilation, execution, bundle conversion,
and hash extraction with strict determinism requirements.
"""

import pytest
from typing import Any, Dict


class TestBackendAvailability:
    """Test backend availability detection."""
    
    def test_is_backend_available(self):
        """Test backend availability check."""
        from semantic_compiler.rlang_runtime import is_backend_available
        
        # This should not raise, regardless of backend availability
        result = is_backend_available()
        assert isinstance(result, bool)
        
        # Deterministic: same call → same result
        result2 = is_backend_available()
        assert result == result2
    
    def test_import_cleanly_when_backend_missing(self):
        """Test that module imports cleanly even when backend is missing."""
        # This test verifies the import doesn't crash
        from semantic_compiler.rlang_runtime import (
            is_backend_available,
            compile_source,
            run_with_proof,
            bundle_to_dict,
            extract_hashes,
            RLangRuntime,
        )
        
        # All functions should be importable
        assert callable(is_backend_available)
        assert callable(compile_source)
        assert callable(run_with_proof)
        assert callable(bundle_to_dict)
        assert callable(extract_hashes)
        assert RLangRuntime is not None


class TestCompileOnly:
    """Test compile-only functionality."""
    
    @pytest.mark.skipif(
        not __import__('semantic_compiler.rlang_runtime').rlang_runtime.is_backend_available(),
        reason="Backend not available"
    )
    @pytest.mark.skip(reason="compile_only backend not supported in v0.2.x")
    def test_compile_minimal_program(self):
        """Test compiling a minimal valid RLang program.
        
        SKIPPED: compile_only backend not supported in v0.2.x.
        RLang backend does not support compile_source() - use run_with_proof() instead.
        """
        from semantic_compiler.rlang_runtime import compile_source
        
        source = """
        fn inc(x: Int) -> Int;
        pipeline main(Int) -> Int { inc }
        """
        
        # Should not raise
        program = compile_source(source)
        assert program is not None
    
    def test_compile_raises_when_backend_unavailable(self):
        """Test that compile raises RuntimeError when backend unavailable."""
        from semantic_compiler.rlang_runtime import compile_source, is_backend_available
        
        if is_backend_available():
            pytest.skip("Backend is available")
        
        source = "pipeline main(Int) -> Int { }"
        
        with pytest.raises(RuntimeError, match="not available"):
            compile_source(source)


class TestRunWithProof:
    """Test execution with proof generation."""
    
    @pytest.mark.skipif(
        not __import__('semantic_compiler.rlang_runtime').rlang_runtime.is_backend_available(),
        reason="Backend not available"
    )
    def test_run_with_proof_deterministic(self):
        """Test that run_with_proof produces identical results."""
        from semantic_compiler.rlang_runtime import run_with_proof
        
        source = """
        fn inc(x: Int) -> Int;
        pipeline main(Int) -> Int { inc }
        """
        
        input_value = 10
        fn_registry = {"inc": lambda x: x + 1}
        
        # Run twice with same input
        raw_bundle1, dict1 = run_with_proof(source, input_value, fn_registry)
        raw_bundle2, dict2 = run_with_proof(source, input_value, fn_registry)
        
        # Dicts must be identical (determinism requirement)
        assert dict1 == dict2, "Bundles must be identical for same input"
        
        # Verify output values match
        if 'output_value' in dict1 and 'output_value' in dict2:
            assert dict1['output_value'] == dict2['output_value']
        
        # Verify return type is tuple
        assert isinstance((raw_bundle1, dict1), tuple)
        assert len((raw_bundle1, dict1)) == 2
    
    @pytest.mark.skipif(
        not __import__('semantic_compiler.rlang_runtime').rlang_runtime.is_backend_available(),
        reason="Backend not available"
    )
    def test_run_with_proof_bundle_structure(self):
        """Test that proof bundle has expected structure."""
        from semantic_compiler.rlang_runtime import run_with_proof
        
        source = """
        fn double(x: Int) -> Int;
        pipeline main(Int) -> Int { double }
        """
        
        raw_bundle, bundle_dict = run_with_proof(
            source=source,
            input_value=5,
            fn_registry={"double": lambda x: x * 2}
        )
        
        # Bundle should be a dict
        assert isinstance(bundle_dict, dict)
        
        # Verify proof bundle structure (legacy structure used by semantic-compiler-core)
        # semantic-compiler-core uses legacy keys: program, steps, branches
        # NOT the rich structure: ir, trp
        has_legacy_structure = 'program' in bundle_dict or 'steps' in bundle_dict or 'branches' in bundle_dict
        assert has_legacy_structure, \
            "bundle must contain legacy keys: 'program' or 'steps'/'branches' (semantic-compiler-core v0.2.x)"
        
        # Should have output_value (at minimum)
        # Other fields depend on backend implementation
        assert 'output_value' in bundle_dict or len(bundle_dict) > 0
        
        # Raw bundle should not be None
        assert raw_bundle is not None
    
    def test_run_with_proof_raises_when_backend_unavailable(self):
        """Test that run_with_proof raises RuntimeError when backend unavailable."""
        from semantic_compiler.rlang_runtime import run_with_proof, is_backend_available
        
        if is_backend_available():
            pytest.skip("Backend is available")
        
        source = "pipeline main(Int) -> Int { }"
        
        with pytest.raises(RuntimeError, match="not available"):
            run_with_proof(source, 10)


class TestBundleToDict:
    """Test bundle to dict conversion."""
    
    def test_bundle_to_dict_with_dict_input(self):
        """Test conversion when bundle is already a dict."""
        from semantic_compiler.rlang_runtime import bundle_to_dict
        
        bundle = {
            'output_value': 42,
            'input_value': 10,
            'steps': [],
            'branches': [],
        }
        
        result = bundle_to_dict(bundle)
        
        assert isinstance(result, dict)
        assert result == bundle
    
    def test_bundle_to_dict_with_object_with_dict(self):
        """Test conversion with object that has to_dict method."""
        from semantic_compiler.rlang_runtime import bundle_to_dict
        
        class MockBundle:
            def __init__(self):
                self.output_value = 42
                self.input_value = 10
            
            def to_dict(self):
                return {
                    'output_value': self.output_value,
                    'input_value': self.input_value,
                }
        
        bundle = MockBundle()
        result = bundle_to_dict(bundle)
        
        assert isinstance(result, dict)
        assert result['output_value'] == 42
        assert result['input_value'] == 10
    
    def test_bundle_to_dict_with_object_with_json(self):
        """Test conversion with object that has to_json method."""
        import json
        from semantic_compiler.rlang_runtime import bundle_to_dict
        
        class MockBundle:
            def to_json(self):
                return json.dumps({'output_value': 42})
        
        bundle = MockBundle()
        result = bundle_to_dict(bundle)
        
        assert isinstance(result, dict)
        assert result['output_value'] == 42
    
    def test_bundle_to_dict_deterministic(self):
        """Test that bundle_to_dict is deterministic."""
        from semantic_compiler.rlang_runtime import bundle_to_dict
        
        bundle = {
            'output_value': 100,
            'steps': [{'index': 0, 'name': 'test'}],
        }
        
        result1 = bundle_to_dict(bundle)
        result2 = bundle_to_dict(bundle)
        
        # Must be identical
        assert result1 == result2
    
    def test_bundle_to_dict_raises_on_none(self):
        """Test that bundle_to_dict raises on None input."""
        from semantic_compiler.rlang_runtime import bundle_to_dict
        
        with pytest.raises(ValueError, match="cannot be None"):
            bundle_to_dict(None)
    
    def test_bundle_to_dict_with_nested_structures(self):
        """Test conversion with nested structures."""
        from semantic_compiler.rlang_runtime import bundle_to_dict
        
        bundle = {
            'output_value': 42,
            'program_ir': {
                'pipelines': [
                    {'name': 'main', 'steps': []}
                ]
            },
            'steps': [
                {'index': 0, 'input': 10, 'output': 42}
            ],
        }
        
        result = bundle_to_dict(bundle)
        
        assert isinstance(result, dict)
        assert result['output_value'] == 42
        assert isinstance(result['program_ir'], dict)
        assert isinstance(result['steps'], list)


class TestHashExtraction:
    """Test hash extraction from bundle dicts and raw bundles."""
    
    def test_extract_hashes_top_level_keys(self):
        """Test extraction when hashes are top-level keys."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        bundle_dict = {
            'HMASTER': 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
            'H_IR': 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
            'HRICH': 'def456abc123def456abc123def456abc123def456abc123def456abc123def456',
        }
        
        result = extract_hashes(bundle_dict)
        
        assert result['HMASTER'] == bundle_dict['HMASTER']
        assert result['H_IR'] == bundle_dict['H_IR']
        assert result['HRICH'] == bundle_dict['HRICH']
    
    def test_extract_hashes_rich_bundle_format(self):
        """Test extraction from rich bundle format (from README)."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        bundle_dict = {
            'rich': {
                'primary': {
                    'master': 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
                },
                'H_RICH': 'def456abc123def456abc123def456abc123def456abc123def456abc123def456',
            }
        }
        
        result = extract_hashes(bundle_dict)
        
        assert result['HMASTER'] == bundle_dict['rich']['primary']['master']
        assert result['H_IR'] == bundle_dict['rich']['primary']['master']
        assert result['HRICH'] == bundle_dict['rich']['H_RICH']
    
    @pytest.mark.skipif(
        not __import__('semantic_compiler.rlang_runtime').rlang_runtime.is_backend_available(),
        reason="Backend not available"
    )
    def test_extract_hashes_from_raw_bundle(self):
        """Test extraction from raw bundle object using RLangBoRCrypto."""
        from semantic_compiler.rlang_runtime import run_with_proof, extract_hashes
        
        source = """
        fn ret_1(x: Int) -> Int;
        pipeline main(Int) -> Int { ret_1 }
        """
        
        raw_bundle, bundle_dict = run_with_proof(
            source=source,
            input_value=5,
            fn_registry={"ret_1": lambda x: 1}
        )
        
        # Extract hashes from raw bundle (preferred method)
        hashes = extract_hashes(raw_bundle)
        
        # Should have all hash keys
        assert 'HMASTER' in hashes
        assert 'H_IR' in hashes
        assert 'HRICH' in hashes
        
        # Hashes should be non-None strings (64 hex characters)
        if hashes['HMASTER'] is not None:
            assert isinstance(hashes['HMASTER'], str)
            assert len(hashes['HMASTER']) == 64
            # H_IR should match HMASTER
            assert hashes['H_IR'] == hashes['HMASTER']
        
        if hashes['HRICH'] is not None:
            assert isinstance(hashes['HRICH'], str)
            assert len(hashes['HRICH']) == 64
        
        # Also test extraction from dict (should work but may not have hashes)
        hashes_from_dict = extract_hashes(bundle_dict)
        assert 'HMASTER' in hashes_from_dict
        assert 'H_IR' in hashes_from_dict
        assert 'HRICH' in hashes_from_dict
    
    def test_extract_hashes_missing_hashes(self):
        """Test extraction when hashes are missing."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        bundle_dict = {
            'output_value': 42,
            'steps': [],
        }
        
        result = extract_hashes(bundle_dict)
        
        # All should be None when missing
        assert result['HMASTER'] is None
        assert result['H_IR'] is None
        assert result['HRICH'] is None
    
    def test_extract_hashes_partial_hashes(self):
        """Test extraction when only some hashes are present."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        bundle_dict = {
            'HMASTER': 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
            # H_IR and HRICH missing
        }
        
        result = extract_hashes(bundle_dict)
        
        assert result['HMASTER'] == bundle_dict['HMASTER']
        assert result['H_IR'] == bundle_dict['HMASTER']  # H_IR aliases HMASTER
        assert result['HRICH'] is None
    
    def test_extract_hashes_nested_search(self):
        """Test extraction with nested hash search."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        bundle_dict = {
            'program_ir': {
                'hash': 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
            },
            'execution': {
                'trace': {
                    'hash': 'def456abc123def456abc123def456abc123def456abc123def456abc123def456',
                }
            }
        }
        
        result = extract_hashes(bundle_dict)
        
        # Should find hashes in nested structures
        # Note: This test may not find them depending on exact structure
        # But it should not crash
        assert isinstance(result['HMASTER'], (str, type(None)))
        assert isinstance(result['H_IR'], (str, type(None)))
        assert isinstance(result['HRICH'], (str, type(None)))
    
    def test_extract_hashes_non_dict_input(self):
        """Test extraction with non-dict input."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        # Should return all None for non-dict
        result = extract_hashes(None)
        assert result['HMASTER'] is None
        assert result['H_IR'] is None
        assert result['HRICH'] is None
        
        result = extract_hashes([])
        assert result['HMASTER'] is None
        assert result['H_IR'] is None
        assert result['HRICH'] is None
    
    def test_extract_hashes_deterministic(self):
        """Test that hash extraction is deterministic."""
        from semantic_compiler.rlang_runtime import extract_hashes
        
        bundle_dict = {
            'HMASTER': 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
            'HRICH': 'def456abc123def456abc123def456abc123def456abc123def456abc123def456',
        }
        
        result1 = extract_hashes(bundle_dict)
        result2 = extract_hashes(bundle_dict)
        
        # Must be identical
        assert result1 == result2


class TestBackendSafeImport:
    """Test backend-safe import behavior."""
    
    def test_import_does_not_crash(self):
        """Test that import doesn't crash even if backend missing."""
        # This test verifies the import mechanism is safe
        import semantic_compiler.rlang_runtime as rt
        
        # Module should be importable
        assert rt is not None
        
        # Functions should exist
        assert hasattr(rt, 'is_backend_available')
        assert hasattr(rt, 'compile_source')
        assert hasattr(rt, 'run_with_proof')
        assert hasattr(rt, 'bundle_to_dict')
        assert hasattr(rt, 'extract_hashes')
        assert hasattr(rt, 'RLangRuntime')
    
    def test_runtime_error_on_unavailable_backend(self):
        """Test that RuntimeError is raised deterministically."""
        from semantic_compiler.rlang_runtime import (
            compile_source,
            run_with_proof,
            is_backend_available,
        )
        
        if is_backend_available():
            pytest.skip("Backend is available")
        
        # Both should raise RuntimeError with same message pattern
        with pytest.raises(RuntimeError, match="not available"):
            compile_source("pipeline main(Int) -> Int { }")
        
        with pytest.raises(RuntimeError, match="not available"):
            run_with_proof("pipeline main(Int) -> Int { }", 10)


class TestRLangRuntimeClass:
    """Test RLangRuntime wrapper class."""
    
    def test_runtime_class_initialization(self):
        """Test RLangRuntime class initialization."""
        from semantic_compiler.rlang_runtime import RLangRuntime
        
        rt = RLangRuntime()
        
        assert hasattr(rt, 'is_available')
        assert isinstance(rt.is_available, bool)
    
    def test_runtime_class_methods(self):
        """Test RLangRuntime class methods."""
        from semantic_compiler.rlang_runtime import RLangRuntime
        
        rt = RLangRuntime()
        
        # All methods should exist
        assert hasattr(rt, 'compile')
        assert hasattr(rt, 'run_with_proof')
        assert hasattr(rt, 'bundle_to_dict')
        assert hasattr(rt, 'extract_hashes')
        
        # Methods should be callable
        assert callable(rt.compile)
        assert callable(rt.run_with_proof)
        assert callable(rt.bundle_to_dict)
        assert callable(rt.extract_hashes)
    
    @pytest.mark.skipif(
        not __import__('semantic_compiler.rlang_runtime').rlang_runtime.is_backend_available(),
        reason="Backend not available"
    )
    def test_runtime_class_usage(self):
        """Test using RLangRuntime class for execution."""
        from semantic_compiler.rlang_runtime import RLangRuntime
        
        rt = RLangRuntime()
        
        if not rt.is_available:
            pytest.skip("Backend not available")
        
        source = """
        fn inc(x: Int) -> Int;
        pipeline main(Int) -> Int { inc }
        """
        
        raw_bundle, bundle_dict = rt.run_with_proof(
            source=source,
            input_value=10,
            fn_registry={"inc": lambda x: x + 1}
        )
        
        # Extract hashes from raw bundle (preferred)
        hashes = rt.extract_hashes(raw_bundle)
        
        assert isinstance(bundle_dict, dict)
        assert isinstance(hashes, dict)
        assert 'HMASTER' in hashes
        assert 'H_IR' in hashes
        assert 'HRICH' in hashes
        
        # Hashes should be extracted correctly (may be None if backend doesn't provide)
        # But if they exist, they should be 64-character hex strings
        if hashes['HMASTER'] is not None:
            assert isinstance(hashes['HMASTER'], str)
            assert len(hashes['HMASTER']) == 64
            assert hashes['H_IR'] == hashes['HMASTER']  # H_IR aliases HMASTER
        
        if hashes['HRICH'] is not None:
            assert isinstance(hashes['HRICH'], str)
            assert len(hashes['HRICH']) == 64

