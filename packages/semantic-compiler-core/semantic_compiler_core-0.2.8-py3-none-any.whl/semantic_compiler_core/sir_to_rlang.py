"""
Deterministic SIR → RLang Translation

This module converts validated SIR v0.1 pipelines into canonical, compilable RLang source code.

Physics-Layer Constraints:
- Deterministic formatting (4-space indentation, no trailing spaces, stable ordering)
- Pure expressions only (no side effects, no randomness)
- Canonical output (byte-for-byte identical for identical SIR)
- Respects RLang Physics invariants (determinism, canonicalization, IR compatibility)
"""

import os
from typing import Any, Optional

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
)
from . import logger

# Debug flag controlled by SC_DEBUG environment variable
DEBUG = os.environ.get("SC_DEBUG", "0") == "1"


def safe_debug(msg: str) -> None:
    """Safely log debug message, catching BrokenPipeError."""
    try:
        logger.debug(msg)
    except BrokenPipeError:
        pass


# Operator mapping: SIR → RLang
OP_MAP = {
    "gt": ">",
    "lt": "<",
    "ge": ">=",
    "le": "<=",
    "eq": "==",
    "neq": "!=",
    # Note: "in", "not_in", "between" are not yet supported in RLang v0.2.1
    # They will need to be lowered to supported operators
}


def make_output_fn_name(value: int) -> str:
    """
    Convert an integer output value into a valid RLang function name.
    
    Examples:
        1   → ret_1
        0   → ret_0
        -1  → ret_neg_1
        -50 → ret_neg_50
        None → ret_null (for null literals, though not supported in SIR v0.1)
    """
    # Handle None (null literal) - not supported in SIR v0.1 but handle gracefully
    if value is None:
        return "ret_null"
    
    if isinstance(value, bool):
        # Avoid bool subclass of int weirdness
        value = int(value)
    
    if value < 0:
        fn_name = f"ret_neg_{abs(value)}"
    else:
        fn_name = f"ret_{value}"
    
    if DEBUG:
        safe_debug(f"make_output_fn_name: value={value} → {fn_name}")
    
    return fn_name


def _escape_string(value: str) -> str:
    """
    Escape string literals for RLang.
    Deterministic: same string → same escaped output.
    """
    # Escape backslashes first
    value = value.replace("\\", "\\\\")
    # Escape quotes
    value = value.replace('"', '\\"')
    # Escape newlines
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    return f'"{value}"'


def _format_literal(value: Any) -> str:
    """
    Format a JSON-safe literal value as RLang literal.
    Deterministic: same value → same formatted output.
    """
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        # Normalize float representation (deterministic)
        if value.is_integer():
            return str(int(value))
        # Use fixed precision for determinism
        return f"{value:.10f}".rstrip("0").rstrip(".")
    elif isinstance(value, str):
        return _escape_string(value)
    else:
        raise ValueError(f"Unsupported literal type: {type(value).__name__}")


def _format_field_access(field_name: str) -> str:
    """
    Format field access as RLang attribute access.
    Deterministic: same field → same output.
    """
    # Field names in SIR are strings like "amount", "vendor", etc.
    # In RLang, we access via __value.field_name
    return f"__value.{field_name}"


