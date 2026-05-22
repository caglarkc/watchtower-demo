# Sentinel — Yeni Ürün Fikri: LLM Destekli İç Ağ İzleme Sistemi
## Tam Konuşma Kaydı

---

> **Bağlam:** Bu konuşma, mevcut `sentinel-coming` monoreposu sahibiyle yeni bir ürün fikri üzerine yapılan araştırma ve mimari planlama oturumudur.

---

**User:**
> Böyle bir productim var. Ve md'sini attım sana extra olarak. Tamam şimdi bu proje ile ilgili bir şey yapmayacağız. Sadece farklı bir fikrim var ve bu projeye mi entegre etmeliyim iki farklı product olup beraber mi sunmalıyım onu düşünüyorum. Fikir şu, bir şirketin tüm kapalı sunucularında dolanan mailleri, kimin ne kadar veri çektiğini ve günlük değişimlerini izleyen bir llm destekli cli. Örneğin bir worker normalde her gün ortalama 1-2 gb arası veri çekerken anormal şekilde 100 gb veri çekti, bu bir veri kaçırma sebebi olabileceği için manager uyarılmalı ve önlem alınmalı. Aslında üst bir manager, her akışı izleyen ve şirketin yöneticisine veya yetkilisine olağan dışı durumlarda haber veren bir llm destekli cli düşünüyorum. Sence nasıl olabilir?

**Claude:**
> Bu çok güçlü bir fikir. Sentinel'in gözlemlenebilirlik DNA'sına çok iyi oturuyor aslında — sadece altyapı metriklerini değil, insan davranışı metriklerini de izliyorsun bu sefer.
>
> **Güçlü yönler:**
> - Gerçek bir pain point: DLP araçları ya çok pahalı (Symantec, Forcepoint) ya da çok karmaşık
> - LLM burada gerçekten değer yaratıyor — kural tabanlı sistemler "100 GB çekti, alert" yapar ama bağlamı anlayamaz. LLM "bu kişi zaten veri yedekleme ekibinde, ama saat 03:00'da çekmiş" gibi yorumlayabilir
> - CLI formatı IT/SecOps ekipleri için doğal
>
> **Riskler / Zorluklar:**
> - KVKK/GDPR: çalışanların davranışını izlemek yasal düzenlemelere takılabilir
> - False positive yönetimi kritik
> - Şirket içi veri erişimi entegrasyonu karmaşık
>
> **Sentinel'e Entegre mi, Ayrı Ürün mü?**
> Bence ayrı ürün, ama aynı monorepo. Sentinel altyapı odaklı, bu yeni fikir insan/davranış odaklı. Hedef kitle bile farklı: Sentinel → DevOps/SRE, yeni ürün → IT Security/CISO. Ama CLI mimarisi, LLM entegrasyonu, MCP desteği, hook pipeline gibi tüm core bileşenler ortak kullanılabilir.

---

**User:**
> Q: İzleme kapsamı ne olsun? → Tüm kullanıcı aktivitesi (login, dosya erişimi, mail, veri)
> Q: Hedef müşteri kitlesi kim? → Her ikisi de (KOBİ + Enterprise)

**Claude:**
> Güzel seçimler. Bu iki cevap birleşince ürün ciddi anlamda genişliyor.
>
> **Ürün Kimliği:** "Employee Activity Intelligence" olarak konumlandır. İsim önerisi: **Watchtower** veya **Vigil** — Sentinel ile aynı semantik aileden.
>
> **Mimari ihtiyaçlar:**
> - Veri katmanı: Exchange/Google Workspace API, NetFlow/sFlow, Windows Event Log, Active Directory/LDAP
> - Baseline engine: LLM'i her event'e çalıştırma, önce istatistiksel baseline, LLM sadece yüksek anomali skoru olanlara baksın
> - Alert pipeline: Sentinel'in hook pipeline'ına benzer
>
> **Sentinel ile ilişki:** `observability-gateway` pattern'ini buraya da uygula. Tüm veri kaynaklarına read-only adapter'lar yaz, normalize et — Sentinel CLI bu veriyi okuyabilsin. Bu durumda ayrı ürün değil, Sentinel'in bir security modülü olur.

