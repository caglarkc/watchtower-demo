# Watchtower — Roller, Erişim ve Bildirim Yapısı

> Bu belge Watchtower sistemini **kimin kullandığını**, **kimin izlendiğini** ve **bildirimlerin kime gittiğini** tanımlar.
> Her şirket için bu yapı farklıdır; sistem hem AD/LDAP'tan otomatik öğrenir hem de manuel konfigürasyona izin verir.

---

## 1. İlk Açılış — Bootstrap Admin

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

## 2. İzleyenler — Watchtower Kullanıcı Rolleri

### 2.1 Sistem Yöneticisi (`role: system_admin`)

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

### 2.2 Güvenlik Operatörü (`role: security_operator`)

**Kim:** SOC analisti, IT güvenlik uzmanı. Birden fazla olabilir.

**Neler yapabilir:**
- Tüm çalışanların alertlerini görür ve yönetir
- Alert durumlarını değiştirir (`open → investigating → true/false positive`)
- Kural önerilerini inceler
- Raporları görür

**Bildirim:** Tüm ALERT ve CRITICAL alertleri alır.

---

### 2.3 Departman Yöneticisi (`role: dept_manager`)

**Kim:** Muhasebe müdürü, yazılım ekip lideri vb. Her departman için ayrı tanımlanır.

**Neler yapabilir:**
- Sadece kendi departmanındaki çalışanların alertlerini görür
- Alert durumunu değiştiremez; sadece okur ve yorumunu ekleyebilir
- Kendi ekibiyle ilgili raporları alır

**Bildirim:** Kendi ekibinden gelen WARNING ve üstü alertleri alır.

---

### 2.4 Yönetici Gözlemci (`role: executive_viewer`) *(opsiyonel)*

**Kim:** CISO, CEO, Genel Müdür gibi üst yönetim.

**Neler yapabilir:**
- Yalnızca özet dashboard ve CRITICAL alertleri görür
- Hiçbir şeyi değiştiremez

**Bildirim:** Yalnızca CRITICAL alertleri alır.

---

## 3. İzlenenler — Çalışan Yapısı

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
| `risk_group` | Sistem hesaplar | Normal / Elevated / High (ayrılmakta olan, kritik erişimli vb.) |
| `access_groups` | AD grupları | Hangi sistemlere erişim yetkisi var |

**Bu bilgiler öğrenme modunda otomatik çekilir; eksik veya yanlış olanlar manuel olarak düzenlenir.**

---

## 4. Hiyerarşi Öğrenme Stratejisi

Şirketin organizasyon yapısı iki yoldan kurulur:

### 4.1 Otomatik — AD/LDAP'tan Çekme (Öğrenme Modunda)

Sistem bağlandığı AD/LDAP üzerinden:
- OU (Organizational Unit) yapısını okur → departman hiyerarşisini çıkarır
- `manager` attribute'unu okur → kimin kime bağlı olduğunu öğrenir
- Grup üyeliklerini okur → yetki profillerini oluşturur

### 4.2 Manuel Düzeltme / Tamamlama

AD verileri her zaman tam değildir. Sistem yöneticisi:
- Eksik `manager` bağlantılarını el ile ekler
- Departman isimlerini standartlaştırır
- Watchtower kullanıcı rollerini çalışanlarla eşleştirir (örn: "Ahmet Yılmaz = dept_manager of Muhasebe")

---

## 5. Bildirim Yönlendirme Kuralları

| Alert Seviyesi | Giden Kişiler |
|---------------|---------------|
| `LOG` | Kimseye gitmez, sadece loglanır |
| `WARNING` | Güvenlik Operatörü |
| `ALERT` | Güvenlik Operatörü + Çalışanın Departman Yöneticisi |
| `CRITICAL` | Güvenlik Operatörü + Departman Yöneticisi + Sistem Yöneticisi + Yönetici Gözlemci |

**Özel kural — Yönetici anomalisi:**
Alert üretilen kişi bir Departman Yöneticisiyse, bildirim o kişinin yöneticisine değil doğrudan Sistem Yöneticisi + Güvenlik Operatörüne gider.

**Bildirim kanalları:** Telegram (varsayılan) + CLI + e-posta (opsiyonel)

---

## 6. Çok Şirket / Çoklu Kurulum

Her şirket kurulumu birbirinden tamamen izoledir:
- Ayrı veritabanı
- Ayrı kullanıcı ve rol tablosu
- Ayrı bootstrap admin

Aynı sunucuda birden fazla şirket çalışabilir; birbirinin verilerine erişemez.

---

*Bu belge sistem tasarımının bir parçasıdır. Teknik implementasyon detayları için bkz. [watchtower-master-plan.md](watchtower-master-plan.md)*
