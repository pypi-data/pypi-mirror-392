from __future__ import annotations

from typing import Iterable, List, Tuple

from .lean_check import lean_check_many
from .schema import EditDAGPayload, InvariantError, LeanCheckSummary, SchemaError


def preflight(
  paths: Iterable[str],
) -> List[Tuple[LeanCheckSummary, EditDAGPayload]]:
  """Run schema + structural checks over a collection of JSON DAGs.

  This is the \"no-Lean\" mode: it validates the normalized JSON EditDAGs
  and returns detailed summaries for downstream tooling.
  """

  from pathlib import Path

  dag_paths = [Path(p) for p in paths]
  return lean_check_many(dag_paths)


def preflight_check(paths: Iterable[str]) -> None:
  """Preflight check that raises on any schema/invariant violation."""

  try:
    preflight(paths)
  except (SchemaError, InvariantError) as exc:
    raise SystemExit(str(exc)) from exc


__all__ = ["preflight", "preflight_check"]