---

**User:**
> Peki şirketler zaten bir çalışanının bilgisayarını izliyor ve neler yaptığını kontrol ediyorlar. Bazıları bunu tamamen kapalı kutu şeklinde sadece kendi sunucularında çalıştırıyorlar, bazıları ise tüm dünyaya açık fakat araya bir firewall koyup hem izleme hem de güvenlik önlemi alıyorlar, bazılarında ise hiçbiri yok. Yani aslında üç farklı hedef var. Hem kapalı sunucuda tam erişimde hem de yarı yarıya firewall ile açık kaynakta kontrol nasıl bir sistem kuruluyor ve kullanılıyor. Önce kullanılan yapıları anlamaya çalışmak lazım. THY tamamen kendi sunucusunu kapalı şekilde kullandırıyor çalışanlarına, bunu da araştırabilirsin. Yapıyı, mimariyi anlamak istiyorum.

**Claude:**
> *(Araştırma sonuçları)*
>
> **Tip 1 — Tam Kapalı (Air-Gapped):** THY, savunma şirketleri, bankalar. Fiziksel air-gap'te sistemler harici ağlarla hiçbir bağlantısı yok. THY, IPS, firewall, proxy, WAF, SIEM, tehdit istihbaratı gibi neredeyse her güvenlik teknolojisini kullanan 2.000+ IT çalışanına sahip yapı. Bu şirketler SIEM kuruyor — Splunk, IBM QRadar veya Elastic Stack on-premise çalıştırılıyor.
>
> **Tip 2 — Hibrit (Firewall + DMZ):** KOBİ'lerin büyük çoğunluğu. İnternete açık ama firewall, VPN ve DMZ var. Endpoint agent'lar, Active Directory logları, firewall logları bir merkezi SIEM'e akıyor.
>
> **Tip 3 — Açık / Hiç Yoksa:** Küçük şirketler, startup'lar. Microsoft 365 veya Google Workspace, aktif izleme yok.
>
> **Asıl önemli kavram: UEBA** (User and Entity Behavior Analytics) — senin fikrin tam bu kategoriye giriyor. Tüm bağlı veri kaynaklarından kullanıcı verisi toplayarak baseline davranış profili oluşturur, sapmalar gerçek zamanlı alert üretir.
>
> **Pazar boşluğu:** Splunk, Microsoft Sentinel, IBM QRadar çok pahalı, çok karmaşık, CLI değil dashboard odaklı, LLM yorumu yok. Senin potansiyel boşluğun: **KOBİ'ler için, LLM destekli, CLI tabanlı, on-premise çalışabilen hafif bir UEBA.**

---

**User:**
> Yani şunu daha net anlamam lazım, bir kapalı sunucuda tamamen usb fiziksel bağlantı aracılı mı oluyor? Ben şöyle düşünmüştüm hani bir sunucu olur wifi modemleri gibi fakat dışarı ağa değil iç ağ oluşturup orada bir sistem düşünmüştüm ama yanlış mı düşünmüşüm acaba?

