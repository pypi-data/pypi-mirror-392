"""
SIR v0.1 Validator: Validates and normalizes Semantic IR structures.
"""

from typing import Any, Dict, List, Set, Tuple, Union
import json

from .sir_model import (
    DecisionPipeline,
    DecisionStep,
    SetOutputStep,
    Predicate,
    BoolExpr,
    CondExpr,
    Step,
    InputType,
    InputTypeScalar,
    InputTypeRecord,
    sir_from_dict,
    sir_to_dict,
)


class SIRValidationError(Exception):
    """Raised when SIR validation fails."""
    pass


# Allowed operators
ALLOWED_CONDITION_OPS = {"gt", "lt", "ge", "le", "eq", "neq", "in", "not_in", "between"}
ALLOWED_BOOL_COMBINERS = {"all", "any", "not"}

# JSON-safe types
JSON_SAFE_TYPES = (int, float, str, bool, type(None))


def is_json_safe(value: Any) -> bool:
    """Check if a value is JSON-safe (int, float, str, bool, None)."""
    return isinstance(value, JSON_SAFE_TYPES)


def validate_input_type(input_type: InputType, path: str = "") -> List[str]:
    """
    Validate an InputType (SIR v0.2).
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    if isinstance(input_type, InputTypeScalar):
        if input_type.dtype not in {"Int", "Float", "String", "Bool"}:
            errors.append(
                f"{path}: Invalid scalar type '{input_type.dtype}'. "
                f"Allowed: Int, Float, String, Bool"
            )
    
    elif isinstance(input_type, InputTypeRecord):
        if not isinstance(input_type.fields, dict):
            errors.append(f"{path}: Record 'fields' must be a dict")
        elif len(input_type.fields) == 0:
            errors.append(f"{path}: Record must have at least one field")
        else:
            # Validate field names and types
            for field_name, field_type in input_type.fields.items():
                if not isinstance(field_name, str) or not field_name.strip():
                    errors.append(
                        f"{path}.fields[{field_name}]: Field name must be non-empty string"
                    )
                elif not field_name.replace("_", "").isalnum():
                    errors.append(
                        f"{path}.fields[{field_name}]: Field name must be valid identifier "
                        f"(alphanumeric + underscore)"
                    )
                if field_type not in {"Int", "Float", "String", "Bool"}:
                    errors.append(
                        f"{path}.fields[{field_name}]: Invalid field type '{field_type}'. "
                        f"Allowed: Int, Float, String, Bool"
                    )
    else:
        errors.append(
            f"{path}: Invalid InputType: expected InputTypeScalar or InputTypeRecord, "
            f"got {type(input_type).__name__}"
        )
    
    return errors


def _collect_field_references_from_cond(expr: CondExpr, input_name: str, fields: Set[str]) -> None:
    """
    Helper: recursively collect field names from condition expressions.
    Field names are strings in predicate args that are not the input_name itself.
    """
    if isinstance(expr, Predicate):
        # First arg is field name if it's a string
        if expr.args and isinstance(expr.args[0], str):
            field_ref = expr.args[0]
            # If it's not the input_name itself, it's a field reference
            if field_ref != input_name:
                fields.add(field_ref)
    elif isinstance(expr, BoolExpr):
        for term in expr.terms:
            _collect_field_references_from_cond(term, input_name, fields)


def validate_field_references(
    pipeline: DecisionPipeline,
    path: str = ""
) -> List[str]:
    """
    Validate that all field references in predicates match input_type.fields (SIR v0.2).
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Collect all field references from conditions
    referenced_fields = set()
    
    def collect_from_step(step: Step):
        if isinstance(step, DecisionStep):
            if step.condition:
                _collect_field_references_from_cond(step.condition, pipeline.input_name, referenced_fields)
            for s in step.then_steps:
                collect_from_step(s)
            for s in step.else_steps:
                collect_from_step(s)
    
    for step in pipeline.steps:
        collect_from_step(step)
    
    # If input_type is record, check all referenced fields exist
    if isinstance(pipeline.input_type, InputTypeRecord):
        defined_fields = set(pipeline.input_type.fields.keys())
        for field_name in referenced_fields:
            if field_name not in defined_fields:
                errors.append(
                    f"{path}: Field '{field_name}' referenced in predicate but not "
                    f"defined in input_type.fields. Defined fields: {sorted(defined_fields)}"
                )
    
    # If input_type is None or scalar, check that no field references exist
    # (except the input_name itself, which is allowed for scalar)
    elif pipeline.input_type is None or isinstance(pipeline.input_type, InputTypeScalar):
        # Remove input_name from referenced fields (it's allowed for scalar)
        referenced_fields.discard(pipeline.input_name)
        
        if referenced_fields:
            errors.append(
                f"{path}: Field references found ({sorted(referenced_fields)}) but "
                f"input_type is scalar or missing. Use record input_type for field access."
            )
    
    return errors


