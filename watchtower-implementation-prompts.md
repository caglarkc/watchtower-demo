# Watchtower Implementation Prompts

Bu dokuman Watchtower urununu sifirdan production-ready hale getirecek AI gorev promptlarini icerir.

Kural:

- Fazlar sirasiyla uygulanir.
- Test gecmeden sonraki faza gecilmez.
- Test fail olursa implementor once hatayi duzeltir, sonra ayni testleri tekrar calistirir.
- Teslimde degisen dosyalar, yazilan testler, calistirilan testler, sonuc ve kalan riskler zorunludur.
- `server-stack/` urun kodu degildir; sadece E2E test lab olarak kullanilir.
- LLM final alert karari vermez.
- Manager feedback direkt stable rule yapmaz; `pending_rule -> approve -> stable`.
- Kod yazacak AI, verilen faz kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli tum komutlari calistirmaya yetkilidir.
- Komut/test fail olursa teslim etmez; once hatayi duzeltir, sonra ayni komutu/gate'i tekrar calistirir ve pass kanitiyla teslim eder.

---

## Genel PM Prompt

```text
[GOREV]
GOREV: Watchtower product implementation fazlarini sirasiyla yonet, alt gorevlere bol, test kaniti olmadan faz kapatma.
FAZ: Tum Fazlar
ROL: test
SKILL: /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-pm-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Urun klasoru: /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo
- Test lab: /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-features-final.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-scenarios-final.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/simulation/feature_catalog/features.yml
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/reports/real/coverage/real_final_gate.json

YAPILACAK:
1. Faz 0'dan Faz 11'e kadar sirayla ilerle.
2. Her faz icin tek sahipli alt gorevler uret.
3. Her alt gorevde tekil rol belirt: taxonomy, connector, storage, baseline, decision, langgraph, llm, cli, test veya docs.
4. Her fazda test dosyasi yazilmasini ve testlerin calistirilmasini zorunlu kil.
5. Test fail olursa fazi kapatma; implementor'a revizyon ver.
6. Faz kapanisinda degisen dosyalar, testler, komutlar ve riskleri ozetle.

TESTLER:
1. Her fazin kendi gate komutlari calismali.
2. Faz 10'da server-stack 81 feature / 83 scenario E2E gate calismali.
3. Faz 11'de production readiness gate calismali.

TESLIM KRITERLERI:
- Faz faz sonuc raporu
- Her faz icin test kaniti
- Fail varsa revizyon kaydi
- Kalan riskler
```

---

## Faz 0 — Taxonomy & Architecture Freeze

```text
[GOREV]
GOREV: 81 feature icin Watchtower feature taxonomy dosyasini ve validator testlerini olustur.
FAZ: Faz 0 — Taxonomy & Architecture Freeze
ROL: taxonomy
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-features-final.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/simulation/feature_catalog/features.yml
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/reports/real/coverage/real_final_gate.json
- Etkilenecek dosyalar:
  - watchtower/config/feature_taxonomy.yml
  - watchtower/config/__init__.py
  - watchtower/taxonomy/
  - tests/config/test_feature_taxonomy.py

YAPILACAK:
1. Referans dosyalar icin preflight varlik kontrolu yaz.
2. 81 feature icin `watchtower/config/feature_taxonomy.yml` olustur.
3. Her feature icin su alanlari doldur:
   - feature_id
   - primary_detection_class
   - secondary_detection_classes
   - default_severity_floor
   - requires_baseline
   - can_be_feedback_learned
   - requires_approval_for_suppression
   - required_context
   - server_stack_replay_refs
4. Detection class degerleri sadece sunlar olabilir:
   - policy-rule
   - hard-rule
   - baseline-anomaly
   - cross-signal
5. Policy-rule entry'lerinde suppression icin approval zorunlu olsun.
6. Taxonomy loader ve schema validator yaz.
7. Server-stack feature id'leri ile 81/81 uyumu test et.

TESTLER:
1. `pytest tests/config/test_feature_taxonomy.py -v`
2. Testler sunlari assert etmeli:
   - preflight referans dosyalari mevcut
   - taxonomy 81 feature iceriyor
   - duplicate feature_id yok
   - unknown primary class yok
   - her entry zorunlu alanlari iceriyor
   - policy-rule entry'lerinde `requires_approval_for_suppression=true`
   - baseline-anomaly entry'lerinde baseline context var
   - server-stack features.yml ile feature id set'i ayni

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- 81/81 taxonomy pass kaniti
- kalan riskler
```

