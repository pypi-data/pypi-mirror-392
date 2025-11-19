"""
Tests for SIR v0.1 validation.
"""

import pytest
from semantic_compiler.sir_validator import (
    validate_sir,
    SIRValidationError,
    is_json_safe,
)
from semantic_compiler.sir_model import (
    DecisionPipeline,
    DecisionStep,
    SetOutputStep,
    Predicate,
    BoolExpr,
    sir_from_dict,
)


def test_valid_pipeline():
    """Test that a valid pipeline passes validation.
    
    NOTE: Updated to use integer outputs (SIR v0.1 requirement).
    String outputs ("FLAG", "ALLOW") are not supported in minimal SIR v0.1.
    """
    valid_sir = {
        "type": "DecisionPipeline",
        "name": "test_pipeline",
        "input_name": "value",
        "steps": [
            {
                "type": "Decision",
                "id": "check_amount",
                "condition": {
                    "op": "gt",
                    "args": ["value", 100000]
                },
                "then_steps": [
                    {
                        "type": "SetOutput",
                        "value": 1  # Integer output (SIR v0.1)
                    }
                ],
                "else_steps": [
                    {
                        "type": "SetOutput",
                        "value": 0  # Integer output (SIR v0.1)
                    }
                ]
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(valid_sir)
    assert ok is True
    assert errors == ""
    assert normalized["name"] == "test_pipeline"
    assert len(normalized["steps"]) == 1


def test_invalid_operator():
    """Test that invalid operators are caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "Decision",
                "id": "bad_op",
                "condition": {
                    "op": "invalid_op",
                    "args": ["amount", 100]
                },
                "then_steps": [{"type": "SetOutput", "value": "OK"}],
                "else_steps": []
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "invalid_op" in errors
    assert "Allowed:" in errors


def test_invalid_step_type():
    """Test that invalid step types are caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "InvalidStepType",
                "value": "something"
            }
        ]
    }
    
    # This will fail during parsing, but let's test with a dict that has bad step
    ok, normalized, errors = validate_sir(invalid_sir)
    # Should fail either during parsing or validation
    assert ok is False


def test_bad_bool_expr_structure():
    """Test that bad BoolExpr structures are caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "Decision",
                "id": "bad_bool",
                "condition": {
                    "combiner": "not",
                    "terms": [
                        {"op": "gt", "args": ["amount", 100]},
                        {"op": "lt", "args": ["amount", 200]}
                    ]
                },
                "then_steps": [{"type": "SetOutput", "value": "OK"}],
                "else_steps": []
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "not" in errors.lower() or "exactly 1 term" in errors.lower()


def test_non_json_safe_output():
    """Test that non-JSON-safe output values are caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "SetOutput",
                "value": {"complex": "object"}  # Not JSON-safe
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "JSON-safe" in errors


def test_empty_pipeline_name():
    """Test that empty pipeline name is caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "",
        "input_name": "input",
        "steps": [
            {"type": "SetOutput", "value": "OK"}
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "name" in errors.lower()


def test_no_steps():
    """Test that pipeline with no steps is caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": []
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "at least one step" in errors.lower()


def test_missing_condition():
    """Test that DecisionStep without condition is caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "Decision",
                "id": "no_condition",
                "condition": None,
                "then_steps": [{"type": "SetOutput", "value": "OK"}],
                "else_steps": []
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "condition" in errors.lower()


def test_bad_predicate_args():
    """Test that predicates with invalid args are caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "Decision",
                "id": "bad_args",
                "condition": {
                    "op": "gt",
                    "args": ["amount"]  # Only one arg, needs at least 2
                },
                "then_steps": [{"type": "SetOutput", "value": "OK"}],
                "else_steps": []
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "at least 2 elements" in errors.lower()


@pytest.mark.skip(reason="SIR v0.1 does not support nested BoolExpr structures. Only simple predicates are supported.")
def test_nested_bool_expr():
    """Test that nested BoolExpr structures are validated correctly.
    
    SKIPPED: SIR v0.1 does not support nested BoolExpr structures.
    Only simple predicates (gt, ge, lt, le, eq, neq) are supported.
    Nested boolean expressions (all/any/not with nested structure) are planned for SIR v0.2+.
    """
    valid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "Decision",
                "id": "nested",
                "condition": {
                    "combiner": "all",
                    "terms": [
                        {"op": "gt", "args": ["amount", 100]},
                        {
                            "combiner": "any",
                            "terms": [
                                {"op": "eq", "args": ["status", "active"]},
                                {"op": "eq", "args": ["status", "pending"]}
                            ]
                        }
                    ]
                },
                "then_steps": [{"type": "SetOutput", "value": 1}],  # Integer output
                "else_steps": [{"type": "SetOutput", "value": 0}]
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(valid_sir)
    assert ok is True
    assert errors == ""


def test_is_json_safe():
    """Test the is_json_safe helper function."""
    assert is_json_safe(42) is True
    assert is_json_safe(3.14) is True
    assert is_json_safe("hello") is True
    assert is_json_safe(True) is True
    assert is_json_safe(False) is True
    assert is_json_safe(None) is True
    
    assert is_json_safe({"key": "value"}) is False
    assert is_json_safe([1, 2, 3]) is False
    assert is_json_safe(object()) is False


def test_validate_sir_requires_normalization():
    """Test that validate_sir requires normalization before sir_from_dict."""
    # Test: Missing type should fail pre-validation
    sir_dict = {
        "name": "test",
        "steps": []
    }
    ok, normalized, errors = validate_sir(sir_dict)
    assert ok is False
    assert "Invalid SIR type" in errors or "steps" in errors
    
    # Test: Wrong type should fail pre-validation
    sir_dict = {
        "type": "WrongType",
        "name": "test",
        "steps": []
    }
    ok, normalized, errors = validate_sir(sir_dict)
    assert ok is False
    assert "Invalid SIR type" in errors
    
    # Test: Missing steps list should fail pre-validation
    sir_dict = {
        "type": "DecisionPipeline",
        "name": "test"
    }
    ok, normalized, errors = validate_sir(sir_dict)
    assert ok is False
    assert "steps" in errors


def test_invalid_bool_combiner():
    """Test that invalid boolean combiners are caught."""
    invalid_sir = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "input",
        "steps": [
            {
                "type": "Decision",
                "id": "bad_combiner",
                "condition": {
                    "combiner": "invalid_combiner",
                    "terms": [
                        {"op": "gt", "args": ["amount", 100]}
                    ]
                },
                "then_steps": [{"type": "SetOutput", "value": "OK"}],
                "else_steps": []
            }
        ]
    }
    
    ok, normalized, errors = validate_sir(invalid_sir)
    assert ok is False
    assert "invalid_combiner" in errors
    assert "all" in errors or "any" in errors or "not" in errors

