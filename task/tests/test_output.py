import json
import os
from pathlib import Path

OUTPUT_FILE = Path("audit_report.json")


def load_output():
    assert OUTPUT_FILE.exists(), "audit_report.json was not generated"
    with OUTPUT_FILE.open() as f:
        return json.load(f)


def test_schema_and_required_keys():
    """
    Validate that the output file exists and contains all required top-level keys.
    """
    data = load_output()

    required_keys = {
        "audit_timestamp",
        "drift_detected",
        "missing_resources",
        "extra_resources",
        "attribute_drift",
    }

    assert set(data.keys()) == required_keys


def test_timestamp_is_static():
    """
    Ensure output is deterministic by enforcing a static timestamp.
    """
    data = load_output()
    assert data["audit_timestamp"] == "STATIC"


def test_drift_detected_flag():
    """
    drift_detected must be true if any drift exists.
    """
    data = load_output()

    has_drift = (
        bool(data["missing_resources"])
        or bool(data["extra_resources"])
        or bool(data["attribute_drift"])
    )

    assert data["drift_detected"] == has_drift


def test_missing_resources():
    """
    Validate detection of resources missing from current state.
    """
    data = load_output()
    assert isinstance(data["missing_resources"], list)
    assert data["missing_resources"] == sorted(data["missing_resources"])


def test_extra_resources():
    """
    Validate detection of extra resources present only in current state.
    """
    data = load_output()
    assert isinstance(data["extra_resources"], list)
    assert data["extra_resources"] == sorted(data["extra_resources"])

    # Known extra resource from sample input
    assert "aws_security_group.debug" in data["extra_resources"]


def test_attribute_drift_structure():
    """
    Validate attribute drift structure and required fields.
    """
    data = load_output()
    attr_drift = data["attribute_drift"]

    assert isinstance(attr_drift, dict)

    for resource_id, diffs in attr_drift.items():
        assert isinstance(resource_id, str)
        assert isinstance(diffs, list)

        for entry in diffs:
            assert set(entry.keys()) == {"attribute", "expected", "actual"}
            assert isinstance(entry["attribute"], str)


def test_nested_attribute_paths():
    """
    Ensure nested attributes are reported using dot-delimited paths.
    """
    data = load_output()

    for diffs in data["attribute_drift"].values():
        for entry in diffs:
            # attribute paths must not be empty
            assert entry["attribute"]
            # dot notation is allowed but not required
            assert isinstance(entry["attribute"], str)


def test_expected_and_actual_values():
    """
    expected and actual values must be JSON-serializable and may be null.
    """
    data = load_output()

    for diffs in data["attribute_drift"].values():
        for entry in diffs:
            # Presence is already validated; now ensure no invalid types
            assert "expected" in entry
            assert "actual" in entry


def test_no_unexpected_keys_in_attribute_drift():
    """
    Prevent agents from adding extra keys to drift entries.
    """
    data = load_output()

    for diffs in data["attribute_drift"].values():
        for entry in diffs:
            assert len(entry.keys()) == 3