---

## Faz 1 — Product Skeleton

```text
[GOREV]
GOREV: Watchtower urun package, CLI skeleton, config, migration, tenant/bootstrap ve mode controller altyapisini kur.
FAZ: Faz 1 — Product Skeleton
ROL: cli
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - pyproject.toml
  - watchtower/
  - watchtower/cli/
  - watchtower/config/
  - watchtower/storage/
  - watchtower/domain/
  - tests/unit/
  - tests/integration/

YAPILACAK:
1. `watchtower/` Python package iskeletini olustur.
2. Typer tabanli `wt` CLI skeleton kur.
3. Config loader yaz: env + config file + defaults.
4. SQLite migration sistemi kur.
5. Tenant modelini ve bootstrap admin zorunlulugunu ekle.
6. Mode controller yaz: `learn`, `run`, `hybrid`.
7. Audit logging temelini ekle.
8. MVP'de Telegram ekleme; CLI-first kal.

TESTLER:
1. `pytest tests/unit tests/integration -v`
2. Testler sunlari assert etmeli:
   - fresh DB migration calisir
   - tenant isolation baslar
   - bootstrap admin yoksa protected komutlar calismaz
   - mode default `learn`
   - mode switch `learn -> run -> hybrid` calisir
   - CLI smoke: `wt status`, `wt modes get`

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- CLI smoke ciktilari
- kalan riskler
```

---

## Faz 2 — Connector & Ingest

```text
[GOREV]
GOREV: Read-only connector protocolunu, server-stack/file/elasticsearch/wazuh connectorlarini ve raw event ingest store'unu uygula.
FAZ: Faz 2 — Connector & Ingest
ROL: connector
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md
- Etkilenecek dosyalar:
  - watchtower/connectors/
  - watchtower/ingest/
  - watchtower/storage/
  - watchtower/domain/events.py
  - tests/connectors/
  - tests/integration/test_ingest_*.py

YAPILACAK:
1. Connector protocol tanimla:
   - health()
   - poll(cursor, limit)
   - ack(cursor)
   - schema_hint()
2. `server_stack_connector` yaz; server-stack log/evidence dosyalarini read-only okusun.
3. `file_jsonl_connector` yaz.
4. `elasticsearch_connector` yaz; health/query testlenebilir olsun.
5. `wazuh_connector` icin Wazuh-compatible REST adapter skeleton yaz.
6. Cursor ve deduplication modelini uygula.
7. Raw event store ve source cursor tablolarini migration'a ekle.
8. Connector failure tum sistemi dusurmemeli.

TESTLER:
1. `pytest tests/connectors tests/integration -v`
2. Testler sunlari assert etmeli:
   - mock connector contract pass
   - server-stack log ingestion pass
   - file JSONL ingestion pass
   - elasticsearch health/query mocked veya local pass
   - cursor duplicate event yazmaz
   - source failure graceful degradation

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- ingest edilen raw event sayisi ornegi
- kalan riskler
```

---

## Faz 3 — Normalization & Candidate Extraction

