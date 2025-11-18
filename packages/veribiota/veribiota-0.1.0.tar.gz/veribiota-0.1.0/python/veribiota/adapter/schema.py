from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


class SchemaError(ValueError):
  """Raised when the EditDAG JSON fails basic schema validation."""


class InvariantError(ValueError):
  """Raised when structural invariants are violated."""


@dataclass
class NodePayload:
  node_id: str
  depth: int
  prob: float


@dataclass
class EdgePayload:
  src: str
  dst: str
  prob: float
  event_kind: Optional[str] = None


@dataclass
class EditDAGPayload:
  version: str
  nodes: List[NodePayload]
  edges: List[EdgePayload]
  root: str


@dataclass
class LeanCheckSummary:
  dag_name: str
  node_ids: List[str]
  id_to_index: Dict[str, int]
  root_id: str
  root_index: int
  depths: Dict[str, int]
  node_probabilities: Dict[str, float]
  outgoing_probabilities: Dict[str, float]
  leaf_probability_mass: float
  acyclic: bool
  root_unique: bool
  depth_increases: bool
  transitions_conserve_probability: bool
  leaves_conserve_probability: bool

  @property
  def all_invariants_ok(self) -> bool:
    return (
      self.acyclic
      and self.root_unique
      and self.depth_increases
      and self.transitions_conserve_probability
      and self.leaves_conserve_probability
    )


def _require(condition: bool, message: str) -> None:
  if not condition:
    raise SchemaError(message)


def _require_invariants(condition: bool, message: str) -> None:
  if not condition:
    raise InvariantError(message)


def _as_float(value: object, *, path: str) -> float:
  if isinstance(value, (int, float)):
    return float(value)
  raise SchemaError(f"{path} must be a number")


def _as_int(value: object, *, path: str) -> int:
  if isinstance(value, int) and value >= 0:
    return value
  raise SchemaError(f"{path} must be a non-negative integer")


def _as_str(value: object, *, path: str) -> str:
  if isinstance(value, str) and value:
    return value
  raise SchemaError(f"{path} must be a non-empty string")


def load_edit_dag(obj: Mapping[str, object]) -> EditDAGPayload:
  """Parse a raw JSON object into a validated EditDAGPayload."""

  version = _as_str(obj.get("version"), path="version")
  _require(
    version == "veribiota.edit_dag.v1",
    f"unsupported EditDAG version {version!r}",
  )

  raw_nodes = obj.get("nodes")
  _require(isinstance(raw_nodes, list) and raw_nodes, "nodes must be a non-empty array")

  nodes: List[NodePayload] = []
  seen_ids: set[str] = set()
  for idx, raw_node in enumerate(raw_nodes):
    if not isinstance(raw_node, Mapping):
      raise SchemaError(f"nodes[{idx}] must be an object")
    node_id = _as_str(raw_node.get("id"), path=f"nodes[{idx}].id")
    _require(node_id not in seen_ids, f"duplicate node id {node_id!r}")
    seen_ids.add(node_id)
    depth = _as_int(raw_node.get("depth"), path=f"nodes[{idx}].depth")
    prob = _as_float(raw_node.get("prob"), path=f"nodes[{idx}].prob")
    nodes.append(NodePayload(node_id=node_id, depth=depth, prob=prob))

  raw_edges = obj.get("edges")
  _require(isinstance(raw_edges, list), "edges must be an array")

  edges: List[EdgePayload] = []
  for idx, raw_edge in enumerate(raw_edges or []):
    if not isinstance(raw_edge, Mapping):
      raise SchemaError(f"edges[{idx}] must be an object")
    src = _as_str(raw_edge.get("src"), path=f"edges[{idx}].src")
    dst = _as_str(raw_edge.get("dst"), path=f"edges[{idx}].dst")
    prob = _as_float(raw_edge.get("prob"), path=f"edges[{idx}].prob")
    event_kind_value = raw_edge.get("event_kind")
    event_kind: Optional[str]
    if event_kind_value is None:
      event_kind = None
    else:
      event_kind = _as_str(event_kind_value, path=f"edges[{idx}].event_kind")
    edges.append(EdgePayload(src=src, dst=dst, prob=prob, event_kind=event_kind))

  root = _as_str(obj.get("root"), path="root")

  return EditDAGPayload(version=version, nodes=nodes, edges=edges, root=root)