**Claude:**
> Hayır, yanlış düşünmemişsin. Tam tersine çok doğru düşünüyorsun.
>
> **İki farklı "kapalı" var:**
>
> *Gerçek Air-Gap (Ekstrem):* Sadece savunma, nükleer, istihbarat gibi ultra-kritik sistemlerde. Fiziksel olarak hiçbir ağ bağlantısı yok, USB ile veri taşınıyor. Bu senin hedef kitlen değil.
>
> *İç Ağ (Private LAN/Intranet) — Senin Düşündüğün Bu:* THY, büyük bankalar, hastaneler, fabrikalar hepsi böyle çalışıyor:
> ```
> İnternet → Firewall/Router → İç Ağ (Private Network)
>                               ├── Çalışan bilgisayarları
>                               ├── Mail sunucusu (Exchange)
>                               ├── Dosya sunucusu
>                               ├── Active Directory
>                               └── Senin aracın buraya kurulur
> ```
> Çalışanlar birbirleriyle konuşuyor, mail gönderiyor, dosya paylaşıyor — ama tüm bu trafik dışarı çıkmıyor, iç ağda dönüyor.
>
> **Senin ürünün bu yapıda ne yapar:** Şirketin iç ağındaki bir sunucuya kurulur. Active Directory'den login, mail sunucusundan trafik, switch/router'dan GB verisi çeker, analiz eder. Hiçbir şey dışarı çıkmaz.

---

**User:**
> Peki hedef olarak halihazırda olan bu kapalı sunucuları izleme araçlarına bir cli entegrasyonunu, yani ilk 3 kategoriden tamamen kapalı sunucu olan birinciye yönelik, hazır sistemlerine entegre bir şey düşünsek. Bunun için hangi araçları kullandığını ve nasıl bağlanacağımı öğrenmem lazım, bunu araştır.

**Claude:**
> *(Araştırma sonuçları)*
>
> **Araç Ekosistemi:**
>
> *Enterprise (THY, büyük bankalar):* Splunk ve IBM QRadar dominant.
>
> *KOBİ ve orta ölçekli:* Elastic/ELK Stack ve **Wazuh** (tamamen ücretsiz, open source) çok yaygın.
>
> **Her aracın API bağlantı yapısı:**
>
> *Splunk:* REST API, Basic Auth/API Token/OAuth. `curl -k -u admin:pass https://localhost:8089/services/...`
>
> *IBM QRadar:* HTTPS istekleri belirli URL endpoint'lerine, IBM GitHub'ında API CLI client mevcut.
>
> *Wazuh (en ilginç):* Açık kaynaklı RESTful API — curl veya herhangi bir script ile kullanılabilir. JWT token ile: `curl -k -X METHOD "https://<HOST_IP>:55000/<ENDPOINT>" -H "Authorization: Bearer <JWT_TOKEN>"`. Wazuh'un REST API'si LLM entegrasyonu için doğrudan uygun, MCP üzerinden AI asistanlarına bağlanmak için hazır yapı mevcut.
>
> *Elastic Stack:* Self-managed deployment, air-gapped ortamlar dahil esnek deployment. Kibana REST API + Elasticsearch query API.
>
> **Kritik çıkarım:** Bu 4 aracın hepsinde REST API var, iç ağdan HTTP/HTTPS ile bağlanılıyor, JWT veya API key ile auth. Yani CLI'ın mevcut SIEM'in üstüne oturan bir **LLM yorumlama + doğal dil sorgulama katmanı** olacak.

---

**User:**
> Bu araçlar veri olarak ne topluyor ve nasıl döndürüyor? Sonuçlar önceden tanımlanmış bir model olarak mı yoksa uçsuz bucaksız veri tipleri ile mi?

