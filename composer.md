# Watchtower UEBA — Simülasyon Test Senaryoları

Toplam: **174** senaryo | İç ağ (private LAN) only | 35 çalışan profili

Kategoriler: veri sızdırma, yetkisiz erişim, insider threat, credential ihlali,
dış saldırı desteği, kazara ihlal, politika ihlali, diğer

---

## 1. Gece Yedek Çekimi

**SENARYO ADI:** Gece Yedek Çekimi
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Muhasebe çalışanı normalde gündüz 200-400 MB finans sunucusundan rapor çekerken Cuma 23:47'de aynı sunucudan 18.4 GB toplu dosya indiriyor; arşiv (.zip) ve CSV paketleri.
**NEDEN ŞÜPHELİ:** Rol için olağandışı saat, tek oturumda 45x veri hacmi, arşiv formatı toplu dışa aktarım paterni.
**NORMAL BASELINE'DAN SAPMA:** Günlük ort. 320 MB → 18.4 GB; saat 09-18 dışı ilk kez.
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** İşten ayrılma öncesi veya rakibe veri taşıma girişimlerinde sık görülür.

---

## 2. USB Toplu Kopya

**SENARYO ADI:** USB Toplu Kopya
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış temsilcisi CRM sunucusundan 2.1 GB veriyi 14 dakikada USB'ye kopyalıyor.
**NEDEN ŞÜPHELİ:** Satışta USB yasak; CRM toplu okuma + USB yazma korelasyonu.
**NORMAL BASELINE'DAN SAPMA:** USB: ayda 0-1 → 2.1 GB tek sefer.
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Fuar öncesi offline sunum.

---

## 3. Payroll Dump

**SENARYO ADI:** Payroll Dump
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** İK
**OLAY:** İK uzmanı payroll-db'den tüm maaş tablosunu 890 MB SQL export ile indiriyor.
**NEDEN ŞÜPHELİ:** Tam tablo export; normal iş akışı tek çalışan sorgusu.
**NORMAL BASELINE'DAN SAPMA:** Ort. 2-5 MB → 890 MB.
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Maaş bilgisi sızdırma/şantaj.

---

## 4. Kaynak Kod Arşivi

**SENARYO ADI:** Kaynak Kod Arşivi
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Geliştirici git-mirror'dan 4.7 GB tüm repo ağacı çekiyor; projesi tek microservice.
**NEDEN ŞÜPHELİ:** Yetkili repo dışı tüm branch çekimi; hafta sonu.
**NORMAL BASELINE'DAN SAPMA:** 150 MB/hafta → 4.7 GB; repo 1→47.
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Ayrılış öncesi IP biriktirme.

---

## 5. Hukuk Dava Arşivi

**SENARYO ADI:** Hukuk Dava Arşivi
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Hukuk
**OLAY:** Hukuk danışmanı dava-arsiv'ten 120 PDF'i ZIP ile 3.2 GB indiriyor.
**NEDEN ŞÜPHELİ:** Toplu indirme; müşteri kodlu dosya adları.
**NORMAL BASELINE'DAN SAPMA:** 5-10 dosya/gün → 120 dosya.
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Mahkeme hazırlığı meşru olabilir.

---

## 6. BI Ham PII Export

**SENARYO ADI:** BI Ham PII Export
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Analist DWH'den ham müşteri PII ile 12 GB parquet export alıyor.
**NEDEN ŞÜPHELİ:** Dashboard sorgusu 50-200 MB; ham PII export nadir.
**NORMAL BASELINE'DAN SAPMA:** 12 GB vs ort. 180 MB.
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Yanlış tüm veri seçimi.

---

## 7. Stajyer CRM Export

**SENARYO ADI:** Stajyer CRM Export
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer 2. haftada CRM'den 45.000 satır müşteri kaydını Excel'e aktarıyor (220 MB).
**NEDEN ŞÜPHELİ:** Stajyer yetkisi demo ortamı; prod export yok.
**NORMAL BASELINE'DAN SAPMA:** İlk CRM export; 9x satır üst sınır.
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Görev yanlış anlaşılması.

---

## 8. CFO USB Kopya

**SENARYO ADI:** CFO USB Kopya
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CFO
**OLAY:** CFO bütçe sunucusundan 1.8 GB indirip ardından USB'ye kopyalıyor.
**NEDEN ŞÜPHELİ:** İndirme meşru; USB CFO baseline'ında yılda 0.
**NORMAL BASELINE'DAN SAPMA:** USB olayı: 0 → 1.8 GB.
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** YK sunumu + politika ihlali.

---

## 9. Destek Ticket PII

**SENARYO ADI:** Destek Ticket PII
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Destek attachment store'dan 800 ticket ekini 6.1 GB zip'liyor.
**NEDEN ŞÜPHELİ:** Kimlik fotokopisi ve ekran görüntüsü içerebilir.
**NORMAL BASELINE'DAN SAPMA:** 50 MB/gün → 6.1 GB.
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Yedekleme bahanesi.

---

## 10. Admin Yanlış VM

**SENARYO ADI:** Admin Yanlış VM
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Admin prod-HR VM snapshot'ını workstation'a 90 GB çekiyor.
**NEDEN ŞÜPHELİ:** Hedef workstation; backup job dışı saat.
**NORMAL BASELINE'DAN SAPMA:** Tek sefer 90 GB.
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Operasyon hatası.

---

## 11. LDAP Bulk Bind

**SENARYO ADI:** LDAP Bulk Bind
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** SOC analisti prod ldap-replica'ya test bind ile 12.000 auth/dk üretiyor.
**NEDEN ŞÜPHELİ:** Test prod'da; rate limit aşımı.
**NORMAL BASELINE'DAN SAPMA:** 50 → 12.000 auth/dk
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Pen test unutulmuş.

---

## 12. Deploy Key 3 IP

**SENARYO ADI:** Deploy Key 3 IP
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** svc-deploy API key 3 farklı workstation IP'den kullanılıyor.
**NEDEN ŞÜPHELİ:** Key tek makineye bağlı olmalı.
**NORMAL BASELINE'DAN SAPMA:** Kaynak IP: 1 → 3
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Slack'te key paylaşımı.

---

## 13. Stajyer Çift Oturum

**SENARYO ADI:** Stajyer Çift Oturum
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer hesabı aynı anda 2 workstation'da aktif; biri mentor masası değil.
**NEDEN ŞÜPHELİ:** Hesap paylaşımı.
**NORMAL BASELINE'DAN SAPMA:** Eşzamanlı oturum: 2 host
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Mentor şifre vermiş.

---

## 14. CEO Asistan İK

**SENARYO ADI:** CEO Asistan İK
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** CEO
**OLAY:** CEO hesabı İK sunucusuna erişiyor; session fingerprint asistan PC.
**NEDEN ŞÜPHELİ:** İmpersonation riski.
**NORMAL BASELINE'DAN SAPMA:** CEO→İK: yılda 0
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Asistan devri.

---

## 15. Gece Admin TGT

**SENARYO ADI:** Gece Admin TGT
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Admin hesabından 02:00'de 8 sunucuya ardışık Kerberos TGT.
**NEDEN ŞÜPHELİ:** Lateral movement işareti.
**NORMAL BASELINE'DAN SAPMA:** Gece TGT: 0 → 8
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** PtH sonrası.

---

## 16. Jira Key Bulk

**SENARYO ADI:** Jira Key Bulk
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** Read-only Jira key ile gece 40.000 issue API çağrısı.
**NEDEN ŞÜPHELİ:** Read-only ile bulk export.
**NORMAL BASELINE'DAN SAPMA:** 200/gün → 40.000
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Rapor scripti.

---

## 17. Paylaşılan RDP

**SENARYO ADI:** Paylaşılan RDP
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Muhasebe kullanıcısı başka departman PC'sine RDP; kendi şifresiyle ikinci oturum.
**NEDEN ŞÜPHELİ:** Credential sharing.
**NORMAL BASELINE'DAN SAPMA:** RDP hedef: 0 → 3 farklı host/hafta
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Acil fatura onayı.

---

## 18. Token Vault Dump

**SENARYO ADI:** Token Vault Dump
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Admin iç HashiCorp Vault audit'te 200 secret read; bakım penceresi dışı.
**NEDEN ŞÜPHELİ:** Secret enumeration.
**NORMAL BASELINE'DAN SAPMA:** Vault read: 5/gün → 200
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Compromise veya kötü niyet.

---

## 19. Stajyer Mentor ADUC

**SENARYO ADI:** Stajyer Mentor ADUC
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer RDP ile mentor PC'den ADUC açıyor.
**NEDEN ŞÜPHELİ:** Paylaşılan credential.
**NORMAL BASELINE'DAN SAPMA:** RDP mentor: 0
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Eğitim kötü uygulama.

---

## 20. CFO Asistan Mail

**SENARYO ADI:** CFO Asistan Mail
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** CFO
**OLAY:** CFO mailbox'tan toplu mail silme; client IP asistan subnet.
**NEDEN ŞÜPHELİ:** Yetki devri ihlali.
**NORMAL BASELINE'DAN SAPMA:** Toplu silme: 0
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Temizlik talebi.

---

## 21. Satış ERP Erişim

**SENARYO ADI:** Satış ERP Erişim
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış rep finans-erp'ye RDP; fatura modülü açık.
**NEDEN ŞÜPHELİ:** Satış grubunda ERP yok.
**NORMAL BASELINE'DAN SAPMA:** İlk ERP erişim
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Komisyon araştırması.

---

## 22. Junior Prod DB

**SENARYO ADI:** Junior Prod DB
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Junior dev prod-db-01 SSMS SELECT *.
**NEDEN ŞÜPHELİ:** Prod sadece DBA.
**NORMAL BASELINE'DAN SAPMA:** Prod: 0
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Bug fix bahanesi.

---

## 23. Hukuk Performans

**SENARYO ADI:** Hukuk Performans
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Hukuk
**OLAY:** Hukuk performans-değerlendirme share'ine erişiyor.
**NEDEN ŞÜPHELİ:** Dava dışı HR.
**NORMAL BASELINE'DAN SAPMA:** İlk erişim
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** İş davası.

---

## 24. Muhasebe DA Deneme

**SENARYO ADI:** Muhasebe DA Deneme
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Domain Admin grubuna ekleme denemesi başarısız.
**NEDEN ŞÜPHELİ:** Privilege escalation.
**NORMAL BASELINE'DAN SAPMA:** AD write: 0
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Phishing sonrası.

---

## 25. PM SIEM Konsol

**SENARYO ADI:** PM SIEM Konsol
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** PM SIEM web konsoluna login.
**NEDEN ŞÜPHELİ:** SOC rolü yok.
**NORMAL BASELINE'DAN SAPMA:** İlk SIEM
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Proje inceleme.

---

## 26. Stajyer Get-ADUser

