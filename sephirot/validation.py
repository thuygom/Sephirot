"""Validation helpers for Sephirot seed specs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ambiguity import next_questions, score_spec
from .canon import PATHS, SEPHIROT


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    key: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    ambiguity: float
    threshold: float
    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]
    next_questions: tuple[dict[str, Any], ...]


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _issue(level: str, key: str, message: str) -> ValidationIssue:
    return ValidationIssue(level=level, key=key, message=message)


def _threshold(spec: dict[str, Any]) -> float:
    try:
        return float(spec.get("threshold", 0.2))
    except (TypeError, ValueError):
        return 0.2


def _validate_top_level(spec: dict[str, Any], errors: list[ValidationIssue]) -> None:
    for key in ("malkuth", "kether", "sephira", "paths"):
        if key not in spec:
            errors.append(_issue("error", key, f"Missing required top-level key: {key}."))
        elif not _is_mapping(spec[key]):
            errors.append(_issue("error", key, f"Expected {key} to be an object."))


def _validate_state_blocks(spec: dict[str, Any], errors: list[ValidationIssue]) -> None:
    required = {
        "malkuth": ("human_state", "current_state", "evidence"),
        "kether": ("target_state", "success_condition", "evidence"),
    }
    for block_name, fields in required.items():
        block = spec.get(block_name)
        if not _is_mapping(block):
            continue
        for field in fields:
            if field not in block:
                errors.append(
                    _issue(
                        "error",
                        f"{block_name}.{field}",
                        f"Missing required field: {block_name}.{field}.",
                    )
                )


def _validate_sephira(
    spec: dict[str, Any],
    errors: list[ValidationIssue],
    warnings: list[ValidationIssue],
) -> None:
    sephira = spec.get("sephira")
    if not _is_mapping(sephira):
        return

    canonical_names = {profile.name for profile in SEPHIROT}
    present_names = set(sephira)
    for missing in sorted(canonical_names - present_names):
        errors.append(_issue("error", f"sephira.{missing}", f"Missing Sephira node: {missing}."))
    for extra in sorted(present_names - canonical_names):
        warnings.append(_issue("warning", f"sephira.{extra}", f"Unknown extra Sephira node: {extra}."))

    for profile in SEPHIROT:
        node = sephira.get(profile.name)
        if not _is_mapping(node):
            if profile.name in sephira:
                errors.append(
                    _issue(
                        "error",
                        f"sephira.{profile.name}",
                        f"Expected sephira.{profile.name} to be an object.",
                    )
                )
            continue
        for field in ("focus_value", "domain_instantiation", "desired_state", "evidence", "qliphoth_risk"):
            if field not in node:
                errors.append(
                    _issue(
                        "error",
                        f"sephira.{profile.name}.{field}",
                        f"Missing required field: sephira.{profile.name}.{field}.",
                    )
                )
        if node.get("focus_value") and node.get("focus_value") != profile.focus_value:
            warnings.append(
                _issue(
                    "warning",
                    f"sephira.{profile.name}.focus_value",
                    f"Expected default focus value '{profile.focus_value}'.",
                )
            )


def _validate_paths(
    spec: dict[str, Any],
    errors: list[ValidationIssue],
    warnings: list[ValidationIssue],
) -> None:
    paths = spec.get("paths")
    if not _is_mapping(paths):
        return

    canonical_numbers = {str(profile.number) for profile in PATHS}
    present_numbers = set(paths)
    for missing in sorted(canonical_numbers - present_numbers, key=int):
        errors.append(_issue("error", f"paths.{missing}", f"Missing CQ path: {missing}."))
    for extra in sorted(present_numbers - canonical_numbers):
        warnings.append(_issue("warning", f"paths.{extra}", f"Unknown extra CQ path: {extra}."))

    for profile in PATHS:
        key = str(profile.number)
        path = paths.get(key)
        if not _is_mapping(path):
            if key in paths:
                errors.append(
                    _issue(
                        "error",
                        f"paths.{key}",
                        f"Expected paths.{key} to be an object.",
                    )
                )
            continue
        for field in ("from", "to", "cq", "answer", "evidence", "qliphoth_check"):
            if field not in path:
                errors.append(_issue("error", f"paths.{key}.{field}", f"Missing required field: paths.{key}.{field}."))
        if path.get("from") != profile.source:
            errors.append(
                _issue(
                    "error",
                    f"paths.{key}.from",
                    f"Expected source {profile.source} for path {key}.",
                )
            )
        if path.get("to") != profile.target:
            errors.append(
                _issue(
                    "error",
                    f"paths.{key}.to",
                    f"Expected target {profile.target} for path {key}.",
                )
            )
        if path.get("cq") and path.get("cq") != profile.cq:
            warnings.append(
                _issue(
                    "warning",
                    f"paths.{key}.cq",
                    "CQ text differs from the default Hermetic-style profile.",
                )
            )


def validate_spec(spec: dict[str, Any]) -> ValidationReport:
    """Validate a seed spec against the canonical Sephirot contract."""

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    if not _is_mapping(spec):
        issue = _issue("error", "$", "Seed spec must be a JSON object.")
        return ValidationReport(
            ok=False,
            ambiguity=1.0,
            threshold=0.2,
            errors=(issue,),
            warnings=(),
            next_questions=(),
        )

    if spec.get("schema_version") not in (None, "0.1"):
        warnings.append(
            _issue(
                "warning",
                "schema_version",
                "This CLI currently validates schema_version 0.1.",
            )
        )

    _validate_top_level(spec, errors)
    _validate_state_blocks(spec, errors)
    _validate_sephira(spec, errors, warnings)
    _validate_paths(spec, errors, warnings)

    ambiguity = score_spec(spec)
    threshold = _threshold(spec)
    questions = tuple(
        {
            "key": item.key,
            "weight": item.weight,
            "missing": item.missing,
            "question": item.question,
        }
        for item in next_questions(spec, limit=8)
    )
    if ambiguity > threshold:
        warnings.append(
            _issue(
                "warning",
                "ambiguity",
                f"Ambiguity {ambiguity:.3f} is above threshold {threshold:.3f}; build remains gated.",
            )
        )

    return ValidationReport(
        ok=not errors and ambiguity <= threshold,
        ambiguity=ambiguity,
        threshold=threshold,
        errors=tuple(errors),
        warnings=tuple(warnings),
        next_questions=questions,
    )


def report_as_dict(report: ValidationReport) -> dict[str, Any]:
    """Convert a validation report to plain JSON-serializable data."""

    return {
        "ok": report.ok,
        "ambiguity": report.ambiguity,
        "threshold": report.threshold,
        "errors": [issue.__dict__ for issue in report.errors],
        "warnings": [issue.__dict__ for issue in report.warnings],
        "next_questions": list(report.next_questions),
    }
