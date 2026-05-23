# Watchtower — Ürün Tasarım Kararları

> Bu belge Watchtower'ın ne yaptığını, nasıl çalıştığını ve neden böyle tasarlandığını tanımlar.
> Teknik implementasyon değil, ürün kararlarının kaydıdır.

---

## 1. Sistemin Amacı

Watchtower, şirket iç ağında çalışan bir **insan davranışı izleme sistemi**dır.

- **Ne izler:** Çalışanların dijital hareketlerini — hangi dosyaya ne zaman dokundu, hangi sunucuya bağlandı, ne kadar veri çekti, hangi saatte giriş yaptı, hangi grupta değişiklik oldu.
- **Ne arar:** Policy violation (zaten yanlış olan şeyler) ve davranış sapması (o kişi için normalden kopma).
- **Ne yapar:** Anomali tespit edince CLI'da alert/case üretir, LLM destekli açıklama ve öneri hazırlar; opsiyonel kanallar açıldıysa ilgili kişilere bildirim gönderir.
- **Ne yapmaz:** Müdahale etmez, engellemez, kesmez. Sadece izler ve uyarır.

---

## 2. Üç Çalışma Modu

### 2.1 Öğrenme Modu

**Amaç:** Şirketi tanı, hiçbir uyarı üretme.

- Sıfır alert. Hiçbir bildirim gitmez.
- Sistem tüm çalışanları, departmanları, hiyerarşiyi, yetki yapısını öğrenir.
- AD/LDAP'tan otomatik veri çeker; eksikler manuel tamamlanır.
- LLM bu modda tamamen öğrenmeye odaklıdır: profil belgesi üretir, departman kategorileri çıkarır.
- Çıktı: her kullanıcı ve her departman için davranış profili + baseline verisi.

### 2.2 Hibrit Mod

**Amaç:** Öğrenmeye devam et, aynı zamanda bildiklerinle izle.

- Öğrenme devam eder; yeni çalışanlar, değişen roller sisteme işlenir.
- Aynı zamanda mevcut profillere dayanarak anomali tespiti yapar ve alert üretir.
- Öğrenme tabanı büyüdükçe alertler olgunlaşır, false positive azalır.

### 2.3 Çalışma Modu

**Amaç:** Tam operasyonel izleme, öğrenme kapalı.

- Öğrenme tamamen durur.
- Sistem sadece mevcut profiller ve kurallarla izler ve uyarır.
- Profiller değişmez; mod değiştirilmeden güncellenmez.

---

## 3. İlk Açılış — Bootstrap Admin

Sistem ilk kez kurulduğunda tek bir şey yapılır:

```
Watchtower ilk kez başlatılıyor.
Sistem yöneticisi hesabı oluşturun.

Kullanıcı adı: ___________
Şifre:        ___________
E-posta:      ___________

[ Hesabı Oluştur ]
```

- Bu hesap o şirkete ait Watchtower kurulumunun **tek sahibidir**.
- Tüm entegrasyonları başlatan, diğer kullanıcıları ekleyen, sistemi yapılandıran kişidir.
- Başka kimse sisteme erişemez; bu hesap oluşturulmadan sistem çalışmaz.
- Sonradan değiştirilebilir ama her zaman en az 1 aktif sistem yöneticisi zorunludur.

---

## 4. İzleyenler — Watchtower Kullanıcı Rolleri

### 4.1 Sistem Yöneticisi (`role: system_admin`)

**Kim:** Watchtower'ı kuran ve yöneten kişi. Tipik olarak IT Güvenlik Müdürü veya CISO.

**Neler yapabilir:**
- Tüm çalışanları ve alertleri görür
- Diğer kullanıcıları ekler / rollerini değiştirir
- Departman → yönetici eşlemesini düzenler
- Sistem modunu değiştirir (Öğrenme / Hibrit / Çalışma)
- Kuralları onaylar veya siler
- Tüm raporlara erişir

**Bildirim:** Tüm CRITICAL alertleri alır.