**Claude:**
> Kısa cevap: ikisi arasında bir yerde. Ne tamamen tanımlı bir model, ne de uçsuz bucaksız kaos. Her araç bunu farklı çözüyor.
>
> **Ham gerçek — veri kaynakları karmaşıktır:**
> ```
> Windows PC'ler    → Event Log (XML tabanlı)
> Linux sunucular   → Syslog (düz metin)
> Firewall/switch   → Syslog (vendor'a göre format değişir)
> Web uygulamaları  → JSON loglar
> Mail sunucusu     → Kendi özel formatı
> ```
>
> **Normalizasyon katmanı:** Wazuh 3 aşamada işliyor — pre-decoding (temel alanlar), decoding (structured field parsing), rule matching (alert üretimi). Tümü JSON formatında `alerts.json`'a yazılıyor.
>
> Splunk CIM farklı kaynaklardaki aynı verinin farklı isimlendirilmesi sorununu çözüyor. Elastic'te bu ECS (Elastic Common Schema).
>
> **API'den gelen alert JSON örneği (Wazuh):**
> ```json
> {
>   "timestamp": "2026-05-21T10:23:11.000Z",
>   "rule": { "id": "5710", "level": 10, "description": "..." },
>   "agent": { "id": "003", "name": "workstation-ali", "ip": "192.168.1.45" },
>   "data": { "srcip": "192.168.1.200", "dstuser": "admin_fake" },
>   "full_log": "sshd: Failed password for invalid user..."
> }
> ```
> **Tanımlı:** `timestamp`, `rule.id`, `rule.level`, `agent` — her alert'te standart.
> **Tanımsız:** `data.*` alanları — kaynağa göre tamamen değişiyor.
>
> **Çıkarım:** CLI'ın iki katmana ihtiyacı var — adaptör katmanı (SIEM'e özel) + LLM katmanı (data.* alanlarını bağlama göre yorumla). Wazuh'ta önceden tanımlanmamış uygulama/cihaz logları için custom decoder yazılması gerekiyor; LLM tam burada değer katıyor.

---

**User:**
> Yani aslında el ele kapısından daha çok başta bir LangGraph yapısı gerekiyor ki gelen verinin ne olduğunu anlasın, ona göre analiz yapsın.

**Claude:**
> Tam isabetli düşündün. Ama bir adım geri çekilelim — LangGraph burada doğru araç mı?
>
> Senin problemi: bilinmeyen format veri gelir → ne olduğu anlaşılır → bağlama göre analiz → anomali varsa alert.
>
> Bu bir agentic loop — LangGraph bunu çözebilir ama Sentinel'in kendi agent mimarisinden özünde çok farklı değil. Asıl karar: bu pipeline Sentinel CLI'ın bir parçası mı çalışacak, yoksa Sentinel'den bağımsız sürekli çalışan bir servis mi?

---

**User:**
> Q: Veri anlama katmanı için hangi yaklaşımı düşünüyorsun? → LangGraph ile ayrı bir pipeline

**Claude:**
> Tamam, mimariyi netleştirelim.
>
> **Problemin gerçek yapısı — 5 adım:**
> 1. SIEM'den ham veri çek (format belirsiz)
> 2. Veriyi tanı / sınıflandır ("bu bir login eventi")
> 3. Bağlam ekle ("bu user normalde böyle mi davranır")
> 4. Anomali skoru üret ("bu şüpheli mi?")
> 5. Alert kararı ver ("yöneticiyi uyar mı?")
>
> **LangGraph ne yapar, ne yapmaz:**
> - Yapar: conditional, stateful, multi-step akışı yönetir
> - Sorun: ek dependency, ek kompleksite
> - Asıl değeri: "veriyi anlamadım, farklı bir decoder dene" gibi döngüsel mantık varsa
>
> **İki seçenek:**
>
> *Seçenek A — LangGraph servisi (bağımsız):*
> ```
> Wazuh/Splunk API → LangGraph Pipeline (ayrı Python servisi)
> ├── Node 1: Veri çek + format tanı
> ├── Node 2: User baseline'ı getir
> ├── Node 3: Anomali skoru hesapla
> └── Node 4: Alert kararı → webhook/mail
>     ↑
>  Sentinel CLI buraya bağlanır (okuma/sorgulama için)
> ```
>
> *Seçenek B — Sentinel agent loop içinde:*
> ```
> Sentinel CLI → siem_query() tool → LLM hem tanır hem analiz eder
> ```

---

**User:**
> Anthropic'ten tamamen bağımsız olacak product. LangGraph kısmında da şöyle bir durum olucak, bir noktada veri karmaşası ve karışıklık olucak. Bunun için fallback mekanizması ile farklı bir llm yapısı ile halihazırda entegre olmamış, gerekli kuralları tanımlanmamış yapıları AI aracılığı ile entegre etmek gerekiyor.

