"""
AEP Intermediate Representation (IR) Validator v1.0

Validates LLM-generated Execution Plans against the AEP-IR-1.0 specification.

Usage:
    python validator.py plan.json              # Validate a single plan file
    python validator.py --dir plans/           # Validate all plans in a directory
    python validator.py --stdin                # Read plan from stdin
"""

import json
import sys
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# ENV-5 checksum verification uses the SAME canonicalization module the runner
# uses to create envelopes (single source of truth — see canonical.py).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canonical import checksum as canonical_checksum, CANONICAL_STANDARD  # noqa: E402


# ──────────────────────────────────────────────
# Types
# ──────────────────────────────────────────────

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationFinding:
    def __init__(self, severity: ValidationSeverity, rule: str, message: str, node_id: Optional[str] = None):
        self.severity = severity
        self.rule = rule
        self.message = message
        self.node_id = node_id

    def __repr__(self):
        prefix = f"[{self.severity.value.upper()}] [Rule {self.rule}]"
        loc = f" (node: {self.node_id})" if self.node_id else ""
        return f"{prefix}{loc}: {self.message}"

    def to_dict(self):
        return {
            "severity": self.severity.value,
            "rule": self.rule,
            "message": self.message,
            "node_id": self.node_id,
        }


VALID_NODE_TYPES = {"transformation", "tool_call", "mutation", "sync"}
VALID_EFFECTS = {"READ", "WRITE", "CALL_TOOL", "EMIT_EVENT", "YIELD"}
VALID_ACCESS = {"read", "write"}
VALID_MUTABILITY = {"readonly", "mutable"}
VALID_SCOPES = {"execution", "session", "persistent"}
VALID_PRIMITIVE_TYPES = {"string", "number", "boolean", "null"}
VALID_STRUCTURED_TYPES = {"object", "array"}
VALID_TYPES = VALID_PRIMITIVE_TYPES | VALID_STRUCTURED_TYPES

# ASCII-only report characters for Windows compatibility
PASS_CHAR = "[OK]"
FAIL_CHAR = "[FAIL]"
ARROW_CHAR = "  ->"


# ──────────────────────────────────────────────
# Validator
# ──────────────────────────────────────────────

