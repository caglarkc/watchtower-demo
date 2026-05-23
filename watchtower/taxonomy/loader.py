"""Load feature taxonomy from YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from watchtower.config import FEATURE_TAXONOMY_PATH
from watchtower.taxonomy.models import FeatureTaxonomy
from watchtower.taxonomy.validator import validate_feature_taxonomy


def load_feature_taxonomy(
    path: Path | None = None,
    *,
    server_stack_features_yml: Path | None = None,
    validate: bool = True,
) -> FeatureTaxonomy:
    """Load and optionally validate the feature taxonomy YAML."""
    taxonomy_path = path or FEATURE_TAXONOMY_PATH
    with taxonomy_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    taxonomy = FeatureTaxonomy.model_validate(raw)
    if validate:
        validate_feature_taxonomy(taxonomy, server_stack_features_yml)
    return taxonomy