**Claude:**
> Şimdi çok net bir tablo ortaya çıktı.
>
> **Gerçek mimari ihtiyacı:**
> ```
> Bilinmeyen SIEM/format gelir → "Bu ne?" → tanımlı mı?
>     ↓ EVET                        ↓ HAYIR
> Bilinen adapter kullan        Fallback LLM
>                               "Bu veriyi anla, kural yaz, entegre et"
> ```
>
> **Tam Pipeline Şeması:**
> ```
> START
>   ↓
> [Ingest Node] → Ham veri çek
>   ↓
> [Schema Detection Node] ← LLM #1 (hızlı/ucuz, Gemini Flash veya Haiku)
> "Bu Wazuh mu, Splunk mu, yoksa bilinmeyen bir şey mi?"
>   ├─ KNOWN → [Known Adapter Node] → normalize et
>   └─ UNKNOWN → [Fallback Node] ← LLM #2 (güçlü, Opus seviyesi)
>                "Bu veriyi analiz et, field mapping yaz, kural üret"
>                   ↓
>            [Validation Node] → normalize edilmiş event
>                   ↓
>            [Baseline Node] → bu user için normal davranış nedir?
>                   ↓
>            [Anomaly Score Node]
>                   ↓
>            LOW → LOG    HIGH → [Alert Node]
> ```
>
> **İki farklı LLM rolü:**
> - LLM #1: Schema Detector — hızlı, ucuz, classification odaklı
> - LLM #2: Fallback Integrator — güçlü, reasoning odaklı, nadir çalışır
>
> **LangGraph'ın buradaki değeri:** conditional routing, state persistence (üretilen kural saklanır, tekrar kullanılır), retry/validation loop.

---

**User:**
> Otonom denenebilir, amacımız otonom öneri. Sonuç olarak herhangi bir eylem alınmayacağı için sadece daha sonradan kuralları değiştirme kısmı ekleriz, sorun olma durumunda silme işlemi yapılır.

**Claude:**
> Mükemmel karar. "Öner ama dokunma, gerekirse sil" prensibi hem güvenli hem satılabilir.
>
> **Öğrenme mekanizması:**
> ```
> Fallback LLM kural üretir → Rule Store'a yazar (pending)
> → Bir sonraki aynı format gelir → Otomatik kullanılır (otonom)
> → Yönetici isterse: onayla (stable) / sil / düzenle
> ```
>
> **Rule Store JSON yapısı:**
> ```json
> {
>   "id": "rule_auto_20260521_001",
>   "source": "fallback_llm",
>   "status": "pending",
>   "format_signature": "vendor_x_firewall",
>   "field_mapping": { "raw_field": "normalized_field" },
>   "confidence": 0.87,
>   "created_at": "2026-05-21",
>   "used_count": 3,
>   "last_used": "2026-05-21"
> }
> ```
> `used_count` kritik: 10 kez başarıyla kullanıldıysa `stable` promote edilebilir.
>
> **Tam sistem mimarisi:**
> ```
> SIEM Katmanı (Wazuh/Splunk/QRadar/Elastic) — REST API
>         ↓
> LangGraph Pipeline
>   [Ingest] → [Schema Detect/LLM#1]
>                ├─ KNOWN → [Known Adapter]
>                └─ UNKNOWN → [Fallback LLM#2]
>                         ↓
>              [Normalize] → [Baseline] → [Anomaly Score]
>                                              ↓
>                                    LOW: LOG  HIGH: ALERT
>         ↓                                    ↓
>   Rule Store (SQLite)               CLI Layer (sorgu + alert)
> ```

---