**SENARYO ADI:** Stajyer Get-ADUser
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Stajyer
**OLAY:** PowerShell Get-ADUser -Filter *.
**NEDEN ŞÜPHELİ:** AD okuma yok.
**NORMAL BASELINE'DAN SAPMA:** Cmdlet: 0
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Tutorial.

---

## 27. CFO Git Gezinme

**SENARYO ADI:** CFO Git Gezinme
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** CFO
**OLAY:** CFO git-internal'da repo listesi geziyor.
**NEDEN ŞÜPHELİ:** C-level kod erişimi yok.
**NORMAL BASELINE'DAN SAPMA:** İlk git
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Yanlış link.

---

## 28. Destek DC RDP

**SENARYO ADI:** Destek DC RDP
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Şifre reset için DC'ye RDP.
**NEDEN ŞÜPHELİ:** DC sadece IT Admin.
**NORMAL BASELINE'DAN SAPMA:** DC RDP: 0
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Yanlış prosedür.

---

## 29. Veri Analisti Prod

**SENARYO ADI:** Veri Analisti Prod
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Analist prod-ml-feature store'a write.
**NEDEN ŞÜPHELİ:** Prod write yasak.
**NORMAL BASELINE'DAN SAPMA:** Write: 0
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Model güncelleme.

---

## 30. İK Finans Modül

**SENARYO ADI:** İK Finans Modül
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** İK
**OLAY:** İK çalışanı finans onay modülünde bekleyen ödemeleri görüntülüyor.
**NEDEN ŞÜPHELİ:** Çapraz yetki yok.
**NORMAL BASELINE'DAN SAPMA:** Finans modül: 0
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Bordro uyumsuzluğu araştırması.

---

## 31. CTO HR Backup

**SENARYO ADI:** CTO HR Backup
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** CTO
**OLAY:** CTO hr-backup share'ine yazma denemesi.
**NEDEN ŞÜPHELİ:** CTO HR write yok.
**NORMAL BASELINE'DAN SAPMA:** Write deneme
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Yanlış klasör.

---

## 32. Ayrılış Ramp

**SENARYO ADI:** Ayrılış Ramp
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** İstifadan 5 gün önce günlük çekim 200 MB→3 GB.
**NEDEN ŞÜPHELİ:** Offboarding pattern.
**NORMAL BASELINE'DAN SAPMA:** 5 gün artış
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Klasik insider.

---

## 33. İK Disiplin Tarama

**SENARYO ADI:** İK Disiplin Tarama
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** İK
**OLAY:** İK 12 çalışanın disiplin kaydına bakıyor.
**NEDEN ŞÜPHELİ:** Need-to-know.
**NORMAL BASELINE'DAN SAPMA:** 12 profil
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Dedikodu.

---

## 34. Satış Segment Model

**SENARYO ADI:** Satış Segment Model
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Satış
**OLAY:** Ayrılan rep müşteri segmentasyon modeline 3 gün erişiyor.
**NEDEN ŞÜPHELİ:** Rakip verisi.
**NORMAL BASELINE'DAN SAPMA:** Model+ayrılış
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Headhunter.

---

## 35. Shadow Admin

**SENARYO ADI:** Shadow Admin
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Yeni local admin svc_monitor; change ticket yok.
**NEDEN ŞÜPHELİ:** Shadow account.
**NORMAL BASELINE'DAN SAPMA:** Yeni hesap
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Kalıcı erişim.

---

## 36. Sahte Tedarikçi IBAN

**SENARYO ADI:** Sahte Tedarikçi IBAN
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Tedarikçi master'da onaysız IBAN değişikliği.
**NEDEN ŞÜPHELİ:** Fraud.
**NORMAL BASELINE'DAN SAPMA:** Onaysız write
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Vendor fraud.

---

## 37. SOC Log Suppress

**SENARYO ADI:** SOC Log Suppress
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** SOC kendi host için SIEM suppress rule ekliyor.
**NEDEN ŞÜPHELİ:** Anti-forensics.
**NORMAL BASELINE'DAN SAPMA:** Self suppress
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Kendi ihlali.

---

## 38. PM Maliyet Gizleme

**SENARYO ADI:** PM Maliyet Gizleme
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** Proje maliyet tablosunda 50 hücre toplu güncelleme.
**NEDEN ŞÜPHELİ:** Yetkisiz finans write.
**NORMAL BASELINE'DAN SAPMA:** 50x write
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Bütçe manipülasyon.

---

## 39. ML Model Hırsızlık

**SENARYO ADI:** ML Model Hırsızlık
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** ML artifact 2.3 GB indirme; export policy ihlal.
**NEDEN ŞÜPHELİ:** IP hırsızlığı.
**NORMAL BASELINE'DAN SAPMA:** Export: 0
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Yan iş.

---

## 40. CEO Asistan Strateji

**SENARYO ADI:** CEO Asistan Strateji
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** CEO
**OLAY:** Asistan CEO mailinden strateji ekleri toplu forward iç kullanıcıya.
**NEDEN ŞÜPHELİ:** Veri minimizasyonu.
**NORMAL BASELINE'DAN SAPMA:** Toplu forward: 0
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Hız için prosedür atlandı.

---

## 41. Stajyer Sınav Cevapları

**SENARYO ADI:** Stajyer Sınav Cevapları
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer eğitim sunucusundan sınav bankası indiriyor.
**NEDEN ŞÜPHELİ:** Yetkisiz eğitim verisi.
**NORMAL BASELINE'DAN SAPMA:** İlk erişim
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Arkadaşa paylaşım.

---

## 42. İç Spear Phishing

**SENARYO ADI:** İç Spear Phishing
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** İç Exchange'den 'Acil şifre yenile' linki; fake-sso credential girişi.
**NEDEN ŞÜPHELİ:** Harvesting iç mail.
**NORMAL BASELINE'DAN SAPMA:** Fake SSO login
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Spear phishing.

---

## 43. SMB Yayılma

**SENARYO ADI:** SMB Yayılma
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** 15 dk'da 40 host SMB445 tarama.
**NEDEN ŞÜPHELİ:** Lateral spread.
**NORMAL BASELINE'DAN SAPMA:** SMB: 2 → 40
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Worm/APT.

---

## 44. Pass-the-Hash

**SENARYO ADI:** Pass-the-Hash
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Tek host'tan admin hash ile 6 sunucu PSRemoting.
**NEDEN ŞÜPHELİ:** PtH.
**NORMAL BASELINE'DAN SAPMA:** PSRemoting burst
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Mimikatz.

---

## 45. İç DNS TXT

**SENARYO ADI:** İç DNS TXT
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** İç DNS'e anormal TXT sorgu hacmi.
**NEDEN ŞÜPHELİ:** DNS exfil.
**NORMAL BASELINE'DAN SAPMA:** TXT 500x
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** C2.

---

## 46. Stajyer Macro

**SENARYO ADI:** Stajyer Macro
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Stajyer
**OLAY:** İç mail Word macro; ardından LDAP enum.
**NEDEN ŞÜPHELİ:** Malware zinciri.
**NORMAL BASELINE'DAN SAPMA:** Macro+LDAP
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Fatura macro.

---

## 47. Satış Fake IT

**SENARYO ADI:** Satış Fake IT
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Satış
**OLAY:** Teams'te sahte IT hesabına OTP kodu gönderildi (iç).
**NEDEN ŞÜPHELİ:** Sosyal mühendislik.
**NORMAL BASELINE'DAN SAPMA:** OTP paylaşım
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Helpdesk taklidi.

---

## 48. Printer Spooler

**SENARYO ADI:** Printer Spooler
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Print-nightmare exploit iç print server'dan SYSTEM denemesi.
**NEDEN ŞÜPHELİ:** Exploit iç ağ.
**NORMAL BASELINE'DAN SAPMA:** Spooler RPC spike
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Unpatched print.

---

## 49. Güvenlik Tool İndirme

**SENARYO ADI:** Güvenlik Tool İndirme
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** İç file server'dan bilinmeyen .exe (mimikatz benzeri hash).
**NEDEN ŞÜPHELİ:** Malware hash.
**NORMAL BASELINE'DAN SAPMA:** Yeni binary
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Kırmızı takım artefaktı kaldı.

---

## 50. Reply-All Fiyat

**SENARYO ADI:** Reply-All Fiyat
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Satış
**OLAY:** Tüm şirket DL'sine müşteri fiyat listesi eki.
**NEDEN ŞÜPHELİ:** İç mail sızıntı.
**NORMAL BASELINE'DAN SAPMA:** All-staff+ek
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Reply-all.

---

## 51. Prod INSERT

**SENARYO ADI:** Prod INSERT
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Test script prod HR DB INSERT.
**NEDEN ŞÜPHELİ:** Prod yazma hatası.
**NORMAL BASELINE'DAN SAPMA:** INSERT: 0
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Connection string.

---

## 52. Everyone ACL

**SENARYO ADI:** Everyone ACL
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** File server'da everyone read ACL.
**NEDEN ŞÜPHELİ:** Over-permission.
**NORMAL BASELINE'DAN SAPMA:** ACL everyone
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Hızlı paylaşım.

---

## 53. CEO USB Autorun

**SENARYO ADI:** CEO USB Autorun
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** CEO
**OLAY:** CEO USB; AV autorun alert.
**NEDEN ŞÜPHELİ:** Malware giriş.
**NORMAL BASELINE'DAN SAPMA:** USB nadir
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Konferans USB.

---

## 54. Açık Oturum Muhasebe

**SENARYO ADI:** Açık Oturum Muhasebe
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Paylaşılan PC'de başka oturum açık; muhasebe devam ediyor.
**NEDEN ŞÜPHELİ:** Session overlap.
**NORMAL BASELINE'DAN SAPMA:** Overlap
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Temizlik.

---

## 55. Admin rm Typo

**SENARYO ADI:** Admin rm Typo
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Backup script yanlış path 200 GB silme.
**NEDEN ŞÜPHELİ:** Destructive.
**NORMAL BASELINE'DAN SAPMA:** Delete spike
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** rm typo.

---

## 56. İK Yanlış Ek

**SENARYO ADI:** İK Yanlış Ek
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** İK
**OLAY:** İş sözleşmesi taslağı yanlışlıkla tüm-hands iç mail.
**NEDEN ŞÜPHELİ:** HR veri leak.
**NORMAL BASELINE'DAN SAPMA:** All-hands HR
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Autocomplete.

---

## 57. Destek Müşteri CC

**SENARYO ADI:** Destek Müşteri CC
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Ticket yanıtında iç not yerine müşteri PII iç ağ mailine yapıştırıldı.
**NEDEN ŞÜPHELİ:** Yanlış kanal.
**NORMAL BASELINE'DAN SAPMA:** PII iç mail
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Kopyala-yapıştır.

---

## 58. Steam 4 Saat