def predicate_to_rlang(
    pred: Predicate,
    input_name: str = "value",
    input_type: Optional[InputType] = None,
    strict: bool = False
) -> str:
    """
    Convert SIR Predicate to RLang comparison expression.
    
    SIR: {"op": "gt", "args": ["value", 10]}
    RLang: (__value > 10)  (if input_name is "value" and scalar input)
    
    SIR: {"op": "gt", "args": ["income", 50000]}
    RLang: (__value.income > 50000)  (if input_type is record with "income" field)
    
    Deterministic: same predicate → same RLang expression.
    
    Args:
        pred: Predicate to convert
        input_name: Name of the input variable
        input_type: Optional input type (scalar or record)
        strict: If True, validate operator exists in OP_MAP before conversion
    """
    if pred.op not in OP_MAP:
        if strict:
            raise ValueError(
                f"Unsupported operator '{pred.op}' in strict mode. "
                f"Supported: {', '.join(sorted(OP_MAP.keys()))}"
            )
        # Handle unsupported operators by raising error
        # In future, these could be lowered to supported operators
        raise ValueError(
            f"Unsupported predicate operator '{pred.op}'. "
            f"Supported: {', '.join(sorted(OP_MAP.keys()))}"
        )
    
    if len(pred.args) < 2:
        raise ValueError(f"Predicate must have at least 2 args, got {len(pred.args)}")
    
    left_arg = pred.args[0]
    right_arg = pred.args[1]
    
    # Left side: determine if this is a field access (SIR v0.2)
    if isinstance(left_arg, str):
        # Check if left_arg is a field name (not input_name)
        if input_type is not None and isinstance(input_type, InputTypeRecord):
            # Record input: check if left_arg is a field
            if left_arg in input_type.fields:
                # Field access: __value.field_name
                left_expr = f"__value.{left_arg}"
            elif left_arg == input_name:
                # Direct reference to record itself (rare, but possible)
                left_expr = "__value"
            else:
                # Unknown field: treat as field access (will be caught by validator)
                left_expr = f"__value.{left_arg}"
        else:
            # Scalar input: if left_arg matches input_name, use __value
            if left_arg == input_name:
                left_expr = "__value"
            else:
                # Field-like reference in scalar context: use __value.field (backward compat)
                left_expr = f"__value.{left_arg}"
    else:
        left_expr = _format_literal(left_arg)
    
    # Right side: always a literal
    right_expr = _format_literal(right_arg)
    
    op_symbol = OP_MAP[pred.op]
    
    # Parenthesize for deterministic parsing
    return f"({left_expr} {op_symbol} {right_expr})"


def boolexpr_to_rlang(
    b: BoolExpr,
    input_name: str = "value",
    input_type: Optional[InputType] = None,
    strict: bool = False
) -> str:
    """
    Convert SIR BoolExpr to RLang boolean expression.
    
    SIR: {"combiner": "all", "terms": [pred1, pred2]}
    RLang: ((<pred1>) && (<pred2>))
    
    Deterministic: same BoolExpr → same RLang expression.
    Terms are processed in order (deterministic).
    """
    if b.combiner == "not":
        if len(b.terms) != 1:
            raise ValueError(f"'not' combiner must have exactly 1 term, got {len(b.terms)}")
        term_expr = condexpr_to_rlang(b.terms[0], input_name, input_type, strict)
        # Parenthesize for deterministic parsing
        return f"(!({term_expr}))"
    
    elif b.combiner == "all":
        if len(b.terms) < 1:
            raise ValueError(f"'all' combiner must have at least 1 term")
        # Process terms in order (deterministic)
        term_exprs = [condexpr_to_rlang(term, input_name, input_type, strict) for term in b.terms]
        # Parenthesize each term and combine with &&
        parenthesized = [f"({expr})" for expr in term_exprs]
        return f"({' && '.join(parenthesized)})"
    
    elif b.combiner == "any":
        if len(b.terms) < 1:
            raise ValueError(f"'any' combiner must have at least 1 term")
        # Process terms in order (deterministic)
        term_exprs = [condexpr_to_rlang(term, input_name, input_type, strict) for term in b.terms]
        # Parenthesize each term and combine with ||
        parenthesized = [f"({expr})" for expr in term_exprs]
        return f"({' || '.join(parenthesized)})"
    
    else:
        raise ValueError(f"Unknown BoolExpr combiner: {b.combiner}")


