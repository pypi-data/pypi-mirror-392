from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional, Union

# -------------------------------
# Primitive operator types
# -------------------------------

ConditionOp = Literal[
    "gt", "lt", "ge", "le",
    "eq", "neq",
    "in", "not_in",
    "between",
]

BoolCombOp = Literal["all", "any", "not"]

# -------------------------------
# Input type definitions (SIR v0.2)
# -------------------------------

InputTypeKind = Literal["scalar", "record"]

@dataclass
class InputTypeScalar:
    """
    Scalar input type (Int, Float, String, Bool).
    For backward compatibility, scalar inputs default to Int.
    """
    kind: Literal["scalar"] = "scalar"
    dtype: Literal["Int", "Float", "String", "Bool"] = "Int"
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "InputTypeScalar":
        return InputTypeScalar(
            kind="scalar",
            dtype=data.get("type", data.get("dtype", "Int"))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": "scalar",
            "type": self.dtype,
        }


@dataclass
class InputTypeRecord:
    """
    Record input type with named fields.
    Fields are stored as field_name -> type_name mapping.
    Field ordering is canonicalized (sorted alphabetically) for determinism.
    """
    kind: Literal["record"] = "record"
    fields: Dict[str, str] = field(default_factory=dict)  # field_name -> type_name
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "InputTypeRecord":
        fields_raw = data.get("fields", {})
        # Ensure fields dict is properly typed
        fields = {}
        for k, v in fields_raw.items():
            if isinstance(k, str) and isinstance(v, str):
                fields[k] = v
        # Canonicalize: sort fields alphabetically for determinism
        fields = dict(sorted(fields.items()))
        return InputTypeRecord(
            kind="record",
            fields=fields
        )
    
    def to_dict(self) -> Dict[str, Any]:
        # Canonicalize: sort fields alphabetically for determinism
        sorted_fields = dict(sorted(self.fields.items()))
        return {
            "kind": "record",
            "fields": sorted_fields,
        }


# Union type for input types
InputType = Union[InputTypeScalar, InputTypeRecord]

# -------------------------------
# Condition expressions
# -------------------------------