---

### 4.2 Güvenlik Operatörü (`role: security_operator`)

**Kim:** SOC analisti, IT güvenlik uzmanı. Birden fazla olabilir.

**Neler yapabilir:**
- Tüm çalışanların alertlerini görür ve yönetir
- Alert durumlarını değiştirir (`open → investigating → true/false positive`)
- Kural önerilerini inceler
- Raporları görür

**Bildirim:** Tüm ALERT ve CRITICAL alertleri alır.

---

### 4.3 Departman Yöneticisi (`role: dept_manager`)

**Kim:** Muhasebe müdürü, yazılım ekip lideri vb. Her departman için ayrı tanımlanır.

**Neler yapabilir:**
- Sadece kendi departmanındaki çalışanların alertlerini görür
- Alert durumunu değiştiremez; sadece okur ve yorumunu ekleyebilir
- Kendi ekibiyle ilgili raporları alır

**Bildirim:** Kendi ekibinden gelen WARNING ve üstü alertleri alır.

---

### 4.4 Yönetici Gözlemci (`role: executive_viewer`) *(opsiyonel)*

**Kim:** CISO, CEO, Genel Müdür gibi üst yönetim.

**Neler yapabilir:**
- Yalnızca özet dashboard ve CRITICAL alertleri görür
- Hiçbir şeyi değiştiremez

**Bildirim:** Yalnızca CRITICAL alertleri alır.

---

## 5. İzlenenler — Çalışan Yapısı

Watchtower şirketin tüm çalışanlarını izler. Her çalışan şu bilgilerle tanımlanır:

| Alan | Kaynak | Açıklama |
|------|--------|----------|
| `user_id` | AD/LDAP | Sistemdeki benzersiz kimlik |
| `display_name` | AD/LDAP | Görünen ad |
| `email` | AD/LDAP | E-posta adresi |
| `department` | AD/LDAP + manuel | Muhasebe, Hukuk, IT vb. |
| `role_title` | AD/LDAP + manuel | CFO, Stajyer, Analist vb. |
| `seniority` | Manuel / HRIS | Junior / Mid / Senior / Manager / Executive |
| `manager_id` | AD/LDAP + manuel | Kimin altında çalışıyor |
| `risk_group` | Sistem hesaplar | Normal / Elevated / High |
| `access_groups` | AD grupları | Hangi sistemlere erişim yetkisi var |

**Bu bilgiler öğrenme modunda otomatik çekilir; eksik veya yanlış olanlar manuel olarak düzenlenir.**

---

## 6. Hiyerarşi Öğrenme Stratejisi

Şirketin organizasyon yapısı iki yoldan kurulur:

**Otomatik (Öğrenme Modunda):** AD/LDAP'tan OU yapısı, manager attribute ve grup üyelikleri çekilir.

**Manuel tamamlama:** Eksik bağlantılar, standartlaştırılmamış departman isimleri, Watchtower rol atamaları el ile yapılır.

---

## 7. Bildirim Yönlendirme Kuralları

| Alert Seviyesi | Giden Kişiler |
|---------------|---------------|
| `LOG` | Kimseye gitmez, sadece loglanır |
| `WARNING` | Güvenlik Operatörü |
| `ALERT` | Güvenlik Operatörü + Çalışanın Departman Yöneticisi |
| `CRITICAL` | Güvenlik Operatörü + Departman Yöneticisi + Sistem Yöneticisi + Yönetici Gözlemci |

**Özel kural — Yönetici anomalisi:**
Alert üretilen kişi bir Departman Yöneticisiyse, bildirim o kişinin yöneticisine değil doğrudan Sistem Yöneticisi + Güvenlik Operatörüne gider.

**Bildirim kanalları:** CLI varsayılandır. Telegram, e-posta ve webhook opsiyoneldir; MVP için Telegram zorunlu değildir.

---

## 8. Anomali Karar Motoru

### 8.1 Kural Motoru — Bağlamlı Eşik ve Karar Tespiti

