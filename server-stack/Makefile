.PHONY: up down config clean feature feature-negative scenario scenario-negative test-smoke test-features test-scenarios test-phase1 test-phase2 test-phase3 test-integration test-integration-phase3 coverage coverage-phase1 coverage-phase2 coverage-phase3 coverage-scenarios coverage-all seed-baseline seed-phase1 seed-phase2 seed-phase3 seed-scenarios test-all real-up real-down seed-real-all real-feature real-feature-negative test-real test-real-all real-coverage

PYTHON ?= .venv/bin/python
PYTEST ?= .venv/bin/pytest
COMPOSE ?= docker compose

up:
	$(COMPOSE) up -d
	@mkdir -p logs/{identity,samba,dns,dhcp,zeek,endpoint,postfix,dovecot,roundcube,postgres,gitea,nginx,app,artifact,siem,hypervisor,ai_gateway,proxy,cloud,vault,mattermost,cups,badge,hris,suitecrm,wiki,dlp,activity} reports/features reports/scenarios reports/coverage reports/scenario_logs

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v --remove-orphans

config:
	$(COMPOSE) config

seed-phase1:
	@mkdir -p logs/{identity,samba,dns,dhcp,zeek,endpoint} reports/features
	$(PYTHON) simulation/event_generator/generate_phase1_replays.py

seed-phase2:
	$(PYTHON) simulation/event_generator/generate_phase2_replays.py

seed-phase3:
	$(PYTHON) simulation/event_generator/generate_phase3_replays.py

seed-scenarios:
	$(PYTHON) simulation/scenarios/generate_scenario_replays.py

seed-baseline: seed-phase1 seed-phase2 seed-phase3 seed-scenarios

feature:
	@test -n "$(FEATURE)" || (echo "Usage: make feature FEATURE=F-001" && exit 1)
	$(PYTHON) simulation/event_generator/run_feature.py --feature $(FEATURE) --mode positive

feature-negative:
	@test -n "$(FEATURE)" || (echo "Usage: make feature-negative FEATURE=F-001" && exit 1)
	$(PYTHON) simulation/event_generator/run_feature.py --feature $(FEATURE) --mode negative

scenario:
	@test -n "$(SCENARIO)" || (echo "Usage: make scenario SCENARIO=S-001" && exit 1)
	$(PYTHON) simulation/scenarios/run_scenario.py --scenario $(SCENARIO) --mode positive

scenario-negative:
	@test -n "$(SCENARIO)" || (echo "Usage: make scenario-negative SCENARIO=S-001" && exit 1)
	$(PYTHON) simulation/scenarios/run_scenario.py --scenario $(SCENARIO) --mode negative

test-smoke:
	$(PYTEST) tests/smoke -v

test-features:
	$(PYTEST) tests/feature -v

test-scenarios:
	$(PYTEST) tests/scenario -v

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
	$(PYTHON) simulation/feature_catalog/report_coverage.py --all

coverage-phase1:
	$(PYTHON) simulation/feature_catalog/report_coverage.py --phase 1

coverage-phase2:
	$(PYTHON) simulation/feature_catalog/report_coverage.py --phase 2

coverage-phase3:
	$(PYTHON) simulation/feature_catalog/report_coverage.py --phase 3

coverage-scenarios:
	$(PYTHON) simulation/scenarios/report_scenario_coverage.py --all

coverage-all: coverage coverage-scenarios

test-all: seed-baseline test-smoke test-features test-scenarios coverage-all

# --- RI-0 Real parity foundation (does not replace synthetic test-all) ---

real-up:
	$(COMPOSE) up -d
	$(COMPOSE) --profile real-identity up -d
	@mkdir -p reports/real/{features,scenarios,coverage,logs} logs/samba logs/dns seeds/real
	@chmod -R a+rwX logs/dns logs/samba 2>/dev/null || true

real-down:
	$(COMPOSE) --profile real-identity down
	$(COMPOSE) down

seed-real-identity:
	$(PYTHON) simulation/real/seed_real_identity.py

seed-real-files:
	$(PYTHON) simulation/real/seed_real_files.py

seed-real-all: seed-real-identity seed-real-files
	$(PYTHON) simulation/real/seed_real_all.py

real-feature:
	@test -n "$(FEATURE)" || (echo "Usage: make real-feature FEATURE=F-001" && exit 1)
	$(PYTHON) simulation/real/run_real_feature.py --feature $(FEATURE) --mode positive

real-feature-negative:
	@test -n "$(FEATURE)" || (echo "Usage: make real-feature-negative FEATURE=F-001" && exit 1)
	$(PYTHON) simulation/real/run_real_feature.py --feature $(FEATURE) --mode negative

test-real:
	$(PYTEST) tests/real -v

test-real-p0:
	$(PYTEST) tests/real/features -m p0 -v

test-real-all: seed-real-all test-real test-real-p0 real-coverage

real-coverage:
	$(PYTHON) simulation/real/report_real_coverage.py --all
