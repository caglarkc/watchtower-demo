"""Schema and business-rule validation for feature taxonomy."""

from __future__ import annotations

from pathlib import Path

import yaml

from watchtower.config import PREFLIGHT_REFERENCES
from watchtower.taxonomy.models import (
    BASELINE_CONTEXT_TOKENS,
    VALID_DETECTION_CLASSES,
    FeatureTaxonomy,
    FeatureTaxonomyEntry,
)


class TaxonomyValidationError(ValueError):
    """Raised when taxonomy validation fails."""


def _load_server_stack_feature_ids(path: Path) -> set[str]:
    with path.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)
    features = catalog.get("features", [])
    return {item["feature_id"] for item in features if "feature_id" in item}


def validate_feature_taxonomy(
    taxonomy: FeatureTaxonomy,
    server_stack_features_yml: Path | None = None,
) -> None:
    """Validate taxonomy structure and cross-reference server-stack catalog."""
    errors: list[str] = []

    if taxonomy.total_features != 81:
        errors.append(f"total_features must be 81, got {taxonomy.total_features}")

    if len(taxonomy.features) != 81:
        errors.append(f"features list must contain 81 entries, got {len(taxonomy.features)}")

    ids = [entry.feature_id for entry in taxonomy.features]
    if len(ids) != len(set(ids)):
        dupes = sorted({fid for fid in ids if ids.count(fid) > 1})
        errors.append(f"duplicate feature_id values: {dupes}")

    for entry in taxonomy.features:
        errors.extend(_validate_entry(entry))

    policy_from_list = set(taxonomy.policy_rule_features)
    policy_from_entries = {
        e.feature_id
        for e in taxonomy.features
        if e.primary_detection_class == "policy-rule"
    }
    if policy_from_list != policy_from_entries:
        missing = policy_from_entries - policy_from_list
        extra = policy_from_list - policy_from_entries
        if missing:
            errors.append(f"policy_rule_features missing ids: {sorted(missing)}")
        if extra:
            errors.append(f"policy_rule_features has unknown ids: {sorted(extra)}")

    features_path = server_stack_features_yml or PREFLIGHT_REFERENCES[
        "server_stack_features_yml"
    ]
    if features_path.is_file():
        stack_ids = _load_server_stack_feature_ids(features_path)
        taxonomy_ids = taxonomy.feature_ids
        if taxonomy_ids != stack_ids:
            only_taxonomy = sorted(taxonomy_ids - stack_ids)
            only_stack = sorted(stack_ids - taxonomy_ids)
            if only_taxonomy:
                errors.append(
                    f"taxonomy ids not in server-stack: {only_taxonomy}"
                )
            if only_stack:
                errors.append(
                    f"server-stack ids missing from taxonomy: {only_stack}"
                )

    if errors:
        raise TaxonomyValidationError("; ".join(errors))


def _validate_entry(entry: FeatureTaxonomyEntry) -> list[str]:
    errors: list[str] = []
    fid = entry.feature_id

    if entry.primary_detection_class not in VALID_DETECTION_CLASSES:
        errors.append(f"{fid}: unknown primary_detection_class")

    for secondary in entry.secondary_detection_classes:
        if secondary not in VALID_DETECTION_CLASSES:
            errors.append(f"{fid}: unknown secondary class {secondary}")

    if entry.primary_detection_class == "policy-rule":
        if not entry.requires_approval_for_suppression:
            errors.append(
                f"{fid}: policy-rule must set requires_approval_for_suppression=true"
            )
        if entry.requires_baseline:
            errors.append(f"{fid}: policy-rule must not require baseline")
        if entry.can_be_feedback_learned:
            errors.append(f"{fid}: policy-rule must not be feedback-learned")

    if entry.primary_detection_class == "hard-rule":
        if entry.requires_baseline:
            errors.append(f"{fid}: hard-rule must not require baseline")
        if entry.can_be_feedback_learned:
            errors.append(f"{fid}: hard-rule must not be feedback-learned")

    if entry.primary_detection_class == "baseline-anomaly":
        if not entry.requires_baseline:
            errors.append(f"{fid}: baseline-anomaly must require baseline")
        if not entry.has_baseline_context():
            errors.append(f"{fid}: baseline-anomaly missing baseline context")
        if not entry.can_be_feedback_learned:
            errors.append(f"{fid}: baseline-anomaly should allow feedback learning")

    if entry.primary_detection_class == "cross-signal":
        if len(entry.required_context) < 2:
            errors.append(f"{fid}: cross-signal needs multi-source required_context")

    if not entry.server_stack_replay_refs:
        errors.append(f"{fid}: server_stack_replay_refs must not be empty")

  if not entry.required_context:
        errors.append(f"{fid}: required_context must not be empty")

    return errors
