# Watchtower Hardening Prompts — Faz 12-16

Bu dosya Watchtower'i production-candidate seviyesinden daha olgun, runtime davranisi kanitlanmis product seviyesine tasimak icin kullanilacak AI gorev promptlarini icerir.

## Kesin Ek Kural — Mock-Free Realistic Validation

Bu fazlarda "mock data ile A yazinca B donuyor mu" seklinde test kabul edilmez.

Zorunlu dogrulama yaklasimi:

- Testler gercek Watchtower runtime akisini kullanmali: source poll -> raw event -> normalization -> candidate -> graph -> alert/finding/case.
- Veri kaynagi olarak oncelik server-stack replay/real evidence, JSONL log dosyalari, temp SQLite state ve CLI/daemon komutlari olmalidir.
- LLM testi icin statik mock provider cevabi kullanilmaz; `.env` icinde Gemini test provider bilgisi varsa live Gemini contract calistirilir.
- LLM yoksa sadece fail-open davranisi test edilir; "mock LLM su JSON'u dondu" testi bu fazlari kapatmaya yetmez.
- Worker/kullanici davranisi testleri gercek event dizisi, baseline observation, profile snapshot ve alert explanation uzerinden dogrulanir.
- LLM final alert karari vermez; LLM sadece mevcut deterministic karar/baseline/alert baglamini yorumlar.
- Server-stack urun kodu olarak degistirilmez; server-stack yalnizca test/lab/evidence kaynagi olarak kullanilir.
- Test fail olursa teslim edilmez; hata duzeltilir ve ayni gate tekrar calistirilir.

---

## Genel Hardening PM Prompt

```text
[GOREV]
GOREV: Watchtower hardening Faz 12-16 islerini sirayla yonet; mock-free realistic validation kaniti olmadan faz kapatma.
FAZ: Faz 12-16 Hardening
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

YAPILACAK:
1. Faz 12'den Faz 16'ya sirayla ilerle.
2. Her faz icin tek sahipli alt gorevler uret.
3. Mock-free validation kuralini her alt goreve gate olarak ekle.
4. Static mock provider, hardcoded expected response veya sadece unit-level fake data ile faz kapatma.
5. Worker/kullanici davranisi kanitini gercek event dizisi + DB state + CLI/daemon output + LLM explanation uzerinden iste.
6. Her faz sonunda degisen dosyalar, yazilan testler, calistirilan komutlar ve kalan riskleri raporla.

TESTLER:
1. Her faz kendi gate komutlarini calistirmali.
2. Faz 12 daemon loop tek komutla ingest-normalize-candidate-graph-alert/finding kaniti uretmeli.
3. Faz 13 restart sonrasi pending interrupt/checkpoint resume kaniti uretmeli.
4. Faz 14 live/realistic connector contract ve outage/backoff kaniti uretmeli.
5. Faz 15 operator case workflow'u gercek alert/case uzerinde kanitlamali.
6. Faz 16 metrics/log/soak kaniti uretmeli; mock-only test kabul edilmez.

TESLIM KRITERLERI:
- Faz faz sonuc raporu
- Mock-free validation kaniti
- Calistirilan komutlar
- Fail varsa revizyon kaydi
- Kalan riskler
```

---

## Faz 12 — Daemon Pipeline Runtime