**SENARYO ADI:** Steam 4 Saat
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** İş istasyonunda Steam 4 saat process.
**NEDEN ŞÜPHELİ:** Acceptable use.
**NORMAL BASELINE'DAN SAPMA:** Steam 4h
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Mola oyunu.

---

## 59. Mail Forward Kural

**SENARYO ADI:** Mail Forward Kural
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** İK
**OLAY:** İç mailbox forward kuralı kişisel iç mailbox'a.
**NEDEN ŞÜPHELİ:** Mail policy.
**NORMAL BASELINE'DAN SAPMA:** Yeni kural
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Evden okuma.

---

## 60. Dual NIC Bypass

**SENARYO ADI:** Dual NIC Bypass
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Satış
**OLAY:** İkinci NIC ile doğrudan file server.
**NEDEN ŞÜPHELİ:** Segment bypass.
**NORMAL BASELINE'DAN SAPMA:** Dual NIC
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Hız.

---

## 61. DLP Disable

**SENARYO ADI:** DLP Disable
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Stajyer
**OLAY:** DLP agent 2 saat disabled.
**NEDEN ŞÜPHELİ:** Tamper.
**NORMAL BASELINE'DAN SAPMA:** DLP stop
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** False positive korkusu.

---

## 62. Crack Matlab

**SENARYO ADI:** Crack Matlab
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Lisanssız Matlab crack installer.
**NEDEN ŞÜPHELİ:** Software policy.
**NORMAL BASELINE'DAN SAPMA:** Crack
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Lisans maliyeti.

---

## 63. Kişisel Cloud Sync

**SENARYO ADI:** Kişisel Cloud Sync
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Satış
**OLAY:** OneDrive sync client kurulum denemesi (iç policy blok).
**NEDEN ŞÜPHELİ:** Dış sync yasak.
**NORMAL BASELINE'DAN SAPMA:** Client install
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Yedek alışkanlığı.

---

## 64. Hukuk Torrent

**SENARYO ADI:** Hukuk Torrent
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Hukuk
**OLAY:** İç ağda BitTorrent benzeri P2P port dinleme (torrent değil update araç).
**NEDEN ŞÜPHELİ:** P2P yasak.
**NORMAL BASELINE'DAN SAPMA:** Port 6881
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Yanlış araç.

---

## 65. İK+Muhasebe Collusion

**SENARYO ADI:** İK+Muhasebe Collusion
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Muhasebe+İK aynı dakikada aynı tedarikçi kaydı değişiyor.
**NEDEN ŞÜPHELİ:** Collusion.
**NORMAL BASELINE'DAN SAPMA:** 2 user 1 record
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** İki kişi bypass.

---

## 66. Satış→Hukuk Dosya

**SENARYO ADI:** Satış→Hukuk Dosya
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış indiriyor; 10 dk sonra Hukuk aynı dosya.
**NEDEN ŞÜPHELİ:** Zincir transfer.
**NORMAL BASELINE'DAN SAPMA:** Sıralı erişim
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Ortaklık veya sızıntı.

---

## 67. Dev Deploy SoD

**SENARYO ADI:** Dev Deploy SoD
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Prod deploy manual trigger; IT onay yok.
**NEDEN ŞÜPHELİ:** SoD.
**NORMAL BASELINE'DAN SAPMA:** Deploy no ticket
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Cuma baskısı.

---

## 68. CTO+CFO Gece

**SENARYO ADI:** CTO+CFO Gece
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** CTO
**OLAY:** CTO+CFO gece strateji sunucusu.
**NEDEN ŞÜPHELİ:** Koordinasyon.
**NORMAL BASELINE'DAN SAPMA:** Dual C-level
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Board.

---

## 69. SOC+IT Incident

**SENARYO ADI:** SOC+IT Incident
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** SOC+IT log sunucusuna write.
**NEDEN ŞÜPHELİ:** IR koordinasyon.
**NORMAL BASELINE'DAN SAPMA:** Dual write
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Incident.

---

## 70. PM+Dev Export

**SENARYO ADI:** PM+Dev Export
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** PM Jira export + dev git clone aynı proje saat.
**NEDEN ŞÜPHELİ:** Proje kapanış.
**NORMAL BASELINE'DAN SAPMA:** Correlated
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Teslim.

---

## 71. Destek CRM PCI

**SENARYO ADI:** Destek CRM PCI
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** CRM kredi kartı alanı görüntüleme.
**NEDEN ŞÜPHELİ:** PCI.
**NORMAL BASELINE'DAN SAPMA:** CC view
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Gereksiz.

---

## 72. İK Satış Komisyon

**SENARYO ADI:** İK Satış Komisyon
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** İK
**OLAY:** İK satış komisyon tablosuna erişiyor; satış müdürü habersiz.
**NEDEN ŞÜPHELİ:** Çapraz HR-finans.
**NORMAL BASELINE'DAN SAPMA:** İlk komisyon erişim
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Şikayet araştırması.

---

## 73. Muhasebe Gece ERP

**SENARYO ADI:** Muhasebe Gece ERP
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Pazar 01:12'de ERP'den 5 yıllık genel muhasebe defteri 4.2 GB export.
**NEDEN ŞÜPHELİ:** Hafta sonu gece; tam defter export.
**NORMAL BASELINE'DAN SAPMA:** Saat+ hacim 20x
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Yıl kapanışı kopyası.

---

## 74. Satış Pipeline Dump

**SENARYO ADI:** Satış Pipeline Dump
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış pipeline DB'den tüm fırsatlar+marj 1.1 GB; normal günlük 15 MB dashboard.
**NEDEN ŞÜPHELİ:** Marj verisi toplu.
**NORMAL BASELINE'DAN SAPMA:** 1.1 GB vs 15 MB
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Rakip işe geçiş.

---

## 75. Güvenlik IOC List

**SENARYO ADI:** Güvenlik IOC List
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** SOC threat-intel share'den 600 MB IOC paketi USB'ye.
**NEDEN ŞÜPHELİ:** SOC USB nadir; IOC dışarı değerli.
**NORMAL BASELINE'DAN SAPMA:** USB 600 MB
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Konferans sunumu.

---

## 76. Proje Yöneticisi SOW

**SENARYO ADI:** Proje Yöneticisi SOW
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** Tüm aktif SOW ve teklif PDF'leri 2.8 GB tek sefer.
**NEDEN ŞÜPHELİ:** Müşteri fiyatları içerir.
**NORMAL BASELINE'DAN SAPMA:** 50 dosya vs 3
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Taşeron paylaşımı.

---

## 77. Destek Şifre Reset Log

**SENARYO ADI:** Destek Şifre Reset Log
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** 1 saatte 35 kullanıcı şifre reset; normal 3-5.
**NEDEN ŞÜPHELİ:** Account takeover hazırlığı.
**NORMAL BASELINE'DAN SAPMA:** Reset: 5 → 35
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Sosyal mühendislik sonrası.

---

## 78. CTO API Key Rotate

**SENARYO ADI:** CTO API Key Rotate
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** CTO
**OLAY:** CTO tech-radar API key eski key ile hâlâ 200 call; rotate sonrası.
**NEDEN ŞÜPHELİ:** Rotate sonrası eski key.
**NORMAL BASELINE'DAN SAPMA:** Eski key aktif
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Otomasyon güncellenmemiş.

---

## 79. İK Bordro Toplu Mail

**SENARYO ADI:** İK Bordro Toplu Mail
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** İK
**OLAY:** Bordro ekleri yanlış departman DL'sine.
**NEDEN ŞÜPHELİ:** Maaş leak.
**NORMAL BASELINE'DAN SAPMA:** DL yanlış
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Outlook autocomplete.

---

## 80. Yazılım Secrets Repo

**SENARYO ADI:** Yazılım Secrets Repo
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** secrets-repo'dan 40 .env dosyası indirme.
**NEDEN ŞÜPHELİ:** Credential dosyaları.
**NORMAL BASELINE'DAN SAPMA:** 40 dosya
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Acil prod fix.

---

## 81. CFO Tax Audit Pack

**SENARYO ADI:** CFO Tax Audit Pack
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CFO
**OLAY:** Vergi denetim paketi 6 GB indirme meşru; ardından yazdırma kuyruğu 4000 sayfa.
**NEDEN ŞÜPHELİ:** Fiziksel exfil riski.
**NORMAL BASELINE'DAN SAPMA:** Print spike
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Denetim meşru.

---

## 82. Stajyer SharePoint

**SENARYO ADI:** Stajyer SharePoint
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer yönetim kurulu SharePoint library browse.
**NEDEN ŞÜPHELİ:** Board library yasak.
**NORMAL BASELINE'DAN SAPMA:** İlk erişim
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Link paylaşıldı.

---

## 83. IT Admin GPO Değişik

**SENARYO ADI:** IT Admin GPO Değişik
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** IT Admin
**OLAY:** USB disable GPO devre dışı; change yok.
**NEDEN ŞÜPHELİ:** Policy weaken.
**NORMAL BASELINE'DAN SAPMA:** GPO change
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Kendi exfil için.

---

## 84. Muhasebe Çift Onay Bypass

**SENARYO ADI:** Muhasebe Çift Onay Bypass
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** 50.000 TL üzeri ödeme tek onayla geçirilmiş.
**NEDEN ŞÜPHELİ:** SoD ihlali.
**NORMAL BASELINE'DAN SAPMA:** Tek onay
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Fraud.

---

## 85. Satış İç Rakip Mail

**SENARYO ADI:** Satış İç Rakip Mail
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış iç mailde rakip firma adı+teklif detayı forward.
**NEDEN ŞÜPHELİ:** Rekabet ihlali.
**NORMAL BASELINE'DAN SAPMA:** Rakip keyword
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Müşteri şikayeti.

---

## 86. Hukuk Privileged Mail

**SENARYO ADI:** Hukuk Privileged Mail
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Hukuk
**OLAY:** Attorney-client privileged klasör 1.5 GB indirme.
**NEDEN ŞÜPHELİ:** Ayrıcalıklı içerik toplu.
**NORMAL BASELINE'DAN SAPMA:** 1.5 GB
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Dış hukuk bürosu.

---

## 87. Veri Analisti Maskesiz

**SENARYO ADI:** Veri Analisti Maskesiz
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** DWH sorgusunda PII mask kaldırılmış kolonlar.
**NEDEN ŞÜPHELİ:** Mask bypass.
**NORMAL BASELINE'DAN SAPMA:** Mask off
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Analiz kolaylığı.

---

## 88. CEO Takvim Export

**SENARYO ADI:** CEO Takvim Export
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CEO
**OLAY:** CEO Exchange takvim 3 yıl .ics export 40 MB.
**NEDEN ŞÜPHELİ:** Strateji toplantıları.
**NORMAL BASELINE'DAN SAPMA:** İlk export
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Asistan yedek.

---

## 89. Güvenlik Yanlış Quarantine