def validate_predicate(pred: Predicate, path: str = "") -> List[str]:
    """
    Validate a Predicate.
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    if pred.op not in ALLOWED_CONDITION_OPS:
        allowed_str = ", ".join(sorted(ALLOWED_CONDITION_OPS))
        errors.append(
            f"{path}: Invalid operator '{pred.op}'. Allowed: {allowed_str}"
        )
    
    if not isinstance(pred.args, list):
        errors.append(f"{path}: Predicate 'args' must be a list, got {type(pred.args).__name__}")
    elif len(pred.args) < 2:
        errors.append(f"{path}: Predicate 'args' must have at least 2 elements")
    else:
        # Validate args are JSON-safe
        for i, arg in enumerate(pred.args):
            if not is_json_safe(arg):
                errors.append(
                    f"{path}.args[{i}]: Value must be JSON-safe (int/float/str/bool/null), "
                    f"got {type(arg).__name__}"
                )
    
    return errors


def validate_bool_expr(expr: BoolExpr, path: str = "", visited: Set[int] = None) -> List[str]:
    """
    Validate a BoolExpr recursively.
    Returns list of error messages (empty if valid).
    """
    if visited is None:
        visited = set()
    
    errors = []
    
    if expr.combiner not in ALLOWED_BOOL_COMBINERS:
        allowed_str = ", ".join(sorted(ALLOWED_BOOL_COMBINERS))
        errors.append(
            f"{path}: Invalid combiner '{expr.combiner}'. Allowed: {allowed_str}"
        )
    
    if expr.combiner == "not":
        if len(expr.terms) != 1:
            errors.append(f"{path}: 'not' combiner must have exactly 1 term, got {len(expr.terms)}")
    elif expr.combiner in ("all", "any"):
        if len(expr.terms) < 1:
            errors.append(f"{path}: '{expr.combiner}' combiner must have at least 1 term")
    
    # Recursively validate terms
    for i, term in enumerate(expr.terms):
        term_path = f"{path}.terms[{i}]"
        
        if isinstance(term, Predicate):
            errors.extend(validate_predicate(term, term_path))
        elif isinstance(term, BoolExpr):
            # Check for circular references using object id
            term_id = id(term)
            if term_id in visited:
                errors.append(f"{term_path}: Circular reference detected in BoolExpr")
            else:
                visited.add(term_id)
                errors.extend(validate_bool_expr(term, term_path, visited))
                visited.discard(term_id)
        else:
            errors.append(
                f"{term_path}: Term must be Predicate or BoolExpr, got {type(term).__name__}"
            )
    
    return errors


def validate_cond_expr(expr: CondExpr, path: str = "", visited: Set[int] = None) -> List[str]:
    """Validate a CondExpr (Predicate or BoolExpr)."""
    if visited is None:
        visited = set()
    
    if isinstance(expr, Predicate):
        return validate_predicate(expr, path)
    elif isinstance(expr, BoolExpr):
        return validate_bool_expr(expr, path, visited)
    else:
        return [f"{path}: Condition must be Predicate or BoolExpr, got {type(expr).__name__}"]


def validate_step(step: Step, path: str = "", visited_steps: Set[int] = None) -> List[str]:
    """
    Validate a Step (DecisionStep or SetOutputStep).
    Returns list of error messages (empty if valid).
    """
    if visited_steps is None:
        visited_steps = set()
    
    errors = []
    
    if isinstance(step, DecisionStep):
        step_path = f"{path}[DecisionStep id='{step.id}']"
        
        if step.condition is None:
            errors.append(f"{step_path}: DecisionStep must have a non-None 'condition'")
        else:
            errors.extend(validate_cond_expr(step.condition, f"{step_path}.condition"))
        
        # Validate then_steps
        for i, then_step in enumerate(step.then_steps):
            then_path = f"{step_path}.then_steps[{i}]"
            step_id = id(then_step)
            if step_id in visited_steps:
                errors.append(f"{then_path}: Circular reference detected in step graph")
            else:
                visited_steps.add(step_id)
                errors.extend(validate_step(then_step, then_path, visited_steps))
                visited_steps.discard(step_id)
        
        # Validate else_steps
        for i, else_step in enumerate(step.else_steps):
            else_path = f"{step_path}.else_steps[{i}]"
            step_id = id(else_step)
            if step_id in visited_steps:
                errors.append(f"{else_path}: Circular reference detected in step graph")
            else:
                visited_steps.add(step_id)
                errors.extend(validate_step(else_step, else_path, visited_steps))
                visited_steps.discard(step_id)
    
    elif isinstance(step, SetOutputStep):
        step_path = f"{path}[SetOutputStep]"
        
        if not is_json_safe(step.value):
            errors.append(
                f"{step_path}: 'value' must be JSON-safe (int/float/str/bool/null), "
                f"got {type(step.value).__name__}"
            )
    
    else:
        errors.append(f"{path}: Step must be DecisionStep or SetOutputStep, got {type(step).__name__}")
    
    return errors


def validate_sir(sir: Union[Dict[str, Any], DecisionPipeline]) -> Tuple[bool, Dict[str, Any], str]:
    """
    Validate and normalize a SIR (Semantic IR).
    
    Before calling sir_from_dict, ensures:
    - normalize_sir_dict() has been applied (if sir is dict)
    - dict["type"] == "DecisionPipeline"
    - "steps" is a list
    
    Args:
        sir: Either a dict or DecisionPipeline object
        
    Returns:
        Tuple of (is_valid: bool, normalized_dict: Dict, error_message: str)
        If valid, error_message is None or empty string.
        If invalid, error_message contains human-readable errors.
    """
    # Convert dict to DecisionPipeline if needed
    if isinstance(sir, dict):
        # Ensure normalization has been applied
        # Check that type is DecisionPipeline
        if sir.get("type") != "DecisionPipeline":
            return False, sir, f"Invalid SIR type: expected 'DecisionPipeline', got '{sir.get('type')}'"
        
        # Check that steps is a list
        if "steps" not in sir or not isinstance(sir.get("steps"), list):
            return False, sir, f"Invalid SIR structure: 'steps' must be a list"
        
        try:
            pipeline = sir_from_dict(sir)
        except Exception as e:
            return False, sir, f"Failed to parse SIR dict: {e}"
    elif isinstance(sir, DecisionPipeline):
        pipeline = sir
    else:
        return False, {}, f"Invalid SIR type: expected dict or DecisionPipeline, got {type(sir).__name__}"
    
    errors = []
    
    # Validate pipeline structure
    if not isinstance(pipeline.name, str) or not pipeline.name.strip():
        errors.append("Pipeline 'name' must be a non-empty string")
    
    # NEW (SIR v0.2): Validate input_type if present
    if pipeline.input_type is not None:
        errors.extend(validate_input_type(pipeline.input_type, "input_type"))
    
    if not isinstance(pipeline.steps, list):
        errors.append("Pipeline 'steps' must be a list")
    elif len(pipeline.steps) == 0:
        errors.append("Pipeline must have at least one step")
    else:
        # Validate each step
        visited_steps = set()
        for i, step in enumerate(pipeline.steps):
            step_path = f"steps[{i}]"
            step_id = id(step)
            if step_id in visited_steps:
                errors.append(f"{step_path}: Duplicate step reference detected")
            else:
                visited_steps.add(step_id)
                errors.extend(validate_step(step, step_path, visited_steps.copy()))
    
    # NEW (SIR v0.2): Validate field references match input_type
    errors.extend(validate_field_references(pipeline, ""))
    
    if errors:
        error_msg = "\n".join(errors)
        return False, sir_to_dict(pipeline), error_msg
    
    # Normalize: convert back to dict (already normalized by to_dict)
    normalized = sir_to_dict(pipeline)
    
    return True, normalized, ""