```text
[GOREV]
GOREV: Watchtower ingest-normalize-candidate-graph-alert akisini tek daemon runtime loop olarak uygula ve server-stack kanitiyla dogrula.
FAZ: Faz 12 — Daemon Pipeline Runtime
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
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/reports/real/coverage/real_final_gate.json
- Etkilenecek dosyalar:
  - watchtower/daemon/
  - watchtower/cli/main.py
  - watchtower/cli/commands_production.py
  - watchtower/services/app.py
  - watchtower/storage/migrations/versions/
  - tests/daemon/
  - tests/e2e/
  - docs/operations.md

MOCK-FREE KURAL:
- Static mock connector veya hardcoded event listesiyle faz kapatma.
- Test verisi server-stack replay/real evidence veya gercek JSONL log dosyasindan okunmali.
- Assertion "A input -> B output" degil, DB'de raw_events, normalized_events, candidate_events, graph_runs, alerts/silent_findings zinciri uzerinden yapilmali.

YAPILACAK:
1. `wt daemon run` komutunu ekle.
2. Daemon loop su adimlari tek runtime akista calistirsin:
   - enabled source poll
   - raw event store
   - normalization
   - candidate extraction
   - graph run
   - alert/silent finding/learning event persist
3. Source bazli interval, limit, cursor ve backoff uygula.
4. Graceful shutdown ve max-iterations test modu ekle.
5. Source failure diger source'lari durdurmasin.
6. Learn/run/hybrid mode davranisini daemon icinde dogrula.
7. Daemon audit ve per-loop summary uret.

TESTLER:
1. `pytest tests/daemon tests/e2e/test_daemon_pipeline*.py -v`
2. `pytest tests/ -q`
3. Testler sunlari assert etmeli:
   - server-stack kaynakli gercek replay/log event daemon ile raw -> normalized -> candidate olur
   - learn mode daemon 0 alert + silent finding + learning event uretir
   - run mode daemon alert/case uretir ve baseline learning update yapmaz
   - hybrid mode daemon alert + controlled learning uretir
   - cursor tekrar calistirmada duplicate raw/candidate uretmez
   - bir source fail olunca baska source islenmeye devam eder
   - CLI `wt daemon run --once` veya `--max-iterations 1` pass olur

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- daemon pipeline DB evidence ozeti
- learn/run/hybrid runtime kaniti
- kalan riskler
```

---

## Faz 13 — Durable Graph Checkpoint & Approval Resume

```text
[GOREV]
GOREV: LangGraph checkpoint'i process-ici MemorySaver'dan kalici SQLite checkpoint'e tasiyip restart sonrasi human approval resume davranisini kanitla.
FAZ: Faz 13 — Durable Graph Checkpoint & Approval Resume
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
  - watchtower/graph/runner.py
  - watchtower/graph/deps.py
  - watchtower/config/settings.py
  - watchtower/storage/migrations/versions/
  - watchtower/cli/
  - tests/graph/
  - tests/e2e/
  - docs/operations.md

MOCK-FREE KURAL:
- Restart/resume testi sadece in-memory object reuse ile gecemez.
- Test iki ayri app/session/runner instance'i acmali ve checkpoint'i diskten geri yuklemeli.
- Pending approval senaryosu gercek pending_rule/approval state'i ile calismali.

YAPILACAK:
1. Kalici graph checkpoint ayari ekle:
   - enabled/disabled
   - checkpoint DB path
   - retention
2. MemorySaver'i sadece test/dev fallback yap; production default durable olsun.
3. Graph interrupt state'ini checkpoint DB'de sakla.
4. Restart sonrasi `Command(resume=...)` ile graph devam etsin.
5. Pending rule approval resume CLI veya service API ile calissin.
6. Checkpoint cleanup/retention ekle.
7. Graph audit ile checkpoint id/thread id iliskisini raporla.

TESTLER:
1. `pytest tests/graph tests/e2e/test_graph_durable_checkpoint*.py -v`
2. `pytest tests/ -q`
3. Testler sunlari assert etmeli:
   - app process/runner yeniden yaratildiktan sonra checkpoint bulunur
   - approval interrupt kaldigi yerden devam eder
   - approved pending_rule stable rule'a donusur
   - graph run completed olur ve audit zinciri korunur
   - checkpoint retention eski completed state'i temizler
   - MemorySaver production default degildir

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- restart/resume DB evidence
- checkpoint retention kaniti
- kalan riskler
```

---

## Faz 14 — Production Connector Hardening

