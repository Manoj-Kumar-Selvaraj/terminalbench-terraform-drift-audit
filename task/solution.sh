#!/usr/bin/env bash
set -euo pipefail

python3 - << 'EOF'
import json
from pathlib import Path

IDEAL_FILE = Path("ideal_state.json")
CURRENT_FILE = Path("current_state.json")
OUTPUT_FILE = Path("audit_report.json")

def load_json(path):
    with path.open() as f:
        return json.load(f)

def normalize_resources(doc):
    """
    Converts resource list into a dict:
    {
      "type.name": { "attributes": {...} }
    }
    """
    result = {}
    for r in doc.get("resources", []):
        rid = f"{r['type']}.{r['name']}"
        result[rid] = r.get("attributes", {})
    return result

def flatten(obj, prefix=""):
    """
    Recursively flattens nested dicts into dot-delimited paths.
    Only dict recursion is supported. Lists are treated as atomic.
    """
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.update(flatten(v, path))
            else:
                items[path] = v
    else:
        items[prefix] = obj
    return items

ideal_doc = load_json(IDEAL_FILE)
current_doc = load_json(CURRENT_FILE)

ideal_resources = normalize_resources(ideal_doc)
current_resources = normalize_resources(current_doc)

ideal_ids = set(ideal_resources.keys())
current_ids = set(current_resources.keys())

missing_resources = sorted(ideal_ids - current_ids)
extra_resources = sorted(current_ids - ideal_ids)

attribute_drift = {}

for rid in sorted(ideal_ids & current_ids):
    ideal_attrs = flatten(ideal_resources.get(rid, {}))
    current_attrs = flatten(current_resources.get(rid, {}))

    all_keys = set(ideal_attrs.keys()) | set(current_attrs.keys())
    diffs = []

    for key in sorted(all_keys):
        expected = ideal_attrs.get(key)
        actual = current_attrs.get(key)

        if expected != actual:
            diffs.append({
                "attribute": key,
                "expected": expected,
                "actual": actual
            })

    if diffs:
        attribute_drift[rid] = diffs

drift_detected = bool(
    missing_resources or
    extra_resources or
    attribute_drift
)

output = {
    "audit_timestamp": "STATIC",
    "drift_detected": drift_detected,
    "missing_resources": missing_resources,
    "extra_resources": extra_resources,
    "attribute_drift": attribute_drift
}

with OUTPUT_FILE.open("w") as f:
    json.dump(output, f, indent=2, sort_keys=True)

EOF