```text
[GOREV]
GOREV: Unified event schema, known adapters, unknown schema queue ve candidate extractor katmanini kur.
FAZ: Faz 3 — Normalization & Candidate Extraction
ROL: storage
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/simulation/feature_catalog/features.yml
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/simulation/feature_catalog/scenarios.yml
- Etkilenecek dosyalar:
  - watchtower/domain/normalized_event.py
  - watchtower/normalization/
  - watchtower/candidates/
  - watchtower/storage/migrations/
  - tests/normalization/
  - tests/candidates/

YAPILACAK:
1. Unified event schema tanimla.
2. Known adapters yaz: server-stack, file JSONL, elasticsearch/wazuh-compatible.
3. Unknown schema queue modeli ekle.
4. LLM kullanmadan deterministic normalization path'i calisir yap.
5. Candidate extractor yaz; raw eventleri dogrudan graph'a sokma.
6. Candidate event store migration ekle.
7. Feature taxonomy ile feature_hint baglantisi kur.

TESTLER:
1. `pytest tests/normalization tests/candidates -v`
2. Testler sunlari assert etmeli:
   - 81 feature fixture normalize olur
   - 83 scenario fixture normalize olur veya scenario source refs cozulur
   - unknown schema queue'ya duser
   - raw event graph'a dogrudan girmez
   - candidate event gerekli actor/action/resource/time alanlarini icerir

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- normalize edilen feature/scenario coverage ozeti
- kalan riskler
```

---

## Faz 4 — Baseline Engine

```text
[GOREV]
GOREV: Kullanici, departman, rol, asset ve zaman penceresi bazli baseline engine'i 45 gun default learning window ile uygula.
FAZ: Faz 4 — Baseline Engine
ROL: baseline
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - watchtower/baseline/
  - watchtower/domain/profiles.py
  - watchtower/storage/migrations/
  - tests/baseline/

YAPILACAK:
1. User, department, role, asset profile modellerini uygula.
2. 45 gun default learning window ekle; config ile degisebilir olsun.
3. Daily/weekly/monthly baseline snapshot hesaplari yaz.
4. Confidence score hesapla.
5. User-specific baseline'in department average tarafindan ezilmesini engelle.
6. Manager/worker farkini role profile'a yansit.
7. Low-confidence baseline ile `run` mode transition onermeme kuralini uygula.

TESTLER:
1. `pytest tests/baseline -v`
2. Testler sunlari assert etmeli:
   - 45 gunluk replay baseline uretir
   - configurable learning duration calisir
   - user-specific normal high-volume davranis normal kalir
   - ayni departmanda manager/worker ayrimi profile yansir
   - confidence dusukse run transition blocked/recommended=false

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- baseline snapshot ornegi
- kalan riskler
```

---

## Faz 5 — Feedback & Rule Approval

```text
[GOREV]
GOREV: Manager/operator feedback, pending_rule, approval workflow, scoped feedback_rule ve expiry/audit mekanizmasini uygula.
FAZ: Faz 5 — Feedback & Rule Approval
ROL: decision
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - watchtower/feedback/
  - watchtower/rules/
  - watchtower/storage/migrations/
  - watchtower/domain/rules.py
  - tests/feedback/
  - tests/rules/

YAPILACAK:
1. Feedback event modeli yaz:
   - expected_behavior
   - false_positive
   - true_positive
   - temporary_exception
   - project_context
   - role_change
   - needs_investigation
2. Pending rule modeli yaz.
3. Approval workflow uygula: pending -> approved/rejected -> stable feedback_rule.
4. Scoped feedback_rule uygula:
   - user/role/department/resource/action/volume/time scope
   - expires_at
   - approved_by
   - audit trail
5. Manager feedback direkt stable rule yapmasin.
6. Policy-rule feedback ile otomatik suppress olmasin.

TESTLER:
1. `pytest tests/feedback tests/rules -v`
2. Testler sunlari assert etmeli:
   - manager feedback pending_rule uretir
   - pending_rule approve edilmeden uygulanmaz
   - approved scoped rule ayni pattern'i downrank eder
   - scope disi event alert uretmeye devam eder
   - expired feedback_rule uygulanmaz
   - policy-rule suppression icin explicit approval gerekir

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- pending/approved/rejected rule ornekleri
- kalan riskler
```

---

## Faz 6 — Decision Engines