```text
[GOREV]
GOREV: Elasticsearch, Wazuh, file JSONL ve server-stack connectorlarini production-grade auth/TLS/pagination/backoff/contract davranislariyla sertlestir.
FAZ: Faz 14 — Production Connector Hardening
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
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/reports/real/coverage/real_final_gate.json
- Etkilenecek dosyalar:
  - watchtower/connectors/
  - watchtower/sources/
  - watchtower/config/settings.py
  - watchtower/cli/commands_production.py
  - tests/connectors/
  - tests/integration/
  - tests/e2e/
  - docs/install.md
  - docs/operations.md

MOCK-FREE KURAL:
- Connector contract sadece fake HTTP response ile kapanmaz.
- Server-stack real evidence, real Elasticsearch endpoint varsa live health/query, yoksa local recorded server-stack log/evidence path'i kullanilmali.
- File connector testleri temp JSONL dosyasina gercek event satirlari yazip cursor/pagination kanitlamali.
- Outage testi gercek kapali port/timeout/backoff davranisi ile yapilmali.

YAPILACAK:
1. Elasticsearch connector:
   - auth header/API key/basic auth
   - TLS verify/CA config
   - search_after veya cursor pagination
   - timeout/retry/backoff
2. Wazuh connector:
   - token auth skeleton'u production config ile tamamla
   - pagination ve time-window cursor
   - health detaylari
3. File JSONL connector:
   - rotation/truncation handling
   - partial line safety
   - large file cursor resume
4. Source onboarding validation ekle.
5. Connector metrics/audit summary uret.
6. Secret masking testlerini connector config icin genislet.

TESTLER:
1. `pytest tests/connectors tests/integration/test_ingest*.py -v`
2. `pytest tests/e2e/test_connector_hardening*.py -v`
3. `pytest tests/production/test_source_outage.py tests/production/test_security_audit.py -v`
4. Testler sunlari assert etmeli:
   - file JSONL rotation ve cursor resume duplicate uretmez
   - Elasticsearch live/realistic health/query path pass veya unavailable ise degraded + fail-open
   - Wazuh unavailable timeout tum daemon'u dusurmez
   - source onboarding invalid config'i reddeder
   - connector secret config audit'te maskelenir
   - server-stack real evidence connector tarafindan read-only okunur

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- connector health/query kaniti
- outage/backoff kaniti
- kalan riskler
```

---

## Faz 15 — Case Management & Operator UX

```text
[GOREV]
GOREV: Gercek alert/case uzerinden operator workflow'unu case timeline, assignment, comments, ticket link ve explainability ciktilariyla olgunlastir.
FAZ: Faz 15 — Case Management & Operator UX
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
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-scenarios-final.md
- Etkilenecek dosyalar:
  - watchtower/domain/alerts.py
  - watchtower/alerts/
  - watchtower/cli/
  - watchtower/query/
  - watchtower/storage/migrations/versions/
  - tests/alerts/
  - tests/cli/
  - tests/e2e/
  - docs/operations.md

MOCK-FREE KURAL:
- Case workflow testi manuel yaratilan bos alert ile kapanmaz.
- En az bir test daemon veya graph E2E akisiyle uretilen gercek alert/case uzerinden calismali.
- LLM explanation testi statik mock cevapla degil, mevcut alert context + baseline/decision breakdown ile yapilmali; Gemini key varsa live Gemini kullanilmali.

YAPILACAK:
1. `case_timeline` modeli ekle:
   - created
   - acknowledged
   - assigned
   - comment_added
   - ticket_linked
   - feedback_submitted
   - closed
2. `wt cases` komutlarini ekle:
   - list/show/assign/comment/link-ticket/timeline/export
3. Alert show output'una explainable score breakdown ekle.
4. LLM explanation mevcut alert/case context'i ile uretilebilsin.
5. Operator query case/alert/timeline kaynaklarini cite etsin.
6. false_positive -> feedback -> pending_rule baglantisini case timeline'a yaz.
7. Export icin JSON ve markdown rapor ekle.

TESTLER:
1. `pytest tests/alerts tests/cli tests/e2e/test_case_workflow*.py -v`
2. `pytest tests/ -q`
3. Testler sunlari assert etmeli:
   - daemon/graph ile uretilen gercek alert case'e donusur
   - ack/assign/comment/ticket/close timeline'a yazilir
   - false_positive feedback pending_rule uretir ve timeline'a baglanir
   - alert/case show score breakdown ve source evidence gosterir
   - LLM explanation deterministic decision'i degistirmez
   - Gemini configured ise live explanation schema validation pass olur
   - query cevabi auditable ve store-backed olur

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- gercek alert/case timeline ornegi
- LLM explanation/citation ornegi
- kalan riskler
```

---

## Faz 16 — Observability, Metrics & Realistic Soak