**User:**
> CLI 7/24 çalışacak, herhangi bir sorunda manager'a direkt uyarı gideceği için 7/24 çalışmalı. Extra olarak CLI query sorguları için — örneğin son 24 saatteki hatalar, uyarılar, sistemin durumu gibi şeyleri görmek sorgulamak için. Sistemin ana amacı mesaj veya sistem içerisinde bir uyarı ile anlık bildirim olduğu için ona göre ayarlanmalı. Extra olarak sistemin birkaç farklı aşaması olucak. Örneğin bir çalışan sistemde 10 GB günlük veri çekmesi normaldir, fakat olağanüstü bir durum yoksa 1000-10000 GB veri çekmemeli — bu tamamen dur durdurulması ve yetki izni gereken bir durum. Fakat bu çalışan 10 değil de 100 GB veri çekse bu uyarı olmalı.

**Claude:**
> Evet, tam anladım. Bu klasik **severity tiering** — tek eşik değil, davranışa göre farklı tepki seviyeleri.
>
> **Severity Sistemi (örnek, statik değil):**
> ```
> Normal baseline: 10 GB/gün
>   ├── 10-50 GB    → LOG (kaydet, sessiz)
>   ├── 50-100 GB   → WARNING (anomali skoru yüksek, izle)
>   ├── 100-500 GB  → ALERT (manager'a bildirim)
>   └── 500 GB+     → CRITICAL (anında bildirim + otomatik işlem önerisi)
> ```
>
> **Ama eşikler statik olmamalı** — LLM bağlama bakar:
> 1. Miktar → baseline'dan sapma
> 2. Zaman → mesai saati mi, gece mi, hafta sonu mu?
> 3. Kişi rolü → IT mi, muhasebe mi, HR mi?
> 4. Hedef → hangi sunucudan veri çekiyor?
> 5. Süre → ani mi (5 dakikada 100 GB) yoksa yavaş mı?
> 6. Geçmiş → bu kişi daha önce böyle yaptı mı?
>
> **Pipeline'a eklenen node:**
> ```
> [Anomaly Score] → [Context Enrichment] → [Severity Decision / LLM]
>                                                ↓
>                                    LOG / WARN / ALERT / CRITICAL
> ```
>
> **Manager'a giden alert formatı:**
> ```
> 🔴 CRITICAL ALERT — 21 Mayıs 2026, 03:47
> Kullanıcı: ali.koc@sirket.com | Departman: Muhasebe
> Olay: 847 GB veri çekimi (baseline: 8 GB/gün)
> Kaynak sunucu: HR-DB-01, FINANCE-DB-02
> Zaman: Gece 03:00-04:00 (mesai dışı)
> LLM Yorumu: Bu kullanıcının rolü için bu miktarda veri çekimi
> olağandışıdır. Gece saatinde gerçekleşmesi ve iki farklı kritik
> sunucuya erişim riski artırıyor.
> Öneri: Oturumu inceleyin, gerekirse IT'yi bilgilendirin.
> ```

---

**User:**
> Ya bu şirketten şirkete, departmandan departmana değişebilir, bu tamamen statik olamaz zaten. Öncelikle kararımız şu zaten, sistem bir süre izlenmeli ve llm sistemin normallerini analiz edip kendine kaydetmeli. Bu süreçte ortalama 1-2 ay arası sürmeli.

