"""Feature taxonomy preflight, schema, and server-stack parity tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from watchtower.config.paths import FEATURE_TAXONOMY_PATH, PREFLIGHT_REFERENCES, PROJECT_ROOT
from watchtower.taxonomy import (
    check_preflight_references,
    load_feature_taxonomy,
    preflight_missing,
    validate_feature_taxonomy,
)
from watchtower.taxonomy.models import REQUIRED_ENTRY_FIELDS, VALID_DETECTION_CLASSES

SERVER_STACK_FEATURES = PREFLIGHT_REFERENCES["server_stack_features_yml"]


@pytest.fixture(scope="module")
def taxonomy():
    return load_feature_taxonomy()


@pytest.fixture(scope="module")
def server_stack_ids() -> set[str]:
    with SERVER_STACK_FEATURES.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)
    return {item["feature_id"] for item in catalog["features"]}


def test_preflight_reference_files_exist():
    missing = preflight_missing(PROJECT_ROOT)
    assert missing == [], f"Missing preflight references: {missing}"
    check_preflight_references(PROJECT_ROOT)


def test_taxonomy_has_81_features(taxonomy):
    assert taxonomy.total_features == 81
    assert len(taxonomy.features) == 81


def test_no_duplicate_feature_ids(taxonomy):
    ids = [entry.feature_id for entry in taxonomy.features]
    assert len(ids) == len(set(ids))


def test_all_primary_classes_known(taxonomy):
    for entry in taxonomy.features:
        assert entry.primary_detection_class in VALID_DETECTION_CLASSES
        for secondary in entry.secondary_detection_classes:
            assert secondary in VALID_DETECTION_CLASSES


def test_each_entry_has_required_fields(taxonomy):
    for entry in taxonomy.features:
        data = entry.model_dump()
        for field_name in REQUIRED_ENTRY_FIELDS:
            assert field_name in data
            assert data[field_name] is not None


def test_policy_rule_requires_approval_for_suppression(taxonomy):
    policy_entries = [
        e for e in taxonomy.features if e.primary_detection_class == "policy-rule"
    ]
    assert len(policy_entries) >= 1
    for entry in policy_entries:
        assert entry.requires_approval_for_suppression is True


def test_baseline_anomaly_has_baseline_context(taxonomy):
    baseline_entries = [
        e for e in taxonomy.features if e.primary_detection_class == "baseline-anomaly"
    ]
    assert len(baseline_entries) >= 1
    for entry in baseline_entries:
        assert entry.requires_baseline is True
        assert entry.has_baseline_context()


def test_server_stack_feature_id_parity(taxonomy, server_stack_ids):
    assert taxonomy.feature_ids == server_stack_ids


def test_policy_rule_list_matches_entries(taxonomy):
    policy_from_entries = {
        e.feature_id
        for e in taxonomy.features
        if e.primary_detection_class == "policy-rule"
    }
    assert set(taxonomy.policy_rule_features) == policy_from_entries


def test_taxonomy_file_validates_via_validator(taxonomy):
    validate_feature_taxonomy(taxonomy, SERVER_STACK_FEATURES)


def test_load_from_default_path():
    loaded = load_feature_taxonomy(FEATURE_TAXONOMY_PATH)
    assert loaded.total_features == 81
