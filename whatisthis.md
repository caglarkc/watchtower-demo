Şu an sistemin yaptığı şey:

Watchtower, kapalı şirket ağı loglarını ve replay/event kaynaklarını okuyup kullanıcı davranışlarını normalize eden, baseline ile karşılaştıran, deterministic karar motorlarıyla alert/case üreten bir UEBA CLI ürününe dönüşmüş durumda.

Akış kabaca şöyle:

```text
connector → raw event → normalization → candidate event
→ baseline / policy / feedback / correlation / severity
→ LangGraph mode routing
→ silent finding veya alert/case
→ CLI ile inceleme, kapatma, suppress, feedback, pending rule approval
```

Modlara göre davranışı:

- `learn`: alert üretmez; silent finding ve baseline learning kaydı üretir.
- `run`: alert/case üretir; baseline öğrenmesini güncellemez.
- `hybrid`: alert üretir ve kontrollü learning update yapar.

LLM tarafı:

- LLM karar vermiyor.
- LLM sadece açıklama, pending rule taslağı, schema mapping, summary/query cevabı gibi destek işleri yapıyor.
- Gemini API çalışıyor; ama LLM olmazsa sistem fail-open devam ediyor.

Feedback tarafı:

- Manager/operator feedback direkt sistemi değiştirmiyor.
- Önce `pending_rule` oluşuyor.
- Security operator veya system admin approve ederse stable feedback rule oluyor.
- `policy-rule` davranışlar otomatik normalleşmiyor.

CLI tarafında:

- bootstrap/admin
- mode get/set
- source health/list
- ingest once
- alert list/show/ack/close/suppress
- silent findings
- baseline görüntüleme
- pending rule approve/reject
- query
- health, migrate, backup, retention, provider/source onboarding

çalışıyor.

Test edilen kapsam:

- 81 feature taxonomy
- 83 server-stack scenario
- connector/ingest
- normalization
- baseline
- feedback approval
- deterministic decision
- LangGraph routing
- LLM gateway
- alert lifecycle
- Docker/backup/health/production readiness

Kısaca: Sistem şu an “kapalı ağ davranış izleme ürünü” olarak kurulabilir MVP/production-candidate seviyesinde; gerçek şirket ortamına geçmeden önce uzun soak, kalıcı graph checkpoint ve tek daemon loop E2E tarafı güçlendirilmeli.