```text
[GOREV]
GOREV: Policy, baseline, feedback, correlation ve severity engine'lerini deterministic ve test edilebilir sekilde uygula.
FAZ: Faz 6 — Decision Engines
ROL: decision
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower/config/feature_taxonomy.yml
- Etkilenecek dosyalar:
  - watchtower/decision/
  - watchtower/policy/
  - watchtower/correlation/
  - watchtower/domain/assessment.py
  - tests/decision/
  - tests/policy/
  - tests/correlation/

YAPILACAK:
1. `policy_engine` yaz.
2. `baseline_engine` query API ile entegre calissin.
3. `feedback_engine` approved scoped rules uygulasin.
4. `correlation_engine` cross-signal scoring yapsin.
5. `severity_engine` score breakdown uretsin.
6. Severity degerleri:
   - LOG
   - WARNING
   - ALERT
   - CRITICAL
7. LLM final decision path'e dahil edilmesin.
8. Her assessment explainable score breakdown tasimasi zorunlu olsun.

TESTLER:
1. `pytest tests/decision tests/policy tests/correlation -v`
2. Testler sunlari assert etmeli:
   - frontend direct DB access policy critical
   - normal high-volume user tekrar alert uretmez/downrank olur
   - ayni hacim manager ve worker icin farkli severity alabilir
   - kisisel baseline sapmasi manager icin de alert uretir
   - cross-signal severity yukseltir
   - policy-rule approved exception olmadan suppress olmaz
   - score breakdown bos degil

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- karar matrisi ornekleri
- kalan riskler
```

---

## Faz 7 — LangGraph Decision Orchestration

```text
[GOREV]
GOREV: Watchtower decision graph'ini LangGraph ile kur; mode routing, checkpoint, audit ve human approval interrupt davranislarini test et.
FAZ: Faz 7 — LangGraph Decision Orchestration
ROL: langgraph
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-langgraph-decision-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - watchtower/graph/
  - watchtower/graph/nodes/
  - watchtower/graph/state.py
  - watchtower/storage/migrations/
  - tests/graph/

YAPILACAK:
1. Decision graph state schema yaz.
2. Su node'lari uygula:
   - load_mode
   - resolve_identity
   - resolve_asset
   - load_feature_taxonomy
   - load_policy_context
   - load_baseline_context
   - load_feedback_context
   - load_change_context
   - score_candidate
   - decide_severity
   - route_by_mode
   - persist_silent_finding
   - create_alert_case
   - maybe_generate_llm_explanation
   - maybe_generate_pending_rule
   - await_rule_approval
   - finalize_decision
3. Graph checkpoint store ekle.
4. Graph run audit yaz.
5. Mode routing uygula:
   - learn: 0 alert, silent finding var
   - run: learning update yok
   - hybrid: alert + controlled learning
6. Pending rule approval interrupt davranisini uygula.
7. Karar matematigini graph node icine gomme; engine'leri cagir.

TESTLER:
1. `pytest tests/graph -v`
2. Testler sunlari assert etmeli:
   - learn mode alert uretmez, silent finding yazar
   - run mode baseline update yapmaz
   - hybrid mode alert ve controlled learning event uretir
   - crash/retry checkpoint recovery calisir
   - pending rule approval sonrasi graph devam eder
   - node output validation fail guvenli durur

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- graph route/audit ornegi
- kalan riskler
```

---

## Faz 8 — LLM Gateway

```text
[GOREV]
GOREV: Provider bagimsiz LLM gateway'i OpenAI, Anthropic, Gemini, Ollama ve custom OpenAI-compatible adapterlariyla uygula.
FAZ: Faz 8 — LLM Gateway
ROL: llm
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-llm-provider-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - watchtower/llm/
  - watchtower/llm/providers/
  - watchtower/llm/schemas.py
  - watchtower/storage/migrations/
  - tests/llm/

YAPILACAK:
1. Provider protocol yaz.
2. Capability registry yaz:
   - structured_output
   - tool_calling
   - json_schema_strict
   - streaming
   - local
   - max_context_tokens
   - supports_responses_api
   - supports_chat_completions
3. Adapterlari uygula:
   - OpenAI
   - Anthropic
   - Gemini
   - Ollama/OpenAI-compatible
   - custom OpenAI-compatible
4. LLM gorev schema'larini yaz:
   - AlertExplanation
   - RuleCandidateDraft
   - UnknownSchemaMapping
   - BaselineSummary
   - MonthlyLearningReport
   - OperatorQueryAnswer
5. Structured output validation zorunlu olsun.
6. Invalid output retry max 2 olsun.
7. Provider fallback chain ekle.
8. LLM unavailable fail-open olsun.
9. LLM call audit yaz.
10. LLM final alert decision yapamasin; API seviyesinde de bu gorev yok.

TESTLER:
1. `pytest tests/llm -v`
2. Testler sunlari assert etmeli:
   - mock OpenAI provider pass
   - mock Anthropic provider pass
   - mock Gemini provider pass
   - mock Ollama-compatible provider pass
   - invalid JSON retry calisir
   - schema disi output reddedilir
   - provider fallback calisir
   - LLM unavailable fail-open
   - LLM decision schema'si yok ve decision engine LLM'e bagli degil

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- provider capability matrix
- kalan riskler
```