**SENARYO ADI:** Güvenlik Yanlış Quarantine
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** SOC yanlışlıkla finans batch dosyasını quarantine.
**NEDEN ŞÜPHELİ:** İş kesintisi.
**NORMAL BASELINE'DAN SAPMA:** False positive
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** İmzası benzer malware.

---

## 90. Destek RDP Müşteri

**SENARYO ADI:** Destek RDP Müşteri
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Müşteri demo için uzun süre ekran paylaşım kaydı iç sunucuda.
**NEDEN ŞÜPHELİ:** Kayıt policy.
**NORMAL BASELINE'DAN SAPMA:** 8 saat kayıt
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Eğitim videosu.

---

## 91. PM Jira Admin

**SENARYO ADI:** PM Jira Admin
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** PM Jira admin panelinde kullanıcı silme denemesi.
**NEDEN ŞÜPHELİ:** Admin yetkisi yok.
**NORMAL BASELINE'DAN SAPMA:** Delete user
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Temizlik.

---

## 92. Yazılım CI Token

**SENARYO ADI:** Yazılım CI Token
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** CI token ile artifact registry'den 30 container image pull gece.
**NEDEN ŞÜPHELİ:** Gece toplu pull.
**NORMAL BASELINE'DAN SAPMA:** 30 image
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Yerel test.

---

## 93. İK Sağlık Verisi

**SENARYO ADI:** İK Sağlık Verisi
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** İK
**OLAY:** Sağlık sigortası claim kayıtları 120 çalışan 450 MB.
**NEDEN ŞÜPHELİ:** Hassas sağlık.
**NORMAL BASELINE'DAN SAPMA:** 450 MB
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** KVKK ihlali riski.

---

## 94. Muhasebe VPN İç

**SENARYO ADI:** Muhasebe VPN İç
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Muhasebe evden VPN ile ERP; normal. Ancak aynı anda ofis workstation aktif.
**NEDEN ŞÜPHELİ:** İki lokasyon aynı kullanıcı.
**NORMAL BASELINE'DAN SAPMA:** Dual location
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** VPN açık unutulmuş.

---

## 95. Satış Demo DB

**SENARYO ADI:** Satış Demo DB
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış demo-db'ye değil prod-crm'e bağlanmış connection string.
**NEDEN ŞÜPHELİ:** Prod CRM satışta kısıtlı.
**NORMAL BASELINE'DAN SAPMA:** Prod bağlantı
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Config hatası.

---

## 96. Stajyer Printer

**SENARYO ADI:** Stajyer Printer
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer confidential yazıcı kuyruğuna 200 sayfa CV baskı.
**NEDEN ŞÜPHELİ:** Yanlış printer.
**NORMAL BASELINE'DAN SAPMA:** Confidential queue
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Yanlış seçim.

---

## 97. IT Admin SNMP

**SENARYO ADI:** IT Admin SNMP
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Compromised host SNMP community string ile 50 switch poll.
**NEDEN ŞÜPHELİ:** Reconnaissance.
**NORMAL BASELINE'DAN SAPMA:** SNMP burst
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Monitoring tool taklidi.

---

## 98. CTO Lab Sunucu

**SENARYO ADI:** CTO Lab Sunucu
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** CTO
**OLAY:** CTO prod-payment'e lab credential ile bağlanma denemesi.
**NEDEN ŞÜPHELİ:** Lab cred prod'da.
**NORMAL BASELINE'DAN SAPMA:** Cross cred
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Yanlış env.

---

## 99. CFO Hedge Model

**SENARYO ADI:** CFO Hedge Model
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CFO
**OLAY:** Finans modeling sunucusundan hedge senaryoları 900 MB.
**NEDEN ŞÜPHELİ:** CFO yetkili; USB follow.
**NORMAL BASELINE'DAN SAPMA:** USB after
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Danışman paylaşımı.

---

## 100. Güvenlik Honeypot

**SENARYO ADI:** Güvenlik Honeypot
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** Honeypot share'e erişim; gerçek saldırgan değil pentest.
**NEDEN ŞÜPHELİ:** Honeypot tetik.
**NORMAL BASELINE'DAN SAPMA:** Expected
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Kırmızı takım.

---

## 101. Yazılım Dependency Confusion

**SENARYO ADI:** Yazılım Dependency Confusion
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** İç artifact repo'ya bilinmeyen paket publish denemesi.
**NEDEN ŞÜPHELİ:** Supply chain.
**NORMAL BASELINE'DAN SAPMA:** Publish deneme
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Poisoned package.

---

## 102. İK Exit Interview

**SENARYO ADI:** İK Exit Interview
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** İK
**OLAY:** Ayrılan çalışanın exit interview kaydı 8 kişiye forward.
**NEDEN ŞÜPHELİ:** Gizlilik.
**NORMAL BASELINE'DAN SAPMA:** 8 recipient
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Prosedür ihlali.

---

## 103. Muhasebe E-Fatura

**SENARYO ADI:** Muhasebe E-Fatura
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** E-fatura arşiv sunucusundan 1 yıl XML 3.5 GB.
**NEDEN ŞÜPHELİ:** Toplu arşiv.
**NORMAL BASELINE'DAN SAPMA:** 3.5 GB
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Mali müşavir.

---

## 104. Satış Ses Kaydı

**SENARYO ADI:** Satış Ses Kaydı
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Satış
**OLAY:** Müşteri görüşme ses kaydı izinsiz paylaşım klasörüne.
**NEDEN ŞÜPHELİ:** Kayıt onayı yok.
**NORMAL BASELINE'DAN SAPMA:** Share upload
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Kalite kontrol bahanesi.

---

## 105. Destek Admin Panel

**SENARYO ADI:** Destek Admin Panel
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Destek hesabı ile admin-helpdesk impersonation 12 kullanıcı.
**NEDEN ŞÜPHELİ:** Impersonation abuse.
**NORMAL BASELINE'DAN SAPMA:** 12 impersonate
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Hızlı çözüm.

---

## 106. Proje Yöneticisi Timesheet

**SENARYO ADI:** Proje Yöneticisi Timesheet
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** PM 4 çalışanın timesheet'ini onaysız düzenliyor.
**NEDEN ŞÜPHELİ:** Timesheet fraud.
**NORMAL BASELINE'DAN SAPMA:** 4 user edit
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Proje maliyeti düşürme.

---

## 107. Veri Analisti Notebook

**SENARYO ADI:** Veri Analisti Notebook
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Jupyter notebook output 800 MB iç PII cache.
**NEDEN ŞÜPHELİ:** Cache leak.
**NORMAL BASELINE'DAN SAPMA:** 800 MB cache
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Notebook unutulmuş.

---

## 108. CEO Driver USB

**SENARYO ADI:** CEO Driver USB
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** CEO
**OLAY:** Şoför CEO laptop'a USB takıyor (şarj+cihaz).
**NEDEN ŞÜPHELİ:** Üçüncü taraf USB.
**NORMAL BASELINE'DAN SAPMA:** Foreign USB
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Şarj kablosu.

---

## 109. Hukuk e-Discovery

**SENARYO ADI:** Hukuk e-Discovery
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Hukuk
**OLAY:** e-Discovery export 12 GB PST iç mail.
**NEDEN ŞÜPHELİ:** Büyük PST.
**NORMAL BASELINE'DAN SAPMA:** 12 GB
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Dava meşru.

---

## 110. Stajyer Git Push

**SENARYO ADI:** Stajyer Git Push
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer read-only repo'ya push denemesi başarısız.
**NEDEN ŞÜPHELİ:** Write deneme.
**NORMAL BASELINE'DAN SAPMA:** Push fail
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Tutorial hatası.

---

## 111. IT Admin DHCP Rogue

**SENARYO ADI:** IT Admin DHCP Rogue
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Yeni DHCP scope office VLAN; değişiklik kaydı yok.
**NEDEN ŞÜPHELİ:** Rogue DHCP.
**NORMAL BASELINE'DAN SAPMA:** New scope
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** MITM hazırlığı.

---

## 112. Muhasebe KDV List

**SENARYO ADI:** Muhasebe KDV List
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** KDV iade listesi tüm müşteriler 600 MB Excel.
**NEDEN ŞÜPHELİ:** Müşteri vergi no.
**NORMAL BASELINE'DAN SAPMA:** 600 MB
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Müşavir.

---

## 113. Satış Whatsapp İç

**SENARYO ADI:** Satış Whatsapp İç
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Satış
**OLAY:** İç mail yerine kişisel whatsapp web iç PC'de müşteri telefon.
**NEDEN ŞÜPHELİ:** Kanal policy.
**NORMAL BASELINE'DAN SAPMA:** WhatsApp web
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Alışkanlık.

---

## 114. İK Org Chart Export

**SENARYO ADI:** İK Org Chart Export
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** İK
**OLAY:** Tam organizasyon+telefon+doğum tarihi export.
**NEDEN ŞÜPHELİ:** PII aggregate.
**NORMAL BASELINE'DAN SAPMA:** Full org
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Sunum.

---

## 115. Yazılım Log4j Scan

**SENARYO ADI:** Yazılım Log4j Scan
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** İç vulnerability scanner tüm hostlara JNDI probe.
**NEDEN ŞÜPHELİ:** Scanner veya saldırı.
**NORMAL BASELINE'DAN SAPMA:** Probe 200 host
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Patch taraması.

---

## 116. Güvenlik Firewall Rule

**SENARYO ADI:** Güvenlik Firewall Rule
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** Geçici allow rule süresi dolmadan kalıcı yapılmış.
**NEDEN ŞÜPHELİ:** Rule persist.
**NORMAL BASELINE'DAN SAPMA:** Expired rule
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Acil açık unutulmuş.

---

## 117. CFO Bank Swift

**SENARYO ADI:** CFO Bank Swift
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CFO
**OLAY:** SWIFT mesaj arşivi 2 GB indirme.
**NEDEN ŞÜPHELİ:** Finansal mesajlar.
**NORMAL BASELINE'DAN SAPMA:** 2 GB
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Siber soygun hazırlığı.

---

## 118. Destek Passphrase

**SENARYO ADI:** Destek Passphrase
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Destek ticket'ta kullanıcı şifresi plaintext yazmış.
**NEDEN ŞÜPHELİ:** Secret in ticket.
**NORMAL BASELINE'DAN SAPMA:** Plaintext pwd
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Kullanıcı verdi.

---

## 119. PM Risk Register

**SENARYO ADI:** PM Risk Register
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** Risk register tüm projeler 400 MB.
**NEDEN ŞÜPHELİ:** Stratejik riskler.
**NORMAL BASELINE'DAN SAPMA:** 400 MB
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Audit.

---

## 120. Veri Analisti Cross Dept

