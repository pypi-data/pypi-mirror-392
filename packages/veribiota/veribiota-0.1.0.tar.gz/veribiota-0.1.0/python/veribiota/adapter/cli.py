from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path
from typing import List

from .lean_check import (
  EditDAGPayload,
  InvariantError,
  LeanCheckSummary,
  SchemaError,
  lean_check_file,
  lean_check_many,
)
from .preflight import preflight
from .suite_codegen import generate_lean_suite, write_generated_aggregator


def _collect_inputs(pattern: str) -> List[Path]:
  paths = [Path(p) for p in glob.glob(pattern)]
  if not paths:
    raise SystemExit(f"no files matched input pattern: {pattern!r}")
  return sorted(paths)


def cmd_check_json(args: argparse.Namespace) -> int:
  paths = _collect_inputs(args.input)
  try:
    preflight(str(p) for p in paths)
  except (SchemaError, InvariantError) as exc:
    print(f"veribiota: check-json failed: {exc}", file=sys.stderr)
    return 1
  if args.verbose:
    print(f"veribiota: check-json OK for {len(paths)} file(s).")
  return 0


def cmd_lean_check(args: argparse.Namespace) -> int:
  paths = _collect_inputs(args.input)
  out_dir = Path(args.out) if args.out else None
  summaries: List[LeanCheckSummary] = []
  payloads: List[EditDAGPayload] = []
  try:
    for path in paths:
      summary, payload = lean_check_file(path)
      summaries.append(summary)
      payloads.append(payload)
  except (SchemaError, InvariantError) as exc:
    print(f"veribiota: lean-check failed: {exc}", file=sys.stderr)
    return 1
  if out_dir is not None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for summary, payload, path in zip(summaries, payloads, paths, strict=True):
      out_path = out_dir / (path.stem + ".lean-check.json")
      data = {
        "dag": path.name,
        "root": summary.root_id,
        "node_count": len(summary.node_ids),
        "edge_count": len(payload.edges),
        "leaf_probability_mass": summary.leaf_probability_mass,
        "checks": {
          "acyclic": summary.acyclic,
          "root_unique": summary.root_unique,
          "depth_increases": summary.depth_increases,
          "transitions_conserve_probability": summary.transitions_conserve_probability,
          "leaves_conserve_probability": summary.leaves_conserve_probability,
        },
      }
      out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
  if args.verbose:
    print(f"veribiota: lean-check OK for {len(paths)} file(s).")
  return 0


def cmd_generate_suite(args: argparse.Namespace) -> int:
  paths = _collect_inputs(args.input)
  # Schema + structural checks first.
  try:
    summaries_payloads = lean_check_many(paths)
    payloads = [payload for _, payload in summaries_payloads]
  except (SchemaError, InvariantError) as exc:
    print(f"veribiota: generate-suite failed during preflight: {exc}", file=sys.stderr)
    return 1

  project: str | None = getattr(args, "project", None)
  suite: str = (getattr(args, "suite", None) or "DAGs")

  # Precedence:
  # - If --module or --out is provided, use them as-is (backwards compatible).
  # - Else, if --project is provided, derive module + path from project/suite and
  #   also update the Generated aggregator.
  # - Else, fall back to Biosim.VeriBiota.Generated.
  if args.module or args.out:
    module_name = args.module or "Biosim.VeriBiota.Generated"
    out_path = Path(args.out) if args.out else Path("Biosim/VeriBiota/Generated.lean")
    generate_lean_suite(payloads, module_name=module_name, out_path=out_path)
  elif project:
    module_name = f"Biosim.VeriBiota.{project}.{suite}"
    out_path = Path("Biosim") / "VeriBiota" / project / f"{suite}.lean"
    generate_lean_suite(payloads, module_name=module_name, out_path=out_path)
    write_generated_aggregator(project=project, suite=suite)
  else:
    module_name = "Biosim.VeriBiota.Generated"
    out_path = Path("Biosim/VeriBiota/Generated.lean")
    generate_lean_suite(payloads, module_name=module_name, out_path=out_path)

  if args.verbose:
    print(f"veribiota: wrote Lean suite to {out_path}")
  return 0


def cmd_run(args: argparse.Namespace) -> int:
  root = Path(args.veribiota_root or ".").resolve()
  try:
    subprocess.run(["lake", "build"], cwd=root, check=True)
    subprocess.run(["lake", "exe", "veribiota-check"], cwd=root, check=True)
  except subprocess.CalledProcessError as exc:
    return exc.returncode or 1
  return 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="veribiota",
    description="VeriBiota DAG adapter: JSON validation and Lean suite generation.",
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  p_check = subparsers.add_parser(
    "check-json", help="Validate DAG JSON files without invoking Lean."
  )
  p_check.add_argument("--input", required=True, help="Input glob for DAG JSON files.")
  p_check.add_argument(
    "--verbose", action="store_true", help="Print a short success summary."
  )
  p_check.set_defaults(func=cmd_check_json)

  # Alias: `preflight` behaves the same as `check-json` for now.
  p_pre = subparsers.add_parser(
    "preflight", help="Alias for check-json (JSON-only structural checks)."
  )
  p_pre.add_argument("--input", required=True, help="Input glob for DAG JSON files.")
  p_pre.add_argument(
    "--verbose", action="store_true", help="Print a short success summary."
  )
  p_pre.set_defaults(func=cmd_check_json)

  p_lc = subparsers.add_parser(
    "lean-check",
    help="Normalize DAG JSON and emit optional summary JSON for Lean integration.",
  )
  p_lc.add_argument("--input", required=True, help="Input glob for DAG JSON files.")
  p_lc.add_argument(
    "--out",
    help="Optional directory for *.lean-check.json summaries (one per input DAG).",
  )
  p_lc.add_argument(
    "--verbose", action="store_true", help="Print a short success summary."
  )
  p_lc.set_defaults(func=cmd_lean_check)

  p_gen = subparsers.add_parser(
    "generate-suite",
    help="Generate a Lean EditDAG suite module for the given DAG JSON files.",
  )
  p_gen.add_argument("--input", required=True, help="Input glob for DAG JSON files.")
  p_gen.add_argument(
    "--module",
    help=(
      "Explicit Lean module name for the generated suite. "
      "If provided, --project/--suite are ignored. "
      "Default without --project is Biosim.VeriBiota.Generated."
    ),
  )
  p_gen.add_argument(
    "--out",
    help="Filesystem path for the generated .lean file "
    "(default: Biosim/VeriBiota/Generated.lean).",
  )
  p_gen.add_argument(
    "--project",
    help=(
      "Project name used to derive a module like "
      "Biosim.VeriBiota.<Project>.<Suite> and path "
      "Biosim/VeriBiota/<Project>/<Suite>.lean."
    ),
  )
  p_gen.add_argument(
    "--suite",
    help=(
      "Suite name under the project (default: DAGs). "
      "Only used when --project is set and neither --module nor --out "
      "are given."
    ),
  )
  p_gen.add_argument(
    "--verbose", action="store_true", help="Print a short success summary."
  )
  p_gen.set_defaults(func=cmd_generate_suite)

  p_run = subparsers.add_parser(
    "run",
    help="Build and execute `lake exe veribiota-check` in a VeriBiota checkout.",
  )
  p_run.add_argument(
    "--veribiota-root",
    help="Path to VeriBiota checkout (default: current directory).",
  )
  p_run.set_defaults(func=cmd_run)

  return parser


def main(argv: list[str] | None = None) -> None:
  parser = build_parser()
  args = parser.parse_args(argv)
  exit_code = args.func(args)
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
