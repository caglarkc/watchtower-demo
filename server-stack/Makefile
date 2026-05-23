.PHONY: up down config clean feature feature-negative test-smoke test-features test-phase1 test-phase2 test-phase3 test-integration test-integration-phase3 coverage coverage-phase2 coverage-phase3 seed-baseline seed-phase1 seed-phase2 seed-phase3 test-all

PYTHON ?= .venv/bin/python
PYTEST ?= .venv/bin/pytest
COMPOSE ?= docker compose

up:
	$(COMPOSE) up -d
	@mkdir -p logs/{identity,samba,dns,dhcp,zeek,endpoint,postfix,dovecot,roundcube,postgres,gitea,nginx,app,artifact,siem,hypervisor,ai_gateway,proxy,cloud,vault,mattermost,cups,badge,hris,suitecrm,wiki,dlp,activity} reports/features reports/coverage

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v --remove-orphans

config:
	$(COMPOSE) config

seed-baseline: seed-phase1 seed-phase2 seed-phase3

seed-phase1:
	@mkdir -p logs/{identity,samba,dns,dhcp,zeek,endpoint} reports/features
	$(PYTHON) simulation/event_generator/generate_phase1_replays.py

seed-phase2:
	$(PYTHON) simulation/event_generator/generate_phase2_replays.py

seed-phase3:
	$(PYTHON) simulation/event_generator/generate_phase3_replays.py

feature:
	@test -n "$(FEATURE)" || (echo "Usage: make feature FEATURE=F-001" && exit 1)
	$(PYTHON) simulation/event_generator/run_feature.py --feature $(FEATURE) --mode positive

feature-negative:
	@test -n "$(FEATURE)" || (echo "Usage: make feature-negative FEATURE=F-001" && exit 1)
	$(PYTHON) simulation/event_generator/run_feature.py --feature $(FEATURE) --mode negative

test-smoke:
	$(PYTEST) tests/smoke -v

test-features:
	$(PYTEST) tests/feature -v

test-phase1:
	$(PYTEST) tests/feature -m phase1 -v

test-phase2:
	$(PYTEST) tests/feature -m phase2 -v

test-integration:
	$(PYTEST) tests/integration -m phase2 -v

test-phase3:
	$(PYTEST) tests/feature -m phase3 -v

test-integration-phase3:
	$(PYTEST) tests/integration -m phase3 -v

coverage:
	$(PYTHON) simulation/feature_catalog/report_coverage.py --phase 1

coverage-phase2:
	$(PYTHON) simulation/feature_catalog/report_coverage.py --phase 2

test-all: test-smoke test-phase1 test-phase2 test-integration coverage coverage-phase2