def condexpr_to_rlang(
    expr: CondExpr,
    input_name: str = "value",
    input_type: Optional[InputType] = None,
    strict: bool = False
) -> str:
    """
    Convert SIR CondExpr (Predicate or BoolExpr) to RLang expression.
    
    Deterministic: same CondExpr → same RLang expression.
    """
    if isinstance(expr, Predicate):
        return predicate_to_rlang(expr, input_name, input_type, strict)
    elif isinstance(expr, BoolExpr):
        return boolexpr_to_rlang(expr, input_name, input_type, strict)
    else:
        raise TypeError(f"Unknown CondExpr type: {type(expr).__name__}")


def _indent(text: str, level: int) -> str:
    """
    Indent text by level * 4 spaces.
    Deterministic: same input → same output.
    """
    if not text:
        return ""
    indent_str = "    " * level  # Exactly 4 spaces per level
    lines = text.split("\n")
    # Don't indent empty lines at start/end
    result_lines = []
    for i, line in enumerate(lines):
        if line.strip():  # Non-empty line
            result_lines.append(indent_str + line)
        elif i == 0 or i == len(lines) - 1:
            # Empty line at start or end: skip (no blank lines at top/bottom)
            continue
        else:
            # Empty line in middle: preserve but don't indent
            result_lines.append("")
    return "\n".join(result_lines)


def setoutput_to_rlang(step: SetOutputStep, indent_level: int = 1, strict: bool = False) -> str:
    """
    Convert SIR SetOutputStep to RLang function name.
    
    SIR: SetOutputStep(value="FLAG")
    RLang: ret_FLAG (function name for returning this value)
    
    Deterministic: same step → same RLang function name.
    
    Args:
        step: SetOutputStep to convert
        indent_level: Indentation level (unused, kept for compatibility)
        strict: If True, validate SetOutput value is string or int
    """
    if strict:
        if not isinstance(step.value, (str, int, float, bool)) and step.value is not None:
            raise ValueError(f"Invalid SetOutput value type in strict mode: {type(step.value).__name__}")
        if isinstance(step.value, str):
            # Validate string can be sanitized to valid function name
            sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in step.value)[:20]
            if not sanitized or sanitized[0].isdigit():
                raise ValueError(f"SetOutput string value cannot be converted to valid function name: {step.value}")
    
    value_expr = _format_literal(step.value)
    # Generate a deterministic function name based on the value
    # This will be used to create a helper function
    if isinstance(step.value, str):
        # Sanitize string for function name
        func_name = "ret_" + "".join(c if c.isalnum() or c == "_" else "_" for c in step.value)[:20]
    else:
        func_name = make_output_fn_name(step.value)
    return func_name


def decisionstep_to_rlang(
    step: DecisionStep,
    indent_level: int = 1,
    input_name: str = "value",
    input_type: Optional[InputType] = None,
    strict: bool = False
) -> str:
    """
    Convert SIR DecisionStep to RLang if-else expression.
    
    SIR: DecisionStep(condition=C, then_steps=T, else_steps=F)
    RLang:
        if (<C>) {
            <translate T>
        } else {
            <translate F>
        }
    
    Deterministic: same step → same RLang expression.
    
    Args:
        step: DecisionStep to convert
        indent_level: Indentation level
        input_name: Name of the input variable
        input_type: Optional input type
        strict: If True, validate step structure and branches produce valid RLang
    """
    if step.condition is None:
        raise ValueError("DecisionStep must have a non-None condition")
    
    if strict:
        # Validate step structure
        if not step.then_steps:
            raise ValueError("DecisionStep must have non-empty then_steps in strict mode")
        if not step.else_steps:
            raise ValueError("DecisionStep must have non-empty else_steps in strict mode")
        # Validate branches produce legitimate RLang steps
        # Check that then_steps and else_steps contain at least one valid step
        if not isinstance(step.then_steps, list) or len(step.then_steps) == 0:
            raise ValueError("DecisionStep.then_steps must be a non-empty list in strict mode")
        if not isinstance(step.else_steps, list) or len(step.else_steps) == 0:
            raise ValueError("DecisionStep.else_steps must be a non-empty list in strict mode")
    
    # Convert condition to use __value instead of field access
    condition_expr = condexpr_to_rlang(step.condition, input_name, input_type, strict)
    
    # Translate then_steps (should be a single expression/function call)
    then_body = steps_to_rlang(step.then_steps, indent_level + 1, input_name, input_type, strict)
    
    # Translate else_steps (should be a single expression/function call)
    else_body = steps_to_rlang(step.else_steps, indent_level + 1, input_name, input_type, strict)
    
    # Format if-else with deterministic indentation
    indent_str = "    " * indent_level
    result = f"if ({condition_expr}) {{\n"
    if then_body:
        result += _indent(then_body, indent_level + 1) + "\n"
    else:
        # Empty then branch: use default function name (never emit __value as step)
        # ret_0 will be generated as a helper function
        # RLang will call ret_0 with the pipeline input automatically
        result += indent_str + "    ret_0\n"
    result += indent_str + "} else {\n"
    if else_body:
        result += _indent(else_body, indent_level + 1) + "\n"
    else:
        # Empty else branch: use default function name (never emit __value as step)
        # ret_0 will be generated as a helper function
        # RLang will call ret_0 with the pipeline input automatically
        result += indent_str + "    ret_0\n"
    result += indent_str + "}"
    
    return result