**SENARYO ADI:** Veri Analisti Cross Dept
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** İK attrition modeline erişim; sadece satış churn yetkili.
**NEDEN ŞÜPHELİ:** Model scope.
**NORMAL BASELINE'DAN SAPMA:** İK model
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Merak.

---

## 121. Stajyer Cafeteria

**SENARYO ADI:** Stajyer Cafeteria
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer kartı ile gece 02:00 fiziksel giriş+aynı anda VPN.
**NEDEN ŞÜPHELİ:** Fiziksel+logical.
**NORMAL BASELINE'DAN SAPMA:** 02:00 entry
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Projede kalmış.

---

## 122. IT Admin WSUS

**SENARYO ADI:** IT Admin WSUS
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Yanlış patch ring'e finans sunucuları dahil; reboot planlandı.
**NEDEN ŞÜPHELİ:** Change risk.
**NORMAL BASELINE'DAN SAPMA:** Wrong ring
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Grup hatası.

---

## 123. Muhasebe+Satış Ortak USB

**SENARYO ADI:** Muhasebe+Satış Ortak USB
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Aynı USB cihaz ID 2 farklı kullanıcıda 1 saat arayla.
**NEDEN ŞÜPHELİ:** Ortak exfil aracı.
**NORMAL BASELINE'DAN SAPMA:** Same USB ID
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** İki kişi collusion.

---

## 124. Hukuk+CEO Sözleşme

**SENARYO ADI:** Hukuk+CEO Sözleşme
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Hukuk
**OLAY:** Hukuk CEO sözleşme klasörüne erişim; merger hazırlığı duyulmadı.
**NEDEN ŞÜPHELİ:** Erken bilgi.
**NORMAL BASELINE'DAN SAPMA:** CEO contract
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Gizli proje.

---

## 125. Yazılım+IT Secret Rotate

**SENARYO ADI:** Yazılım+IT Secret Rotate
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** IT Admin
**OLAY:** IT rotate ederken dev pipeline kırıldı; dev eski secret ile 500 retry.
**NEDEN ŞÜPHELİ:** Chaos değil saldırı.
**NORMAL BASELINE'DAN SAPMA:** 500 retry
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Koordinasyon eksik.

---

## 126. Satış+Destek Müşteri PII

**SENARYO ADI:** Satış+Destek Müşteri PII
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Destek ticket'tan PII kopyalayıp satış CRM notuna yapıştırma.
**NEDEN ŞÜPHELİ:** PII yayılım.
**NORMAL BASELINE'DAN SAPMA:** CRM note PII
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Hız.

---

## 127. İK+Güvenlik Offboard

**SENARYO ADI:** İK+Güvenlik Offboard
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** Ayrılan IT admin hesabı disable gecikmesi 48 saat; hâlâ VPN.
**NEDEN ŞÜPHELİ:** Offboard SLA.
**NORMAL BASELINE'DAN SAPMA:** 48h active
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** İK bildirimi gecikti.

---

## 128. Stajyer+Muhasebe Fatura

**SENARYO ADI:** Stajyer+Muhasebe Fatura
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer muhasebe ortak ekranda fatura onay tıklıyor.
**NEDEN ŞÜPHELİ:** Yetkisiz onay.
**NORMAL BASELINE'DAN SAPMA:** Approve click
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Shadowing hatası.

---

## 129. CEO+CTO Patent

**SENARYO ADI:** CEO+CTO Patent
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CTO
**OLAY:** Patent başvuru taslakları 1.2 GB indirme.
**NEDEN ŞÜPHELİ:** IP kritik.
**NORMAL BASELINE'DAN SAPMA:** 1.2 GB
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Patent avukatı.

---

## 130. CFO+İK Headcount

**SENARYO ADI:** CFO+İK Headcount
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** CFO
**OLAY:** CFO gizli headcount reduction listesine İK'dan erken erişim.
**NEDEN ŞÜPHELİ:** Insider trading risk.
**NORMAL BASELINE'DAN SAPMA:** Pre-announce
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Sızıntı.

---

## 131. Güvenlik+Yazılım Backdoor

**SENARYO ADI:** Güvenlik+Yazılım Backdoor
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Commit'te obfuscated reverse shell; iç git.
**NEDEN ŞÜPHELİ:** Backdoor.
**NORMAL BASELINE'DAN SAPMA:** Shell signature
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Supply chain.

---

## 132. Proje+Veri Feature Leak

**SENARYO ADI:** Proje+Veri Feature Leak
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Üretim feature store'dan test ortama 5 GB kopya.
**NEDEN ŞÜPHELİ:** Prod→test data.
**NORMAL BASELINE'DAN SAPMA:** 5 GB copy
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Test realism.

---

## 133. Satış Gece CRM

**SENARYO ADI:** Satış Gece CRM
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Satış
**OLAY:** Ayrılan rep Cumartesi 03:00 CRM export.
**NEDEN ŞÜPHELİ:** Off hours+export.
**NORMAL BASELINE'DAN SAPMA:** 03:00
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Rakip.

---

## 134. Muhasebe API Fraud

**SENARYO ADI:** Muhasebe API Fraud
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Banka entegrasyon API key workstation registry'de plaintext.
**NEDEN ŞÜPHELİ:** Secret storage.
**NORMAL BASELINE'DAN SAPMA:** Registry key
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Eski entegrasyon.

---

## 135. İK Sosyal Mühendislik

**SENARYO ADI:** İK Sosyal Mühendislik
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** İK
**OLAY:** İK'ya sahte CEO mail 'acil maaş listesi' ; İK tıklamadı.
**NEDEN ŞÜPHELİ:** Hedef İK.
**NORMAL BASELINE'DAN SAPMA:** Blocked
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** CEO fraud.

---

## 136. Destek Tool İndir

**SENARYO ADI:** Destek Tool İndir
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Remote tool (TeamViewer benzeri) kurulum iç PC.
**NEDEN ŞÜPHELİ:** Remote tool policy.
**NORMAL BASELINE'DAN SAPMA:** Install
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Müşteri desteği.

---

## 137. IT VLAN Hop

**SENARYO ADI:** IT VLAN Hop
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Compromised PC finance VLAN'a route add.
**NEDEN ŞÜPHELİ:** VLAN hop.
**NORMAL BASELINE'DAN SAPMA:** New route
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Segmentation bypass.

---

## 138. CEO Asistan Toplantı

**SENARYO ADI:** CEO Asistan Toplantı
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** CEO
**OLAY:** Gizli yönetim toplantısı kaydı paylaşım linki iç chat.
**NEDEN ŞÜPHELİ:** Gizli kayıt.
**NORMAL BASELINE'DAN SAPMA:** Chat link
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Not alma.

---

## 139. Hukuk Metadata

**SENARYO ADI:** Hukuk Metadata
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Hukuk
**OLAY:** Word dosyalarında eski revision metadata ile 200 dosya.
**NEDEN ŞÜPHELİ:** Hidden metadata.
**NORMAL BASELINE'DAN SAPMA:** 200 doc
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Eski avukat notları.

---

## 140. Stajyer Phishing Test

**SENARYO ADI:** Stajyer Phishing Test
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer güvenlik phishing simülasyonuna tıkladı.
**NEDEN ŞÜPHELİ:** Eğitim metrik.
**NORMAL BASELINE'DAN SAPMA:** Clicked
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Beklenen eğitim.

---

## 141. Yazılım DB Backup Local

**SENARYO ADI:** Yazılım DB Backup Local
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Dev local disk'e prod DB backup restore 15 GB.
**NEDEN ŞÜPHELİ:** Prod data local.
**NORMAL BASELINE'DAN SAPMA:** 15 GB local
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Debug.

---

## 142. Güvenlik Nmap İç

**SENARYO ADI:** Güvenlik Nmap İç
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** Onaysız nmap tüm /16 iç subnet.
**NEDEN ŞÜPHELİ:** Scan policy.
**NORMAL BASELINE'DAN SAPMA:** Full /16
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Pentest.

---

## 143. CFO Expense Fraud

**SENARYO ADI:** CFO Expense Fraud
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** CFO
**OLAY:** CFO kendi expense raporunda onay zinciri bypass (sistem bug).
**NEDEN ŞÜPHELİ:** SoD anomaly.
**NORMAL BASELINE'DAN SAPMA:** Self approve
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Nadir bug.

---

## 144. Muhasebe Zaman Damgası

**SENARYO ADI:** Muhasebe Zaman Damgası
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Sistem saati geri alınmış PC'de fatura tarihi manipülasyon denemesi.
**NEDEN ŞÜPHELİ:** Time tamper.
**NORMAL BASELINE'DAN SAPMA:** Clock skew
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Fraud.

---

## 145. Satış Lisans Anahtarı

**SENARYO ADI:** Satış Lisans Anahtarı
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış CRM lisans anahtarını iç wiki'ye yapıştırma.
**NEDEN ŞÜPHELİ:** Secret in wiki.
**NORMAL BASELINE'DAN SAPMA:** Wiki paste
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Kolay erişim.

---

## 146. İK BGB Eğitim

**SENARYO ADI:** İK BGB Eğitim
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** İK
**OLAY:** Zorunlu KVKK eğitimi 3. kez atlandı; sistem uyarı.
**NEDEN ŞÜPHELİ:** Compliance.
**NORMAL BASELINE'DAN SAPMA:** Skipped x3
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Yoğunluk.

---

## 147. Destek DB Sorgu

**SENARYO ADI:** Destek DB Sorgu
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Destek read-only ticket DB'de UPDATE denemesi.
**NEDEN ŞÜPHELİ:** SQL injection test değil abuse.
**NORMAL BASELINE'DAN SAPMA:** UPDATE
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Merak.

---

## 148. PM Bütçe Excel Makro

**SENARYO ADI:** PM Bütçe Excel Makro
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** Bütçe Excel macro enabled; dışarıdan değil iç mail eki.
**NEDEN ŞÜPHELİ:** Macro risk.
**NORMAL BASELINE'DAN SAPMA:** Macro run
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Eski şablon.

---

## 149. Veri Analisti GPU Farm

**SENARYO ADI:** Veri Analisti GPU Farm
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** GPU cluster admin queue'ya başka departman job submit.
**NEDEN ŞÜPHELİ:** Kaynak hog.
**NORMAL BASELINE'DAN SAPMA:** Foreign job
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Uzun eğitim.

---

## 150. Stajyer Slack Token

**SENARYO ADI:** Stajyer Slack Token
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer bot token'ı public iç channel'a yapıştırma.
**NEDEN ŞÜPHELİ:** Token leak.
**NORMAL BASELINE'DAN SAPMA:** Channel paste
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Yardım istedi.

---

## 151. IT Admin Hypervisor

**SENARYO ADI:** IT Admin Hypervisor
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** IT Admin
**OLAY:** Admin kişisel AD hesabıyla hypervisor console; ayrı admin hesabı policy.
**NEDEN ŞÜPHELİ:** Dual account policy.
**NORMAL BASELINE'DAN SAPMA:** Personal on HV
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Acil reboot.

