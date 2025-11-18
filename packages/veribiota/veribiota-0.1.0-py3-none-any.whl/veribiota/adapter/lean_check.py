from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Mapping, Tuple

from .schema import (
  EditDAGPayload,
  InvariantError,
  LeanCheckSummary,
  SchemaError,
  compute_structural_summary,
  load_edit_dag,
)


def lean_check(dag_json: Mapping[str, object]) -> LeanCheckSummary:
  """Normalize and structurally check a single DAG JSON object."""

  payload = load_edit_dag(dag_json)
  return compute_structural_summary(payload)


def lean_check_file(path: Path) -> Tuple[LeanCheckSummary, EditDAGPayload]:
  """Load, normalize and check a single DAG JSON file."""

  raw = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(raw, Mapping):
    raise SchemaError(f"{path} must contain a JSON object")
  payload = load_edit_dag(raw)
  summary = compute_structural_summary(payload, dag_name=path.name)
  return summary, payload


def lean_check_many(
  paths: Iterable[Path],
) -> List[Tuple[LeanCheckSummary, EditDAGPayload]]:
  """Check many DAG files and return summaries plus payloads."""

  results: List[Tuple[LeanCheckSummary, EditDAGPayload]] = []
  for path in paths:
    results.append(lean_check_file(path))
  return results


__all__ = [
  "lean_check",
  "lean_check_file",
  "lean_check_many",
  "LeanCheckSummary",
  "SchemaError",
  "InvariantError",
  "EditDAGPayload",
]