def steps_to_rlang(
    steps: list[Step],
    indent_level: int = 1,
    input_name: str = "value",
    input_type: Optional[InputType] = None,
    strict: bool = False
) -> str:
    """
    Convert list of SIR Steps to RLang expression.
    
    Steps are processed in order (deterministic).
    For RLang pipelines, we expect a single top-level expression.
    
    Deterministic: same steps → same RLang expression.
    
    CRITICAL: Never returns "__value" as a standalone step.
    Empty branches must return a function name (e.g., ret_0).
    """
    if not steps:
        # Empty steps: return a default function name
        # This should not happen in valid SIR, but we handle it defensively
        # Use ret_0 as a default function (RLang will call it with pipeline input)
        return "ret_0"
    
    # If there's only one step, return it directly
    if len(steps) == 1:
        step = steps[0]
        if isinstance(step, DecisionStep):
            return decisionstep_to_rlang(step, indent_level, input_name, input_type, strict)
        elif isinstance(step, SetOutputStep):
            return setoutput_to_rlang(step, indent_level, strict)
        else:
            raise TypeError(f"Unknown Step type: {type(step).__name__}")
    
    # Multiple steps: chain them (though SIR v0.1 typically has single decision)
    # For now, take the last step as the result
    # This is a simplification - full implementation would chain steps
    last_step = steps[-1]
    if isinstance(last_step, DecisionStep):
        return decisionstep_to_rlang(last_step, indent_level, input_name, input_type, strict)
    elif isinstance(last_step, SetOutputStep):
        return setoutput_to_rlang(last_step, indent_level, strict)
    else:
        raise TypeError(f"Unknown Step type: {type(last_step).__name__}")


def _determine_type_from_value(value: Any) -> str:
    """
    Infer RLang type from JSON-safe value.
    Deterministic: same value → same type.
    """
    if value is None:
        return "Unit"
    elif isinstance(value, bool):
        return "Bool"
    elif isinstance(value, int):
        return "Int"
    elif isinstance(value, float):
        return "Float"
    elif isinstance(value, str):
        return "String"
    else:
        # Default to Int for unknown types (conservative)
        return "Int"