---

## 152. CEO Physical+Data

**SENARYO ADI:** CEO Physical+Data
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** CEO
**OLAY:** CEO after hours bina girişi + aynı saat strateji sunucu 2 GB.
**NEDEN ŞÜPHELİ:** Korelasyon.
**NORMAL BASELINE'DAN SAPMA:** Physical+data
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Board hazırlık.

---

## 153. CTO Open Source Mirror

**SENARYO ADI:** CTO Open Source Mirror
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** CTO
**OLAY:** İç oss-mirror'dan tüm tarball 8 GB.
**NEDEN ŞÜPHELİ:** Mirror tam çekim.
**NORMAL BASELINE'DAN SAPMA:** 8 GB
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Air-gap mirror kurulum.

---

## 154. Güvenlik Alert Fatigue

**SENARYO ADI:** Güvenlik Alert Fatigue
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** SOC 200 alert'i bulk close without investigation.
**NEDEN ŞÜPHELİ:** Process violation.
**NORMAL BASELINE'DAN SAPMA:** Bulk close
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Vardiya sonu.

---

## 155. Yazılım Composer Token

**SENARYO ADI:** Yazılım Composer Token
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** AI IDE token iç git commit'te.
**NEDEN ŞÜPHELİ:** Secret in git.
**NORMAL BASELINE'DAN SAPMA:** Token in repo
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Yanlış commit.

---

## 156. Muhasebe Yinelenen Ödeme

**SENARYO ADI:** Muhasebe Yinelenen Ödeme
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Aynı fatura 2 kez ödeme; farklı referans.
**NEDEN ŞÜPHELİ:** Duplicate pay.
**NORMAL BASELINE'DAN SAPMA:** 2x payment
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Hata veya fraud.

---

## 157. Satış Müşteri Şikayet

**SENARYO ADI:** Satış Müşteri Şikayet
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Satış
**OLAY:** Müşteri şikayet detayı iç all-sales mail.
**NEDEN ŞÜPHELİ:** Müşteri PII.
**NORMAL BASELINE'DAN SAPMA:** All-sales
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Öfke maili.

---

## 158. İK Referans Check

**SENARYO ADI:** İK Referans Check
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** İK
**OLAY:** Aday CV+referans 50 paket 300 MB indirme.
**NEDEN ŞÜPHELİ:** Toplu aday.
**NORMAL BASELINE'DAN SAPMA:** 300 MB
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** İşe alım.

---

## 159. Hukuk İç Soruşturma

**SENARYO ADI:** Hukuk İç Soruşturma
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Hukuk
**OLAY:** Soruşturma dosyasına ilgili çalışan erişiyor (conflict).
**NEDEN ŞÜPHELİ:** Conflict of interest.
**NORMAL BASELINE'DAN SAPMA:** Subject access
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Adalet.

---

## 160. Destek Kiosk Login

**SENARYO ADI:** Destek Kiosk Login
**KATEGORİ:** credential ihlali
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** Ortak kiosk'ta admin oturumu kapatılmamış.
**NEDEN ŞÜPHELİ:** Shared kiosk.
**NORMAL BASELINE'DAN SAPMA:** Open admin
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Vardiya değişimi.

---

## 161. Proje Yöneticisi Vendor

**SENARYO ADI:** Proje Yöneticisi Vendor
**KATEGORİ:** insider threat
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** PM vendor listesine kendi şirketini ekleme denemesi.
**NEDEN ŞÜPHELİ:** Conflict.
**NORMAL BASELINE'DAN SAPMA:** Self vendor
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** Kickback.

---

## 162. Veri Analisti Synthetic

**SENARYO ADI:** Veri Analisti Synthetic
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Sentetik veri üretimi 10 GB; normal.
**NEDEN ŞÜPHELİ:** Baseline genişleme.
**NORMAL BASELINE'DAN SAPMA:** 10 GB synth
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Yeni model.

---

## 163. Stajyer İlk Gün Scan

**SENARYO ADI:** Stajyer İlk Gün Scan
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Stajyer
**OLAY:** Stajyer ilk gün tüm network share listeleme script.
**NEDEN ŞÜPHELİ:** Recon.
**NORMAL BASELINE'DAN SAPMA:** Share enum
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Merak/hacking culture.

---

## 164. IT Admin Cert Expiry

**SENARYO ADI:** IT Admin Cert Expiry
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** IT Admin
**OLAY:** İç TLS cert expire; finans API hata.
**NEDEN ŞÜPHELİ:** Avail impact.
**NORMAL BASELINE'DAN SAPMA:** Cert expired
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Renewal unutuldu.

---

## 165. CEO+CFO+CTO Board

**SENARYO ADI:** CEO+CFO+CTO Board
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** CEO
**OLAY:** Üç C-level aynı saat board sunucusu; normal quarterly.
**NEDEN ŞÜPHELİ:** Expected cluster.
**NORMAL BASELINE'DAN SAPMA:** Quarterly
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Board.

---

## 166. Muhasebe Eski Sürüm

**SENARYO ADI:** Muhasebe Eski Sürüm
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Muhasebe
**OLAY:** Desteklenmeyen Excel 2010 ile macro dosya açma.
**NEDEN ŞÜPHELİ:** EOL software.
**NORMAL BASELINE'DAN SAPMA:** Excel 2010
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Uyumluluk.

---

## 167. Satış+İK Çapraz Mail

**SENARYO ADI:** Satış+İK Çapraz Mail
**KATEGORİ:** kazara ihlal
**KULLANICI ROLÜ:** Satış
**OLAY:** Satış performans düşüklüğü maili yanlışlıkla çalışana gitti.
**NEDEN ŞÜPHELİ:** HR sensitive.
**NORMAL BASELINE'DAN SAPMA:** Wrong recipient
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Otomatik tamamlama.

---

## 168. Yazılım Container Escape

**SENARYO ADI:** Yazılım Container Escape
**KATEGORİ:** dış saldırı desteği
**KULLANICI ROLÜ:** Yazılım Geliştirici
**OLAY:** Dev container'dan host mount /etc/shadow read denemesi.
**NEDEN ŞÜPHELİ:** Escape.
**NORMAL BASELINE'DAN SAPMA:** Shadow read
**BEKLENEN SEVERITY:** CRITICAL
**GERÇEKÇİLİK NOTU:** CVE exploit.

---

## 169. Güvenlik SIEM Rule Test

**SENARYO ADI:** Güvenlik SIEM Rule Test
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Güvenlik Görevlisi
**OLAY:** Kasıtlı test event 50 kez üretildi.
**NEDEN ŞÜPHELİ:** Test noise.
**NORMAL BASELINE'DAN SAPMA:** 50 test
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Rule tuning.

---

## 170. İK Çalışan Foto

**SENARYO ADI:** İK Çalışan Foto
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** İK
**OLAY:** Tüm çalışan fotoğraf arşivi 1.8 GB.
**NEDEN ŞÜPHELİ:** Biyometrik/PII.
**NORMAL BASELINE'DAN SAPMA:** 1.8 GB
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Yeni ID kart.

---

## 171. CFO Treasury

**SENARYO ADI:** CFO Treasury
**KATEGORİ:** yetkisiz erişim
**KULLANICI ROLÜ:** CFO
**OLAY:** CFO treasury trading sistemi read; normalde sadece rapor.
**NEDEN ŞÜPHELİ:** Trading access.
**NORMAL BASELINE'DAN SAPMA:** Trading UI
**BEKLENEN SEVERITY:** WARNING
**GERÇEKÇİLİK NOTU:** Piyasa kontrolü.

---

## 172. Destek Shadow IT

**SENARYO ADI:** Destek Shadow IT
**KATEGORİ:** politika ihlali
**KULLANICI ROLÜ:** Destek Personeli
**OLAY:** İç sunucuda kurulu yetkisiz PostgreSQL instance.
**NEDEN ŞÜPHELİ:** Shadow IT.
**NORMAL BASELINE'DAN SAPMA:** New service
**BEKLENEN SEVERITY:** ALERT
**GERÇEKÇİLİK NOTU:** Ticket DB.

---

## 173. PM Agile Board Export

**SENARYO ADI:** PM Agile Board Export
**KATEGORİ:** veri sızdırma
**KULLANICI ROLÜ:** Proje Yöneticisi
**OLAY:** Sprint board tüm geçmiş 5 yıl JSON 1 GB.
**NEDEN ŞÜPHELİ:** Uzun tarih.
**NORMAL BASELINE'DAN SAPMA:** 5 yıl
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Retrospektif.

---

## 174. Veri Analisti Outlier

**SENARYO ADI:** Veri Analisti Outlier
**KATEGORİ:** diğer
**KULLANICI ROLÜ:** Veri Analisti
**OLAY:** Analist kendi hesabında normal çalışma; sistem false positive testi.
**NEDEN ŞÜPHELİ:** Control case.
**NORMAL BASELINE'DAN SAPMA:** Normal
**BEKLENEN SEVERITY:** LOG
**GERÇEKÇİLİK NOTU:** Negative test.

---





25 izleme fikri — senaryo değil, ölçülebilir kapasite önerileri:

---

**İZLEME ADI:** USB Bağlantı ve Yazma Hacmi  
**KATEGORİ:** donanım  
**VERİ KAYNAĞI:** Windows Event Log (Event ID 6416, 4663), EDR/DLP agent  
**NE İZLENİYOR:** USB takılma/çıkarma, cihaz VID/PID, hedef sunucuya yazılan toplam MB  
**NEDEN DEĞERLI:** Fiziksel veri sızdırma ve kötü amaçlı yazılım taşıma için doğrudan sinyal  
**ANOMALİ SİNYALİ:** Rol baseline’ının 5x üstü tek sefer yazma veya yasaklı cihaz sınıfı  
**UYGULAMA ZORLUĞU:** orta — EDR/DLP gerekir, ham Event Log tek başına yetersiz  
**ÖRNEK METRIK:** Satış rolü: ayda 0 USB yazma → 2.1 GB / 14 dk

---

**İZLEME ADI:** Yazıcı Kuyruğu Hassasiyet Korelasyonu  
**KATEGORİ:** donanım  
**VERİ KAYNAĞI:** Windows Print Service Log, yazıcı SNMP/syslog  
**NE İZLENİYOR:** Kullanıcı başına sayfa sayısı, “confidential/legal” kuyruk seçimi  
**NEDEN DEĞERLI:** Kağıt üzerinden PII/sır sızıntısı; operasyonel maliyet takibi  
**ANOMALİ SİNYALİ:** Gece vardiyasında confidential kuyruğa 200+ sayfa  
**UYGULAMA ZORLUĞU:** orta — Kuyruk adlandırma standardı gerekir  
**ÖRNEK METRIK:** Stajyer: günlük 5 sayfa → 200 sayfa / confidential queue

