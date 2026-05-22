# Sentinel UEBA Integration Prep

## Purpose

This note prepares the integration planning ground for the new product idea described in `sentinel-yeni-urun-konusma.md`.

Working assumption:

- The new product is a separate product in the same monorepo family.
- Sentinel remains infra/observability-focused.
- The new product is a UEBA / insider-risk / internal network monitoring CLI plus daemon.

Suggested working name during planning:

- `watchtower`
- `vigil`
- `sentinel-sec`

## Decision Snapshot From The Conversation

Confirmed from the conversation:

- Product category: LLM-assisted UEBA for private LAN / on-prem environments.
- Runtime mode: 7/24 daemon plus queryable CLI.
- Deployment target: air-gapped-like private networks and closed enterprise environments.
- Core design: existing SIEM/API sources stay in place; the new product becomes an interpretation, normalization, anomaly, and alert layer on top.
- Data strategy: adapters for known sources, fallback LLM path for unknown schemas.
- Learning model: first 1-2 months baseline learning, then active anomaly mode.
- Automation stance: recommend and alert first, do not auto-act on systems.

## Repo Scan Summary

### Best Reuse Candidate: `sentinel-coming`

Why it matters:

- Already has a Python CLI, tool registry, config layering, session/memory support, and read-only gateway pattern.
- Already separates CLI concerns from backend data access through `observability-gateway`.
- Already contains `memory/dream/extract/magic_docs` style components that align with long-running operator workflows.

Directly reusable ideas:

- Read-only gateway pattern
- CLI runtime and config layering
- Session and trajectory handling
- Turn-end memory hooks
- MCP-compatible operator tooling

Should not be reused as-is:

- Prometheus/Loki/Tempo-specific gateway contracts
- Observability-only query shapes

### Best Reuse Candidate For Stateful Analysis: `caglarkc-agent`

Why it matters:

- Already implements a LangGraph-based state machine with planner, dispatcher, worker, executor, validator, reviewer.
- Already has SQLite persistence, checkpointing, approval guard patterns, memory pipeline, daemon orientation, CLI and Telegram surfaces.
- This is the strongest existing reference for a long-running, resumable, stateful pipeline.

Directly reusable ideas:

- LangGraph graph/state patterns
- SQLite + checkpoint lifecycle
- Event bus and scheduler model
- Long-running daemon/service structure
- Memory consolidation and approval patterns

Should not be reused as-is:

- Software-project generation semantics
- File-writing worker/reviewer logic that is specific to coding workflows

### Best Reuse Candidate For General Agent Runtime: `argus`

Why it matters:

- Clean modular runtime for tool execution, permission levels, hooks, skills, trajectories, and multi-provider model access.
- Good reference for hardening the eventual CLI and agent runtime.

Directly reusable ideas:

- Permission model
- Hook model
- Tool registry ergonomics
- Multi-provider abstraction

### Best Reuse Candidate For Desktop Operator Surface: `nookspace`

Why it matters:

- If the product later needs a desktop security console, this is the strongest UI shell in the repo.
- Has session storage, trace visibility, tool transparency, MCP connectors, and sandboxed/local execution surfaces.

Current recommendation:

- Do not make this phase-1 critical.
- Keep it as a phase-3 or phase-4 packaging/UI option after CLI + daemon are stable.

### Useful Pattern References Only

- `estate-agent`: approval-gated tool pipeline and concise vertical product framing.
- `orioncli`: broad tool/plugin/gateway architecture ideas, but likely too wide to use as a direct base.
- `cli-claude`: memory/dreaming integration references already documented in both Sentinel and ARCHON notes.

## Recommended Product Positioning

Recommendation:

- Build as a separate product in the same monorepo family, not as a Sentinel subcommand in phase 1.

Reason:

- Target buyer, event model, alert semantics, storage needs, and compliance requirements differ from infra observability.
- Reuse should happen at pattern/module level, not by collapsing product boundaries too early.

Recommended relationship:

- Shared runtime patterns with Sentinel
- Shared optional UI shell later with NookSpace
- Shared orchestration techniques with ARCHON
- Separate package, config namespace, docs, and release lifecycle

## Proposed Product Shape

```text
SIEM / Internal Sources
  ├── Wazuh
  ├── Splunk
  ├── QRadar
  ├── Elastic
  ├── Exchange / mail
  ├── AD / LDAP
  └── NetFlow / firewall / file logs
            ↓
security-gateway (read-only adapters)
            ↓
langgraph analysis service
  ├── ingest
  ├── source detect
  ├── schema detect
  ├── normalize
  ├── baseline lookup/update
  ├── anomaly score
  ├── severity decision
  ├── alert dispatch
  └── rule learning / fallback integration
            ↓
stores
  ├── sqlite/postgres: events, baselines, rules, alerts
  ├── memory summaries
  └── audit logs
            ↓
operator surfaces
  ├── CLI query/review
  ├── daemon/service status
  ├── Telegram/Slack later
  └── desktop UI later
```