@dataclass
class Predicate:
    """
    Atomic predicate, e.g.:
      {"op": "gt", "args": ["transaction.amount", 100000]}
    """
    op: ConditionOp
    args: List[Any]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Predicate":
        return Predicate(
            op=data["op"],
            args=list(data.get("args", [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": self.op,
            "args": self.args,
        }


@dataclass
class BoolExpr:
    """
    Boolean combination of predicates or other BoolExprs, e.g.:
      {"combiner": "all", "terms": [<CondExpr>, <CondExpr>]}
    """
    combiner: BoolCombOp
    terms: List["CondExpr"] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "BoolExpr":
        combiner: str = data["combiner"]
        raw_terms = data.get("terms", [])
        terms: List[CondExpr] = []
        for t in raw_terms:
            terms.append(condexpr_from_dict(t))
        return BoolExpr(combiner=combiner, terms=terms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "combiner": self.combiner,
            "terms": [condexpr_to_dict(t) for t in self.terms],
        }


# A CondExpr is either a Predicate or a BoolExpr
CondExpr = Union[Predicate, BoolExpr]


def condexpr_from_dict(data: Dict[str, Any]) -> CondExpr:
    """
    Factory: decode a dict into Predicate or BoolExpr.
    We decide based on presence of keys.
    """
    if "op" in data:
        return Predicate.from_dict(data)
    if "combiner" in data:
        return BoolExpr.from_dict(data)
    raise ValueError(f"Invalid CondExpr dict (missing 'op' or 'combiner'): {data!r}")


def condexpr_to_dict(expr: CondExpr) -> Dict[str, Any]:
    if isinstance(expr, Predicate):
        return expr.to_dict()
    if isinstance(expr, BoolExpr):
        return expr.to_dict()
    raise TypeError(f"Unknown CondExpr type: {type(expr)!r}")


# -------------------------------
# Step types
# -------------------------------

@dataclass
class SetOutputStep:
    """
    Terminal step that sets the pipeline output to a literal value.
    Example JSON:
      {
        "type": "SetOutput",
        "value": "FLAG"
      }
    """
    type: Literal["SetOutput"] = "SetOutput"
    value: Any = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SetOutputStep":
        return SetOutputStep(
            type=data.get("type", "SetOutput"),
            value=data.get("value"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "SetOutput",
            "value": self.value,
        }


@dataclass
class DecisionStep:
    """
    Conditional step with then/else branches.
    Example JSON:
      {
        "type": "Decision",
        "id": "high_risk_rule",
        "condition": { ...CondExpr... },
        "then_steps": [ ...Step... ],
        "else_steps": [ ...Step... ]
      }
    """
    type: Literal["Decision"] = "Decision"
    id: str = "rule"
    condition: CondExpr | None = None
    then_steps: List["Step"] = field(default_factory=list)
    else_steps: List["Step"] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DecisionStep":
        cond_raw = data.get("condition")
        condition: Optional[CondExpr] = None
        if cond_raw is not None:
            condition = condexpr_from_dict(cond_raw)

        raw_then = data.get("then_steps", []) or data.get("then", [])
        raw_else = data.get("else_steps", []) or data.get("else", [])

        then_steps = [step_from_dict(s) for s in raw_then]
        else_steps = [step_from_dict(s) for s in raw_else]

        return DecisionStep(
            type=data.get("type", "Decision"),
            id=data.get("id", "rule"),
            condition=condition,
            then_steps=then_steps,
            else_steps=else_steps,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Decision",
            "id": self.id,
            "condition": condexpr_to_dict(self.condition)
            if self.condition is not None
            else None,
            "then_steps": [step_to_dict(s) for s in self.then_steps],
            "else_steps": [step_to_dict(s) for s in self.else_steps],
        }


Step = Union[DecisionStep, SetOutputStep]


def step_from_dict(data: Dict[str, Any]) -> Step:
    step_type = data.get("type")
    if step_type == "Decision":
        return DecisionStep.from_dict(data)
    if step_type == "SetOutput":
        return SetOutputStep.from_dict(data)
    raise ValueError(f"Unknown step type: {step_type!r}")


def step_to_dict(step: Step) -> Dict[str, Any]:
    if isinstance(step, DecisionStep):
        return step.to_dict()
    if isinstance(step, SetOutputStep):
        return step.to_dict()
    raise TypeError(f"Unknown Step type: {type(step)!r}")


# -------------------------------
# Pipeline container
# -------------------------------

@dataclass
class DecisionPipeline:
    """
    Top-level SIR object.

    Example JSON (scalar input):
      {
        "type": "DecisionPipeline",
        "name": "txn_risk",
        "input_name": "transaction",
        "steps": [ ...Step... ]
      }
    
    Example JSON (record input, SIR v0.2):
      {
        "type": "DecisionPipeline",
        "name": "main",
        "input_name": "applicant",
        "input_type": {
          "kind": "record",
          "fields": {"income": "Int", "age": "Int"}
        },
        "steps": [ ...Step... ]
      }
    """
    type: Literal["DecisionPipeline"] = "DecisionPipeline"
    name: str = "pipeline"
    input_name: str = "input"
    input_type: Optional[InputType] = None  # Optional for backward compatibility (SIR v0.2)
    steps: List[Step] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DecisionPipeline":
        # Fix common LLM mistake: "Decision" -> "DecisionPipeline"
        # Always fix "Decision" → "DecisionPipeline" (regardless of steps)
        # Make a copy to avoid mutating the original
        data = dict(data)
        if data.get("type") == "Decision":
            data["type"] = "DecisionPipeline"
        if data.get("type") not in (None, "DecisionPipeline"):
            raise ValueError(f"Unsupported pipeline type: {data.get('type')!r}")

        raw_steps = data.get("steps", [])
        steps = [step_from_dict(s) for s in raw_steps]

        # Parse input_type (SIR v0.2)
        input_type: Optional[InputType] = None
        if "input_type" in data:
            input_type_raw = data["input_type"]
            if isinstance(input_type_raw, dict):
                kind = input_type_raw.get("kind")
                if kind == "record":
                    input_type = InputTypeRecord.from_dict(input_type_raw)
                elif kind == "scalar":
                    input_type = InputTypeScalar.from_dict(input_type_raw)
                # If kind is missing but fields exist, assume record (backward compat)
                elif "fields" in input_type_raw:
                    input_type = InputTypeRecord.from_dict(input_type_raw)
        # Backward compatibility: if no input_type, default to None (implicit scalar Int)

        return DecisionPipeline(
            type="DecisionPipeline",
            name=data.get("name", "pipeline"),
            input_name=data.get("input_name", data.get("input", "input")),
            input_type=input_type,
            steps=steps,
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": "DecisionPipeline",
            "name": self.name,
            "input_name": self.input_name,
            "steps": [step_to_dict(s) for s in self.steps],
        }
        # Include input_type if present (SIR v0.2)
        if self.input_type is not None:
            result["input_type"] = self.input_type.to_dict()
        return result


# -------------------------------
# Helper API used by other modules
# -------------------------------

def sir_from_dict(data: Dict[str, Any]) -> DecisionPipeline:
    """
    Main entry: convert JSON/dict produced by llm_bridge into a DecisionPipeline.
    """
    return DecisionPipeline.from_dict(data)


def sir_to_dict(pipeline: DecisionPipeline) -> Dict[str, Any]:
    """
    Convert a DecisionPipeline back to a plain dict (for JSON serialization).
    """
    return pipeline.to_dict()