---

**İZLEME ADI:** Clipboard Büyük Veri Kopyalama  
**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** DLP endpoint agent, Windows ETW (Clipboard API)  
**NE İZLENİYOR:** Panoya kopyalanan veri boyutu, kaynak uygulama (CRM, Excel, DB client)  
**NEDEN DEĞERLI:** Mail/USB olmadan veri taşıma; sık gözden kaçar  
**ANOMALİ SİNYALİ:** Tek oturumda 50+ MB clipboard veya hassas uygulama → chat/RDP  
**UYGULAMA ZORLUĞU:** zor — OS/agent desteği ve gizlilik politikası  
**ÖRNEK METRIK:** 10 dk içinde 3× 20 MB CRM→Teams yapıştırma

---

**İZLEME ADI:** Ekran Görüntüsü / Screen Capture Sıklığı  
**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** EDR, Windows Graphics Capture API telemetry  
**NE İZLENİYOR:** Saatlik capture event sayısı, hedef process (Snipping Tool, 3rd party)  
**NEDEN DEĞERLI:** Görsel veri exfil; destek/sosyal mühendislik kayıtları  
**ANOMALİ SİNYALİ:** Finans uygulaması açıkken saatte 30+ capture  
**UYGULAMA ZORLUĞU:** zor — Agent ve false positive yönetimi  
**ÖRNEK METRIK:** Muhasebe ERP ekranı: 0/gün → 45 capture / 2 saat

---

**İZLEME ADI:** Sunucu Başına Veri Çekim Profili  
**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** NetFlow/sFlow, firewall east-west log, SMB/NFS proxy log  
**NE İZLENİYOR:** Kullanıcı (veya IP→user map) × hedef sunucu × günlük GB in/out  
**NEDEN DEĞERLI:** UEBA’nın çekirdek sinyali; rol bazlı erişim matrisi  
**ANOMALİ SİNYALİ:** İlk kez erişilen sunucu veya günlük GB’nin 10x üstü  
**UYGULAMA ZORLUĞU:** orta — IP-user eşlemesi (AD session) şart  
**ÖRNEK METRIK:** Dev: git-mirror 150 MB/hafta → 4.7 GB / hafta sonu

---

**İZLEME ADI:** East-West Lateral Protokol Pateni  
**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** NetFlow, Zeek, firewall deny/allow log  
**NE İZLENİYOR:** SMB445, RDP3389, WinRM5985, LDAP389 bağlantı sayısı ve hedef çeşitliliği  
**NEDEN DEĞERLI:** APT yayılması; segmentasyon ihlali  
**ANOMALİ SİNYALİ:** 15 dk’da 40+ farklı internal host’a SMB  
**UYGULAMA ZORLUĞU:** orta — Flow retention ve asset envanteri  
**ÖRNEK METRIK:** Destek PC: 2 SMB host/gün → 40 host / 15 dk

---

**İZLEME ADI:** İç DNS Sorgu Entropisi  
**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** Windows DNS Server Analytical log, BIND query log  
**NE İZLENİYOR:** Kullanıcı/host başına QPS, TXT/NULL oran, NXDOMAIN oranı  
**NEDEN DEĞERLI:** DNS tunneling ve C2 iç ağda sık kullanılır  
**ANOMALİ SİNYALİ:** TXT sorgu hacmi baseline’ın 100x; yüksek subdomain entropi  
**UYGULAMA ZORLUĞU:** orta — Client→user korelasyonu zor  
**ÖRNEK METRIK:** Dev workstation: 10 TXT/saat → 5000 TXT/saat

---

**İZLEME ADI:** İç Mail Gönderim/Alım Hacmi (Yön Ayrımlı)  
**KATEGORİ:** mail  
**VERİ KAYNAĞI:** Exchange Message Tracking, EWS audit, on-prem SMTP log  
**NE İZLENİYOR:** Günlük sent/received, ek boyutu, DL/all-staff oranı, hassas keyword  
**NEDEN DEĞERLI:** Kazara sızıntı ve insider iletişim kanalı  
**ANOMALİ SİNYALİ:** All-staff mail + >5 MB ek veya günlük gönderim 8x  
**UYGULAMA ZORLUĞU:** kolay — Exchange log olgun  
**ÖRNEK METRIK:** Satış: 20 mail/gün → 1 mail tüm şirket + 8 MB fiyat listesi

---

**İZLEME ADI:** Mail Forward/Delegate Kural Değişimi  
**KATEGORİ:** mail  
**VERİ KAYNAĞI:** Exchange Management audit, EWS  
**NE İZLENİYOR:** Yeni inbox rule, auto-forward, delegate ekleme/silme  
**NEDEN DEĞERLI:** Gizli exfil ve hesap ele geçirme sonrası kalıcılık  
**ANOMALİ SİNYALİ:** İlk kez dış mailbox’a forward veya gece oluşturulan kural  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** İK: forward rule sayısı 0 → 1 (kişisel iç mailbox)

---

**İZLEME ADI:** Kerberos / NTLM Auth Hacmi ve Hedef Çeşitliliği  
**KATEGORİ:** kimlik  
**VERİ KAYNAĞI:** Windows Security Log (4624, 4776), DC syslog  
**NE İZLENİYOR:** Saatlik başarılı/başarısız logon, kaynak IP çeşitliliği, TGT istekleri  
**NEDEN DEĞERLI:** Credential abuse, brute force, PtH  
**ANOMALİ SİNYALİ:** Başarısız logon 50+/dk veya 1 kullanıcı → 8 host gece TGT  
**UYGULAMA ZORLUĞU:** orta — DC log hacmi yüksek, SIEM filtre gerekir  
**ÖRNEK METRIK:** Admin: gece 02:00’de 0 TGT → 8 farklı sunucu TGT

---

**İZLEME ADI:** Eşzamanlı Oturum ve Oturum Lokasyonu  
**KATEGORİ:** kimlik  
**VERİ KAYNAĞI:** AD, VPN concentrator log, 802.1X NAC  
**NE İZLENİYOR:** Aynı anda aktif workstation sayısı, VPN + ofis fiziksel giriş korelasyonu  
**NEDEN DEĞERLI:** Hesap paylaşımı ve çalıntı credential  
**ANOMALİ SİNYALİ:** 2+ farklı host aynı anda veya VPN+ofis çakışması  
**UYGULAMA ZORLUĞU:** orta — Fiziksel badge entegrasyonu opsiyonel  
**ÖRNEK METRIK:** Stajyer: 1 oturum → 2 workstation eşzamanlı

---

**İZLEME ADI:** AD Grup Üyeliği ve Privileged Değişiklik  
**KATEGORİ:** kimlik  
**VERİ KAYNAĞI:** Windows Security 4728/4729/4732, AD replication audit  
**NE İZLENİYOR:** Domain Admins, Enterprise Admins, hassas grup add/remove  
**NEDEN DEĞERLI:** Privilege escalation ve shadow admin  
**ANOMALİ SİNYALİ:** Muhasebe hesabının DA grubuna ekleme denemesi  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** DA üye değişikliği: 0/ay → 1 başarısız deneme

---

**İZLEME ADI:** Servis Hesabı ve API Key Kullanım Haritası  
**KATEGORİ:** kimlik  
**VERİ KAYNAĞI:** API gateway log, Vault audit, uygulama access log  
**NE İZLENİYOR:** Key başına çağrı sayısı, kaynak IP, endpoint, saat  
**NEDEN DEĞERLI:** Paylaşılan secret ve sızıntı sonrası abuse  
**ANOMALİ SİNYALİ:** Tek key → 3 IP veya rotate sonrası eski key aktif  
**UYGULAMA ZORLUĞU:** orta — Her uygulama farklı log formatı  
**ÖRNEK METRIK:** svc-deploy key: 1 IP → 3 workstation / gece 40k call

---

**İZLEME ADI:** Uygulama Süresi ve Process Ağacı  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** Sysmon (1/3), Wazuh syscheck, EDR process telemetry  
**NE İZLENİYOR:** SAP, Jira, Excel, VS Code, Steam vb. günlük aktif süre ve parent-child  
**NEDEN DEĞERLI:** Politika ihlali ve shadow IT (yetkisiz araç)  
**ANOMALİ SİNYALİ:** Steam 4 saat mesai içi veya bilinmeyen .exe 30+ dk  
**UYGULAMA ZORLUĞU:** orta — Process allowlist bakımı  
**ÖRNEK METRIK:** Geliştirici: VS Code 6h normal → Steam 4h aynı gün

---

**İZLEME ADI:** Veritabanı Sorgu Hacmi ve Tablo Kapsamı  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** SQL Server audit, PostgreSQL pg_audit, proxy query log  
**NE İZLENİYOR:** Kullanıcı×DB×günlük satır/MB, SELECT * oranı, tablo adı çeşitliliği  
**NEDEN DEĞERLI:** Payroll/CRM dump; prod erişim ihlali  
**ANOMALİ SİNYALİ:** Tek sorguda *employees* veya 890 MB result set  
**UYGULAMA ZORLUĞU:** orta — DB audit performans etkisi  
**ÖRNEK METRIK:** İK payroll: 2–5 MB/sorgu → 890 MB export

---

**İZLEME ADI:** Git/Artifact Erişim ve Clone Hacmi  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** GitLab/Gitea audit log, reverse proxy, git-mirror NetFlow  
**NE İZLENİYOR:** Clone/pull GB, erişilen repo sayısı, push denemesi  
**NEDEN DEĞERLI:** Kaynak kod ve secret sızıntısı  
**ANOMALİ SİNYALİ:** 1 proje yetkisi → 47 repo / 4.7 GB hafta sonu  
**UYGULAMA ZORLUĞU:** kolay — Git audit olgun  
**ÖRNEK METRIK:** Dev: 1 repo/150 MB hafta → 47 repo / 4.7 GB

---

**İZLEME ADI:** Dosya Sunucusu Toplu Okuma/Yazma  
**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Windows Security 4663, NAS syslog, SMB audit  
**NE İZLENİYOR:** Share×kullanıcı×dosya sayısı×MB, DELETE/WRITE oranı  
**NEDEN DEĞERLI:** Toplu exfil ve ransomware hazırlığı  
**ANOMALİ SİNYALİ:** 1 saatte 120 dosya READ veya 200 GB DELETE  
**UYGULAMA ZORLUĞU:** orta — Log hacmi; share bazlı filtre  
**ÖRNEK METRIK:** Hukuk arşiv: 5–10 dosya/gün → 120 PDF / 3.2 GB

---

**İZLEME ADI:** ACL ve “Everyone” İzin Değişikliği  
**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Windows Security 4670, 4911, file server audit  
**NE İZLENİYOR:** Yeni ACE, inheritance kırılması, Everyone Read/Write  
**NEDEN DEĞERLI:** Kazara over-permission ve kalıcı açık kapı  
**ANOMALİ SİNYALİ:** Everyone Read on confidential share  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** PM share: özel ACL → Everyone Read (tek event)

