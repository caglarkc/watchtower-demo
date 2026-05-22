# Watchtower UEBA — Final Senaryo Kütüphanesi

**Toplam:** 83 senaryo | İç ağ (private LAN) only | 35+ kullanıcı profili  
**Kaynak:** ChatGPT + Gemini + Composer çıktılarından derlendi; en iyi kalite ve en yüksek özgünlük seçildi.

**Kategoriler:**
- [Veri Sızdırma](#veri-sızdırma) (15)
- [Credential İhlali](#credential-i̇hlali) (12)
- [Yetkisiz Erişim](#yetkisiz-erişim) (12)
- [Insider Threat](#insider-threat) (10)
- [Kazara İhlal](#kazara-i̇hlal) (8)
- [Politika İhlali](#politika-i̇hlali) (8)
- [Dış Saldırı Desteği](#dış-saldırı-desteği) (8)
- [Sosyal Mühendislik](#sosyal-mühendislik) (5)
- [Çapraz/Multi-User](#çaprrazmulti-user-korelasyon) (5)

---

## Veri Sızdırma

---

### S-001: Gece Yarısı Finans Paylaşımı

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** CFO  
**OLAY:** CFO, normalde yalnızca mesai saatlerinde eriştiği finans sunucusuna gece 02:17'de bağlanır. Ardından son çeyrek bütçe klasöründen 18 GB veri çekip bunu iç ağdaki ortak bir yazıcı-tarama sunucusuna geçici olarak kopyalar.  
**NEDEN ŞÜPHELİ:** Saat dışı erişim, alışılmadık veri hacmi ve CFO'nun rutininde olmayan ara sunucu kullanımı birlikte yüksek risk oluşturur.  
**NORMAL BASELINE'DAN SAPMA:** CFO'nun tipik veri çekişi günde 300–800 MB iken olayda 18 GB. Normal login penceresi 08:00–19:00 iken erişim 02:17.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-002: Gece Yedek Çekimi

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Muhasebe  
**OLAY:** Muhasebe çalışanı normalde gündüz 200–400 MB finans sunucusundan rapor çekerken Cuma 23:47'de aynı sunucudan 18.4 GB toplu dosya indiriyor; arşiv (.zip) ve CSV paketleri.  
**NEDEN ŞÜPHELİ:** Rol için olağandışı saat, tek oturumda 45x veri hacmi, arşiv formatı toplu dışa aktarım paterni.  
**NORMAL BASELINE'DAN SAPMA:** Günlük ort. 320 MB → 18.4 GB; saat 09–18 dışı ilk kez.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-003: Satış Ekibinden Sessiz CRM Dökümü

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Satış  
**OLAY:** Ayrılma sürecindeki satış çalışanı, müşteri CRM verilerini parça parça iç ağdaki bölgesel paylaşım klasörlerine çıkarır ve dosya adlarını toplantı notu gibi masum isimlerle değiştirir.  
**NEDEN ŞÜPHELİ:** Küçük partiler halinde tekrarlı veri çıkarımı ve isim maskeleme davranışı tipik sızdırma taktiğidir.  
**NORMAL BASELINE'DAN SAPMA:** Kullanıcının normal haftalık müşteri export toplamı 200 MB altındayken 3 günde toplam 12.6 GB aktarım.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-004: IT Admin Fazladan USB Yedekleme

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin, bakım amacıyla aldığı veritabanı yedeğini şirket onaylı olmayan harici diske aktarır. Aktarım iç ağda yedekleme sunucusundan admin iş istasyonuna, oradan USB'ye yapılır.  
**NEDEN ŞÜPHELİ:** Büyük hacimli hassas veri aktarımı ile eşzamanlı USB bağlantısı birleşince veri kaçırma riski oluşur.  
**NORMAL BASELINE'DAN SAPMA:** Normal yedek işlemleri doğrudan backup appliance'a giderken olayda 240 GB veri admin PC'si üzerinden geçmiş.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-005: CTO'nun Gizli Yedek Klasörü

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** CTO  
**OLAY:** CTO, birleşme görüşmeleri sırasında teknik durum tespit dokümanlarını standart M&A kasası yerine kendi adında yeni bir dahili paylaşım klasörüne toplar ve erişim geçmişini temizlemeye çalışır.  
**NEDEN ŞÜPHELİ:** Yeni oluşturulmuş kişisel klasöre hassas belgelerin konsolide edilmesi ve log temizleme girişimi ciddi alarm üretmelidir.  
**NORMAL BASELINE'DAN SAPMA:** CTO normalde 2 paylaşımlı klasör kullanırken olay haftasında 1 yeni özel klasöre 74 belge taşınmış.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-006: Kaynak Kod Deposunun Kitlesel Klonlanması

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Bir yazılımcı, normalde sadece üzerinde çalıştığı tek bir projeye erişmesi gerekirken şirketin self-hosted Git sunucusundaki tüm 40 farklı kod deposunu ardışık olarak bilgisayarına klonluyor.  
**NEDEN ŞÜPHELİ:** Rolün normal proje odağını aşan kitlesel kod indirme davranışı; ayrılış niyetiyle örtüşen pattern.  
**NORMAL BASELINE'DAN SAPMA:** Haftalık ortalama 1 depo indirmeden tek günde 40 depo; 150 MB → 4.7 GB.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-007: Geçici Toplantı Dosyasında Gizlenen Veritabanı Dökümü

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Geliştirici, kullanıcı tablosundan aldığı büyük veri çıktısını "Sprint_Retrospective_Backup" adıyla ortak proje klasörüne kaydeder.  
**NEDEN ŞÜPHELİ:** Maskelenmiş dosya adıyla hassas veri saklama ve rol dışı veri export'u tespit edilmelidir.  
**NORMAL BASELINE'DAN SAPMA:** Dev ortamında tipik sorgu sonucu 5–20 MB iken olay dosyası 6.8 GB ve prod kaynaktan alınmış.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-008: Yedekleme Sunucusundan Olağan Dışı Veri Çekme

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin, şirketin ana yedekleme sunucusundan pazar günü kendi bilgisayarına 120 GB veri çekiyor ve ardından yerel makinesine bir USB disk bağlıyor.  
**NEDEN ŞÜPHELİ:** Büyük hacimli yedek verisinin production ortamı dışındaki son kullanıcı makinesine indirilmesi; USB bağlantısıyla korelasyon.  
**NORMAL BASELINE'DAN SAPMA:** Hafta sonu, tek seferde 120 GB USB aktivitesi senkronizasyonu.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-009: BI Ham PII Export

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Veri Analisti  
**OLAY:** Analist DWH'den ham müşteri PII ile 12 GB parquet export alıyor.  
**NEDEN ŞÜPHELİ:** Dashboard sorgusu normalde 50–200 MB; ham PII export nadir ve KVKK/GDPR uyumsuz.  
**NORMAL BASELINE'DAN SAPMA:** 12 GB vs ort. 180 MB.  
**BEKLENEN SEVERITY:** ALERT

---

### S-010: İK'dan Toplu CV Arşivi Kopyası

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK uzmanı, geçmiş aday havuzunu analiz etmek için tüm CV arşivini merkezi İK sunucusundan kendi departman paylaşım alanına kopyalar.  
**NEDEN ŞÜPHELİ:** PII içeren verilerin gereksiz çoğaltılması ve büyük hacimli taşınması veri koruma riski doğurur.  
**NORMAL BASELINE'DAN SAPMA:** Günlük ortalama 20–30 CV erişimi varken olayda 4.800 dosya tek oturumda kopyalanmış.  
**BEKLENEN SEVERITY:** ALERT

---

### S-011: CEO Mail Kutusundan Toplu Arşiv Export

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** CEO  
**OLAY:** CEO hesabı, dahili mail sisteminde tüm ekleriyle birlikte arşiv export işlemi başlatır. 14 yıllık içerik paketlenmektedir.  
**NEDEN ŞÜPHELİ:** Yönetim iletişiminin toplu dışa aktarımı çok yüksek hassasiyetlidir; kurumsal anlaşmazlık veya kişisel arşivleme işareti.  
**NORMAL BASELINE'DAN SAPMA:** CEO kutusunda daha önce hiç full export yapılmamışken olayda 14 yıllık içerik paketlenmiş.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-012: Stajyer CRM Export

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Stajyer  
**OLAY:** Stajyer 2. haftada CRM'den 45.000 satır müşteri kaydını Excel'e aktarıyor (220 MB).  
**NEDEN ŞÜPHELİ:** Stajyer yetkisi demo ortamı; prod export yok. İlk hafta kitlesel veri indirme baseline yokken yapılmış.  
**NORMAL BASELINE'DAN SAPMA:** İlk CRM export; 9x satır üst sınır.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-013: Destek Ticket PII Toplu Arşivi

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** Destek Personeli  
**OLAY:** Destek çalışanı attachment store'dan 800 ticket ekini 6.1 GB zip'liyor.  
**NEDEN ŞÜPHELİ:** Kimlik fotokopisi ve ekran görüntüsü içerebilir; toplu arşivleme bahaneli veri çıkarımı.  
**NORMAL BASELINE'DAN SAPMA:** 50 MB/gün → 6.1 GB.  
**BEKLENED SEVERITY:** ALERT

---

### S-014: Admin Prod-HR VM Snapshot

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Admin prod-HR VM snapshot'ını kendi workstation'ına 90 GB çekiyor.  
**NEDEN ŞÜPHELİ:** Hedef workstation; backup job dışı saat; snapshot çekimi operasyon prosedürü dışı.  
**NORMAL BASELINE'DAN SAPMA:** Tek sefer 90 GB; backup system bypass.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-015: Payroll SQL Dump

**KATEGORİ:** veri sızdırma  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK uzmanı payroll-db'den tüm maaş tablosunu 890 MB SQL export ile indiriyor.  
**NEDEN ŞÜPHELİ:** Tam tablo export; normal iş akışı tek çalışan sorgusu olmalı.  
**NORMAL BASELINE'DAN SAPMA:** Ort. 2–5 MB → 890 MB; SELECT * tablo dökümü.  
**BEKLENED SEVERITY:** CRITICAL

---

## Credential İhlali

---

### S-016: Gece Admin Kerberos TGT Zinciri

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Admin hesabından gece 02:00'de 8 farklı sunucuya ardışık Kerberos TGT isteği yapılıyor. Change ticket yok.  
**NEDEN ŞÜPHELİ:** Lateral movement işareti; PtH (Pass-the-Hash) saldırısı sonrası ağda yayılım paterni.  
**NORMAL BASELINE'DAN SAPMA:** Gece TGT: 0 → 8 farklı hedef.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-017: Token Vault Dump

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Admin iç HashiCorp Vault audit'te 200 secret read; bakım penceresi dışı saat.  
**NEDEN ŞÜPHELİ:** Secret enumeration; hesap compromise veya kötü niyet.  
**NORMAL BASELINE'DAN SAPMA:** Vault read: 5/gün → 200 tek saat.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-018: Domain Admin Hesabıyla Sıra Dışı Giriş

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** En yetkili IT Admin hesabı ile pazar günü saat 04:00'te, normalde hiç kullanmadığı bir muhasebe bilgisayarı üzerinden Active Directory sunucusuna login olunuyor.  
**NEDEN ŞÜPHELİ:** Olağan dışı zaman + olağan dışı kaynak makine + yüksek yetkili hesap kombinasyonu.  
**NORMAL BASELINE'DAN SAPMA:** Hafta içi mesai saatleri dışına çıkılması ve kaynak makine baseline sapması.  
**BEKLENEN SEVERITY:** CRITICAL

---

### S-019: Hizmet Hesabının Kötüye Kullanımı

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Sadece uygulamaların birbiriyle konuşması için ayrılmış yüksek yetkili bir SQL servis hesabı kullanılarak bir IT Admin'in masaüstü bilgisayarından SQL sunucusuna interaktif oturum açılıyor.  
**NEDEN ŞÜPHELİ:** Non-interactive olması gereken hesabın insan tarafından manuel kullanılması.  
**NORMAL BASELINE'DAN SAPMA:** Servis hesabının kaynak IP baseline değişmiş; Logon Type 2 (interaktif).  
**BEKLENED SEVERITY:** CRITICAL

---

### S-020: Çoklu Lokasyon Çakışması

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** CEO  
**OLAY:** CEO hesabı aynı 20 dakikalık dilimde hem yönetim katındaki sabit cihazdan hem de bodrum kattaki toplantı odası terminalinden aktif işlem yapıyor.  
**NEDEN ŞÜPHELİ:** Fiziksel olarak imkânsız eşzamanlılık; hesap paylaşımı veya oturum ele geçirilmesi.  
**NORMAL BASELINE'DAN SAPMA:** CEO hesabında tarihsel olarak paralel oturum görülmemiş; iki farklı cihaz ve iki farklı iç lokasyon.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-021: Eski Credential ile API Kullanımı

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Ekipten ayrılmak üzere olan geliştirici, 47 gündür kullanılmayan ve iptal edilmesi gereken eski test API token'ını hâlâ çalışır halde bulur ve bunu kullanarak kullanıcı veri setlerini sorgular.  
**NEDEN ŞÜPHELİ:** Süresi dolması gereken credential'ın tekrar kullanılması; yetki deprovisioning zafiyeti.  
**NORMAL BASELINE'DAN SAPMA:** İlgili token 47 gündür kullanılmıyorken olayda bir saatte 1.200 çağrı.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-022: API Servis Hesabını İnsan Gibi Kullanan Analist

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** Veri Analisti  
**OLAY:** Veri analisti, rapor çıkarmayı hızlandırmak için bir servis hesabının API anahtarını paylaşımlı nottan alıp kendi makinesinden manuel sorgular yapar.  
**NEDEN ŞÜPHELİ:** Servis credential'ının interaktif kullanıcı oturumunda kullanılması politika dışı.  
**NORMAL BASELINE'DAN SAPMA:** İlgili servis anahtarı normalde 1 entegrasyon sunucusundan çağrı yaparken olayda analist iş istasyonundan 430 API çağrısı.  
**BEKLENED SEVERITY:** ALERT

---

### S-023: Muhasebe Terminalinden Gece Loginleri

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** Muhasebe  
**OLAY:** Muhasebe çalışanının hesabı, çalışanın binada olmadığı bir gecede muhasebe terminali yerine geliştirici alanındaki paylaşımlı bir cihazdan kullanılıyor.  
**NEDEN ŞÜPHELİ:** Fiziksel konum ile kullanıcı erişim noktası uyuşmazlığı; hesap paylaşımı veya ele geçirilmiş oturum.  
**NORMAL BASELINE'DAN SAPMA:** Kullanıcının önceki 90 günde hiç 21:00 sonrası oturumu yokken olayda 01:09'da login; cihaz tipi de ilk kez değişmiş.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-024: Deploy Key 3 Farklı IP

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** svc-deploy API key 3 farklı workstation IP'sinden kullanılıyor.  
**NEDEN ŞÜPHELİ:** Key tek makineye bağlı olmalı; Slack'te key paylaşımı veya credential sızıntısı.  
**NORMAL BASELINE'DAN SAPMA:** Kaynak IP: 1 → 3.  
**BEKLENED SEVERITY:** ALERT

---

### S-025: Admin Hesaplarının Çapraz Kullanımı

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** 1. IT Admin, o gün izinli olan 2. IT Admin'in bilgisayarına uzaktan RDP ile bağlanıp onun kimlik bilgileriyle ağda işlemler gerçekleştiriyor.  
**NEDEN ŞÜPHELİ:** İzinli olan personelin hesabının aktifleşmesi; hesap izlenebilirliği ortadan kalkıyor.  
**NORMAL BASELINE'DAN SAPMA:** İzin günü + farklı kaynak IP'den aktif oturum.  
**BEKLENED SEVERITY:** ALERT

---

### S-026: Stajyer Çift Oturum

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** Stajyer  
**OLAY:** Stajyer hesabı aynı anda 2 farklı workstation'da aktif; biri mentor masası değil tanımsız bir cihaz.  
**NEDEN ŞÜPHELİ:** Hesap paylaşımı; mentor şifreyi vermiş veya credential sızıntısı.  
**NORMAL BASELINE'DAN SAPMA:** Eşzamanlı oturum: 1 host → 2 host.  
**BEKLENED SEVERITY:** ALERT

---

### S-027: İç Ağda Gizli Posta Kuralı Oluşturma

**KATEGORİ:** credential ihlali  
**KULLANICI ROLÜ:** Satış  
**OLAY:** Satış çalışanı hesabında, belirli müşteri anahtar kelimelerini içeren dahili mailleri otomatik olarak gizli bir klasöre taşıyan kural oluşturuluyor.  
**NEDEN ŞÜPHELİ:** Kalıcı veri toplama amacı taşıyan gizli mail kuralı; hesap ele geçirilme sonrası kalıcılık veya insider toplama taktiği.  
**NORMAL BASELINE'DAN SAPMA:** Kullanıcının daha önce 0 kuralı varken olayda 3 yeni filtre kuralı.  
**BEKLENED SEVERITY:** ALERT

---

## Yetkisiz Erişim

---

### S-028: IT Admin Yetki Zinciri

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin kullanıcısı, vardiya dışı saatte önce etki alanı denetleyicisine, sonra hukuk arşiv sunucusuna, ardından muhasebe veritabanı yedeğine erişiyor. Bu erişimler için resmi değişiklik kaydı bulunmuyor.  
**NEDEN ŞÜPHELİ:** Ayrı departmanlara ait yüksek hassasiyetli sistemlere kısa sürede ardışık erişim; yatay keşif veya hazırlık hareketi.  
**NORMAL BASELINE'DAN SAPMA:** Admin'in günlük ortalama kritik sistem erişimi 2–3 hedef iken olayda 7 hedefe 23 dakika içinde erişilmiş.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-029: Hukuk Belgelerine Meraklı Geliştirici

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Bir geliştirici, görev alanıyla ilgisi olmadığı halde hukuk departmanının sözleşme arşivi sunucusunda dosya isimlerini tarar ve sonrasında üç birleşme sözleşmesini indirir.  
**NEDEN ŞÜPHELİ:** İş rolü ile erişilen veri arasında bağ bulunmaması; hassas klasörlerde hedefli gezinme.  
**NORMAL BASELINE'DAN SAPMA:** Geliştiricinin normal sunucu erişim profili yalnızca dev/test iken ilk kez hukuk sunucusuna 41 dosya sorgusu yapılmış.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-030: Yetki Yükseltme (Privilege Escalation)

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** 3 IT Admin'den en kıdemsiz olanı, iç ağdaki Active Directory üzerinde kendi kişisel hesabını "Domain Admins" grubuna ekliyor.  
**NEDEN ŞÜPHELİ:** Onay mekanizmasından geçmemiş kritik rol atanması; içeriden tehdit.  
**NORMAL BASELINE'DAN SAPMA:** AD grup değişikliği: 0/ay → 1 beklenmedik ekleme.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-031: CTO Bilgisayarından SSH Anahtarı Hasadı

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** CTO  
**OLAY:** CTO'nun yerel bilgisayarındaki tüm sunucu SSH private key dosyaları (.pem, .id_rsa) taranıyor ve iç ağdaki bir geliştirici bilgisayarına kopyalanıyor.  
**NEDEN ŞÜPHELİ:** Kritik kimlik doğrulama dosyalarının ağ içinde yer değiştirmesi; ele geçirilmiş makine paterni.  
**NORMAL BASELINE'DAN SAPMA:** SSH key dosyalarına erişim sıklığında anomali; hedef değişikliği.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-032: Junior Dev Prod Veritabanı Erişimi

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Junior developer prod-db-01'e SSMS ile bağlanarak SELECT * sorgular yapıyor.  
**NEDEN ŞÜPHELİ:** Prod sadece DBA; junior geliştirici bug fix bahanesiyle erişmiş.  
**NORMAL BASELINE'DAN SAPMA:** Prod erişimi: 0 → 1 oturum.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-033: Destek Personeli DC RDP

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Destek Personeli  
**OLAY:** Şifre reset için Domain Controller'a RDP bağlantısı.  
**NEDEN ŞÜPHELİ:** DC sadece IT Admin erişimli; destek personeli yanlış prosedür veya privilege escalation denemesi.  
**NORMAL BASELINE'DAN SAPMA:** DC RDP: 0 → 1 oturum.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-034: Muhasebe Domain Admin Grubu Denemesi

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Muhasebe  
**OLAY:** Domain Admin grubuna ekleme denemesi başarısız; muhasebe kullanıcısından AD write komutu.  
**NEDEN ŞÜPHELİ:** Privilege escalation; phishing sonrası credential abuse.  
**NORMAL BASELINE'DAN SAPMA:** AD write: 0 → 1 başarısız deneme.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-035: Stajyer Ağ Keşfi

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Stajyer  
**OLAY:** Yazılım stajyeri, ağ taraması yaparak erişim izni olmayan İK sunucusunun IP adresine bağlanmaya çalışıyor.  
**NEDEN ŞÜPHELİ:** Rol tanımında olmayan bir sunucu segmentine erişim denemesi; merak kaynaklı keşif.  
**NORMAL BASELINE'DAN SAPMA:** Haftalık 0 olan İK segmenti bağlantı denemesinin 1'e çıkması.  
**BEKLENED SEVERITY:** ALERT

---

### S-036: Veri Analistinin Tüm Posta Kutusu Taraması

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Veri Analisti  
**OLAY:** Veri analisti, müşteri duygu analizi projesi için yalnızca destek ekibi maillerini alması gerekirken dahili mail arşiv sunucusunda tüm departman kutularını tarıyor.  
**NEDEN ŞÜPHELİ:** Veri kapsamının gereksiz biçimde genişletilmesi; "önce hepsini alalım sonra filtreleriz" yaklaşımı.  
**NORMAL BASELINE'DAN SAPMA:** Analistin normal mail veri seti tek paylaşımlı kutu iken olayda 9 farklı departman kutusuna sorgu gitmiş.  
**BEKLENED SEVERITY:** ALERT

---

### S-037: Satıştan Muhasebeye Kesişen Erişim

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Satış  
**OLAY:** Satış çalışanı, prim hesaplamasını kontrol etmek için muhasebe paylaşım klasöründe bordro tablolarını arar ve farklı çalışanların maaş sayfalarını açar.  
**NEDEN ŞÜPHELİ:** Gerekçesi kişisel merak olan, departman sınırını aşan hassas belge erişimi.  
**NORMAL BASELINE'DAN SAPMA:** Satış çalışanının önceki 6 ayda muhasebe sunucusuna erişimi yokken olay günü 18 dosya açılmış.  
**BEKLENED SEVERITY:** ALERT

---

### S-038: Güvenlik Duvarı Kurallarının Esnetilmesi

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Bir IT Admin, iç ağdaki kritik finans sunucusuna kendi bilgisayarından her porttan erişebilmek için yerel firewall üzerinde "Any-Any" izni veren kural tanımlıyor.  
**NEDEN ŞÜPHELİ:** Sıkı korunan bir segmente yönelik kuralların güvensiz şekilde genişletilmesi.  
**NORMAL BASELINE'DAN SAPMA:** Güvenlik politikasında baseline dışı gevşeme; change ticket yok.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-039: PM SIEM Konsol Erişimi

**KATEGORİ:** yetkisiz erişim  
**KULLANICI ROLÜ:** Proje Yöneticisi  
**OLAY:** PM SIEM web konsoluna login oluyor.  
**NEDEN ŞÜPHELİ:** SOC rolü yok; proje inceleme bahanesiyle güvenlik izleme altyapısına erişim.  
**NORMAL BASELINE'DAN SAPMA:** İlk SIEM erişimi.  
**BEKLENED SEVERITY:** ALERT

---

## Insider Threat

---

### S-040: Shadow Admin Hesabı Oluşturma

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Yeni local admin hesabı "svc_monitor" oluşturuluyor; change ticket yok.  
**NEDEN ŞÜPHELİ:** Shadow account; kalıcı erişim için arka kapı.  
**NORMAL BASELINE'DAN SAPMA:** Onaysız yeni hesap oluşturma.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-041: Sahte Tedarikçi IBAN Değişikliği

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** Muhasebe  
**OLAY:** Tedarikçi master'da onaysız IBAN değişikliği yapılıyor.  
**NEDEN ŞÜPHELİ:** Vendor fraud; onay workflow bypass edilmiş.  
**NORMAL BASELINE'DAN SAPMA:** Onaysız write; IBAN değişikliği change ticket yok.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-042: SOC Log Suppress Kuralı

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** Güvenlik Görevlisi  
**OLAY:** SOC çalışanı kendi host IP'si için SIEM'de suppress rule ekliyor.  
**NEDEN ŞÜPHELİ:** Anti-forensics; kendi ihlalini gizleme girişimi.  
**NORMAL BASELINE'DAN SAPMA:** Self-suppress kuralı: 0 → 1.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-043: Admin Tarafından Eski Yedeklerin Silinmesi

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** İşten çıkarılacağını öğrenen bir IT Admin, şirketin son 6 aylık offline teyp veya ağ tabanlı arşiv yedeklerini kalıcı olarak sistemden temizliyor.  
**NEDEN ŞÜPHELİ:** Normal rotasyon dışı kitlesel ve geri döndürülemez yedek silme; sabotaj niyeti.  
**NORMAL BASELINE'DAN SAPMA:** Günlük silme limitlerinin %1000 üzerine çıkılması.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-044: Yönetici Yetkisiyle Kitlesel Log Silme

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Bir IT Admin, iç ağdaki merkezi log sunucusuna bağlanarak son 24 saate ait sistem erişim loglarını siliyor.  
**NEDEN ŞÜPHELİ:** Log temizleme komutu ile servis durdurma işlemi; iz silme.  
**NORMAL BASELINE'DAN SAPMA:** Log hacminin bir anda sıfıra düşmesi ve temizlik komutu tespiti.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-045: İK Hesabından Gece Mail Arşiv Taraması

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK çalışanı, işten çıkarma planlarıyla ilgili bilgileri toplamak için yöneticilerin dahili mail arşivinde meta-veri araması yapar.  
**NEDEN ŞÜPHELİ:** Görev alanını aşan yönetim iletişimi keşfi; iş güvencesi kaygısı kaynaklı.  
**NORMAL BASELINE'DAN SAPMA:** İK kullanıcısının normal mail erişimi kendi kutusu ve İK shared box iken olayda 4 yönetim kutusunda arama.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-046: İK Sisteminde Hayalet Çalışan Oluşturma

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK yöneticisi, şirkette gerçekte var olmayan "hayalet bir çalışan" profili oluşturup ERP sistemine kaydediyor ve ona maaş hesabı tanımlamaya çalışıyor.  
**NEDEN ŞÜPHELİ:** Süreç akış anomalisi; eksik belgeler (sabıka kaydı yok, imza sirküsü yok); iç muhasebe zimmeti.  
**NORMAL BASELINE'DAN SAPMA:** Onboarding akış adımları eksik; ERP'de kayıt + maaş tanımı korelasyonu.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-047: Ayrılış Öncesi Veri Rampa-Up

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** İstifadan 5 gün önce günlük veri çekimi 200 MB'dan 3 GB'a çıkıyor.  
**NEDEN ŞÜPHELİ:** Offboarding pattern; ayrılış öncesi IP biriktirme.  
**NORMAL BASELINE'DAN SAPMA:** 5 gün sürekli artış; istifa tarihiyle korelasyon.  
**BEKLENED SEVERITY:** ALERT

---

### S-048: PM Proje Maliyet Tablosu Toplu Güncelleme

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** Proje Yöneticisi  
**OLAY:** PM proje maliyet tablosunda 50 hücreyi toplu olarak güncelliyor.  
**NEDEN ŞÜPHELİ:** Yetkisiz finans write; bütçe manipülasyon girişimi.  
**NORMAL BASELINE'DAN SAPMA:** Normalde 2–3 güncelleme/gün iken 50x write tek oturumda.  
**BEKLENED SEVERITY:** ALERT

---

### S-049: Muhasebe Login Saatleri Toplu İnceleme

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** Muhasebe  
**OLAY:** Muhasebe çalışanı, işten çıkarma söylentileri sonrası kimlerin geç kaldığını anlamak için erişim loglarını toplar.  
**NEDEN ŞÜPHELİ:** Kişisel motivasyonla çalışan davranış verisi toplama; rol dışı log erişimi.  
**NORMAL BASELINE'DAN SAPMA:** Muhasebe rolünün access log görüntüleme ihtiyacı yokken olayda 35 kullanıcıya ait giriş kayıtları çekilmiş.  
**BEKLENED SEVERITY:** ALERT

---

### S-050: Satış Müşteri Segmentasyon Modeline Erişim

**KATEGORİ:** insider threat  
**KULLANICI ROLÜ:** Satış  
**OLAY:** Ayrılan satış temsilcisi müşteri segmentasyon modeline ayrılışından 3 gün önce erişiyor.  
**NEDEN ŞÜPHELİ:** Rakibe değerli verinin toplanması; headhunter senaryosu.  
**NORMAL BASELINE'DAN SAPMA:** Model + ayrılış korelasyonu; erişim sıklığı artışı.  
**BEKLENED SEVERITY:** ALERT

---

## Kazara İhlal

---

### S-051: Yanlış Paylaşılan Bordro Klasörü

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Muhasebe  
**OLAY:** Muhasebe çalışanı, aylık bordro belgelerini ekip içi paylaşıma koymak isterken erişim izinlerini yanlış ayarlar ve klasörü şirket içindeki tüm kullanıcıların okuyabileceği şekilde yayınlar.  
**NEDEN ŞÜPHELİ:** Hassas finans verisinin yetki seviyesi dışında geniş erişime açılması.  
**NORMAL BASELINE'DAN SAPMA:** Normalde bordro klasörleri yalnızca 4 personel ve CFO'ya açıkken erişim kapsamı 35 kullanıcıya açılmış.  
**BEKLENED SEVERITY:** ALERT

---

### S-052: İK'dan Yanlış Odaya Giden Hassas Mail

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK çalışanı, disiplin sürecine ait belgeleri iç ağ posta sistemi üzerinden yalnızca hukuk ekibine göndermek isterken "Legal-All" yerine benzer isimli "Leadership-All" grubunu seçer.  
**NEDEN ŞÜPHELİ:** Hassas mail ekinin normal dışı geniş dahili dağıtım listesine gitmesi; veri minimizasyonu ihlali.  
**NORMAL BASELINE'DAN SAPMA:** Bu tip ekler normalde 2–4 alıcıya giderken olayda 11 kişiye ulaştırılmış.  
**BEKLENED SEVERITY:** WARNING

---

### S-053: Yeni Yazılımcının Hatalı Script Döngüsü

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** İşe yeni başlayan yazılımcı, yazdığı hatalı test scripti yüzünden iç veri tabanı sunucusuna saniyede 5000 hatalı login isteği gönderiyor.  
**NEDEN ŞÜPHELİ:** Bruteforce saldırısına benzer aşırı yoğun hatalı istek trafiği; DoS etkisi.  
**NORMAL BASELINE'DAN SAPMA:** Saniyede 1 bağlantı isteği → 5000.  
**BEKLENED SEVERITY:** ALERT

---

### S-054: Canlı Ortam Yerine Test Aracı Yanlışlığı

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Yazılımcı, kendi lokalinde denemesi gereken güvenlik zafiyet tarama aracını yanlışlıkla iç ağdaki canlı müşteri veri tabanına doğru çalıştırıyor.  
**NEDEN ŞÜPHELİ:** Geliştirici IP'sinden canlı veritabanına binlerce anomali içeren SQL sorgu hatası.  
**NORMAL BASELINE'DAN SAPMA:** Veri tabanı hata loglarında anlık patlama; proddan gelen 4xx burst.  
**BEKLENED SEVERITY:** ALERT

---

### S-055: USB ile İçeri Veri Taşıyan Stajyer

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Stajyer  
**OLAY:** Stajyer, eğitim sunumunu hazırlamak için örnek müşteri verisini şirketin güvenli paylaşım alanı yerine USB belleğe kopyalar, sonra bunu toplantı odasındaki ortak cihaza takar.  
**NEDEN ŞÜPHELİ:** Yetkisiz taşınabilir medya kullanımı; örnek veri içinde gerçek müşteri kayıtları.  
**NORMAL BASELINE'DAN SAPMA:** Stajyer cihazlarında USB bağlantısı kapalıyken ilk kez dış depolama tanınmış ve 2.4 GB veri yazılmış.  
**BEKLENED SEVERITY:** ALERT

---

### S-056: Destek Personelinin Aşırı Geniş Oturum Süresi

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Destek Personeli  
**OLAY:** Destek personeli, bir kullanıcının yazıcı sorununu çözmek için uzaktan bağlanır ve oturum açıkken kullanıcının yetkili klasörlerinde gezerek yanlışlıkla hassas İK belgelerini açar.  
**NEDEN ŞÜPHELİ:** Sorunla ilgisiz dosya erişimi; hassas bölümlere yan gezinme.  
**NORMAL BASELINE'DAN SAPMA:** Tipik destek oturumları 10–15 dakika sürerken olay 52 dakika sürmüş ve 27 hassas dosya açılmış.  
**BEKLENED SEVERITY:** WARNING

---

### S-057: Veri Analistinin Legal Hold Dosyalarını Dahil Etmesi

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Veri Analisti  
**OLAY:** Analist, şirket verisini temizlerken hukuki saklama kapsamındaki dosyaları da kendi veri setine dahil eder.  
**NEDEN ŞÜPHELİ:** Legal hold altındaki veriye uygunsuz erişim ve çoğaltma; hukuki risk.  
**NORMAL BASELINE'DAN SAPMA:** Legal hold klasörlerine analist erişimi baseline'da sıfırken olayda 3.200 dosya indekslenmiş.  
**BEKLENED SEVERITY:** ALERT

---

### S-058: Hukuk Bilgisayarına Bilinmeyen USB Takılması

**KATEGORİ:** kazara ihlal  
**KULLANICI ROLÜ:** Hukuk  
**OLAY:** Hukuk müşaviri, bir davanın delillerini incelemek üzere müvekkilden gelen ve içinde ne olduğu bilinmeyen denetimsiz bir USB belleği bilgisayarına takıyor.  
**NEDEN ŞÜPHELİ:** İç ağ güvenliğini tehlikeye atacak envanter dışı harici depolama aktivitesi; potansiyel malware taşıyıcısı.  
**NORMAL BASELINE'DAN SAPMA:** Donanım baseline ihlali; yeni vendor ID.  
**BEKLENED SEVERITY:** ALERT

---

## Politika İhlali

---

### S-059: Stajyerin Kaynak Kod Aynası

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** Stajyer  
**OLAY:** Yeni başlayan stajyer, eğitim amaçlı incelemek için üretim kod deposunun tam kopyasını dahili dosya sunucusundaki kişisel çalışma alanına alır. Kopya içinde servis anahtarlarının eski versiyonları da bulunur.  
**NEDEN ŞÜPHELİ:** Gerekenden fazla erişim, hacimli kopyalama ve gizli credential artığı bulunan içeriklerin kişisel alana taşınması.  
**NORMAL BASELINE'DAN SAPMA:** Stajyerler normalde yalnızca eğitim reposuna erişirken erişilen repo sayısı 1'den 7'ye, veri miktarı 150 MB'tan 9 GB'a çıkmış.  
**BEKLENED SEVERITY:** ALERT

---

### S-060: Hukuk Klasörünü Yedekleyen PM

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** Proje Yöneticisi  
**OLAY:** PM, sözleşme değişikliklerini kaçırmamak için hukuk paylaşım klasörünü kendi proje klasörüne periyodik olarak kopyalayan küçük bir iç script çalıştırır.  
**NEDEN ŞÜPHELİ:** Yetkisiz otomasyon, departman verisinin çoğaltılması ve erişim kapsamının fiilen genişletilmesi.  
**NORMAL BASELINE'DAN SAPMA:** PM kullanıcılarında otomatik kopyalama script'i baseline'da yokken olayda günde 4 kez senkron çalışmış.  
**BEKLENED SEVERITY:** ALERT

---

### S-061: PM'den Gereksiz Credential İstemi

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** Proje Yöneticisi  
**OLAY:** Proje yöneticisi, teslim tarihi baskısı nedeniyle geliştiricilerden test ortamı parolalarını iç ağ mesajlaşma aracı üzerinden ister ve bunları kendi notlarında saklar.  
**NEDEN ŞÜPHELİ:** Paylaşılan credential kullanımı ve rol dışı erişim talebi; organizasyonel risk.  
**NORMAL BASELINE'DAN SAPMA:** PM rolünün normalde doğrudan sistem login'i bulunmazken iki günde 6 farklı credential talebi.  
**BEKLENED SEVERITY:** ALERT

---

### S-062: Sabit Şifre Koda Gömme

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Yazılımcı, iç ağdaki test sunucusunun root şifresini ve API anahtarını açık metin olarak kodun içine yazıp iç Git sunucusuna push ediyor.  
**NEDEN ŞÜPHELİ:** UEBA/DLP'nin code commit içeriğinde açık şifre örüntülerini yakalaması; tüm iç kullanıcılar credential'ı görebilir.  
**NORMAL BASELINE'DAN SAPMA:** Güvenli kod yazım baseline'ından sapma; hardcoded secret pattern.  
**BEKLENED SEVERITY:** ALERT

---

### S-063: Süresi Dolan Şifrelerin Toplu Uzatılması

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin, şirketin şifre politikası gereği süresi dolan 10 kritik personelin şifre değişim zorunluluğunu script ile 180 gün daha erteliyor.  
**NEDEN ŞÜPHELİ:** Kurumsal şifre rotasyon politikasının toplu olarak delinmesi.  
**NORMAL BASELINE'DAN SAPMA:** Şifre geçerlilik sürelerinde toplu sapma manipülasyonu.  
**BEKLENED SEVERITY:** WARNING

---

### S-064: Stajyerin Wi-Fi Ağı Sniffing Denemesi

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** Stajyer  
**OLAY:** Stajyer, iç ağa bağlı bilgisayarına kurduğu network analiz aracıyla yerel ağdaki paketleri dinlemeye (sniffing) çalışıyor.  
**NEDEN ŞÜPHELİ:** Normal bir kullanıcı makinesinden ağa promiscuous modda paket istekleri gönderilmesi; ciddi güvenlik kuralı ihlali.  
**NORMAL BASELINE'DAN SAPMA:** Ağ kartı modunun değişimi ve lokal ağda sıra dışı ARP trafiği.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-065: Geçici Erişim Süresinin Aşılması

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin, bir dış danışmanın işi için açtığı geçici iç ağ erişim hesabını, iş bitmesine rağmen 2 hafta boyunca kapatmıyor ve hesap üzerinden ağda veri akışı devam ediyor.  
**NEDEN ŞÜPHELİ:** Kapatılma tarihi geçmiş bir hesabın iç ağda aktif olması; unutulmuş ghost hesap.  
**NORMAL BASELINE'DAN SAPMA:** Politika dışı aktif hesap; expiry geçilmiş.  
**BEKLENED SEVERITY:** WARNING

---

### S-066: Hukuk Toplu PDF OCR Geçici Klasörü

**KATEGORİ:** politika ihlali  
**KULLANICI ROLÜ:** Hukuk  
**OLAY:** Hukuk çalışanı, arama kolaylığı için binlerce sözleşmeyi OCR işlemi yapmak üzere geçici ortak klasöre koyar; klasör BT ekibinin de erişimine açıktır.  
**NEDEN ŞÜPHELİ:** Hassas belgelerin işleme bahanesiyle erişim yüzeyinin genişletilmesi.  
**NORMAL BASELINE'DAN SAPMA:** Hukuk belgeleri normalde 2 kullanıcıya açıkken olay klasörü 9 kullanıcı erişimine açılmış.  
**BEKLENED SEVERITY:** ALERT

---

## Dış Saldırı Desteği

---

### S-067: Güvenlik Görevlisinin Sunucu Odası Erişim Olayı

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** Güvenlik Görevlisi  
**OLAY:** Güvenlik görevlisi, gece vardiyasında sunucu odasında bakım ekibi olduğunu söyleyen kişilere kapı açar. Aynı zaman aralığında içerideki bakım terminalinden çok sayıda kimlik doğrulama denemesi görülür.  
**NEDEN ŞÜPHELİ:** Fiziksel erişim olayı ile iç ağda başarısız login patlamasının korele olması kritik sinyaldir.  
**NORMAL BASELINE'DAN SAPMA:** Normalde bakım terminalinde saatte 5'ten az login varken olay saatinde 86 başarısız deneme.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-068: Admin Bilgisayarından Agresif Port Taraması

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** Bir IT Admin'in bilgisayarından, şirketin tüm iç subnetlerine yönelik 22, 80, 443 ve 445 portlarını kapsayan agresif tarama başlatılıyor. Normal bakım saatleri dışı, habersiz.  
**NEDEN ŞÜPHELİ:** Ele geçirilmiş admin makinesi; iç ağda lateral movement öncesi haritalama.  
**NORMAL BASELINE'DAN SAPMA:** Dakikadaki bağlantı isteği sayısının normal admin baseline'ını %2000 aşması.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-069: DNS Sunucu Yönlendirme Manipülasyonu

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** İç ağdaki yerel DNS sunucusunun ayarlarında değişiklik yapılarak, şirket içi maillerin döndüğü mail sunucusunun IP adresi sahte bir lokal IP'ye yönlendiriliyor.  
**NEDEN ŞÜPHELİ:** Kritik ağ altyapısında yetkisiz DNS yönlendirmesi; Man-in-the-Middle hazırlığı.  
**NORMAL BASELINE'DAN SAPMA:** DNS kayıtlarında ani değişiklik; change ticket yok.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-070: Domain Controller Üzerinde Credential Dumping Script

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin hesabı ile Active Directory sunucusu üzerinde tüm kullanıcı şifre özetlerini hafızadan çeken karmaşık bir PowerShell scripti çalıştırılıyor.  
**NEDEN ŞÜPHELİ:** Normal yönetim aktivitelerinde kullanılmayan; Mimikatz benzeri script tespiti.  
**NORMAL BASELINE'DAN SAPMA:** PowerShell komut geçmişinde baseline dışı -EncodedCommand argümanları.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-071: Geliştirici Bilgisayarından SSH Kaba Kuvvet Saldırısı

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Bir yazılımcının bilgisayarı saldırganlar tarafından ele geçirilmiş ve bu bilgisayar üzerinden iç ağdaki ana veri tabanına dakikada 300 SSH login denemesi yapılıyor.  
**NEDEN ŞÜPHELİ:** Yazılımcı bilgisayarının zombi gibi kullanılması; iç ağda brute-force.  
**NORMAL BASELINE'DAN SAPMA:** Başarısız SSH bağlantı baseline'ının radikal artışı; geliştirici makinesinden anomalous destination.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-072: CTO Hesabından Ağ Trafik Kopyalama Kuralı

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** CTO  
**OLAY:** CTO hesabı kullanılarak iç ağdaki omurga anahtarlayıcıya bağlanılıyor ve tüm trafiği bir IT Admin bilgisayarına kopyalayan SPAN/Mirror kuralı ekleniyor.  
**NEDEN ŞÜPHELİ:** CTO'nun operasyonel olarak switch yapılandırması yapmaması gerekir; trafiğin izinsiz kopyalanması MitM hazırlığı.  
**NORMAL BASELINE'DAN SAPMA:** CTO hesabının network cihazlarında aktif komut çalıştırması: baseline 0.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-073: İK Bilgisayarında Keylogger Çalışması

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK çalışanının bilgisayarında, basılan tuşları kaydeden zararlı bir arka plan süreci çalışıyor ve toplanan verileri iç ağdaki sahte bir yerel paylaşım klasörüne yazıyor.  
**NEDEN ŞÜPHELİ:** Kullanıcı bilgisayarında yetkisiz dosya yazma ve API dinleme süreçleri.  
**NORMAL BASELINE'DAN SAPMA:** İşletim sistemi API çağrılarında anomali; bilinmeyen process parent.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-074: Docker Container Escape Denemesi

**KATEGORİ:** dış saldırı desteği  
**KULLANICI ROLÜ:** Yazılım Geliştirici  
**OLAY:** Dev container'dan host mount /etc/shadow dosyasına okuma denemesi yapılıyor.  
**NEDEN ŞÜPHELİ:** Container escape; CVE exploit veya kasıtlı güvenlik testi.  
**NORMAL BASELINE'DAN SAPMA:** Container host mount read denemesi: 0 → 1.  
**BEKLENED SEVERITY:** CRITICAL

---

## Sosyal Mühendislik

---

### S-075: CEO Asistanı Gibi Davranan Arama Sonrası Erişim

**KATEGORİ:** sosyal mühendislik  
**KULLANICI ROLÜ:** CEO  
**OLAY:** CEO, şirket içi destek masasını arayan ve kendini yönetim ofisinden biri gibi tanıtan kişinin yönlendirmesiyle "sunum hazırlığı" bahanesiyle iç ağdaki proje klasörlerine normalde kullanmadığı terminal odasından giriş yapar.  
**NEDEN ŞÜPHELİ:** CEO hesabının olağan dışı terminalden kullanılması; alışılmadık klasör erişimi ve kısa süreli çoklu belge açılışı.  
**NORMAL BASELINE'DAN SAPMA:** CEO genelde yalnızca kendi dizüstünden erişirken ilk kez ortak toplantı terminali; erişilen klasör sayısı 2'den 11'e.  
**BEKLENED SEVERITY:** ALERT

---

### S-076: CFO'dan Gelen Acil Onay Talebi Sonrası Yetki Verme

**KATEGORİ:** sosyal mühendislik  
**KULLANICI ROLÜ:** IT Admin  
**OLAY:** IT Admin, CFO adına dahili chat üzerinden gelen "hemen erişim aç" mesajına güvenerek geçici kullanıcıya muhasebe klasörü yetkisi verir; daha sonra mesajın CFO'nun açık kalan toplantı odası oturumundan gönderildiği anlaşılır.  
**NEDEN ŞÜPHELİ:** Yönetici hesabından olağandışı kanal kullanımı, aciliyet ve yetki değişikliği kombinasyonu.  
**NORMAL BASELINE'DAN SAPMA:** CFO normalde erişim talebini ticket sistemiyle iletirken olayda ilk kez chat üzerinden ve gece 21:40'ta talep gelmiş.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-077: Hukuk Ekibine CFO Adına Gelen Sahte İç Mail

**KATEGORİ:** sosyal mühendislik  
**KULLANICI ROLÜ:** Hukuk  
**OLAY:** Hukuk çalışanı, CFO'dan gelmiş gibi görünen ama şirket içi mail sunucusunda farklı bir istemci imzası taşıyan bir dahili mail alır. Mail, sözleşme klasörlerinin acil paylaşılmasını ister.  
**NEDEN ŞÜPHELİ:** İç mail sahteciliği, anormal istemci izi ve aciliyet dili birlikte sosyal mühendislik göstergesi.  
**NORMAL BASELINE'DAN SAPMA:** CFO iç maillerinin %95'i tek cihazdan gelirken bu iletide ilk kez farklı workstation kimliği görülmüş.  
**BEKLENED SEVERITY:** ALERT

---

### S-078: Sosyal Mühendislik Tuzağına Düşen Yeni Başlayan

**KATEGORİ:** sosyal mühendislik  
**KULLANICI ROLÜ:** Destek Personeli  
**OLAY:** Şirkete yeni giren destek personeli, iç mailden gelen "IT Şifre Yenileme" görünümlü (aslında ele geçirilmiş başka bir çalışandan gelen) linke tıklayıp kimlik bilgilerini iç ağdaki sahte bir portala giriyor.  
**NEDEN ŞÜPHELİ:** İç ağdaki güvenilmeyen bir IP adresine hassas form verisi gönderimi.  
**NORMAL BASELINE'DAN SAPMA:** Yeni kullanıcının anormal HTTP POST aktivitesi; formun hedef IP'si bilinmeyen.  
**BEKLENED SEVERITY:** ALERT

---

### S-079: Tüm Şirkete Sahte CEO İstifa Maili

**KATEGORİ:** sosyal mühendislik  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK personelinin hesabı kullanılarak tüm şirkete "CEO'muz istifa etmiştir, detaylar ektedir" şeklinde sahte bir iç mail atılıyor.  
**NEDEN ŞÜPHELİ:** Mail dili ve üslubu normal İK kurumsal iletişim baseline'ından sapma; panik dili ve aciliyet; hesap ele geçirilmiş.  
**NORMAL BASELINE'DAN SAPMA:** İK hesabından tüm-şirket dağıtım listesine mail: ilk kez ve gece saatinde.  
**BEKLENED SEVERITY:** CRITICAL

---

## Çapraz/Multi-User Korelasyon

---

### S-080: Çok Kaynaklı Kademeli İhlal Simülasyonu

**KATEGORİ:** çapraz/multi-user  
**KULLANICI ROLÜ:** IT Admin (zincir lider)  
**OLAY:** Önce stajyer yanlışlıkla ortak credential'ı wiki'ye koyar, sonra geliştirici bunu görüp test API'sine girer, ardından IT Admin anomaliyi gizlemek için log ayarlarını değiştirir; son aşamada satış çalışanı müşteri export'u yapar.  
**NEDEN ŞÜPHELİ:** Birden çok düşük ve orta seviye olayın birbirini tetikleyerek tam ölçekli ihlale dönüşmesi; 4 farklı departman aktörü.  
**NORMAL BASELINE'DAN SAPMA:** Tekil olarak sıradan görünen olaylar, 24 saat içinde birbirine bağlı 4 aktörle korele.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-081: Çoklu Departman Zincirli Fiziksel-Dijital Saldırı

**KATEGORİ:** çapraz/multi-user  
**KULLANICI ROLÜ:** Güvenlik Görevlisi (zincir başlangıcı)  
**OLAY:** Güvenlik görevlisi sunucu odasına doğrulanmamış bakım ekibini alır; kısa süre sonra IT Admin hesabından hukuk ve finans sistemlerine erişim başlar; ardından destek personeli cihazından log temizleme denenir.  
**NEDEN ŞÜPHELİ:** Fiziksel olay + yüksek ayrıcalıklı erişim + çapraz departman hedefleme + delil temizleme tek zincirde 40 dakikada birleşmiş.  
**NORMAL BASELINE'DAN SAPMA:** Bu üç olay tipi normalde birbirinden bağımsızken burada korele şekilde gerçekleşmiş.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-082: İK ve Bilgi İşlem Çapraz Hesap Manipülasyonu

**KATEGORİ:** çapraz/multi-user  
**KULLANICI ROLÜ:** İK  
**OLAY:** İK personeli, bir IT Admin ile iş birliği yaparak işten çıkarılacak olan bir yazılımcının hesabının şifresini habersizce değiştiriyor ve hesaba İK bilgisayarından erişerek eski maillerini siliyor.  
**NEDEN ŞÜPHELİ:** Hesap şifresi olağan dışı şekilde sıfırlanmış ve hemen ardından farklı departman IP'sinden oturum açılmış.  
**NORMAL BASELINE'DAN SAPMA:** Eş zamanlı hesap değişim ve lokasyon sapma anomalisi; kollusyon pattern.  
**BEKLENED SEVERITY:** CRITICAL

---

### S-083: Aynı Dosyaya Zincirleme Çapraz Departman Erişimi

**KATEGORİ:** çapraz/multi-user  
**KULLANICI ROLÜ:** Satış + Hukuk  
**OLAY:** Satış temsilcisi gizlilik sözleşmesi dosyasını indirir; 10 dakika sonra aynı dosyaya hukuk departmanından farklı bir kullanıcı erişir; akabinde dosya üçüncü kez yeniden adlandırılmış şekilde başka bir paylaşımda görülür.  
**NEDEN ŞÜPHELİ:** Aynı hassas dosyanın kısa sürede farklı departman kullanıcılarından geçmesi; collusion veya zincirleme veri toplama.  
**NORMAL BASELINE'DAN SAPMA:** Tek dosyaya 3 kullanıcı / farklı departman / 30 dakika penceresi: baseline'da hiç görülmemiş.  
**BEKLENED SEVERITY:** ALERT

---

*Bu kütüphane Watchtower UEBA simülasyon ortamında test edilecek anormal davranış setini kapsar. Her senaryo için log üretimi, severity doğrulaması ve LangGraph pipeline korelasyonu test edilecektir.*