```text
[GOREV]
GOREV: Watchtower runtime icin structured logs, metrics, health degradation ve realistic soak gate'lerini ekle.
FAZ: Faz 16 — Observability, Metrics & Realistic Soak
ROL: test
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
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md
- Etkilenecek dosyalar:
  - watchtower/observability/
  - watchtower/health/
  - watchtower/daemon/
  - watchtower/cli/commands_production.py
  - scripts/soak_short.sh
  - scripts/soak_24h.sh
  - tests/load/
  - tests/production/
  - docs/operations.md
  - docs/production-readiness-report.md

MOCK-FREE KURAL:
- Soak testi sadece sleep veya fake loop sayaciyla kapanmaz.
- Soak, gercek source poll + raw/normalized/candidate/graph/case path'inden event gecirmeli.
- Metrics testleri runtime tarafindan uretilen gercek counters/histograms/log records uzerinden assert etmeli.

YAPILACAK:
1. Structured JSON logging ekle:
   - source_id
   - tenant_id
   - run_id
   - graph_thread_id
   - event counts
   - severity
   - error class
2. Metrics store/endpoint/CLI ekle:
   - events_polled_total
   - raw_events_stored_total
   - normalized_events_total
   - candidates_total
   - graph_runs_total
   - alerts_total
   - source_errors_total
   - llm_calls_total
   - loop_duration_ms
3. `wt metrics` komutu ekle.
4. Health report degraded/unhealthy sebeplerini metrics ile baglasin.
5. Short soak script gercek daemon loop + server-stack replay/log kaynagi kullansin.
6. 24h soak dokumani ve resumable output raporu uretsin.
7. Production readiness raporuna metrics/soak kaniti ekle.

TESTLER:
1. `pytest tests/production tests/load -v`
2. `./scripts/soak_short.sh`
3. `pytest tests/ -q`
4. Testler sunlari assert etmeli:
   - short soak gercek event isler ve metrics artar
   - source outage health degraded yapar ama daemon devam eder
   - structured logs secret maskeler
   - `wt metrics` counters gosterir
   - loop duration ve error counters kaydedilir
   - production readiness JSON metrics/soak sonucunu icerir

TESLIM KRITERLERI:
- degisen dosyalar
- yazilan testler
- calistirilan testler
- metrics snapshot
- short soak raporu
- kalan riskler
```

---

## Final Hardening Acceptance Prompt

```text
[GOREV]
GOREV: Faz 12-16 hardening teslimlerini mock-free validation kuralina gore incele; eksik gerçek runtime kaniti varsa kabul etme.
FAZ: Final Hardening Acceptance
ROL: test
SKILL:
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-pm-mode/SKILL.md
- /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/skills/watchtower-test-mode/SKILL.md

YETKI VE CALISTIRMA:
- Bu gorev kapsaminda gerekli her komutu calistirmaya yetkilisin.
- Test fail olursa kabul verme; revizyon gorevi uret.
- Server-stack urun kodu olarak degistirilmez; server-stack komutlari ve testleri E2E dogrulama icin calistirilabilir.

BAGLAM:
- Proje: Watchtower product
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md

YAPILACAK:
1. Faz 12-16 teslimlerini oku.
2. Her faz icin degisen dosyalar, yazilan testler, calistirilan komutlar ve riskleri listele.
3. Mock-free validation kuralini denetle:
   - static mock provider ile kapanan test var mi?
   - hardcoded A->B response testi faz kaniti olarak sunulmus mu?
   - gercek daemon/runtime DB state kaniti var mi?
   - worker/kullanici davranisi event->baseline->LLM explanation akisi ile kanitlanmis mi?
4. Eksik varsa kabul verme ve revizyon promptu uret.
5. Her sey pass ise final hardening acceptance raporu yaz.

TESTLER:
1. `pytest tests/ -q`
2. `pytest tests/daemon tests/e2e tests/graph tests/production tests/load -q`
3. `cd server-stack && make test-all`
4. `cd server-stack && make test-real-all`
5. `./scripts/soak_short.sh`
6. Gemini `.env` configured ise live Gemini explanation contract calistirilmis olmali.

TESLIM KRITERLERI:
- final hardening acceptance report
- pass/fail matrisi
- mock-free validation karari
- calistirilan komutlar
- kalan riskler
- kabul veya red karari
```