**Claude:**
> Kesinlikle doğru. Bu zaten endüstri standardı yaklaşım — **baseline learning period.** Hiçbir UEBA sistemi ilk günden alert üretmez, önce öğrenir.
>
> **İki Fazlı Sistem:**
> ```
> FAZ 1: Learning (1-2 ay) — "Sessiz izleme, sadece öğren"
>         ↓
> FAZ 2: Active (süresiz) — "Artık baseline var, anomali tespit et"
> ```
>
> **Learning fazında ne öğrenilmeli:**
> ```
> Kullanıcı bazında:
> ├── Günlük ortalama veri çekimi
> ├── Saatsel dağılım (09:00-18:00 arası mı hep?)
> ├── Hangi sunuculara erişiyor
> ├── Hafta içi / hafta sonu farkı
> └── Departman normları (muhasebe ayın sonu daha fazla çeker)
>
> Departman bazında:
> ├── Ekip ortalaması
> ├── Sezonsal değişimler (yıl sonu, rapor dönemleri)
> └── Rol bazlı beklentiler
> ```
>
> **Learning fazı mimarisi:**
> ```
> [Raw Events] → [Learning Node] (sürekli)
>   ├── Her gün: günlük özet
>   ├── Her hafta: haftalık pattern güncelle
>   └── Ay sonu: LLM "dreaming"
>                tüm veriyi analiz et → baseline profil oluştur
>                       ↓
>                [Baseline Store]
>                user_id: {
>                  daily_avg: 12.3 GB,
>                  peak_day: Salı,
>                  peak_hour: 14:00-16:00,
>                  usual_servers: [...],
>                  role_context: "muhasebe",
>                  seasonal: { month_end: 2.3x normal }
>                }
> ```
>
> **Faz geçiş kriterleri (otomatik):**
> - 30+ gün geçti ✓
> - Kullanıcı başına 20+ aktif gün verisi ✓
> - Departman başına 15+ kullanıcı verisi ✓
> - LLM confidence score > 0.75 ✓
> → Manager onayı ister, sonra Active faza geçer
>
> **Kritik: Baseline statik değil.** Active fazda da öğrenme devam eder — rolling window (son 90 günün ağırlıklı ortalaması). Rol değişirse, yeni proje başlarsa sistem adapte olur.

---

**User:**
> Peki şimdi genel sistem ve planlama süreci gibi her şeyi düşündük, konuştuk. Şimdi her şeyi eksiksiz şekilde bana md ver. Her mesajlaşmayı, user: "", claude: "" şeklinde her mesajı sırayla içeren bir md oluştur.

**Claude:**
> *(Bu dosya)*

---

## Özet: Ürün Mimarisi (Nihai)

### Kimlik
- **Tip:** Anthropic'ten bağımsız, LLM destekli iç ağ izleme CLI'ı
- **Kategori:** UEBA (User and Entity Behavior Analytics)
- **Hedef:** KOBİ + Enterprise, kapalı iç ağ (private LAN) ortamları
- **Sentinel ile ilişki:** Ayrı ürün, aynı monorepo

### Teknoloji Stack
- **Orkestrasyon:** LangGraph (Python)
- **LLM #1:** Hızlı/ucuz model (Gemini Flash, Haiku) — schema detection
- **LLM #2:** Güçlü model (Opus seviyesi) — fallback integration
- **Rule Store:** SQLite (pending/stable/deleted kurallar)
- **Baseline Store:** JSON/SQLite (kullanıcı + departman profilleri)
- **SIEM Entegrasyonu:** Wazuh, Splunk, QRadar, Elastic — REST API / JWT

### Çalışma Modları
- **7/24 daemon:** Sürekli izleme + anlık alert üretimi
- **CLI sorgu:** `query "son 24 saatteki uyarılar"`, `query "sistem durumu"`

### İki Ana Faz
- **Faz 1 — Learning (1-2 ay):** Sessiz izleme, baseline oluşturma, LLM dreaming
- **Faz 2 — Active:** Dinamik eşikler, severity tiering, manager alertleri

### Alert Seviyeleri
- `LOG` → Sessiz kayıt
- `WARNING` → Anomali skoru yüksek, izle
- `ALERT` → Manager bildirimi
- `CRITICAL` → Anlık bildirim + işlem önerisi

### Kural Yönetimi
- Fallback LLM → otomatik kural üretir → `pending` statüsünde başlar
- Otonom kullanım: bir sonraki aynı formatta otomatik devreye girer
- Yönetici: onayla (`stable`) / sil / düzenle

---

*Oluşturulma tarihi: 21 Mayıs 2026*
*Konuşma: sentinel-coming yeni ürün planlama oturumu*