def sir_to_rlang(sir: DecisionPipeline, strict: bool = False) -> str:
    """
    Deterministically convert a validated SIR v0.1 pipeline
    into canonical, compilable RLang source code.
    
    Physics-Layer Guarantees:
    - Deterministic formatting (4-space indentation, no trailing spaces)
    - Stable ordering (pipeline header, main function, steps)
    - Byte-for-byte identical output for identical SIR
    - Pure expressions only (no side effects, no randomness)
    - Directly compilable by rlang-compiler PyPI package
    
    Args:
        sir: Validated DecisionPipeline object
        strict: If True, perform strict validation:
            - Validate operator exists in OP_MAP
            - Validate SIR fields (type, input_name, steps)
            - Validate then/else produce legitimate RLang steps
            - Raise clean semantic errors with no printing
        
    Returns:
        RLang source code string (deterministic, canonical)
        
    Raises:
        ValueError: If SIR contains unsupported constructs or fails strict validation
        TypeError: If SIR structure is invalid
    """
    if DEBUG:
        safe_debug(f"DEBUG_sir_to_rlang: Starting SIR→RLang conversion")
        safe_debug(f"DEBUG_sir_to_rlang: SIR name = {sir.name}")
        safe_debug(f"DEBUG_sir_to_rlang: SIR input_name = {sir.input_name}")
        safe_debug(f"DEBUG_sir_to_rlang: SIR steps count = {len(sir.steps)}")
    
    if not isinstance(sir, DecisionPipeline):
        raise TypeError(f"Expected DecisionPipeline, got {type(sir).__name__}")
    
    if not sir.steps:
        raise ValueError("Pipeline must have at least one step")
    
    # STRICT MODE VALIDATION
    if strict:
        # Validate canonical SIR form
        if sir.type != "DecisionPipeline":
            raise ValueError(f"Invalid SIR: type must be 'DecisionPipeline', got '{sir.type}'")
        if not sir.input_name:
            raise ValueError("Invalid SIR: missing field 'input_name'")
        if not sir.steps:
            raise ValueError("Invalid SIR: missing field 'steps'")
        
        # Validate each step structure
        for i, step in enumerate(sir.steps):
            if isinstance(step, DecisionStep):
                if step.condition is None:
                    raise ValueError(f"Invalid SIR: DecisionStep at index {i} missing 'condition'")
                if not step.then_steps:
                    raise ValueError(f"Invalid SIR: DecisionStep at index {i} missing 'then_steps'")
                if not step.else_steps:
                    raise ValueError(f"Invalid SIR: DecisionStep at index {i} missing 'else_steps'")
    
    # Determine input/output types from pipeline structure (SIR v0.2)
    # For SIR v0.1 (scalar), we use Int as default
    input_type_str = "Int"  # Default: pipeline input is Int
    output_type = "Int"  # Default: pipeline output is Int
    
    # NEW (SIR v0.2): Determine input type from sir.input_type
    record_type_name = None
    if sir.input_type is not None:
        if isinstance(sir.input_type, InputTypeScalar):
            input_type_str = sir.input_type.dtype
        elif isinstance(sir.input_type, InputTypeRecord):
            # Generate record type name from pipeline name (deterministic)
            base_name = sir.name if sir.name else "Input"
            record_type_name = base_name.capitalize()
            # Ensure valid identifier (alphanumeric + underscore)
            record_type_name = "".join(c if c.isalnum() or c == "_" else "_" for c in record_type_name)
            if not record_type_name or record_type_name[0].isdigit():
                record_type_name = "Input_" + record_type_name
            input_type_str = record_type_name
    
    # Try to infer output type from last SetOutputStep
    for step in reversed(sir.steps):
        if isinstance(step, SetOutputStep):
            output_type = _determine_type_from_value(step.value)
            break
    
    # Generate pipeline name (sanitized, deterministic)
    pipeline_name = sir.name if sir.name else "pipeline"
    # Ensure valid identifier (alphanumeric + underscore)
    pipeline_name = "".join(c if c.isalnum() or c == "_" else "_" for c in pipeline_name)
    if not pipeline_name or pipeline_name[0].isdigit():
        pipeline_name = "pipeline_" + pipeline_name
    
    # Collect all unique return values to generate helper functions
    return_values = set()
    def collect_return_values(steps):
        for step in steps:
            if isinstance(step, SetOutputStep):
                return_values.add(step.value)
            elif isinstance(step, DecisionStep):
                collect_return_values(step.then_steps)
                collect_return_values(step.else_steps)
    
    collect_return_values(sir.steps)
    
    # CRITICAL: Always ensure ret_0 exists for empty branch fallback
    # Check if ret_0 is needed (when steps_to_rlang returns ret_0(__value))
    # We'll add it to return_values if not present
    if 0 not in return_values:
        # Check if we have any empty branches that would need ret_0
        def has_empty_branches(steps):
            for step in steps:
                if isinstance(step, DecisionStep):
                    if not step.then_steps or not step.else_steps:
                        return True
                    if has_empty_branches(step.then_steps) or has_empty_branches(step.else_steps):
                        return True
            return False
        
        if has_empty_branches(sir.steps) or not sir.steps:
            return_values.add(0)  # Add 0 to ensure ret_0 is generated
    
    # Generate helper function declarations for return values
    helper_functions = []
    func_name_map = {}  # Map value -> function name
    for value in sorted(return_values, key=str):  # Deterministic ordering
        if isinstance(value, str):
            func_name = "ret_" + "".join(c if c.isalnum() or c == "_" else "_" for c in value)[:20]
        else:
            func_name = make_output_fn_name(value)
        func_name_map[value] = func_name
        helper_functions.append(f"fn {func_name}(x: {input_type_str}) -> {output_type};")
    
    # NEW (SIR v0.2): Generate record type declaration if needed
    result_parts = []  # Initialize result_parts for building RLang output
    if sir.input_type is not None and isinstance(sir.input_type, InputTypeRecord):
        # Emit record type declaration (fields sorted alphabetically for determinism)
        record_fields = []
        for field_name, field_type in sorted(sir.input_type.fields.items()):
            record_fields.append(f"    {field_name}: {field_type}")
        
        record_decl = f"type {record_type_name} = Record {{\n"
        record_decl += ",\n".join(record_fields)
        record_decl += "\n};"
        result_parts.append(record_decl)
        result_parts.append("")  # Blank line after type declaration
    
    # Generate pipeline body expression
    input_name = sir.input_name if sir.input_name else "value"
    pipeline_body = steps_to_rlang(
        sir.steps,
        indent_level=1,
        input_name=input_name,
        input_type=sir.input_type,  # NEW: pass input_type
        strict=strict
    )
    
    # Replace function names in pipeline body with actual function names
    # (This is already handled by setoutput_to_rlang, but we need to ensure consistency)
    
    # Generate complete RLang code
    # Format: deterministic, no trailing spaces, no blank lines at top/bottom
    # RLang syntax: pipeline name(Type) -> Type { expression }
    # Note: result_parts already initialized above if record type exists
    
    # Add helper function declarations
    if helper_functions:
        result_parts.extend(helper_functions)
        result_parts.append("")  # Blank line between functions and pipeline
    
    # Add pipeline declaration
    result_parts.append(f"pipeline {pipeline_name}({input_type_str}) -> {output_type} {{")
    if pipeline_body:
        result_parts.append("    " + pipeline_body.replace("\n", "\n    "))
    result_parts.append("}")
    
    result = "\n".join(result_parts)
    
    # Remove trailing whitespace from each line (deterministic)
    lines = result.split("\n")
    cleaned_lines = [line.rstrip() for line in lines]
    result = "\n".join(cleaned_lines)
    
    # Remove blank lines at top and bottom
    lines = result.split("\n")
    # Remove leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    # Remove trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()
    
    final_result = "\n".join(lines)
    
    if DEBUG:
        safe_debug(f"DEBUG_sir_to_rlang: RLang generation complete")
        safe_debug(f"DEBUG_sir_to_rlang: RLang length = {len(final_result)} chars")
        safe_debug(f"DEBUG_sir_to_rlang: RLang preview (first 200 chars): {final_result[:200]}...")
        # Log operator mappings used
        for op in ["gt", "lt", "ge", "le", "eq", "neq"]:
            if op in OP_MAP and OP_MAP[op] in final_result:
                safe_debug(f"DEBUG_sir_to_rlang: Operator '{op}' → '{OP_MAP[op]}' found in output")
    
    return final_result