class IRValidator:
    """
    Validates AEP IR Execution Plans against the AEP-IR-1.0 specification.
    """

    def __init__(self, plan: Dict[str, Any]):
        self.plan = plan
        self.findings: List[ValidationFinding] = []
        self._node_ids: Set[str] = set()
        self._declared_bindings: Dict[str, Dict] = {}
        self._declared_capabilities: Set[str] = set()

    # ── Public API ──────────────────────────────

    def validate(self) -> List[ValidationFinding]:
        """Run all validation rules and return findings."""
        self._validate_envelope()
        self._validate_plan_header()
        self._validate_nodes()
        self._validate_edges()
        self._validate_dag_acyclic()
        self._validate_binding_usage()
        self._validate_capability_coverage()
        self._validate_type_effect_consistency()
        self._validate_cross_references()
        self._validate_input_origins()    # §7.4 Rule 5
        self._validate_mutable_conflicts() # §2.2
        return self.findings

    def is_valid(self) -> bool:
        """Returns True if no ERROR-level findings."""
        return not any(f.severity == ValidationSeverity.ERROR for f in self.findings)

    def report_summary(self) -> Dict:
        """Produce a structured summary of validation results."""
        errors = [f for f in self.findings if f.severity == ValidationSeverity.ERROR]
        warnings = [f for f in self.findings if f.severity == ValidationSeverity.WARNING]

        rejection_modes = {}
        for f in errors:
            rejection_modes.setdefault(f.rule, 0)
            rejection_modes[f.rule] += 1

        return {
            "valid": self.is_valid(),
            "total_findings": len(self.findings),
            "errors": len(errors),
            "warnings": len(warnings),
            "rejection_modes": rejection_modes,
            "findings": [f.to_dict() for f in self.findings],
        }

    # ── Envelope (§6.2) ─────────────────────────

    def _validate_envelope(self):
        if not isinstance(self.plan, dict):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "ENV-1", "Plan must be a JSON object"
            ))
            return

        if "plan" not in self.plan:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "ENV-2", "Missing 'plan' field in envelope"
            ))
        if "checksum" not in self.plan:
            self.findings.append(ValidationFinding(
                ValidationSeverity.WARNING, "ENV-3",
                "Missing 'checksum' field in envelope (required in production)"
            ))

        # Check that checksum isn't inside the plan itself (§5.4 note)
        if isinstance(self.plan.get("plan"), dict) and "checksum" in self.plan["plan"]:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "ENV-4",
                "Checksum field found inside plan object — checksum must live in the envelope only"
            ))

        # ENV-5: the declared checksum MUST equal the SHA256 of the canonical
        # plan (Compiled Artifact Envelope, §6.2). This is the integrity check
        # that makes the checksum meaningful instead of decorative.
        declared = self.plan.get("checksum")
        plan_obj = self.plan.get("plan")
        if declared is not None and isinstance(plan_obj, (dict, list)):
            try:
                recomputed = canonical_checksum(plan_obj)
            except Exception as e:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "ENV-5",
                    f"Could not verify checksum ({CANONICAL_STANDARD}): {e}"
                ))
            else:
                if declared != recomputed:
                    self.findings.append(ValidationFinding(
                        ValidationSeverity.ERROR, "ENV-5",
                        f"Checksum mismatch: envelope declares "
                        f"{str(declared)[:16]}... but the canonical plan hashes "
                        f"to {recomputed[:16]}..."
                    ))

    # ── PlanHeader (§5.4) ───────────────────────

    def _validate_plan_header(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-1", "Plan must be a JSON object"
            ))
            return

        header = plan.get("plan_header")
        if not isinstance(header, dict):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-2", "Missing or invalid 'plan_header'"
            ))
            return

        # ir_version
        if "ir_version" not in header:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-3", "Missing 'ir_version' in plan_header"
            ))
        elif not isinstance(header["ir_version"], str):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-4", "'ir_version' must be a string"
            ))

        # plan_id
        if "plan_id" not in header:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-5", "Missing 'plan_id' in plan_header"
            ))
        elif not isinstance(header["plan_id"], str):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-6", "'plan_id' must be a string"
            ))

        # declared_capabilities
        if "declared_capabilities" not in header:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-7",
                "Missing 'declared_capabilities' in plan_header"
            ))
        elif not isinstance(header["declared_capabilities"], list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-8",
                "'declared_capabilities' must be an array"
            ))
        else:
            for i, cap in enumerate(header["declared_capabilities"]):
                if not isinstance(cap, str):
                    self.findings.append(ValidationFinding(
                        ValidationSeverity.ERROR, "PH-9",
                        f"Capability at index {i} must be a string, got {type(cap).__name__}"
                    ))
                else:
                    self._declared_capabilities.add(cap)

        # declared_bindings
        if "declared_bindings" not in header:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-10",
                "Missing 'declared_bindings' in plan_header"
            ))
        elif not isinstance(header["declared_bindings"], list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-11",
                "'declared_bindings' must be an array"
            ))
        else:
            for i, binding in enumerate(header["declared_bindings"]):
                self._validate_binding(binding, f"declared_bindings[{i}]")

        # Verify no checksum in plan_header (§5.4 NOTE)
        if "checksum" in header:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "PH-12",
                "Checksum must NOT appear in plan_header — it lives in the envelope (§5.4)"
            ))

    # ── Binding (§3) ────────────────────────────

    def _validate_binding(self, binding: Any, path: str):
        if not isinstance(binding, dict):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-1", f"{path}: binding must be an object"
            ))
            return

        # name (REQUIRED)
        if "name" not in binding:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-2", f"{path}: missing 'name'"
            ))
        elif not isinstance(binding["name"], str) or not binding["name"]:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-3", f"{path}: 'name' must be a non-empty string"
            ))
        else:
            if binding["name"] in self._declared_bindings:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "B-4",
                    f"{path}: duplicate binding name '{binding['name']}'"
                ))
            self._declared_bindings[binding["name"]] = binding

        # type (REQUIRED)
        if "type" not in binding:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-5", f"{path}: missing 'type'"
            ))
        elif not isinstance(binding["type"], str):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-6", f"{path}: 'type' must be a string"
            ))
        elif binding["type"] not in VALID_TYPES:
            self.findings.append(ValidationFinding(
                ValidationSeverity.WARNING, "B-7",
                f"{path}: unknown type '{binding['type']}' "
                f"(expected one of {sorted(VALID_TYPES)})"
            ))

        # mutability (REQUIRED, default: readonly)
        mutability = binding.get("mutability", "readonly")
        if mutability not in VALID_MUTABILITY:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-8",
                f"{path}: 'mutability' must be one of {sorted(VALID_MUTABILITY)}, "
                f"got '{mutability}'"
            ))

        # scope (REQUIRED, default: execution)
        scope = binding.get("scope", "execution")
        if scope not in VALID_SCOPES:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-9",
                f"{path}: 'scope' must be one of {sorted(VALID_SCOPES)}, got '{scope}'"
            ))

        # capability (REQUIRED)
        if "capability" not in binding:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-10", f"{path}: missing 'capability'"
            ))
        elif not isinstance(binding["capability"], str):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "B-11",
                f"{path}: 'capability' must be a string"
            ))

    # ── Nodes (§2.3) ────────────────────────────

    def _validate_nodes(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        if nodes is None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-1", "Missing 'nodes' array in plan"
            ))
            return
        if not isinstance(nodes, list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-2", "'nodes' must be an array"
            ))
            return
        if len(nodes) == 0:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-3",
                "'nodes' array is empty — plan must have at least one node"
            ))
            return

        for i, node in enumerate(nodes):
            self._validate_node(node, i)

    def _validate_node(self, node: Any, index: int):
        if not isinstance(node, dict):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-4",
                f"nodes[{index}]: node must be an object"
            ))
            return

        node_id = node.get("id", f"<nodes[{index}]>")
        context = f"nodes[{index}] (id='{node_id}')"

        # id (REQUIRED, unique)
        if "id" not in node:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-5", f"{context}: missing 'id' field"
            ))
        elif not isinstance(node["id"], str) or not node["id"]:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-6",
                f"{context}: 'id' must be a non-empty string"
            ))
        elif node["id"] in self._node_ids:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-7",
                f"{context}: duplicate node id '{node['id']}'"
            ))
        else:
            self._node_ids.add(node["id"])
            node_id = node["id"]

        # type (REQUIRED)
        node_type = node.get("type")
        if node_type is None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-8", f"{context}: missing 'type' field"
            ))
        elif node_type not in VALID_NODE_TYPES:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-9",
                f"{context}: invalid type '{node_type}'. "
                f"Must be one of {sorted(VALID_NODE_TYPES)}"
            ))

        # effects (REQUIRED)
        effects = node.get("effects")
        if effects is None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-10", f"{context}: missing 'effects' field"
            ))
        elif not isinstance(effects, list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-11",
                f"{context}: 'effects' must be an array"
            ))
        else:
            for j, effect in enumerate(effects):
                if not isinstance(effect, str):
                    self.findings.append(ValidationFinding(
                        ValidationSeverity.ERROR, "N-12",
                        f"{context}: effects[{j}] must be a string"
                    ))
                elif effect not in VALID_EFFECTS:
                    self.findings.append(ValidationFinding(
                        ValidationSeverity.ERROR, "N-13",
                        f"{context}: invalid effect '{effect}'. "
                        f"Valid effects: {sorted(VALID_EFFECTS)}"
                    ))

        # capabilities (REQUIRED)
        capabilities = node.get("capabilities")
        if capabilities is None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-14",
                f"{context}: missing 'capabilities' field"
            ))
        elif not isinstance(capabilities, list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-15",
                f"{context}: 'capabilities' must be an array"
            ))
        else:
            for j, cap in enumerate(capabilities):
                if not isinstance(cap, str):
                    self.findings.append(ValidationFinding(
                        ValidationSeverity.ERROR, "N-16",
                        f"{context}: capabilities[{j}] must be a string"
                    ))

        # inputs (REQUIRED)
        inputs = node.get("inputs")
        if inputs is None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-17",
                f"{context}: missing 'inputs' field"
            ))
        elif not isinstance(inputs, list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-18",
                f"{context}: 'inputs' must be an array"
            ))

        # outputs (REQUIRED)
        outputs = node.get("outputs")
        if outputs is None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-19",
                f"{context}: missing 'outputs' field"
            ))
        elif not isinstance(outputs, list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-20",
                f"{context}: 'outputs' must be an array"
            ))

        # Validate BindingRefs
        for ref_list, ref_name in [(inputs or []), "inputs"], [(outputs or []), "outputs"]:
            if isinstance(ref_list, list):
                for j, ref in enumerate(ref_list):
                    self._validate_binding_ref(ref, f"{context}.{ref_name}[{j}]")

        # payload (OPTIONAL)
        # sync nodes MUST NOT have payload (§2.3)
        if node.get("type") == "sync" and "payload" in node and node["payload"] is not None:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "N-21",
                f"{context}: sync nodes MUST NOT have payload (§2.3)"
            ))

        # Cross-validation: write access → WRITE effect
        node_type = node.get("type")
        effects_list = node.get("effects")
        if isinstance(effects_list, list):
            has_write_effect = "WRITE" in effects_list
            has_write_access = False
            for ref_list in [node.get("inputs", []), node.get("outputs", [])]:
                if isinstance(ref_list, list):
                    for ref in ref_list:
                        if isinstance(ref, dict) and ref.get("access") == "write":
                            has_write_access = True
                            break

            if has_write_access and not has_write_effect:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "X-1",
                    f"{context}: node has write access on a binding "
                    f"but does not declare WRITE effect (§2.4)"
                ))

    def _validate_binding_ref(self, ref: Any, path: str):
        if not isinstance(ref, dict):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "BR-1",
                f"{path}: binding ref must be an object"
            ))
            return

        # binding (REQUIRED)
        if "binding" not in ref:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "BR-2",
                f"{path}: missing 'binding' field"
            ))
        elif not isinstance(ref["binding"], str):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "BR-3",
                f"{path}: 'binding' must be a string"
            ))

        # access (REQUIRED)
        if "access" not in ref:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "BR-4",
                f"{path}: missing 'access' field"
            ))
        elif ref["access"] not in VALID_ACCESS:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "BR-5",
                f"{path}: 'access' must be one of {sorted(VALID_ACCESS)}, "
                f"got '{ref['access']}'"
            ))

    # ── Edges ───────────────────────────────────

    def _validate_edges(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        edges = plan.get("edges")
        if edges is None:
            return  # edges are OPTIONAL

        if not isinstance(edges, list):
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "E-1", "'edges' must be an array"
            ))
            return

        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "E-2",
                    f"edges[{i}]: edge must be an object"
                ))
                continue

            source = edge.get("source")
            target = edge.get("target")

            if not isinstance(source, str):
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "E-3",
                    f"edges[{i}]: 'source' must be a string"
                ))
            elif source not in self._node_ids:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "E-4",
                    f"edges[{i}]: source '{source}' does not match any node id"
                ))

            if not isinstance(target, str):
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "E-5",
                    f"edges[{i}]: 'target' must be a string"
                ))
            elif target not in self._node_ids:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "E-6",
                    f"edges[{i}]: target '{target}' does not match any node id"
                ))

    # ── DAG Acyclicity (§7.4, Rule 1) ───────────

    def _validate_dag_acyclic(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        edges = plan.get("edges")
        if not isinstance(nodes, list) or not isinstance(edges, list):
            return

        if not self._node_ids:
            return

        # Build adjacency list
        adj = {nid: [] for nid in self._node_ids}
        in_degree = {nid: 0 for nid in self._node_ids}

        for edge in edges:
            if isinstance(edge, dict):
                source = edge.get("source")
                target = edge.get("target")
                if source in adj and target in adj:
                    adj[source].append(target)
                    in_degree[target] = in_degree.get(target, 0) + 1

        # Kahn's algorithm for cycle detection
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited = 0

        while queue:
            node = queue.pop(0)
            visited += 1
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited != len(self._node_ids):
            cycle_nodes = set(self._node_ids) - {
                nid for nid, deg in in_degree.items() if deg == 0
            }
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "DAG-1",
                f"Graph contains a cycle. "
                f"Nodes in cycle or unreachable: {sorted(cycle_nodes)}"
            ))

    # ── Binding Usage (§7.4, Rule 2) ────────────

    def _validate_binding_usage(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        if not isinstance(nodes, list):
            return

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_id = node.get("id", f"nodes[{i}]")

            for ref_list_name in ["inputs", "outputs"]:
                refs = node.get(ref_list_name, [])
                if not isinstance(refs, list):
                    continue
                for j, ref in enumerate(refs):
                    if isinstance(ref, dict):
                        binding_name = ref.get("binding")
                        if isinstance(binding_name, str) and binding_name not in self._declared_bindings:
                            self.findings.append(ValidationFinding(
                                ValidationSeverity.ERROR, "BU-1",
                                f"Node '{node_id}' references binding '{binding_name}' "
                                f"which is not declared in plan_header.declared_bindings"
                            ))

    # ── Capability Coverage (§7.4, Rule 6) ──────

    def _validate_capability_coverage(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        if not isinstance(nodes, list):
            return

        used_capabilities = set()
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            caps = node.get("capabilities", [])
            if isinstance(caps, list):
                for cap in caps:
                    if isinstance(cap, str):
                        used_capabilities.add(cap)

        undeclared = used_capabilities - self._declared_capabilities
        if undeclared:
            self.findings.append(ValidationFinding(
                ValidationSeverity.ERROR, "CC-1",
                f"Capabilities used but not declared in plan_header: "
                f"{sorted(undeclared)}"
            ))

        # Also verify binding capabilities are declared
        for binding_name, binding in self._declared_bindings.items():
            cap = binding.get("capability")
            if isinstance(cap, str) and cap not in self._declared_capabilities:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "CC-2",
                    f"Binding '{binding_name}' requires capability '{cap}' "
                    f"which is not declared in plan_header.declared_capabilities"
                ))

    # ── Type-Effect Consistency (§7.3) ──────────

    def _validate_type_effect_consistency(self):
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        if not isinstance(nodes, list):
            return

        type_effect_rules = {
            "transformation": {"required": set(), "prohibited": {"CALL_TOOL"}},
            "tool_call": {"required": {"CALL_TOOL"}, "prohibited": set()},
            "mutation": {"required": {"WRITE"}, "prohibited": set()},
            "sync": {"required": set(), "prohibited": VALID_EFFECTS},
        }

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_id = node.get("id", f"nodes[{i}]")
            node_type = node.get("type")
            effects = node.get("effects", [])

            if node_type not in type_effect_rules:
                continue

            rules = type_effect_rules[node_type]
            effects_set = set(effects) if isinstance(effects, list) else set()

            # Check required effects
            missing = rules["required"] - effects_set
            if missing:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "TEC-1",
                    f"Node '{node_id}' of type '{node_type}' "
                    f"is missing required effects: {sorted(missing)}"
                ))

            # Check prohibited effects
            prohibited = effects_set & rules["prohibited"]
            if prohibited:
                self.findings.append(ValidationFinding(
                    ValidationSeverity.ERROR, "TEC-2",
                    f"Node '{node_id}' of type '{node_type}' "
                    f"has prohibited effects: {sorted(prohibited)}"
                ))

    # ── Cross-References (write → mutable, capability) (§2.4) ──

    def _validate_cross_references(self):
        """Validate BindingRef write access cross-references (§2.4)."""
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        header = plan.get("plan_header")
        if not isinstance(header, dict):
            return

        nodes = plan.get("nodes")
        if not isinstance(nodes, list):
            return

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_id = node.get("id", f"nodes[{i}]")
            effects = node.get("effects", [])
            effects_set = set(effects) if isinstance(effects, list) else set()

            for ref_list_name in ["inputs", "outputs"]:
                refs = node.get(ref_list_name, [])
                if not isinstance(refs, list):
                    continue
                for j, ref in enumerate(refs):
                    if not isinstance(ref, dict):
                        continue
                    if ref.get("access") != "write":
                        continue

                    binding_name = ref.get("binding")
                    if not isinstance(binding_name, str):
                        continue

                    # Check binding exists
                    binding = self._declared_bindings.get(binding_name)
                    if binding is None:
                        continue  # already reported by BU-1

                    # Binding must be mutable
                    mutability = binding.get("mutability", "readonly")
                    if mutability != "mutable":
                        self.findings.append(ValidationFinding(
                            ValidationSeverity.ERROR, "CR-1",
                            f"Node '{node_id}' writes to binding '{binding_name}' "
                            f"but it has mutability='{mutability}' (must be 'mutable')"
                        ))

                    # Node must declare WRITE effect
                    if "WRITE" not in effects_set:
                        self.findings.append(ValidationFinding(
                            ValidationSeverity.ERROR, "CR-2",
                            f"Node '{node_id}' writes to binding '{binding_name}' "
                            f"but does not declare WRITE effect"
                        ))

                    # PlanHeader must declare the capability
                    binding_cap = binding.get("capability")
                    if isinstance(binding_cap, str) and binding_cap not in self._declared_capabilities:
                        self.findings.append(ValidationFinding(
                            ValidationSeverity.ERROR, "CR-3",
                            f"Node '{node_id}' writes to binding '{binding_name}' "
                            f"which requires capability '{binding_cap}', "
                            f"but it is not declared in plan_header.declared_capabilities"
                        ))

    # ── Input Origin Validation (§7.4, Rule 5) ──

    def _validate_input_origins(self):
        """
        Validate that every node's input binding has a defined origin, per the
        AEP-IR Origin Rules (SPEC/AEP-IR-1.0.md, "Origin Rules" section).

        A binding has a defined origin if and only if AT LEAST ONE holds:
          1. Producer: some node declares a BindingRef with access:write to it.
          2. Default value: its declaration has a non-null 'default' field.
          3. External scope: scope is 'session' or 'persistent' (the value
             originates from the execution environment or persistent storage
             outside the current plan).

        Bindings with scope 'execution' that have no producer and no default
        MUST fail OR-1. (This docstring previously listed only two origins; the
        code already implemented all three — the third, external scope, is
        normative in the Origin Rules section.)
        """
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        edges = plan.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            return

        # Build set of bindings that have defaults or originate from session/environment
        bindings_with_defaults = set()
        external_origin_bindings = set()
        for name, binding in self._declared_bindings.items():
            if "default" in binding and binding["default"] is not None:
                bindings_with_defaults.add(name)
            # session/persistent scope bindings originate from outside the plan
            if binding.get("scope", "execution") in ("session", "persistent"):
                external_origin_bindings.add(name)

        # Build producer map: which bindings are produced by which nodes
        producer_map = {}  # binding_name -> node_id
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            nid = node.get("id")
            if not isinstance(nid, str):
                continue

            outputs = node.get("outputs", [])
            if isinstance(outputs, list):
                for ref in outputs:
                    if isinstance(ref, dict) and isinstance(ref.get("binding"), str):
                        bname = ref["binding"]
                        producer_map[bname] = nid

        # For each node, check its input bindings have an origin
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_id = node.get("id", f"nodes[{i}]")
            inputs = node.get("inputs", [])
            if not isinstance(inputs, list):
                continue

            for j, ref in enumerate(inputs):
                if not isinstance(ref, dict):
                    continue
                bname = ref.get("binding")
                if not isinstance(bname, str):
                    continue
                if bname not in self._declared_bindings:
                    continue  # already flagged by BU-1

                # Check if this binding has a defined origin
                has_producer = bname in producer_map
                has_default = bname in bindings_with_defaults
                has_external_origin = bname in external_origin_bindings

                if not has_producer and not has_default and not has_external_origin:
                    self.findings.append(ValidationFinding(
                        ValidationSeverity.ERROR, "OR-1",
                        f"Node '{node_id}' reads binding '{bname}' "
                        f"which has no producer (no node outputs to it), "
                        f"no default value, and is execution-scoped"
                    ))

    # ── Mutable Conflict Detection (§2.2) ───────

    def _validate_mutable_conflicts(self):
        """
        Detect pairs of nodes that access the same mutable binding
        with at least one WRITE. These are conflict-pairs that the
        scheduler must handle.
        """
        plan = self.plan.get("plan")
        if not isinstance(plan, dict):
            return

        nodes = plan.get("nodes")
        if not isinstance(nodes, list):
            return

        # Build map: binding_name -> list of (node_id, has_write)
        binding_access: Dict[str, List[tuple]] = {}

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            nid = node.get("id", f"nodes[{i}]")
            if not isinstance(nid, str):
                continue

            effects = node.get("effects", [])
            has_write = isinstance(effects, list) and "WRITE" in effects

            for ref_list_name in ["inputs", "outputs"]:
                refs = node.get(ref_list_name, [])
                if not isinstance(refs, list):
                    continue
                for ref in refs:
                    if not isinstance(ref, dict):
                        continue
                    bname = ref.get("binding")
                    if not isinstance(bname, str):
                        continue

                    # Only check mutable bindings
                    binding = self._declared_bindings.get(bname)
                    if binding is None:
                        continue
                    if binding.get("mutability", "readonly") != "mutable":
                        continue

                    if bname not in binding_access:
                        binding_access[bname] = []
                    if (nid, has_write) not in binding_access[bname]:
                        binding_access[bname].append((nid, has_write))

        # Report conflicts: pairs accessing same mutable binding with >=1 WRITE
        for bname, access_list in binding_access.items():
            if len(access_list) < 2:
                continue

            writers = [nid for nid, w in access_list if w]
            readers = [nid for nid, w in access_list if not w]

            if writers and len(access_list) >= 2:
                all_nodes = [nid for nid, _ in access_list]
                self.findings.append(ValidationFinding(
                    ValidationSeverity.WARNING, "MC-1",
                    f"Mutable binding '{bname}' is accessed by multiple nodes "
                    f"with at least one WRITE: {sorted(all_nodes)}. "
                    f"Scheduler must resolve execution order (§2.2)."
                ))


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def validate_plan_file(filepath: str) -> Dict:
    """Validate a single plan JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "file": filepath,
            "valid": False,
            "error": f"Invalid JSON: {e}",
            "total_findings": 1,
            "errors": 1,
            "warnings": 0,
            "rejection_modes": {"PARSE-ERROR": 1},
            "findings": [{
                "severity": "error",
                "rule": "PARSE-1",
                "message": f"Invalid JSON: {e}",
                "node_id": None,
            }],
        }
    except FileNotFoundError:
        return {
            "file": filepath,
            "valid": False,
            "error": f"File not found: {filepath}",
            "total_findings": 1,
            "errors": 1,
            "warnings": 0,
            "rejection_modes": {"IO-ERROR": 1},
            "findings": [{
                "severity": "error",
                "rule": "IO-1",
                "message": f"File not found: {filepath}",
                "node_id": None,
            }],
        }

    validator = IRValidator(plan)
    validator.validate()
    result = validator.report_summary()
    result["file"] = filepath
    return result


def validate_plan_dir(dirpath: str) -> List[Dict]:
    """Validate all .json files in a directory."""
    results = []
    for filename in sorted(os.listdir(dirpath)):
        if filename.endswith(".json"):
            filepath = os.path.join(dirpath, filename)
            results.append(validate_plan_file(filepath))
    return results


def print_report(results: List[Dict]):
    """Pretty-print validation results using ASCII-only characters."""
    total = len(results)
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = total - valid_count

    # Aggregate rejection modes
    all_modes = {}
    for r in results:
        for mode, count in r.get("rejection_modes", {}).items():
            all_modes.setdefault(mode, 0)
            all_modes[mode] += count

    print(f"\n{'='*60}")
    print(f"  AEP-IR-1.0 Validation Report")
    print(f"{'='*60}")
    print(f"  Total plans : {total}")
    if total > 0:
        print(f"  Valid       : {valid_count} ({valid_count/total*100:.1f}% pass rate)")
    print(f"  Invalid     : {invalid_count}")
    print(f"{'='*60}")

    if all_modes:
        print(f"\n  Rejection Modes (by frequency):")
        sorted_modes = sorted(all_modes.items(), key=lambda x: -x[1])
        for mode, count in sorted_modes:
            pct = count / total * 100 if total > 0 else 0
            print(f"    {mode:10s}: {count} ({pct:.1f}%)")

    print(f"\n  Detailed Results:")
    for r in results:
        status = f"{PASS_CHAR} VALID" if r["valid"] else f"{FAIL_CHAR} INVALID"
        fname = os.path.basename(r.get("file", "stdin"))
        print(f"    {fname:45s} {status} ({r['errors']} errors, {r['warnings']} warnings)")
        if not r["valid"] and r.get("findings"):
            for f in r["findings"]:
                if f["severity"] == "error":
                    loc = f" [{f['node_id']}]" if f.get("node_id") else ""
                    print(f"      {ARROW_CHAR} {f['rule']}{loc}: {f['message']}")

    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python validator.py plan.json              # Validate a single plan")
        print("  python validator.py --dir plans/           # Validate all plans in directory")
        print("  python validator.py --stdin                # Read plan from stdin")
        sys.exit(1)

    if sys.argv[1] == "--dir":
        dirpath = sys.argv[2] if len(sys.argv) > 2 else "."
        results = validate_plan_dir(dirpath)
        print_report(results)

    elif sys.argv[1] == "--stdin":
        try:
            plan = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

        validator = IRValidator(plan)
        validator.validate()
        result = validator.report_summary()
        result["file"] = "stdin"
        print_report([result])

    else:
        filepath = sys.argv[1]
        result = validate_plan_file(filepath)
        print_report([result])
        if not result["valid"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