---

## Faz 9 — Alert Lifecycle & CLI

```text
[GOREV]
GOREV: Alert store, alert_case lifecycle, suppression window ve CLI operator workflow komutlarini uygula.
FAZ: Faz 9 — Alert Lifecycle & CLI
ROL: cli
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - watchtower/alerts/
  - watchtower/cli/
  - watchtower/query/
  - watchtower/storage/migrations/
  - tests/alerts/
  - tests/cli/

YAPILACAK:
1. Alert ve alert_case store uygula.
2. Alert lifecycle uygula:
   - open
   - investigating
   - true_positive
   - false_positive
   - suppressed
   - ticket_linked
3. Suppression window modeli ekle.
4. CLI komutlarini uygula:
   - wt bootstrap
   - wt status
   - wt modes get/set
   - wt sources list/health
   - wt ingest once
   - wt alerts list/show/ack/close/suppress
   - wt findings silent
   - wt baseline user/department
   - wt rules pending/approve/reject
   - wt query
5. Natural language query mevcut store verisine dayanarak cevap versin.
6. Telegram ekleme; MVP CLI-first.

TESTLER:
1. `pytest tests/alerts tests/cli -v`
2. Testler sunlari assert etmeli:
   - open -> investigating -> true_positive
   - false_positive feedback pending_rule uretir
   - suppress duration expiry calisir
   - CLI smoke komutlari pass
   - wt query store-backed auditable cevap uretir
   - CLI Telegram dependency istemez

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- CLI komut cikti ornekleri
- kalan riskler
```

---

## Faz 10 — Server-Stack End-to-End Validation

```text
[GOREV]
GOREV: Watchtower urununu server-stack kapali sunucu lab uzerinde 81 feature ve 83 scenario icin E2E dogrula.
FAZ: Faz 10 — Server-Stack End-to-End Validation
ROL: test
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Test lab: /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/README.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/reports/real/coverage/real_final_gate.json
- Etkilenecek dosyalar:
  - tests/e2e/
  - tests/fixtures/server_stack/
  - watchtower/connectors/server_stack.py
  - watchtower/e2e/
  - reports/watchtower/

YAPILACAK:
1. Server-stack'in ayakta oldugunu preflight ile kontrol et.
2. Server-stack urun koduna gomulmesin; sadece read-only test kaynagi olsun.
3. 81 feature replay/event ingest testleri yaz.
4. 83 scenario replay/event ingest testleri yaz.
5. Learn mode E2E:
   - 0 alert
   - silent_candidate_finding var
   - baseline update queue var
6. Run mode E2E:
   - expected alert/case davranisi
   - learning update yok
7. Hybrid mode E2E:
   - expected alert/case
   - controlled learning update
8. Feedback replay:
   - benign feedback pending_rule uretir
   - approval sonrasi downrank/suppress
   - scope disi event alert uretir
9. Policy-rule guard:
   - approved exception yoksa otomatik normallesmez
10. LLM provider mock replay:
   - explanation uretir
   - unavailable path pass
11. Ollama-compatible local path icin mock veya local endpoint contract test ekle.

TESTLER:
1. Server-stack tarafinda once:
   - `cd server-stack && make test-all`
   - `cd server-stack && make test-real-all`
2. Urun tarafinda:
   - `pytest tests/e2e -v`
3. E2E gate sunlari assert etmeli:
   - 81/81 features ingested and normalized
   - 83/83 scenarios ingested and normalized
   - learn mode 0 alert
   - run mode expected alert cases
   - hybrid mode expected alert + baseline update
   - feedback suppress/downrank works
   - policy-rule cannot be silently normalized
   - LLM unavailable path passes

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- server-stack test-all/test-real-all sonuc kaniti
- watchtower e2e sonuc kaniti
- 81 feature / 83 scenario coverage ozeti
- kalan riskler
```