---

**İZLEME ADI:** Mesai Dışı İnteraktif Oturum  
**KATEGORİ:** zamanlama  
**VERİ KAYNAĞI:** AD logon, VPN, RDP gateway, fiziksel badge (opsiyonel)  
**NE İZLENİYOR:** İlk/son aktivite saati, hafta sonu oturum süresi, gece 00–06 login  
**NEDEN DEĞERLI:** Insider ve compromise için güçlü bağlam sinyali  
**ANOMALİ SİNYALİ:** Rol median çıkış 18:00 → 02:30 RDP 3+ saat  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** Muhasebe: hiç gece login → Cuma 23:47 ERP erişim

---

**İZLEME ADI:** Oturum Süresi vs Klavye/Fare Aktivitesi (Boş Oturum)  
**KATEGORİ:** zamanlama  
**VERİ KAYNAĞI:** EDR, Windows session telemetry  
**NE İZLENİYOR:** Unlock süresi ile input event oranı; uzun idle + ağ aktivitesi  
**NEDEN DEĞERLI:** Unattended session abuse (temizlik, paylaşılan PC)  
**ANOMALİ SİNYALİ:** 4 saat idle oturum + sürekli SMB okuma  
**UYGULAMA ZORLUĞU:** zor — Input telemetry gizlilik  
**ÖRNEK METRIK:** Paylaşılan PC: unlock 8h, input 0.1h, SMB 2 GB

---

**İZLEME ADI:** Vardiya Dışı Fiziksel Erişim + Mantıksal Erişim  
**KATEGORİ:** çapraz veri  
**VERİ KAYNAĞI:** Badge/access control, AD, VPN  
**NE İZLENİYOR:** Bina giriş saati × aynı kullanıcı VPN/RDP zamanı  
**NEDEN DEĞERLI:** Çalıntı kart veya uzaktan compromise ayrımı  
**ANOMALİ SİNYALİ:** Gece 02:00 badge + aynı anda strateji sunucu 2 GB  
**UYGULAMA ZORLUĞU:** zor — Fiziksel sistem entegrasyonu  
**ÖRNEK METRIK:** CEO: badge 02:00 + file-srv 2 GB (board hazırlık vs anomali)

---

**İZLEME ADI:** Aynı Dosya/ Kayıt Çoklu Kullanıcı Erişim Zinciri  
**KATEGORİ:** çapraz veri  
**VERİ KAYNAĞI:** SMB audit + CRM/ERP uygulama log  
**NE İZLENİYOR:** Dosya hash veya kayıt ID × 10 dk içinde farklı departman erişimi  
**NEDEN DEĞERLI:** Collusion ve zincirleme sızıntı  
**ANOMALİ SİNYALİ:** Satış indirir → 10 dk sonra Hukuk aynı path  
**UYGULAMA ZORLUĞU:** orta — Ortak kimlik anahtarı (path/record ID)  
**ÖRNEK METRIK:** 2 kullanıcı / 1 dosya / 10 dk arayla

---

**İZLEME ADI:** DLP Agent Sağlık ve Bypass Denemesi  
**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** DLP management server, endpoint heartbeat  
**NE İZLENİYOR:** Agent stop/disable süresi, policy tamper, uninstall denemesi  
**NEDEN DEĞERLI:** Bilinçli önlem alma; stajyer/yeni çalışan profili  
**ANOMALİ SİNYALİ:** DLP 2+ saat offline mesai içi  
**UYGULAMA ZORLUĞU:** kolay — Vendor API  
**ÖRNEK METRIK:** Stajyer: agent uptime %99 → %60 / 2 saat gap

---

**İZLEME ADI:** Yerel Disk’e Prod Veri Restore  
**KATEGORİ:** çapraz veri  
**VERİ KAYNAĞI:** Backup software log, VSS, disk I/O telemetry  
**NE İZLENİYOR:** Workstation’a gelen büyük DB/VM image, prod hostname içeren path  
**NEDEN DEĞERLI:** Debug bahanesiyle prod veriyi endpoint’e taşıma  
**ANOMALİ SİNYALİ:** Laptop’a 15 GB prod-db restore  
**UYGULAMA ZORLUĞU:** orta — Backup tool log parse  
**ÖRNEK METRIK:** Dev disk: +15 GB prod-HR backup local

---

**İZLEME ADI:** Hypervisor ve Yönetim Konsolu Erişimi  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** vCenter/Proxmox audit, jump host session log  
**NE İZLENİYOR:** Kişisel AD hesabı vs ayrı admin hesabı, console session süresi  
**NEDEN DEĞERLI:** SoD ihlali ve altyapı compromise  
**ANOMALİ SİNYALİ:** Policy: sadece svc-hyperv-admin → kişisel hesap console  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** IT Admin: personal account HV console 45 dk

---

**İZLEME ADI:** İç Yazdırma/OCR Pipeline (Scan-to-Share)  
**KATEGORİ:** donanım  
**VERİ KAYNAĞI:** MFP audit log, SMB hedef path  
**NE İZLENİYOR:** Tarama hacmi, hedef share, kullanıcı PIN  
**NEDEN DEĞERLI:** Kağıt→dijital bypass kanalı  
**ANOMALİ SİNYALİ:** Günlük 500+ sayfa scan → legal-archive share  
**UYGULAMA ZORLUĞU:** orta — MFP merkezi log  
**ÖRNEK METRIK:** 20 sayfa/gün → 500 sayfa / legal share

---

**İZLEME ADI:** DHCP/ARP Anomali (Rogue DHCP)  
**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** Windows DHCP audit, switch SNMP trap, Zeek  
**NE İZLENİYOR:** Yeni scope, MAC spoof, aynı IP çift lease  
**NEDEN DEĞERLI:** MITM ve segment bypass hazırlığı  
**ANOMALİ SİNYALİ:** Onaysız office VLAN DHCP scope  
**UYGULAMA ZORLUĞU:** orta  
**ÖRNEK METRIK:** 1 DHCP scope değişikliği / change ticket yok

---

**İZLEME ADI:** Secret Store Okuma Burst  
**KATEGORİ:** kimlik  
**VERİ KAYNAĞI:** HashiCorp Vault audit, CyberArk session log  
**NE İZLENİYOR:** Kullanıcı×secret path×read count, bakım penceresi dışı  
**NEDEN DEĞERLI:** Credential enumeration ve exfil  
**ANOMALİ SİNYALİ:** 5 read/gün → 200 read / 1 saat  
**UYGULAMA ZORLUĞU:** kolay — Vault audit zengin  
**ÖRNEK METRIK:** IT Admin Vault: 5 → 200 secret read

---

**İZLEME ADI:** RDP/PSRemoting Jump Pattern  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** Windows 1149, Sysmon 3, jump server session broker  
**NE İZLENİYOR:** Hop sayısı (A→B→C), süre, hedef rol (DC, finans, backup)  
**NEDEN DEĞERLI:** Lateral movement ve destek prosedür ihlali  
**ANOMALİ SİNYALİ:** Destek → DC RDP veya 1 host → 6 sunucu PSRemoting  
**UYGULAMA ZORLUĞU:** orta  
**ÖRNEK METRIK:** Destek: 0 DC RDP/ay → 1 DC session 20 dk

---

**İZLEME ADI:** SIEM/Log Suppress Kural Değişimi  
**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** Splunk/Elastic/Wazuh manager audit  
**NE İZLENİYOR:** Yeni suppress/whitelist, bulk alert close, rule disable  
**NEDEN DEĞERLI:** Anti-forensics ve alert fatigue suistimali  
**ANOMALİ SİNYALİ:** Kullanıcı kendi host IP için suppress rule  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** SOC: 200 alert bulk close / investigation yok

---

**İZLEME ADI:** İç Ticket Sisteminde Hassas Alan Görüntüleme  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** ServiceNow/Jira audit, CRM field-level log  
**NE İZLENİYOR:** PCI alanı (kart), şifre, TCKN view event  
**NEDEN DEĞERLI:** Gereksiz PII maruziyeti ve PCI scope  
**ANOMALİ SİNYALİ:** Destek rolü CRM’de CC alanı view (ticket dışı)  
**UYGULAMA ZORLUĞU:** orta — Field-level audit her üründe yok  
**ÖRNEK METRIK:** 0 CC view/hafta → 12 view / 1 gün

---

**İZLEME ADI:** Yazılım Kurulum ve Lisans İhlali  
**KATEGORİ:** uygulama  
**VERİ KAYNAĞI:** SCCM/Intune inventory, Sysmon 1, software asset log  
**NE İZLENİYOR:** Yeni installer hash, EOL ürün, crack/tool imzası  
**NEDEN DEĞERLI:** Shadow IT ve malware girişi  
**ANOMALİ SİNYALİ:** Bilinmeyen .exe veya crack installer çalıştı  
**UYGULAMA ZORLUĞU:** kolay  
**ÖRNEK METRIK:** Analist: lisanslı Matlab → crack setup.exe çalıştı

---

**İZLEME ADI:** Printer/Scan → USB Korelasyonu  
**KATEGORİ:** çapraz veri  
**VERİ KAYNAĞI:** MFP log + USB Event + DLP  
**NE İZLENİYOR:** 10 dk içinde büyük scan ardından USB yazma  
**NEDEN DEĞERLI:** “Kağıt yok” exfil zinciri  
**ANOMALİ SİNYALİ:** 300 sayfa scan + 280 MB USB 8 dk sonra  
**UYGULAMA ZORLUĞU:** zor — Zaman penceresi korelasyon motoru  
**ÖRNEK METRIK:** Scan 300 sayfa → USB 280 MB / Δt=8 dk

---

**İZLEME ADI:** Offboarding SLA (Ayrılan Hesap Aktivitesi)  
**KATEGORİ:** zamanlama  
**VERİ KAYNAĞI:** İK HRIS feed + AD disable timestamp + VPN  
**NE İZLENİYOR:** Disable sonrası auth, disable öncesi veri ramp-up  
**NEDEN DEĞERLI:** Klasik insider ve süreç hatası  
**ANOMALİ SİNYALİ:** Disable +48h hâlâ VPN veya ayrılış öncesi 5 gün veri 15x  
**UYGULAMA ZORLUĞU:** orta — HRIS entegrasyonu  
**ÖRNEK METRIK:** İstifa−5 gün: 200 MB/gün → 3 GB/gün

---

Toplam **25 fikir**. Veri kaynağı dağılımı: ağ, kimlik, mail, FS, uygulama, endpoint (USB/yazıcı/clipboard/ekran), çapraz korelasyon ve zamanlama.

İstersen bir sonraki adımda bunları **adapter öncelik matrisi** (MVP / Faz-2) olarak da sıralayabilirim.