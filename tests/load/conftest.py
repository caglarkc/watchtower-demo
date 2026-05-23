"""Load tests share production fixtures."""

from tests.production.conftest import (  # noqa: F401
    bootstrapped_tenant,
    prod_app,
    prod_db,
    prod_settings,
)