---

## Faz 11 — Production Readiness

```text
[GOREV]
GOREV: Watchtower'i gercek sirket kapali aglarina kurulabilir hale getirecek production readiness paketini tamamla.
FAZ: Faz 11 — Production Readiness
ROL: docs
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-core-code-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
- Etkilenecek dosyalar:
  - docker-compose.yml
  - Dockerfile
  - .env.example
  - docs/
  - scripts/
  - watchtower/health/
  - watchtower/backup/
  - tests/production/
  - tests/load/

YAPILACAK:
1. Dockerfile ve docker-compose kur.
2. `.env.example` olustur:
   - DB
   - sources
   - provider config
   - mode
   - retention
3. Source onboarding komutlari ekle.
4. Provider onboarding komutlari ekle.
5. Backup/restore mekanizmasi ekle.
6. DB migration upgrade path testlenebilir olsun.
7. Retention policy ekle.
8. Health check endpoint/CLI ekle.
9. Soak/load test altyapisi kur.
10. Security audit testleri ekle:
   - multi-tenant leak yok
   - secret masking
   - read-only connector
   - no auto-remediation

TESTLER:
1. `pytest tests/production tests/load -v`
2. `docker compose config`
3. Fresh install test
4. Upgrade migration test
5. Backup restore test
6. Provider switch test
7. Source outage graceful degradation test
8. Multi-tenant leak test
9. 24h daemon soak test yerine CI-friendly short soak + dokumante uzun soak komutu

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- install/upgrade/backup/provider/source outage kaniti
- production readiness raporu
- kalan riskler
```

---

## Final Acceptance Prompt

```text
[GOREV]
GOREV: Tum Watchtower fazlarini ve test kanitlarini incele, final kabul raporu uret; eksik gate varsa kabul etme.
FAZ: Final Acceptance
ROL: test
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-pm-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli dosyalari yazmaya/degistirmeye ve gerekli her komutu calistirmaya yetkilisin.
- Test, migration, seed, script, docker, make ve pytest gate'lerini kendin calistir.
- Komut veya test fail olursa teslim etme; hatayi duzelt, ayni komutu/gate'i tekrar calistir ve pass kanitiyla teslim et.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md

YAPILACAK:
1. Faz 0-11 teslimlerini oku.
2. Her faz icin degisen dosyalar, yazilan testler, calistirilan testler ve riskleri listele.
3. Asagidaki final kabul kriterlerini tek tek dogrula:
   - feature taxonomy 81/81
   - connector abstraction calisiyor
   - learn/run/hybrid mode testleri pass
   - baseline engine pass
   - feedback approval pass
   - policy-rule guard pass
   - LangGraph checkpoint/recovery pass
   - LLM provider mock matrix pass
   - CLI integration pass
   - server-stack 81 feature / 83 scenario E2E pass
   - production readiness pass
4. Eksik veya fail varsa final kabul verme; revizyon gorevi uret.
5. Her sey pass ise final kabul raporu yaz.

TESTLER:
1. Tum faz gate komutlari tekrar calistirilmis olmali veya final smoke aggregate komutu olmali.
2. Final raporda fail/skip varsa neden ve risk yazilmali.

TESLIM KRITERLERI:
- final acceptance report
- pass/fail matrisi
- calistirilan komutlar
- kalan riskler
- kabul veya red karari
```