def probability_close_to_one(value: float, *, tol: float = 1e-4) -> bool:
  return abs(value - 1.0) <= tol


def compute_structural_summary(
  dag: EditDAGPayload, *, dag_name: str = "<anonymous>"
) -> LeanCheckSummary:
  """Compute structural invariants for an EditDAG payload."""

  node_ids = [n.node_id for n in dag.nodes]
  id_to_index: Dict[str, int] = {node_id: i for i, node_id in enumerate(node_ids)}

  _require_invariants(
    dag.root in id_to_index, f"root {dag.root!r} does not reference a node"
  )
  root_index = id_to_index[dag.root]

  depths: Dict[str, int] = {n.node_id: n.depth for n in dag.nodes}
  node_probabilities: Dict[str, float] = {n.node_id: n.prob for n in dag.nodes}

  outgoing: Dict[str, List[EdgePayload]] = {node_id: [] for node_id in node_ids}
  for edge in dag.edges:
    _require_invariants(
      edge.src in id_to_index, f"edge src {edge.src!r} does not reference a node"
    )
    _require_invariants(
      edge.dst in id_to_index, f"edge dst {edge.dst!r} does not reference a node"
    )
    outgoing[edge.src].append(edge)

  outgoing_probabilities: Dict[str, float] = {}
  for node_id, fanout in outgoing.items():
    total = sum(e.prob for e in fanout)
    outgoing_probabilities[node_id] = total

  leaf_ids = [node_id for node_id, fanout in outgoing.items() if not fanout]
  leaf_probability_mass = sum(node_probabilities[node_id] for node_id in leaf_ids)

  # Root uniqueness and depth constraints.
  root_nodes = [n for n in dag.nodes if n.node_id == dag.root]
  root_unique = len(root_nodes) == 1 and root_nodes[0].depth == 0

  depth_increases = True
  for edge in dag.edges:
    src_depth = depths[edge.src]
    dst_depth = depths[edge.dst]
    if not (src_depth + 1 <= dst_depth):
      depth_increases = False
      break

  transitions_conserve_probability = True
  for node_id, total in outgoing_probabilities.items():
    fanout = outgoing[node_id]
    if fanout and not probability_close_to_one(total):
      transitions_conserve_probability = False
      break

  leaves_conserve_probability = probability_close_to_one(leaf_probability_mass)

  # Acyclicity via DFS.
  adjacency: Dict[str, List[str]] = {
    node_id: [edge.dst for edge in fanout] for node_id, fanout in outgoing.items()
  }

  acyclic = _is_acyclic(node_ids, adjacency)

  return LeanCheckSummary(
    dag_name=dag_name,
    node_ids=node_ids,
    id_to_index=id_to_index,
    root_id=dag.root,
    root_index=root_index,
    depths=depths,
    node_probabilities=node_probabilities,
    outgoing_probabilities=outgoing_probabilities,
    leaf_probability_mass=leaf_probability_mass,
    acyclic=acyclic,
    root_unique=root_unique,
    depth_increases=depth_increases,
    transitions_conserve_probability=transitions_conserve_probability,
    leaves_conserve_probability=leaves_conserve_probability,
  )


def _is_acyclic(nodes: Sequence[str], adjacency: Mapping[str, Sequence[str]]) -> bool:
  """Detect cycles using DFS with a recursion stack."""

  visited: Dict[str, bool] = {node: False for node in nodes}
  in_stack: Dict[str, bool] = {node: False for node in nodes}

  def dfs(node: str) -> bool:
    if in_stack[node]:
      return False
    if visited[node]:
      return True
    visited[node] = True
    in_stack[node] = True
    try:
      for succ in adjacency.get(node, ()):
        if not dfs(succ):
          return False
    finally:
      in_stack[node] = False
    return True

  return all(dfs(node) for node in nodes if not visited[node])


def summarize_many(
  dags: Iterable[EditDAGPayload],
) -> List[LeanCheckSummary]:
  """Summarize and validate a collection of DAGs."""

  summaries: List[LeanCheckSummary] = []
  for idx, dag in enumerate(dags):
    name = getattr(dag, "name", None) or f"dag_{idx}"
    summaries.append(compute_structural_summary(dag, dag_name=name))
  return summaries