Anomali kararı **kural motoru** tarafından verilir, LLM karar vermez.

**Eşik yapısı — çok katmanlı:**

- Sistem öğrenme modunda kullanıcı, departman, rol, asset ve zaman penceresi bazlı normal davranış profilleri çıkarır.
- Her metrik (veri çekimi, login saati, erişilen sunucu sayısı, SQL sorgu sayısı vb.) için global default, departman, rol-in-department ve kullanıcı özel eşikleri hesaplanır.
- Kullanıcının kendi geçmişi, departman normundan daha açıklayıcıysa kullanıcı baseline'ı öncelik kazanır.
- Manager/operator feedback'i doğrudan sistemi değiştirmez; scoped `pending_rule` üretir ve onaydan sonra uygulanır.
- `policy-rule` ve `hard-rule` sınıfındaki davranışlar baseline ile otomatik normalleşmez; explicit approved exception gerekir.

**Örnek:**
```
Backend departmanı SQL sorgu ortalaması: 100 sorgu/gün
Mehmet'in kişisel normal aralığı: 1000-2000 sorgu/gün
Yiğit'in kişisel normal aralığı: 10-20 sorgu/gün

Mehmet → 1000 sorgu attı → kişisel baseline'a göre normal, alert düşebilir
Yiğit → 100 sorgu attı ve artıyor → kişisel baseline'dan sapma, alert üretilebilir
```

### 8.2 Rol, Seniority ve Feedback Ayrımı

> **Karar:** Aynı departmanda worker, senior, manager ve executive davranışları ayrı profillenmelidir. Departman ortalaması tek başına yeterli değildir.
>
> Manager feedback'i tekrar eden benign pattern'leri azaltmak için kullanılır; ancak feedback `pending_rule → approve → stable` akışından geçmeden otomatik karar kuralı olmaz.

---

## 9. LLM'in Rolü — Yorumlama ve Açıklama

LLM **anomali kararı vermez.** Kural motoru eşiği aştığında devreye girer ve şunları yapar:

1. **Bağlamı okur:** Kullanıcının geçmiş davranışları, departmanı, rolü, saati, eriştiği hedef
2. **Yorumlar:** "Bu gerçekten şüpheli mi, neden şüpheli, hangi kombinasyon riski artırıyor?"
3. **Alert metnini yazar:** Yöneticiye gidecek açıklama ve öneriyi oluşturur

**Alert örneği (LLM çıktısı):**
```
ALERT — 22 Mayıs 2026, 03:47
Kullanıcı: ali.koc@sirket.com | Departman: Muhasebe

Olay: Günlük veri çekimi departman eşiğinin 4x üzerinde (8 GB / eşik: 2 GB)
Saat: Gece 03:00 — normal çalışma saati dışı
Hedef: HR-DB-01, FINANCE-DB-02

Yorum: Bu kullanıcı normalde mesai saatlerinde 300-500 MB veri çeker.
Gece saatinde iki kritik sunucuya erişim ve hacmin 16x artması birlikte
değerlendirildiğinde risk yüksektir.

Öneri: Oturumu inceleyin. Gerekirse IT güvenlik birimini bilgilendirin.
```

**LLM'e gönderilen bağlam paketi:**
- Kullanıcı profili (son 90 günlük davranış özeti)
- Departman ortalaması ve eşik değerleri
- Tetiklenen event'in detayları (saat, hedef, hacim)
- Kullanıcının son 7 günlük aktivitesi

---

## 10. Çok Şirket / Çoklu Kurulum

Her şirket kurulumu birbirinden tamamen izoledir:
- Ayrı veritabanı
- Ayrı kullanıcı ve rol tablosu
- Ayrı bootstrap admin

Aynı sunucuda birden fazla şirket çalışabilir; birbirinin verilerine erişemez.

---

*Teknik implementasyon detayları için bkz. [watchtower-master-plan.md](watchtower-master-plan.md)*
