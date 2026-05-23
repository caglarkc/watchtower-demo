"""Phase 0 catalog integrity tests for feature/scenario coverage manifests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

CATALOG_DIR = Path(__file__).resolve().parents[2] / "simulation" / "feature_catalog"
REQUIRED_FEATURES = 81
REQUIRED_SCENARIOS = 83


@pytest.fixture(scope="module")
def features_doc() -> dict:
    with (CATALOG_DIR / "features.yml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def scenarios_doc() -> dict:
    with (CATALOG_DIR / "scenarios.yml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def matrix_doc() -> dict:
    with (CATALOG_DIR / "coverage_matrix.yml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_feature_count_is_81(features_doc: dict) -> None:
    assert features_doc["total_features"] == REQUIRED_FEATURES
    assert len(features_doc["features"]) == REQUIRED_FEATURES


def test_scenario_count_is_83(scenarios_doc: dict) -> None:
    assert scenarios_doc["total_scenarios"] == REQUIRED_SCENARIOS
    assert len(scenarios_doc["scenarios"]) == REQUIRED_SCENARIOS


def test_no_duplicate_feature_ids(features_doc: dict) -> None:
    ids = [f["feature_id"] for f in features_doc["features"]]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids, key=lambda x: int(x.split("-")[1]))


def test_no_duplicate_scenario_ids(scenarios_doc: dict) -> None:
    ids = [s["scenario_id"] for s in scenarios_doc["scenarios"]]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids, key=lambda x: int(x.split("-")[1]))


def test_each_feature_has_replay_and_evidence(features_doc: dict) -> None:
    for feat in features_doc["features"]:
        fid = feat["feature_id"]
        assert feat.get("positive_command"), f"{fid}: positive_command required"
        assert feat.get("negative_command"), f"{fid}: negative_command required"
        assert feat.get("evidence_path"), f"{fid}: evidence_path required"
        assert "make feature" in feat["positive_command"]
        assert "make feature-negative" in feat["negative_command"]
        assert feat["evidence_path"] == f"reports/features/{fid}.json"


def test_each_scenario_maps_to_features(scenarios_doc: dict) -> None:
    root = CATALOG_DIR.parents[1]
    for scen in scenarios_doc["scenarios"]:
        sid = scen["scenario_id"]
        assert scen.get("feature_ids"), f"{sid}: feature_ids required"
        assert len(scen["feature_ids"]) >= 1
        pos = root / scen["replay_script"]
        neg = root / scen["negative_replay_script"]
        assert pos.exists(), f"{sid}: missing {pos}"
        assert neg.exists(), f"{sid}: missing {neg}"


def test_coverage_matrix_links_valid_features(
    features_doc: dict, scenarios_doc: dict, matrix_doc: dict
) -> None:
    feature_ids = {f["feature_id"] for f in features_doc["features"]}
    scenario_ids = {s["scenario_id"] for s in scenarios_doc["scenarios"]}

    for mapping in matrix_doc["scenario_to_features"]:
        assert mapping["scenario_id"] in scenario_ids
        for fid in mapping["feature_ids"]:
            assert fid in feature_ids

    assert matrix_doc["summary"]["total_features"] == REQUIRED_FEATURES
    assert matrix_doc["summary"]["total_scenarios"] == REQUIRED_SCENARIOS
    assert matrix_doc["summary"]["features_without_scenario"] == []


def test_all_features_covered_by_at_least_one_scenario(matrix_doc: dict) -> None:
    for entry in matrix_doc["feature_to_scenarios"]:
        assert entry["scenario_count"] >= 1, f"{entry['feature_id']} has no scenario"