## Concrete Reuse Plan

### Reuse From `sentinel-coming`

Use as foundation for:

- config loader patterns
- provider abstraction approach
- session and memory layout
- safe tool execution model
- read-only gateway boundary

Likely source areas:

- `sentinel-coming/cli/src/sentinel_cli/config/`
- `sentinel-coming/cli/src/sentinel_cli/tools/`
- `sentinel-coming/cli/src/sentinel_cli/session/`
- `sentinel-coming/cli/src/sentinel_cli/memory/`
- `sentinel-coming/observability-gateway/src/observability_gateway/`

### Reuse From `caglarkc-agent`

Use as foundation for:

- daemon and state-machine orchestration
- durable job lifecycle
- checkpoint/recovery
- background scheduling
- approval and event contracts

Likely source areas:

- `caglarkc-agent/src/core/`
- `caglarkc-agent/src/graph/`
- `caglarkc-agent/src/storage/`
- `caglarkc-agent/src/interfaces/cli/`
- `caglarkc-agent/src/interfaces/telegram/`

### Reuse From `argus`

Use as reference for:

- permission tiers
- tool registry boundaries
- multi-agent and multi-provider runtime abstractions
- hook naming and execution surfaces

Likely source areas:

- `argus/argus/tools/`
- `argus/argus/hooks/`
- `argus/argus/config/`
- `argus/argus/agents/`

### Reuse From `nookspace`

Use later for:

- operator desktop console
- trace and session UX
- connector management UX
- secure local execution wrapper

Likely source areas:

- `nookspace/src/main/session/`
- `nookspace/src/main/tools/`
- `nookspace/src/main/mcp/`
- `nookspace/src/renderer/components/`

## Phase 0 Architecture Decisions

These should be fixed before implementation starts:

1. Product package name and repo location
2. Storage choice for phase 1
3. First supported SIEM target
4. First alert destination
5. First LLM provider strategy for closed networks
6. Whether gateway and analyzer are same process or split services

Recommended defaults:

1. New package under repo root, separate from `sentinel-coming`
2. SQLite first, Postgres optional later
3. Wazuh first
4. CLI + email/webhook first
5. OpenAI-compatible abstraction with local-model path
6. Split service boundary early: gateway separate, analyzer separate

## Phase 1 Delivery Slice

Keep phase 1 narrow:

- Wazuh adapter only
- Normalized event model for login/file-transfer/network-volume anomalies
- Learning mode
- Active mode
- Alert tiers: `log`, `warning`, `alert`, `critical`
- CLI queries:
  - recent alerts
  - user baseline
  - unusual activity in last 24h
  - unknown schema events
- Manager notifications through one channel only

## Domain Model Draft

Core entities:

- `source`
- `raw_event`
- `normalized_event`
- `user_profile`
- `department_profile`
- `baseline_snapshot`
- `anomaly_assessment`
- `rule_candidate`
- `rule_version`
- `alert`
- `alert_ack`
- `learning_window`

## Main Risks Already Visible

### Product Risks

- Compliance and employee privacy constraints
- False positives during early rollout
- Customer-specific baseline drift
- Overusing LLMs where deterministic scoring is enough

### Technical Risks

- Schema sprawl across SIEMs and custom logs
- Closed-network deployment constraints
- Long-term storage growth for raw events
- Alert fatigue without strong deduplication and suppression

### Repo Risks

- There are multiple overlapping agent runtimes in the monorepo; copying too much from all of them will create a fourth inconsistent runtime.
- `sentinel-coming/agentic/` is explicitly reference material, not the main Sentinel product tree.
- Some products are broad platforms; this product should stay opinionated and narrow in phase 1.

## Recommended Boundaries

Build now:

- dedicated security gateway
- dedicated analysis daemon
- dedicated CLI package
- dedicated storage schema

Reuse patterns only:

- Sentinel CLI runtime ideas
- ARCHON LangGraph orchestration ideas
- Argus permission and tool ideas
- NookSpace desktop shell ideas

Avoid in phase 1:

- full desktop app
- plugin marketplace
- many SIEMs at once
- auto-remediation
- mixed infra-observability and employee-behavior telemetry in one schema

## Questions That Still Need Your Decision

These are the remaining blocking product choices:

1. Do you want phase 1 to start as `Wazuh-first`, or do you want `Wazuh + Splunk` together from day one?
2. Is the first alert channel `email`, `Telegram`, `webhook`, or an internal dashboard/CLI inbox?
3. In closed environments, do you want local models to be a hard requirement from day one, or only an optional fallback?
4. Do you want the new product to live as a new root folder beside `sentinel-coming`, or inside `sentinel-coming` as a sibling package?
5. Should phase 1 include mail-source monitoring immediately, or should we start with login/file/network events only?

## Immediate Next Step

After the answers above, the next planning artifact should be:

- a concrete folder layout
- a phase-1 schema draft
- a Wazuh adapter contract
- a LangGraph node contract
- a config/env matrix
- a milestone plan with implementation order
