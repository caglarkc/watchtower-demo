# Watchtower UEBA — Final İzleme Kapasitesi Kataloğu

> [!IMPORTANT]
> **Klasör Ayrımı — Karıştırılmamalı**
>
> - **`watchtower-demo/`** = Bizzat inşa ettiğimiz **ürünün kendisi**. LLM destekli izleme ve uyarı CLI sistemi.
> - **`server-stack/`** = Bu ürünü test etmek için kurduğumuz **kapalı sunucu ortamı**. Simüle edilmiş şirket ağı.
>
> Bu dosya `server-stack` ortamında hangi davranışların izleneceğini tanımlar; `watchtower-demo` bu sinyalleri analiz eder.

**Toplam:** 81 izleme fikri | Kaynak: ChatGPT + Gemini + Composer çıktıları birleştirildi, tekrar edenler tekilleştirildi.  
**Amaç:** Bu liste senaryo değil; sistemin ölçmesi gereken davranışsal sinyal ve metrik önerilerini içerir.

**Kaynak notu:** `VERİ KAYNAĞI` satırlarında mümkün olduğunda önce **gerçek kurumsal kaynak**, sonra Watchtower demo ortamındaki **simülasyon karşılığı** düşünülmüştür. Faz 1 başlangıç kapsamı `Wazuh + AD + file/network login telemetry` ile sınırlıdır; mail ve bazı uygulama kaynakları Faz 2 kapsamındadır.

**Kategoriler:**
- [Ağ Trafiği](#ağ-trafiği) (7)
- [Kimlik ve Erişim](#kimlik-ve-erişim) (8)
- [Mail ve İletişim](#mail-ve-i̇letişim) (14)
- [Yapay Zeka Kullanımı](#yapay-zeka-kullanımı) (7)
- [Dosya Sistemi](#dosya-sistemi) (8)
- [Uygulama ve Süreç](#uygulama-ve-süreç) (10)
- [Donanım ve Uç Nokta](#donanım-ve-uç-nokta) (4)
- [Davranışsal](#davranışsal) (8)
- [Dış Bağlantı ve Çıkış Trafiği](#dış-bağlantı-ve-çıkış-trafiği) (3)
- [Çapraz Veri ve Korelasyon](#çapraz-veri-ve-korelasyon) (5)
- [İnsan Kaynakları ve Personel Yaşam Döngüsü](#i̇nsan-kaynakları-ve-personel-yaşam-döngüsü) (4)
- [Zamanlama](#zamanlama) (3)

Uygulama zorluğu: **Kolay / Orta / Zor**

---

## Ağ Trafiği

---

### F-001: Kullanıcı Başına SMB/Dosya Sunucu Veri Çekim Profili

**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** NetFlow, Zeek, Windows File Server audit, Sysmon  
**NE İZLENİYOR:** Her kullanıcının dosya sunucularından günlük/haftalık çektiği veri miktarı (MB/GB); dosya türü dağılımı  
**NEDEN DEĞERLI:** Veri sızdırma, iç tehdit, yanlış toplu kopyalama ve görev dışı erişimi erken gösterir. UEBA'nın çekirdek sinyali  
**ANOMALİ SİNYALİ:** Kullanıcının baseline'ına göre ani 5x–10x veri çekiş artışı; kısa sürede çok sayıda büyük dosya okunması; ilk kez erişilen sunucu  
**UYGULAMA ZORLUĞU:** Orta — kullanıcı kimliği ile ağ akışını eşlemek gerekir (AD session map)  
**ÖRNEK METRIK:** Normalde günde 800 MB okuyan kullanıcının bir günde 14 GB SMB read yapması

---

### F-002: East-West Lateral Protokol Pateni

**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** NetFlow, Zeek, firewall east-west log  
**NE İZLENİYOR:** SMB/445, RDP/3389, WinRM/5985, LDAP/389 bağlantı sayısı, hedef host çeşitliliği, iki workstation arası doğrudan yüksek hacimli transfer  
**NEDEN DEĞERLI:** APT yayılması, segmentasyon ihlali, ransomware bulaşmış makinelerin diğer bilgisayarları şifreleme girişimi veya P2P korsan paylaşımı  
**ANOMALİ SİNYALİ:** 15 dk'da 40+ farklı iç host'a SMB; iki istemci IP arası haftalık 5 MB'dan 8 GB'a tırmanan trafik  
**UYGULAMA ZORLUĞU:** Orta — Flow retention ve asset envanteri gerekir  
**ÖRNEK METRIK:** Destek PC: 2 SMB host/gün → 40 host / 15 dk

---

### F-003: İç DNS Sorgu Entropisi

**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** Windows DNS Server Analytical log, BIND query log  
**NE İZLENİYOR:** Kullanıcı/host başına QPS, TXT/NULL sorgu oranı, NXDOMAIN oranı, ardışık hostname sıralamaları  
**NEDEN DEĞERLI:** DNS tunneling ve C2 iletişimi iç ağda sık kullanılır; otomatik ağ taraması araçları keşif için yoğun DNS sorgusu üretir  
**ANOMALİ SİNYALİ:** TXT sorgu hacmi baseline'ın 100x; yüksek subdomain entropisi; kısa sürede 4.000 benzersiz hostname sorgusu  
**UYGULAMA ZORLUĞU:** Orta — client→user korelasyonu zor olabilir  
**ÖRNEK METRIK:** Dev workstation: 10 TXT/saat → 5.000 TXT/saat; saatlik 15 benzersiz sorgu → 3 dk içinde 4.000

---

### F-004: İç Ağda SMB/NTLM Sürüm Düşürme (Downgrade)

**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** Zeek, Wireshark, Core Switch Port Mirroring (PCAP)  
**NE İZLENİYOR:** Ağ içi dosya paylaşım protokollerinde eski ve zafiyetli sürümlerin (SMBv1, NTLMv1) kullanım zorlamaları  
**NEDEN DEĞERLI:** Saldırganların iç ağdaki parolaları ele geçirmek için başvurduğu MitM ve relay saldırılarını doğrudan yakalar  
**ANOMALİ SİNYALİ:** Normalde SMBv2/v3 kullanan iş istasyonunun aniden dosya sunucusuyla SMBv1 üzerinden konuşmak istemesi  
**UYGULAMA ZORLUĞU:** Zor — DPI ile ağ trafiği analizi ve sensör konumlandırması gerekir  
**ÖRNEK METRIK:** SMBv1 bağlantı talebi: 0/saat → 50/5 dk

---

### F-005: DHCP/ARP Anomalisi (Rogue DHCP)

**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** Windows DHCP audit, switch SNMP trap, Zeek  
**NE İZLENİYOR:** Yeni DHCP scope, MAC spoofing, aynı IP çift lease, onaysız VLAN DHCP değişikliği  
**NEDEN DEĞERLI:** MITM hazırlığı ve segment bypass; rogue DHCP sunucusu tüm segmenti trafiği dinleyebilir  
**ANOMALİ SİNYALİ:** Onaysız office VLAN'da DHCP scope değişikliği; change ticket yok  
**UYGULAMA ZORLUĞU:** Orta  
**ÖRNEK METRIK:** 1 DHCP scope değişikliği / change ticket yok

---

### F-006: Başarısız Login Patlaması Sonrası Başarılı Erişim

**KATEGORİ:** ağ trafiği (auth)  
**VERİ KAYNAĞI:** Windows Security Log, AD DC logs, LDAP auth logs  
**NE İZLENİYOR:** Tek bir kaynaktan çok sayıda failed login sonrası bir veya birkaç başarılı login; farklı kullanıcı adlarıyla ardışık denemeler (password spraying)  
**NEDEN DEĞERLI:** İç ağdaki brute-force, lateral movement veya credential stuffing girişimlerini net biçimde ortaya koyar  
**ANOMALİ SİNYALİ:** 10+ failed ardından success; 5 farklı hesap denendikten sonra 6.'da başarı; özellikle rol dışı hedef sistemlerde  
**UYGULAMA ZORLUĞU:** Kolay — kimlik doğrulama hatalarını kaynak IP'ye göre korele etmek yeterli  
**ÖRNEK METRIK:** 18 failed SMB auth → hukuk sunucusuna 1 başarılı erişim; 4625 logları ardından 4624

---

### F-007: İç Ağ Port Taraması ve Servis Keşfi

**KATEGORİ:** ağ trafiği  
**VERİ KAYNAĞI:** Zeek conn.log, NetFlow, firewall east-west log, EDR network telemetry  
**NE İZLENİYOR:** Tek host'un kısa sürede çok sayıda iç IP/port kombinasyonuna bağlantı denemesi; başarısız SYN yoğunluğu; servis banner keşfi  
**NEDEN DEĞERLI:** Lateral movement öncesindeki keşif adımını, yanlış yapılandırılmış tarama araçlarını ve ele geçirilmiş uç noktaları erken gösterir  
**ANOMALİ SİNYALİ:** Normalde 3-5 iç servise bağlanan kullanıcının 10 dakikada 200 host veya 1.000 port denemesi üretmesi  
**UYGULAMA ZORLUĞU:** Orta — port tarama ile meşru envanter taramasını asset/owner bilgisiyle ayırmak gerekir  
**ÖRNEK METRIK:** Satış laptop'u: 8 hedef/gün → 12 dakikada 180 iç host ve 25 farklı port

---

## Kimlik ve Erişim

---

### F-008: Kerberos / NTLM Auth Hacmi ve Hedef Çeşitliliği

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** Windows Security Log (4624, 4776), DC syslog  
**NE İZLENİYOR:** Saatlik başarılı/başarısız logon, kaynak IP çeşitliliği, TGT istek pateni, gece saatlerinde yoğunlaşma  
**NEDEN DEĞERLI:** Credential abuse, brute force, Pass-the-Hash (PtH) tespiti için birincil sinyal kaynağı  
**ANOMALİ SİNYALİ:** Başarısız logon 50+/dk; 1 kullanıcı → 8 farklı host gece TGT; lateral movement zinciri  
**UYGULAMA ZORLUĞU:** Orta — DC log hacmi yüksek; SIEM filtre ve korelasyon gerekir  
**ÖRNEK METRIK:** Admin: gece 02:00'de 0 TGT → 8 farklı sunucu TGT

---

### F-009: Eşzamanlı Oturum ve Bina İçi Lokasyon Çakışması

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** AD logon events, NAC, switch port mapping, badge/kartlı geçiş sistemi  
**NE İZLENİYOR:** Aynı kullanıcının fiziksel olarak uyumsuz iç lokasyonlardan eş zamanlı oturum açması  
**NEDEN DEĞERLI:** Hesap paylaşımı, açık bırakılmış oturum veya ele geçirilmiş oturum göstergesi; "bina içi impossible travel"  
**ANOMALİ SİNYALİ:** 10–20 dakika içinde iki farklı kat/segment/cihazda aktif çalışma  
**UYGULAMA ZORLUĞU:** Zor — fiziksel ve dijital sinyalleri birleştirmek gerekir  
**ÖRNEK METRIK:** CEO hesabının hem yönetici katı PC'de hem toplantı odası terminalinde aynı anda aktif olması; stajyer: 1 oturum → 2 workstation eşzamanlı

---

### F-010: Hizmet Hesaplarının İnteraktif Kullanımı

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** Active Directory / Windows Event Log (Logon Type 2 veya 10)  
**NE İZLENİYOR:** Sadece uygulamalar için ayrılmış hesapların insan tarafından RDP/interaktif oturum için kullanılması  
**NEDEN DEĞERLI:** Saldırganların veya izlenmek istemeyen adminlerin şifre politikalarından muaf servis hesaplarını suistimal etmesi  
**ANOMALİ SİNYALİ:** svc_backup veya sql_service gibi hesabın Logon Type 2 veya 10 ile login olması  
**UYGULAMA ZORLUĞU:** Kolay — Logon Type filtrelemesiyle doğrudan tespit edilir  
**ÖRNEK METRIK:** svc_db_sync: 0 interaktif logon/6 ay → 1 RDP oturumu

---

### F-011: AD Grup Üyeliği ve Privileged Değişiklik

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** Windows Security 4728/4729/4732, AD replication audit  
**NE İZLENİYOR:** Domain Admins, Enterprise Admins, hassas gruplara add/remove; onaysız değişiklikler  
**NEDEN DEĞERLI:** Privilege escalation ve shadow admin tespiti için kritik  
**ANOMALİ SİNYALİ:** Muhasebe hesabının DA grubuna ekleme denemesi; change ticket olmayan kritik grup değişikliği  
**UYGULAMA ZORLUĞU:** Kolay  
**ÖRNEK METRIK:** DA üye değişikliği: 0/ay → 1 başarısız deneme

---

### F-012: Servis Hesabı ve API Key Kullanım Haritası

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** API gateway log, HashiCorp Vault audit, uygulama access log  
**NE İZLENİYOR:** Key başına çağrı sayısı, kaynak IP çeşitliliği, endpoint, saat; eski/iptal edilmiş key kullanımı  
**NEDEN DEĞERLI:** Paylaşılan secret ve sızıntı sonrası abuse; rotate edilmemiş key keşfi  
**ANOMALİ SİNYALİ:** Tek key → 3+ farklı IP; rotate sonrası eski key hâlâ aktif; 47 gün sessizlikten sonra 1.200 çağrı  
**UYGULAMA ZORLUĞU:** Orta — her uygulama farklı log formatı  
**ÖRNEK METRIK:** svc-deploy key: 1 IP → 3 workstation; eski token: 0/47gün → 1.200/saat

---

### F-013: Secret Store Okuma Burst

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** HashiCorp Vault audit, CyberArk session log  
**NE İZLENİYOR:** Kullanıcı × secret path × read count; bakım penceresi dışı erişim; toplu enumeration  
**NEDEN DEĞERLI:** Credential enumeration ve exfil tespiti; hesap compromise veya kötü niyet  
**ANOMALİ SİNYALİ:** 5 read/gün → 200 read / 1 saat; bakım dışı saat  
**UYGULAMA ZORLUĞU:** Kolay — Vault audit log zengin  
**ÖRNEK METRIK:** IT Admin Vault: 5 → 200 secret read / bakım penceresi dışı

---

### F-014: Credential Reset ve Unlock Yoğunluğu

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** AD, IAM logs, helpdesk/ticket sistemi  
**NE İZLENİYOR:** Kim tarafından kaç hesabın reset/unlock edildiği ve ticket karşılığı olup olmadığı  
**NEDEN DEĞERLI:** İçeriden tehdit, yetki kötüye kullanımı ve sosyal mühendislik etkisini gösterir  
**ANOMALİ SİNYALİ:** Ticket olmadan çoklu reset; aynı admin'in kısa sürede çok hesap unlock etmesi  
**UYGULAMA ZORLUĞU:** Orta — ticket entegrasyonu gerekebilir  
**ÖRNEK METRIK:** 1 vardiyada 13 password reset, sadece 2 açık ticket

---

### F-015: RDP/PSRemoting Hop Pattern

**KATEGORİ:** kimlik ve erişim  
**VERİ KAYNAĞI:** Windows 1149, Sysmon 3, jump server session broker  
**NE İZLENİYOR:** Hop sayısı (A→B→C), süre, hedef sistem rolü (DC, finans, backup); zincirleme atlama  
**NEDEN DEĞERLI:** Lateral movement ve destek prosedür ihlali tespiti  
**ANOMALİ SİNYALİ:** Destek → DC RDP; 1 host → 6 sunucu PSRemoting zinciri  
**UYGULAMA ZORLUĞU:** Orta  
**ÖRNEK METRIK:** Destek: 0 DC RDP/ay → 1 DC session 20 dk

---

## Mail ve İletişim

---

### F-016: Dahili Mail Gönderim Hacmi ve Ek Boyutu

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Gerçek ortam: Exchange Message Tracking, EWS audit | Demo: Postfix/Dovecot SMTP-IMAP log  
**NE İZLENİYOR:** Günlük sent/received, ek boyutu, dağıtım listesi hedefi (DL/all-staff oranı), hassas keyword içeriği  
**NEDEN DEĞERLI:** Kazara sızıntı ve insider iletişim kanalı tespiti  
**ANOMALİ SİNYALİ:** All-staff mail + >5 MB ek; günlük gönderim 8x artış; normalde 4 alıcılı mailin 35 kişiye gitmesi  
**UYGULAMA ZORLUĞU:** Kolay — Exchange tarafında olgun, demo tarafta Postfix parser ile karşılanır  
**ÖRNEK METRIK:** Satış: 20 mail/gün → 1 mail tüm şirket + 8 MB fiyat listesi

---

### F-017: Mail Forward/Delegate Kural Değişimi

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Gerçek ortam: Exchange Management audit, EWS | Demo: Postfix/Roundcube rule-action logları + custom parser  
**NE İZLENİYOR:** Yeni inbox rule, auto-forward, delegate ekleme/silme; anahtar kelime filtreli kurallar  
**NEDEN DEĞERLI:** Gizli exfil ve hesap ele geçirme sonrası kalıcılık; sessiz veri toplama  
**ANOMALİ SİNYALİ:** İlk kez oluşturulan kural; gece oluşturulan filtré; "salary"/"contract"/"termination" keyword filtresi  
**UYGULAMA ZORLUĞU:** Kolay  
**ÖRNEK METRIK:** İK: forward rule 0 → 1 (kişisel iç mailbox); satış: aynı gün 3 yeni hassas keyword kuralı

---

### F-018: Dahili Mail Kutu Dışı Erişim

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Gerçek ortam: Exchange audit log, mailbox audit | Demo: Dovecot/Roundcube access log + SMTP log  
**NE İZLENİYOR:** Kullanıcının kendi kutusu dışındaki shared mailbox, delegated mailbox veya arşiv kutularına erişimi  
**NEDEN DEĞERLI:** İç yazışma keşfi, yetkisiz delegate kullanımı ve yönetici kutusu takibi  
**ANOMALİ SİNYALİ:** İlk kez erişilen mailbox'lar; kısa süreli ama yoğun içerik okuma; 15 dakikada 120 yönetim maili  
**UYGULAMA ZORLUĞU:** Orta — delegate ve shared access olaylarını normalize etmek gerekir  
**ÖRNEK METRIK:** Analist: kendi kutusu → 9 departman kutusu sorgu

---

### F-019: Mail Ek Entropi ve Dosya Tipi Uyuşmazlığı

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Gerçek ortam: Exchange Transport Agent, Mail Gateway logs | Demo: Postfix transport log + attachment metadata parser  
**NE İZLENİYOR:** İç ağda gönderilen e-posta eklerinde gerçek dosya türü (Magic Number) ile uzantı tutarlılığı ve şifreleme/sıkıştırma entropisi  
**NEDEN DEĞERLI:** DLP filtrelerini atlatmak için uzantı camouflage veya şifreli arşiv kullanımını yakalar  
**ANOMALİ SİNYALİ:** .txt görünen ek aslında şifreli .rar; manzara.png yüksek entropili Encrypted ZIP  
**UYGULAMA ZORLUĞU:** Orta — ek stream analizi veya metadata analizi gerekir  
**ÖRNEK METRIK:** Pazarlama personelinin iç mail ekinde yolladığı manzara.png: yüksek entropili encrypted ZIP

---

### F-020: Gizli Alıcı (BCC) ve Toplu Dağıtım Sapması

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Gerçek ortam: Exchange API | Demo: Postfix message tracking logs  
**NE İZLENİYOR:** Maillere eklenen BCC alıcı sayısı; alakasız departman çalışanlarının toplu mail zincirine dahil edilmesi  
**NEDEN DEĞERLI:** Hassas bilgiyi yöneticilerden gizli şekilde işbirlikçilere veya sahte iç hesaplara iletme taktiği  
**ANOMALİ SİNYALİ:** İki kişi arasında kalması gereken hassas mailin görünmez alıcılarla genişletilmesi; ilk kez 4 stajyerin BCC'de olması  
**UYGULAMA ZORLUĞU:** Kolay — transport log alıcı tipi ayrıştırması  
**ÖRNEK METRIK:** Hukuk müşavirinin 1 yılda ilk kez 4 stajyeri BCC'ye eklemesi

---

### F-021: Kişisel E-posta Adreslerine Ekli Posta Gönderimi

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Gerçek ortam: Exchange Message Tracking, mail gateway DLP | Demo: Postfix transport log + domain classifier  
**NE İZLENİYOR:** Kurumsal hesaptan gmail, hotmail, yahoo ve benzeri kişisel alan adlarına ek içeren posta gönderimi; ek türü ve boyutu  
**NEDEN DEĞERLI:** Kişisel posta kutuları kurumsal denetim dışıdır; veri sızdırma ve yanlış paylaşım için sık kullanılan çıkış yoludur  
**ANOMALİ SİNYALİ:** Daha önce kişisel adrese ek göndermeyen kullanıcının mesai dışı hassas ek göndermesi; ek boyutunda ani artış  
**UYGULAMA ZORLUĞU:** Kolay — alıcı domain sınıflandırması ve attachment metadata yeterlidir  
**ÖRNEK METRIK:** İK uzmanı: 0 kişisel ekli mail/90 gün → 22:40'ta gmail.com adresine 18 MB bordro eki

---

### F-022: Bilinmeyen veya Rakip Kuruluşa Ekli Posta Gönderimi

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Exchange/SMTP gateway logs, CRM/vendor domain envanteri, DLP sınıflandırması  
**NE İZLENİYOR:** Onaylı müşteri/tedarikçi listesinde olmayan veya rakip olabilecek harici domainlere ekli posta gönderimi  
**NEDEN DEĞERLI:** Rekabet hassasiyeti olan dosyaların yanlış veya kötü niyetli paylaşımını gösterir; satış, hukuk ve strateji ekipleri için kritik sinyaldir  
**ANOMALİ SİNYALİ:** İlk kez görülen harici domaine fiyat listesi, sözleşme, müşteri listesi veya ürün dokümanı gönderilmesi  
**UYGULAMA ZORLUĞU:** Orta — domain itibar listesi, müşteri/tedarikçi envanteri ve rakip listesi gerekir  
**ÖRNEK METRIK:** Satış: onaylı domain dışı ilk alıcı + 12 MB "pricing_2026.xlsx" eki

---

### F-023: Mail İçeriğinde Hassas Anahtar Kelime Sinyali

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Mail gateway content inspection, Exchange eDiscovery audit, DLP keyword policy  
**NE İZLENİYOR:** Konu satırı veya gövdede maaş, istifa, gizli, dava, rakip firma adı, birleşme, müşteri listesi gibi hassas kelimeler  
**NEDEN DEĞERLI:** İç tehdit ve yanlış paylaşım senaryolarında iletişim içeriği davranışsal bağlamı güçlendirir  
**ANOMALİ SİNYALİ:** Rol dışı kullanıcının hassas terimli maili geniş dağıtıma veya harici alıcıya göndermesi  
**UYGULAMA ZORLUĞU:** Orta — dil desteği, false positive azaltımı ve gizlilik politikası gerekir  
**ÖRNEK METRIK:** Destek kullanıcısı: "maaş" veya "dava" kelimesi 0/ay → 1 günde 7 harici mail

---

### F-024: Eski Mail Arşivinin Toplu Okunması

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Exchange mailbox audit, IMAP access log, archive mailbox audit  
**NE İZLENİYOR:** Uzun süredir erişilmeyen eski arşiv klasörlerinin kısa sürede toplu okunması, aranması veya export edilmesi  
**NEDEN DEĞERLI:** Yönetici yazışmaları, hukuki süreçler ve ticari sırlar eski arşivlerde yoğunlaşır; hesap ele geçirilmesi sonrası keşif davranışını gösterir  
**ANOMALİ SİNYALİ:** Yıllardır açılmayan arşiv klasöründen yüzlerce mailin dakikalar içinde okunması veya eklerinin indirilmesi  
**UYGULAMA ZORLUĞU:** Orta — mailbox audit olaylarını klasör yaşı ve kullanıcı baseline'ı ile eşlemek gerekir  
**ÖRNEK METRIK:** CEO arşivi: 0 erişim/2 yıl → 35 dakikada 1.200 mail read + 240 ek download

---

### F-025: Kişi Listesi veya Adres Defteri Dışa Aktarımı

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Exchange audit, EWS/Graph API audit, Roundcube/Dovecot export log  
**NE İZLENİYOR:** Kullanıcının kişisel kişi listesini, global adres defterini veya departman dağıtım listelerini dışa aktarması  
**NEDEN DEĞERLI:** Phishing hazırlığı, müşteri/çalışan listesi sızdırma ve ayrılış öncesi bilgi toplama davranışını gösterir  
**ANOMALİ SİNYALİ:** Daha önce export yapmamış kullanıcının yüzlerce kişi kaydını CSV/VCF olarak indirmesi  
**UYGULAMA ZORLUĞU:** Kolay — export event ve API çağrıları doğrudan izlenebilir  
**ÖRNEK METRIK:** Satış kullanıcısı: 0 contact export/1 yıl → 4.800 kayıt CSV export

---

### F-026: Yazışma Üslubu ve Dil Tonu Sapması

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Mail content metadata, NLP style baseline, güvenli içerik analiz pipeline'ı  
**NE İZLENİYOR:** Kullanıcının normal resmiyet seviyesi, dil tonu, yazım kalıpları, imza ve cümle uzunluğu profilinden sapması  
**NEDEN DEĞERLI:** Hesap ele geçirilmesi, sosyal mühendislik ve kullanıcı adına gönderilen sahte talimatları yakalamaya yardımcı olur  
**ANOMALİ SİNYALİ:** Normalde Türkçe ve resmi yazan kullanıcının ani İngilizce, kısa, baskıcı veya link odaklı yazışmaya geçmesi  
**UYGULAMA ZORLUĞU:** Zor — gizlilik, dil modeli kalitesi ve departman bağlamı dikkatli yönetilmelidir  
**ÖRNEK METRIK:** CFO hesabı: tipik 120 kelime resmi yazışma → 9 kelimelik acil ödeme talimatı + yeni alıcı

---

### F-027: Yasaklı veya Politika Dışı İfade Kullanımı

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Mail DLP, HR policy keyword list, eDiscovery audit  
**NE İZLENİYOR:** Tehdit, ayrımcı ifade, gizlilik ihlali riski taşıyan metin, kişisel veri paylaşımı veya şirket iletişim politikasıyla uyumsuz içerik  
**NEDEN DEĞERLI:** Hukuki risk, etik ihlal ve çalışan güvenliği açısından mail kanalı erken uyarı üretir  
**ANOMALİ SİNYALİ:** Hassas veya yasaklı ifadelerin yönetici, aday, müşteri veya geniş dağıtım listelerine gönderilmesi  
**UYGULAMA ZORLUĞU:** Orta — sözlük, bağlam analizi ve insan incelemesi gerektirir  
**ÖRNEK METRIK:** Bir kullanıcıdan 1 gün içinde 5 politika dışı ifade alarmı; 3'ü harici alıcılı

---

### F-028: İlk Kez Yazışılan Harici Alıcıya Hassas Konulu Mail

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Exchange/SMTP logs, mail graph history, DLP keyword classifier  
**NE İZLENİYOR:** Daha önce hiç yazışılmamış harici kişilere veya şirket çalışanı olmayan alıcılara hassas konu/ek içeren mail gönderimi  
**NEDEN DEĞERLI:** Hatalı alıcı seçimi, sahte tedarikçi dolandırıcılığı ve sızıntı girişimlerinde ilk temas paterni güçlü sinyaldir  
**ANOMALİ SİNYALİ:** İlk temas edilen domaine "gizli", "maaş", "dava", "strateji" veya müşteri verisi içeren mail gitmesi  
**UYGULAMA ZORLUĞU:** Orta — geçmiş yazışma grafı ve hassas içerik sınıflandırması gerekir  
**ÖRNEK METRIK:** Hukuk: ilk kez görülen alıcı + "dava dosyası" konusu + 24 MB ek

---

### F-029: Kurumsal Mail Sistemine Kişisel/Bilinmeyen Hesapla Giriş Denemesi

**KATEGORİ:** mail ve iletişim  
**VERİ KAYNAĞI:** Exchange/O365 sign-in logs, IMAP/SMTP auth logs, IdP audit  
**NE İZLENİYOR:** Kurumsal posta altyapısına kişisel, bilinmeyen veya şirket domaini dışındaki hesap kimliğiyle giriş denemesi  
**NEDEN DEĞERLI:** Yanlış yapılandırılmış istemci, kimlik avı sonrası otomasyon veya kurumsal posta sistemine yetkisiz kullanım girişimi göstergesidir  
**ANOMALİ SİNYALİ:** Şirket dışı hesapla IMAP/SMTP auth denemesi; aynı IP'den ardından geçerli kurumsal hesap denemeleri  
**UYGULAMA ZORLUĞU:** Kolay — authentication logları ve domain allowlist yeterlidir  
**ÖRNEK METRIK:** Aynı workstation: personalmail@gmail.com auth fail → 3 dakika sonra 12 kurumsal kullanıcı denemesi

---

## Yapay Zeka Kullanımı

---

### F-030: Harici Yapay Zeka Platformlarına Gizli Veri Gönderimi

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** Secure web gateway, CASB, DLP agent, browser telemetry  
**NE İZLENİYOR:** ChatGPT, Claude, Gemini ve benzeri harici AI platformlarına müşteri bilgisi, finansal veri, personel kaydı veya hukuki belge içeriği gönderimi  
**NEDEN DEĞERLI:** Kurumsal gizli verinin üçüncü taraf AI servislerine taşınması regülasyon, sözleşme ve veri sızıntısı riski üretir  
**ANOMALİ SİNYALİ:** Hassas sınıflı metin veya dosyanın onaysız AI domaine POST edilmesi; büyük prompt payload'ı  
**UYGULAMA ZORLUĞU:** Orta — TLS inspection, CASB veya endpoint DLP entegrasyonu gerekir  
**ÖRNEK METRIK:** Hukuk kullanıcısı: claude.ai'a 4.2 MB "dava_dosyasi.docx" içeriği gönderimi

---

### F-031: Kaynak Kod veya Sistem Mimarisi İçeriğinin AI Sohbetine Yapıştırılması

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** Browser DLP, clipboard telemetry, CASB, proxy request metadata  
**NE İZLENİYOR:** Dahili servis adları, bağlantı bilgileri, kaynak kod, mimari diyagram metni, iş mantığı veya secret içerebilecek kod parçalarının AI arayüzlerine gönderimi  
**NEDEN DEĞERLI:** Kod tabanı ve mimari bilgiler rekabet avantajı ve saldırı yüzeyi bilgisidir; geliştirici üretkenliği ile veri koruma dengesi kurulmalıdır  
**ANOMALİ SİNYALİ:** Repository dosya adı, internal hostname veya config içeren uzun prompt'ların onaysız AI servisine gönderilmesi  
**UYGULAMA ZORLUĞU:** Orta — kod/secret sınıflandırması ve geliştirici allowlist politikası gerekir  
**ÖRNEK METRIK:** Dev workstation: 1.800 satır config ve internal API route listesi chat.openai.com prompt payload'ında

---

### F-032: AI Prompt İçinde İç Sistem, Kullanıcı veya Ağ Bilgisi Geçmesi

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** CASB/DLP content inspection, proxy logs, browser extension telemetry  
**NE İZLENİYOR:** AI platformuna iletilen sorgularda iç sistem adı, kullanıcı adı, parola ipucu, IP adresi, subnet, sunucu rolü veya bağlantı string'i bulunması  
**NEDEN DEĞERLI:** Saldırgan için doğrudan keşif değeri taşıyan iç ağ bilgisinin dış servise taşınmasını gösterir  
**ANOMALİ SİNYALİ:** `10.x.x.x`, internal FQDN, servis hesabı adı veya parola ipucu içeren prompt; güvenlik prosedürüyle birlikte sorulması  
**UYGULAMA ZORLUĞU:** Orta — regex, entity extraction ve false positive kontrolü gerekir  
**ÖRNEK METRIK:** Prompt içinde 14 internal hostname + 3 servis hesabı adı + "password reset procedure"

---

### F-033: Onaylanmamış AI Araçlarının Kurumsal Ağdan Kullanımı

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** Proxy/SWG logs, DNS logs, CASB SaaS discovery  
**NE İZLENİYOR:** Şirket politikasında tanımlanmamış AI domainlerine erişim, yeni AI SaaS kullanımı, kişisel hesapla AI servisi oturumu  
**NEDEN DEĞERLI:** Gölge AI kullanımı veri işleme koşulları bilinmeyen platformlara hassas veri taşınmasına neden olur  
**ANOMALİ SİNYALİ:** İlk kez görülen AI domaine yüksek hacimli POST; departman politikasında olmayan servis kullanımı  
**UYGULAMA ZORLUĞU:** Kolay — domain kategorisi ve SaaS allowlist ile izlenebilir  
**ÖRNEK METRIK:** Pazarlama kullanıcısı: onaysız ai-writer.example domaine 600 MB upload / 1 gün

---

### F-034: AI Platformlarına Dosya Yükleme Hacmi ve İçerik Türü

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** CASB, secure web gateway, endpoint DLP, browser upload telemetry  
**NE İZLENİYOR:** AI platformuna yüklenen dosyaların boyutu, türü, sınıflandırması ve toplu belge/dataset aktarımı  
**NEDEN DEĞERLI:** Prompt metninden daha yüksek riskli olan dosya yüklemeleri, tam doküman ve veri seti sızıntısına yol açabilir  
**ANOMALİ SİNYALİ:** Kısa sürede çok sayıda PDF/XLSX/CSV upload; confidential etiketli dosyanın AI servisine yüklenmesi  
**UYGULAMA ZORLUĞU:** Orta — upload metadata ve DLP sınıflandırması gerekir  
**ÖRNEK METRIK:** Analist: 45 CSV dosyası / 1.6 GB dataset upload to AI platform

---

### F-035: AI ile Şirket Süreçleri ve Güvenlik Prosedürü Keşfi

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** CASB/DLP content inspection, browser history telemetry, security search audit  
**NE İZLENİYOR:** AI aracına şirket süreçleri, yetkiler, güvenlik prosedürleri, erişim onay akışı veya sistem zayıflıkları hakkında detaylı soru sorulması  
**NEDEN DEĞERLI:** İçeriden keşif, sosyal mühendislik hazırlığı veya yeni başlayan bir kullanıcının rol dışı sistem öğrenme girişimi olabilir  
**ANOMALİ SİNYALİ:** "VPN onayı nasıl aşılır", "kim hangi payroll yetkisine sahip" gibi şirket bağlamlı prosedür sorguları  
**UYGULAMA ZORLUĞU:** Zor — niyet analizi ve meşru destek/öğrenme senaryolarını ayırmak gerekir  
**ÖRNEK METRIK:** Stajyer hesabı: 30 dakikada 12 şirket güvenlik prosedürü sorgusu + iç sistem adları

---

### F-036: AI Konuşma Geçmişinde Rekabet, Strateji veya Hukuki Süreç İçeriği

**KATEGORİ:** yapay zeka kullanımı  
**VERİ KAYNAĞI:** Kurumsal onaylı AI tenant audit, CASB, DLP review queue  
**NE İZLENİYOR:** AI konuşmalarında rakip firma adları, stratejik planlar, birleşme/satın alma, devam eden dava veya regülasyon incelemesi içeriği  
**NEDEN DEĞERLI:** Stratejik veya hukuki hassasiyet taşıyan konuların dış AI sistemlerinde işlenmesi üst seviye kurumsal risk oluşturur  
**ANOMALİ SİNYALİ:** Rakip adı + strateji dokümanı + yönetici rolü kombinasyonu; hukuki dosya özetletme girişimi  
**UYGULAMA ZORLUĞU:** Orta — onaylı AI tenant audit varsa kolaylaşır, kişisel AI kullanımı için CASB gerekir  
**ÖRNEK METRIK:** Strateji ekibi kullanıcısı: 9 prompt içinde 3 rakip firma adı + "2026 pricing plan"

---

## Dosya Sistemi

---

### F-037: Departman Dışı Dosya Paylaşım Erişimi

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Windows Event Log, File Server audit log, AD grup üyelikleri  
**NE İZLENİYOR:** Kullanıcının kendi departmanı dışındaki paylaşımlı klasörlere erişim sayısı; ilk kez erişilen hassas klasörler  
**NEDEN DEĞERLI:** Yetkisiz erişim, merak amaçlı gezinme ve yanlış yetki kalıntılarını ortaya çıkarır  
**ANOMALİ SİNYALİ:** İlk kez erişilen hassas klasörler; kısa sürede birden çok departman klasöründe gezinme  
**UYGULAMA ZORLUĞU:** Orta — erişim olaylarını departman/rol bilgisiyle eşlemek gerekir  
**ÖRNEK METRIK:** Satış çalışanının aynı gün hukuk, İK ve muhasebe paylaşımlarında 37 dosya açması

---

### F-038: Dosya Sunucu Toplu Okuma/Yazma Oranı

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Windows Security 4663, NAS syslog, SMB audit  
**NE İZLENİYOR:** Share × kullanıcı × dosya sayısı × MB; DELETE/WRITE oranı; read:write sapması (keşif vs. normal iş)  
**NEDEN DEĞERLI:** Toplu exfil, ransomware hazırlığı ve sessiz keşif aşaması tespiti  
**ANOMALİ SİNYALİ:** 1 saatte 120 dosya READ; read:write oranı 2:1'den 40:1'e; 200 GB DELETE normal rotasyon dışı  
**UYGULAMA ZORLUĞU:** Orta — log hacmi; share bazlı filtre gerekir  
**ÖRNEK METRIK:** Hukuk arşiv: 5–10 dosya/gün → 120 PDF / 3.2 GB

---

### F-039: Kitlesel Dosya Yeniden Adlandırma Hızı

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Dosya Sunucu audit log (File Server Auditing / Syslog)  
**NE İZLENİYOR:** Ortak ağ sürücülerinde saniyede değiştirilen, silinen veya uzantısı manipüle edilen dosya sayısı  
**NEDEN DEĞERLI:** Fidye yazılımlarının ağ paylaşımlarındaki dosyaları şifrelemeye başladığı ilk kritik saniyeleri yakalar  
**ANOMALİ SİNYALİ:** Saniyede 50+ dosya uzantısı değişimi; .locked/.crypto formatlarına toplu dönüşüm  
**UYGULAMA ZORLUĞU:** Orta — büyük file server'larda yüksek log hacmi; performans optimizasyonu gerekir  
**ÖRNEK METRIK:** Normal dosya işlem hızı dakikada 4 → 10 saniyede 500 PDF yeniden adlandırma

---

### F-040: Hassas Dizin Dolaşma (Directory Traversal) Davranışı

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Windows Object Access Auditing, Linux Auditd  
**NE İZLENİYOR:** Kullanıcının daha önce hiç açmadığı alt klasörlere ardışık girip çıkması; içerik açmadan yalnızca dosya adı listeleme (metadata discovery)  
**NEDEN DEĞERLI:** Veri hırsızlığı öncesi değerli bilgi arayan keşifçi personeli; içerik erişimi az ama yüzlerce list/enum işlemi  
**ANOMALİ SİNYALİ:** PM'in 1 yılda sadece 3 klasörle çalışmışken 1 saatte 120 farklı proje klasörünü listelemesi; 20 dk'da 900 file list, sadece 3 dosya open  
**UYGULAMA ZORLUĞU:** Orta — LLM'in erişilen dosya yollarının semantik benzerliğini anlaması gerekir  
**ÖRNEK METRIK:** İçerik erişimi az: 600 read, 8 write, 0 normal iş çıktısı

---

### F-041: ACL ve "Everyone" İzin Değişikliği

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Windows Security 4670, 4911, file server audit  
**NE İZLENİYOR:** Yeni ACE, inheritance kırılması, Everyone Read/Write eklenmesi; confidential share üzerinde izin genişlemesi  
**NEDEN DEĞERLI:** Kazara over-permission, kalıcı açık kapı, kolaylaştırılmış exfil  
**ANOMALİ SİNYALİ:** Confidential share'e Everyone Read eklenmesi; change ticket yok  
**UYGULAMA ZORLUĞU:** Kolay  
**ÖRNEK METRIK:** PM share: özel ACL → Everyone Read (tek event)

---

### F-042: Yerel Diskte Hassas Veri Birikimi

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** DLP agent, EDR file inventory, Windows file auditing  
**NE İZLENİYOR:** Endpoint üzerinde lokal klasörlere düşen hassas belge hacmi ve türü (Documents/Desktop/Temp)  
**NEDEN DEĞERLI:** Network share yerine lokal cache veya staging alanı oluşturulması veri sızıntısına hazırlık olabilir  
**ANOMALİ SİNYALİ:** Kısa sürede 6 GB sözleşme ve maaş dosyası birikmesi; prod-db backup local restore  
**UYGULAMA ZORLUĞU:** Orta — içerik sınıflandırma ve endpoint toplama gerekir  
**ÖRNEK METRIK:** Dev disk: +15 GB prod-HR backup local; analist: 2 saatte 6 GB sözleşme

---

### F-043: Etiketli Hassas Dosyanın Kısıtsız Alana Taşınması

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** DLP label audit, Microsoft Purview/MIP logs, file server audit, EDR file telemetry  
**NE İZLENİYOR:** Gizli, dahili veya regülasyon kapsamlı etiket taşıyan dosyanın public share, herkesin eriştiği klasör, kişisel desktop veya geçici alana kopyalanması/taşınması  
**NEDEN DEĞERLI:** Dosya içeriği sızdırılmadan önce erişim sınırı gevşetilir; yanlış paylaşım ve bilinçli staging davranışı için güçlü sinyaldir  
**ANOMALİ SİNYALİ:** Confidential label'lı dosyanın Everyone Read olan klasöre veya departman dışı ortak alana bırakılması  
**UYGULAMA ZORLUĞU:** Orta — label metadata ile dosya hareket loglarını eşlemek gerekir  
**ÖRNEK METRIK:** "Gizli" etiketli 37 bordro dosyası → public-share/temp klasörüne 12 dakikada kopyalandı

---

### F-044: Bilgi Bankası/Wiki/Intranet Toplu İndirme

**KATEGORİ:** dosya sistemi  
**VERİ KAYNAĞI:** Confluence/SharePoint/wiki audit, intranet web logs, reverse proxy logs  
**NE İZLENİYOR:** İç bilgi bankası, wiki veya intranet portalından kullanıcı başına sayfa görüntüleme, dosya indirme, export ve arama hacmi  
**NEDEN DEĞERLI:** Kurumsal süreç, müşteri, mimari ve operasyon bilgisinin toplu toplanması insider veya hesap ele geçirilmesi sinyalidir  
**ANOMALİ SİNYALİ:** Rolüyle ilgisiz alanlarda kısa sürede yüzlerce sayfa okuma veya attachment download; space export denemesi  
**UYGULAMA ZORLUĞU:** Orta — uygulama audit loglarının normalize edilmesi gerekir  
**ÖRNEK METRIK:** Yeni danışman: 1 saatte 420 wiki sayfası + 88 ek dosya download

---

## Uygulama ve Süreç

---

### F-045: Veritabanı Sorgu Hacmi ve Tablo Kapsamı

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** SQL Server audit, PostgreSQL pg_audit, proxy query log  
**NE İZLENİYOR:** Kullanıcı × DB × günlük satır/MB; SELECT * oranı; tablo adı çeşitliliği; tek sorguda dönen veri boyutu  
**NEDEN DEĞERLI:** Uygulama arayüzünden tek tek bakış yerine arka planda script ile tüm DB'yi dump eden insider tehdidi  
**ANOMALİ SİNYALİ:** Tek sorguda *employees* veya 890 MB result set; günlük 5.000 satır → tek sorguda 2.000.000 satır  
**UYGULAMA ZORLUĞU:** Orta — DB audit performans etkisi dikkatli yönetilmeli  
**ÖRNEK METRIK:** İK payroll: 2–5 MB/sorgu → 890 MB export; analist: 5.000 satır/gün → 2M satır tek sorgu

---

### F-046: Uygulama Süresi ve Süreç Ağacı

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** Sysmon (1/3), Wazuh syscheck, EDR process telemetry  
**NE İZLENİYOR:** SAP, Jira, Excel, VS Code, Steam vb. günlük aktif süre; parent-child süreç ilişkisi; rol dışı uygulama kullanımı  
**NEDEN DEĞERLI:** Politika ihlali, shadow IT ve zararlı makro/script tespiti  
**ANOMALİ SİNYALİ:** Muhasebe cihazında IDE 4 saat; Excel.exe'nin altında powershell.exe -EncodedCommand; Steam mesai içi  
**UYGULAMA ZORLUĞU:** Orta — process allowlist bakımı ve her uygulamanın meşru alt süreç modellemesi gerekir  
**ÖRNEK METRIK:** İK Winword.exe → powershell.exe -ExecutionPolicy Bypass; geliştirici: VS Code 6h + Steam 4h aynı gün

---

### F-047: İç API Çağrı Deseni Sapması

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** API gateway logs, reverse proxy logs, app audit logs  
**NE İZLENİYOR:** Kullanıcı veya servis bazında endpoint, çağrı sıklığı, response size, method tipi; ilk kez erişilen endpoint aileleri  
**NEDEN DEĞERLI:** Toplu veri çekme, yetki dışı endpoint denemesi ve eski token kullanımı  
**ANOMALİ SİNYALİ:** Günde 20 çağrıdan 1 saatte 1.100 GET/export isteğine; response size sıçraması  
**UYGULAMA ZORLUĞU:** Orta — kullanıcı kimliği ile app loglarını düzgün bağlamak gerekir  
**ÖRNEK METRIK:** Normalde 20 çağrı/gün → 1 saatte 1.100 GET/export

---

### F-048: HTTP 4xx Hata Yoğunlaşması

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** İç web sunucu / API Gateway logs (Nginx, IIS, WAF)  
**NE İZLENİYOR:** Bir kullanıcının iç API uç noktalarına istek atarken aldığı 401/403 hatalarının toplam istek oranına göre yüzdesi  
**NEDEN DEĞERLI:** İç ağdaki IDOR/BOLA zafiyetlerini kurcalayan teknik personel veya sızdırılmış araçları gösterir  
**ANOMALİ SİNYALİ:** Toplam istekler içinde hata kodu alma oranının %1'den %80'e çıkması  
**UYGULAMA ZORLUĞU:** Kolay — HTTP status code parsing yeterli  
**ÖRNEK METRIK:** Yazılımcı → İK API: 5 dk içinde 300 adet HTTP 403

---

### F-049: Git/Artifact Erişim ve Clone Hacmi

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** Gerçek ortam: self-hosted Git audit log | Demo: Gitea audit log, reverse proxy, git-mirror NetFlow  
**NE İZLENİYOR:** Clone/pull GB; erişilen repo sayısı; yetkili dışı repo erişimi; push denemesi  
**NEDEN DEĞERLI:** Kaynak kod ve secret sızıntısı; ayrılış öncesi IP biriktirme  
**ANOMALİ SİNYALİ:** 1 proje yetkisi → 47 repo / 4.7 GB hafta sonu; gece saatlerinde yoğun clone aktivitesi  
**UYGULAMA ZORLUĞU:** Kolay — Git audit log olgun  
**ÖRNEK METRIK:** Dev: 1 repo/150 MB hafta → 47 repo / 4.7 GB

---

### F-050: SIEM/Log Suppress Kural Değişimi

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** Splunk/Elastic/Wazuh manager audit  
**NE İZLENİYOR:** Yeni suppress/whitelist, toplu alert kapatma, rule disable; kendi host IP için eklenen kural  
**NEDEN DEĞERLI:** Anti-forensics ve alert fatigue suistimali; kendi ihlalini gizleme girişimi  
**ANOMALİ SİNYALİ:** Kullanıcı kendi host IP için suppress rule ekliyor; 200 alert toplu kapatma / investigation yok  
**UYGULAMA ZORLUĞU:** Kolay  
**ÖRNEK METRIK:** SOC: 200 alert bulk close / investigation yok; self-suppress kural

---

### F-051: Hypervisor ve Yönetim Konsolu Erişimi

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** vCenter/Proxmox audit, jump host session log  
**NE İZLENİYOR:** Kişisel AD hesabı vs ayrı admin hesabı; console session süresi; SoD (Separation of Duties) ihlali  
**NEDEN DEĞERLI:** Altyapı compromise ve SoD ihlali  
**ANOMALİ SİNYALİ:** Policy: sadece svc-hyperv-admin → kişisel hesap HV console  
**UYGULAMA ZORLUĞU:** Kolay  
**ÖRNEK METRIK:** IT Admin: personal account HV console 45 dk

---

### F-052: Yeni Zamanlanmış Görev veya Sistem Servisi Oluşturulması

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** Windows Security/System logs, Sysmon Event ID 1/12/13, Wazuh/Sysmon telemetry  
**NE İZLENİYOR:** Kullanıcı makinesinde veya sunucuda yeni scheduled task, Windows service, cron job veya launch agent oluşturulması; tetikleyici ve çalıştırılan komut  
**NEDEN DEĞERLI:** Kalıcılık mekanizması, otomatik veri toplama ve zararlı yazılım sürekliliği için kullanılan temel tekniktir  
**ANOMALİ SİNYALİ:** Normal kullanıcı hesabıyla SYSTEM yetkili servis oluşturma; geçici klasörden çalışan task; mesai dışı yeni görev  
**UYGULAMA ZORLUĞU:** Kolay — event log ve Sysmon ile doğrudan izlenebilir  
**ÖRNEK METRIK:** Muhasebe PC'si: 0 task oluşturma/6 ay → "Updater" adlı task her 5 dakikada PowerShell çalıştırıyor

---

### F-053: Yedekleme Gölge Kopyalarının Silinmesi veya Devre Dışı Bırakılması

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** Windows Event Log, Sysmon process command line, backup platform audit  
**NE İZLENİYOR:** Volume Shadow Copy silme, backup job durdurma, snapshot retention azaltma, `vssadmin`, `wbadmin`, `bcdedit` ve benzeri komutların kullanımı  
**NEDEN DEĞERLI:** Fidye yazılımı saldırılarında şifreleme öncesi en erken ve en kritik hazırlık adımlarından biridir  
**ANOMALİ SİNYALİ:** Kullanıcı endpoint'inde veya file server'da shadow copy delete komutu; backup servisi policy dışı durdurma  
**UYGULAMA ZORLUĞU:** Kolay — komut satırı ve servis olayları yüksek sinyal taşır  
**ÖRNEK METRIK:** File server: `vssadmin delete shadows /all` + 2 dakika sonra kitlesel rename başlangıcı

---

### F-054: Kodlanmış veya Politika Atlatan Betik Komutları

**KATEGORİ:** uygulama ve süreç  
**VERİ KAYNAĞI:** Sysmon Event ID 1, PowerShell Script Block Logging, Wazuh command telemetry  
**NE İZLENİYOR:** `-EncodedCommand`, `-ExecutionPolicy Bypass`, obfuscation, base64 payload, LOLBin kullanımı ve şüpheli parent process ilişkileri  
**NEDEN DEĞERLI:** Zararlı betik çalıştırma, credential dumping hazırlığı ve makro kaynaklı istismarların ortak göstergesidir  
**ANOMALİ SİNYALİ:** Office uygulaması altından encoded PowerShell; normal kullanıcı cihazında policy bypass komutu  
**UYGULAMA ZORLUĞU:** Orta — komut normalizasyonu ve allowlist gerekir  
**ÖRNEK METRIK:** Winword.exe → powershell.exe `-ExecutionPolicy Bypass -EncodedCommand` / ilk kez görülen hash

---

## Donanım ve Uç Nokta

---

### F-055: USB Takma-Yazma Korelasyonu

**KATEGORİ:** donanım ve uç nokta  
**VERİ KAYNAĞI:** Windows Event Log (6416, 4663), EDR/DLP agent  
**NE İZLENİYOR:** USB takılma/çıkarma, cihaz VID/PID, hedef dosyalar ve yazılan toplam MB; insert sonrası write zaman korelasyonu  
**NEDEN DEĞERLI:** Fiziksel veri sızdırma ve kötü amaçlı yazılım taşıma için doğrudan sinyal; en klasik exfil kanalı  
**ANOMALİ SİNYALİ:** Rol baseline'ının 5x üstü tek sefer yazma; yasaklı cihaz sınıfı; USB takıldıktan 3 dk sonra 8.7 GB PDF/XLSX  
**UYGULAMA ZORLUĞU:** Orta — EDR/DLP gerekir; ham Event Log tek başına yetersiz  
**ÖRNEK METRIK:** Satış: ayda 0 USB yazma → 2.1 GB / 14 dk; CFO: USB olayı 0 → 1.8 GB

---

### F-056: Yazıcı İş Hacmi ve Hassas Belge Korelasyonu

**KATEGORİ:** donanım ve uç nokta  
**VERİ KAYNAĞI:** Windows Print Service Log (Event ID 307/801), yazıcı SNMP/syslog  
**NE İZLENİYOR:** Kullanıcı başına sayfa sayısı, "confidential/legal" kuyruk seçimi, belge tipi ve adı; MFP scan-to-share hedefi  
**NEDEN DEĞERLI:** Kağıt üzerinden fiziksel veri sızdırma; kağıt→dijital bypass kanalı (scan-to-share)  
**ANOMALİ SİNYALİ:** Gece vardiyasında confidential kuyruğa 200+ sayfa; normalde 5 sayfa/gün olan stajyerden 200 sayfa; scan 300 sayfa → USB 280 MB 8 dk sonra  
**UYGULAMA ZORLUĞU:** Orta — kuyruk adlandırma standardı ve MFP merkezi log gerekir  
**ÖRNEK METRIK:** Satış: 15 sayfa/ay → 350 sayfalık döküman tek sefer; İK: 1 saatte 340 sayfa personel dosyası

---

### F-057: Ağ Kartı Promiscuous Mod Değişimi

**KATEGORİ:** donanım ve uç nokta  
**VERİ KAYNAĞI:** Windows Security Log (Event ID 7045), Linux syslog  
**NE İZLENİYOR:** Kullanıcı bilgisayarındaki ağ kartının tüm trafiği dinleyecek promiscuous moda geçirilmesi  
**NEDEN DEĞERLI:** İç ağda habersizce çalıştırılan Wireshark, Ettercap gibi sniffing araçlarını doğrudan yakalar  
**ANOMALİ SİNYALİ:** İş istasyonundaki ağ sürücüsünün monitoring moduna evrilmesi  
**UYGULAMA ZORLUĞU:** Zor — kernel-level olay izleme gerekir  
**ÖRNEK METRIK:** Ethernet kartı promiscuous mode: 0 (Kapalı) → 1 (Açık)

---

### F-058: DLP Agent Sağlık ve Bypass Denemesi

**KATEGORİ:** donanım ve uç nokta  
**VERİ KAYNAĞI:** DLP management server, endpoint heartbeat  
**NE İZLENİYOR:** Agent stop/disable süresi, policy tamper, uninstall denemesi; mesai içi uzun offline süre  
**NEDEN DEĞERLI:** Bilinçli önlem alma; DLP'yi devre dışı bırakıp ardından veri aktarımı paterni  
**ANOMALİ SİNYALİ:** DLP 2+ saat offline mesai içi; agent uptime %99 → %60  
**UYGULAMA ZORLUĞU:** Kolay — vendor API heartbeat  
**ÖRNEK METRIK:** Stajyer: agent uptime %99 → %60 / 2 saat gap

---

## Davranışsal

---

### F-059: Clipboard Büyük Veri Kopyalama

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** DLP endpoint agent, Windows ETW (Clipboard API), Sysmon Event ID 24  
**NE İZLENİYOR:** Panoya kopyalanan veri boyutu, kaynak uygulama (CRM, Excel, DB client), hedef uygulama (chat, RDP, editor)  
**NEDEN DEĞERLI:** Mail/USB olmadan veri taşıma; DLP'yi atlayan görünmez exfil kanalı  
**ANOMALİ SİNYALİ:** Tek oturumda 50+ MB clipboard; hassas uygulama → chat/RDP yapıştırma; bordro ekranından 48.000 karakter kopyalama  
**UYGULAMA ZORLUĞU:** Zor — OS/agent desteği ve gizlilik politikası gerekir  
**ÖRNEK METRIK:** 10 dk içinde 3× 20 MB CRM→Teams yapıştırma; bordro uygulamasından 48.000 karakterlik tablo kopyalama

---

### F-060: Ekran Görüntüsü Alma Frekansı

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** EDR, Windows Graphics Capture API telemetry, OS hook telemetry  
**NE İZLENİYOR:** Saatlik capture event sayısı, hedef process (Snipping Tool, 3rd party), hassas uygulama açıkken alınan screenshot sayısı  
**NEDEN DEĞERLI:** Dosya kopyalamadan hassas içerik toplama; DLP sistemlerini atlayan görsel exfil  
**ANOMALİ SİNYALİ:** CRM/ERP uygulaması etkileşim halindeyken ardışık ve hızlı screenshot; finans uygulaması açıkken saatte 30+ capture  
**UYGULAMA ZORLUĞU:** Zor — agent yetkinliği ve false positive azaltımı gerekir  
**ÖRNEK METRIK:** CFO ekranında 6 dakikada 17 screenshot; muhasebe: haftalık 2 screenshot → maaş excel'i açıkken 10 dk'da 15 screenshot

---

### F-061: Rol Bazlı Sunucu Temas Haritası

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** NetFlow, Sysmon network connections, Windows logs  
**NE İZLENİYOR:** Her rolün tipik olarak temas ettiği sunucu seti ve bu setten sapmalar; ilk kez erişilen kritik sunucular  
**NEDEN DEĞERLI:** Yetkisiz erişim, lateral movement ve yanlış yapılandırma tespiti için çok değerlidir  
**ANOMALİ SİNYALİ:** Stajyer hesabının 1 günde 11 farklı iç sunucuya bağlanması; satış kullanıcısında ilk kez psexec.exe ve powershell.exe -EncodedCommand  
**UYGULAMA ZORLUĞU:** Orta — role-aware baseline gerekir  
**ÖRNEK METRIK:** Stajyer: normalde 1–2 sunucu → 1 günde 11 farklı iç sunucu

---

### F-062: İç Log Arama Anahtar Kelimesi Riski

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** SIEM search audit, log platform query logs, Wazuh/Kibana audit  
**NE İZLENİYOR:** Kullanıcıların log/arama platformunda kullandığı sorgu terimleri; hassas kelime kümelenmesi  
**NEDEN DEĞERLI:** Secret avı, maaş araması, işten çıkarma bilgisi veya hedefli keşif davranışını ortaya çıkarır  
**ANOMALİ SİNYALİ:** "password", "salary", "termination", "token", "discipline" gibi hassas kelimelerin rol dışı kullanıcılarca aranması  
**UYGULAMA ZORLUĞU:** Orta — query audit ve bağlamsal eşleme gerekir  
**ÖRNEK METRIK:** Destek personelinin 1 gün içinde 9 kez "salary" ve "bonus" sorgusu yapması

---

### F-063: Daha Önce Görülmemiş Donanım Kimliğiyle Oturum Denemesi

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** IdP device inventory, EDR asset ID, NAC, AD logon events  
**NE İZLENİYOR:** Kullanıcı hesabıyla daha önce ilişkilendirilmemiş cihaz seri numarası, hardware hash, MAC veya EDR asset ID üzerinden oturum açma denemesi  
**NEDEN DEĞERLI:** Çalıntı kimlik bilgisi, yetkisiz cihaz kullanımı ve kurumsal cihaz envanteri dışı erişim için güçlü sinyaldir  
**ANOMALİ SİNYALİ:** Kullanıcının ilk kez görülen donanımdan hassas uygulama, VPN veya dosya sunucusuna erişmeye çalışması  
**UYGULAMA ZORLUĞU:** Orta — kimlik, cihaz envanteri ve NAC kayıtlarını eşlemek gerekir  
**ÖRNEK METRIK:** CFO hesabı: 0 yeni cihaz/1 yıl → bilinmeyen laptop hardware ID ile 3 failed + 1 successful login

---

### F-064: Normal Aktivite Örüntüsünün Saatler İçinde Yoğunlaşması

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** UEBA baseline store, AD/app/file/network telemetry  
**NE İZLENİYOR:** Haftalara yayılan normal işlem hacminin birkaç saatlik pencereye sıkışması; login, dosya, mail, API ve sorgu olaylarının zaman yoğunluğu  
**NEDEN DEĞERLI:** Ayrılış öncesi veri toplama, hesap ele geçirilmesi veya otomasyonla toplu işlem davranışı için çapraz sinyal üretir  
**ANOMALİ SİNYALİ:** Kullanıcının aylık ortalama dosya okuma, mail export veya API çağrı hacmini tek mesai dışı oturumda üretmesi  
**UYGULAMA ZORLUĞU:** Orta — uzun dönem baseline ve pencere bazlı yoğunluk skoru gerekir  
**ÖRNEK METRIK:** 30 günlük toplam wiki download hacminin %80'i cuma 22:00-23:30 arasında gerçekleşti

---

### F-065: Uzun Süre Kullanılmayan Sistemlere Ani Erişim

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** AD logon, app audit, NetFlow, IAM access logs  
**NE İZLENİYOR:** Kullanıcının daha önce hiç girmediği veya uzun süredir kullanmadığı sistem, sunucu, uygulama veya veri alanlarına ani erişimi  
**NEDEN DEĞERLI:** Keşif, yetki kalıntısı suistimali ve ele geçirilmiş hesapla değerli sistem arama davranışını gösterir  
**ANOMALİ SİNYALİ:** 180+ gündür erişilmeyen uygulamaya mesai dışı giriş; ilk kez kritik sunucuya bağlantı  
**UYGULAMA ZORLUĞU:** Kolay — last-seen ve first-seen kayıtlarıyla izlenebilir  
**ÖRNEK METRIK:** Satış hesabı: ilk kez backup console login + 8 dakika sonra file server yoğun okuma

---

### F-066: Akran Grup Davranışından İstatistiksel Sapma

**KATEGORİ:** davranışsal  
**VERİ KAYNAĞI:** UEBA baseline store, HR/department metadata, telemetry warehouse  
**NE İZLENİYOR:** Aynı departman, rol, kıdem ve lokasyondaki kullanıcı grubuna göre dosya, mail, login, uygulama ve veri hacmi sapmaları  
**NEDEN DEĞERLI:** Kişisel baseline yeni veya zayıf olduğunda peer-group kıyası yanlış yetki, insider ve compromise sinyalini güçlendirir  
**ANOMALİ SİNYALİ:** Aynı roldeki kullanıcıların p95 değerinin çok üstünde veri çekme, gece login veya harici paylaşım davranışı  
**UYGULAMA ZORLUĞU:** Orta — doğru akran grubu tanımı ve istatistiksel eşik gerekir  
**ÖRNEK METRIK:** Aynı roldeki 18 analiste göre p99 üstü: 12x daha fazla DB row export + 6x daha fazla harici mail eki

---

## Dış Bağlantı ve Çıkış Trafiği

---

### F-067: Kişisel Bulut Depolama Hizmetlerine Büyük Dosya Yükleme

**KATEGORİ:** dış bağlantı ve çıkış trafiği  
**VERİ KAYNAĞI:** Proxy/SWG logs, CASB, firewall egress logs, DLP agent  
**NE İZLENİYOR:** Google Drive, Dropbox, OneDrive personal, iCloud, WeTransfer ve benzeri kişisel bulut hizmetlerine upload hacmi, dosya türü ve kullanıcı ilişkisi  
**NEDEN DEĞERLI:** Kurumsal denetim dışı bulut hesapları veri sızdırma ve yanlış paylaşım için ana çıkış kanallarından biridir  
**ANOMALİ SİNYALİ:** Departman baseline'ının üstünde upload; confidential etiketli dosya; kişisel hesap oturumu üzerinden transfer  
**UYGULAMA ZORLUĞU:** Orta — CASB veya TLS-aware proxy görünürlüğü gerekir  
**ÖRNEK METRIK:** Finans kullanıcısı: drive.google.com personal upload 0 → 7.4 GB / 40 dk

---

### F-068: İlk Kez Görülen Harici Adrese Yüksek Hacimli Veri Transferi

**KATEGORİ:** dış bağlantı ve çıkış trafiği  
**VERİ KAYNAĞI:** NetFlow, firewall egress logs, proxy logs, DNS logs  
**NE İZLENİYOR:** Kurumsal ağdan daha önce hiç bağlanılmamış harici IP/domainlere yüksek hacimli upload veya uzun süreli bağlantı  
**NEDEN DEĞERLI:** Yeni C2, geçici dosya paylaşımı, kişisel VPS veya rakip/üçüncü taraf servislerine veri çıkışını yakalar  
**ANOMALİ SİNYALİ:** First-seen domain veya ASN'ye kısa sürede GB seviyesinde outbound veri; DNS yaşı düşük domain  
**UYGULAMA ZORLUĞU:** Orta — first-seen takibi, ASN/domain zenginleştirme ve upload/download ayrımı gerekir  
**ÖRNEK METRIK:** İlk kez görülen `files-transfer.example`: 3.2 GB outbound / 18 dk / tek kullanıcı

---

### F-069: Proxy Üzerinden Şifreli Tünel veya Alışılmadık Protokol Kullanımı

**KATEGORİ:** dış bağlantı ve çıkış trafiği  
**VERİ KAYNAĞI:** Proxy/SWG logs, firewall app-ID, Zeek, DNS logs  
**NE İZLENİYOR:** CONNECT tüneli, SSH-over-HTTPS, DoH, VPN/proxy bypass araçları, alışılmadık port/protokol ve yüksek entropili uzun oturumlar  
**NEDEN DEĞERLI:** Denetimden kaçırılmış veri çıkışı, C2 iletişimi ve politika ihlali için ortak yöntemdir  
**ANOMALİ SİNYALİ:** Standart web trafiği gibi görünen ama uzun süreli, sabit upload üreten tünel; yasaklı VPN/proxy domainleri  
**UYGULAMA ZORLUĞU:** Zor — protokol parmak izi ve false positive azaltımı gerekir  
**ÖRNEK METRIK:** Tek workstation: 6 saat kesintisiz CONNECT tunnel + 1.8 GB outbound + bilinmeyen ASN

---

## Çapraz Veri ve Korelasyon

---

### F-070: Fiziksel Badge Geçişi ile Sistem Login Uyuşmazlığı

**KATEGORİ:** çapraz veri ve korelasyon  
**VERİ KAYNAĞI:** Fiziksel erişim sistemi SQL logu, AD logon events, NAC  
**NE İZLENİYOR:** Çalışanın binaya giriş/çıkış durumu ile dijital erişimlerinin tutarlılığı; badge kaydı yokken workstation logon  
**NEDEN DEĞERLI:** Hesap paylaşımı, açık oturum kullanımı, iç dolandırıcılık ve deprovisioning sorunları  
**ANOMALİ SİNYALİ:** Binaya hiç girmemiş kullanıcının dahili segmentten aktif görünmesi; 09:12 workstation logon / badge kaydı yok  
**UYGULAMA ZORLUĞU:** Zor — saat senkronu ve veri eşleme gerekir  
**ÖRNEK METRIK:** Badge kaydı yokken 09:12'de workstation logon ve dosya erişimi; muhasebe terminalinde gece login / ofis dışı

---

### F-071: Çapraz Kaynak Risk Skoru (Composite Risk Score)

**KATEGORİ:** çapraz veri ve korelasyon  
**VERİ KAYNAĞI:** SIEM, AD, NetFlow, mail audit, EDR, badge sistemi  
**NE İZLENİYOR:** Tek kullanıcının kısa zaman penceresinde birden fazla riskli sinyal üretmesi; sinyal ağırlıklı bileşik skor  
**NEDEN DEĞERLI:** Tek tek düşük önem taşıyan olaylar birleşince gerçek ihlali işaret eder; gerçek ihlallerin büyük çoğunluğu bu zincir şeklinde gelişir  
**ANOMALİ SİNYALİ:** Mesai dışı login + USB takılması + büyük SMB okuma + hassas mail eki çıkarımı zinciri; 45 dk içinde 4 yüksek riskli sinyal  
**UYGULAMA ZORLUĞU:** Zor — korelasyon, ağırlıklandırma ve iyi baseline gerekir  
**ÖRNEK METRIK:** 45 dakikada 4 yüksek riskli sinyal üreten kullanıcı için composite risk score 92/100

---

### F-072: Offboarding SLA — Ayrılan Hesap Aktivitesi

**KATEGORİ:** çapraz veri ve korelasyon  
**VERİ KAYNAĞI:** İK HRIS feed, AD disable timestamp, VPN, dosya sunucu log  
**NE İZLENİYOR:** Disable sonrası auth girişimleri; disable öncesi veri ramp-up; İK istifa bildirimi × dijital aktivite korelasyonu  
**NEDEN DEĞERLI:** Klasik insider tehdit ve hesap lifecycle ihlali  
**ANOMALİ SİNYALİ:** Disable +48h hâlâ VPN aktif; ayrılış öncesi 5 günde veri 15x artış; istifa bildirimi sonraki 48h'de son 30 günün toplamı kadar indirme  
**UYGULAMA ZORLUĞU:** Orta — HRIS entegrasyonu şart  
**ÖRNEK METRIK:** İstifa -5 gün: 200 MB/gün → 3 GB/gün; ayrılan hesap +6 gün hâlâ aktif

---

### F-073: Aynı Dosya/Kayıt Çoklu Kullanıcı Erişim Zinciri

**KATEGORİ:** çapraz veri ve korelasyon  
**VERİ KAYNAĞI:** SMB audit, CRM/ERP uygulama log  
**NE İZLENİYOR:** Dosya hash veya kayıt ID × 10 dakika içinde farklı departman kullanıcı erişimi  
**NEDEN DEĞERLI:** Collusion ve zincirleme veri sızıntısı tespiti  
**ANOMALİ SİNYALİ:** Satış indirir → 10 dk sonra Hukuk aynı path; ardından yeniden adlandırılmış hali başka paylaşımda  
**UYGULAMA ZORLUĞU:** Orta — ortak kimlik anahtarı (path/record ID) gerekir  
**ÖRNEK METRIK:** 2 kullanıcı / 1 hassas dosya / 10 dk arayla; 3. kullanıcı yeniden adlandırılmış kopyayla

---

### F-074: Vardiya Dışı Fiziksel + Mantıksal Erişim Korelasyonu

**KATEGORİ:** çapraz veri ve korelasyon  
**VERİ KAYNAĞI:** Badge/access control, AD, VPN  
**NE İZLENİYOR:** Bina giriş saati × aynı kullanıcı VPN/RDP zamanı; gece badge + büyük veri aktarımı  
**NEDEN DEĞERLI:** Çalıntı kart ile uzaktan compromise ayrımı; gece fiziksel+dijital birlikteliği güçlü ihlal sinyali  
**ANOMALİ SİNYALİ:** Gece 02:00 badge + aynı anda strateji sunucu 2 GB; veya gece 02:00 RDP ama badge yok  
**UYGULAMA ZORLUĞU:** Zor — fiziksel sistem entegrasyonu ve saat senkronu gerekir  
**ÖRNEK METRIK:** CEO: badge 02:00 + file-srv 2 GB (board hazırlık kontrol gerekir)

---

## İnsan Kaynakları ve Personel Yaşam Döngüsü

---

### F-075: Yeni Çalışanın İlk Günlerde Aşırı Sistem Erişimi

**KATEGORİ:** insan kaynakları ve personel yaşam döngüsü  
**VERİ KAYNAĞI:** HRIS onboarding feed, AD/IAM logs, app audit, file server audit  
**NE İZLENİYOR:** Yeni işe başlayan çalışanın ilk günlerinde eriştiği sistem sayısı, veri hacmi, yetki kullanımı ve departman dışı temasları  
**NEDEN DEĞERLI:** Yanlış yetki ataması, hesap paylaşımı, kötü niyetli onboarding veya sosyal mühendislik etkisini erken gösterir  
**ANOMALİ SİNYALİ:** İlk hafta rolüyle ilgisiz çok sayıda sisteme hızlı erişim; hassas klasör veya uygulama export denemesi  
**UYGULAMA ZORLUĞU:** Orta — HRIS başlangıç tarihi ve rol/department baseline gerekir  
**ÖRNEK METRIK:** Yeni stajyer: ilk 2 günde 18 uygulama, 11 file share, 4.5 GB download

---

### F-076: Rol Değişikliği Sonrası Eski Yetkilerin Kullanılması

**KATEGORİ:** insan kaynakları ve personel yaşam döngüsü  
**VERİ KAYNAĞI:** HRIS role-change feed, AD group membership, IAM audit, app access logs  
**NE İZLENİYOR:** Rol değişikliği veya terfi sonrası kaldırılması gereken eski grup/yetkilerle erişimin sürmesi ve bu yetkilerin aktif kullanımı  
**NEDEN DEĞERLI:** Yetki kalıntıları least privilege ihlalidir; çalışan iyi niyetli olsa bile veri kapsamı gereksiz genişler  
**ANOMALİ SİNYALİ:** Eski departman paylaşımına erişim, önceki rolün yönetim paneli veya eski müşteri portföyü export'u  
**UYGULAMA ZORLUĞU:** Orta — HRIS role timeline ile IAM yetki durumunu karşılaştırmak gerekir  
**ÖRNEK METRIK:** Satıştan pazarlamaya geçen kullanıcı: 30 gün sonra hâlâ CRM fiyat onay panelinde 42 işlem

---

### F-077: Resmi İzin Kaydı Varken Sistem Aktivitesi

**KATEGORİ:** insan kaynakları ve personel yaşam döngüsü  
**VERİ KAYNAĞI:** HRIS leave records, AD/VPN/app logs, badge sistemi  
**NE İZLENİYOR:** Resmi izin, hastalık izni veya seyahat kaydı olan kullanıcının kurumsal sistem, ağ veya fiziksel erişim aktivitesinin devam etmesi  
**NEDEN DEĞERLI:** Hesap paylaşımı, açık oturum suistimali, ele geçirilmiş hesap veya politika dışı çalışma düzenini gösterir  
**ANOMALİ SİNYALİ:** İzinli kullanıcıdan mesai saatinde VPN, dosya sunucu veya ERP işlemi; aynı gün badge kaydı olmaması  
**UYGULAMA ZORLUĞU:** Orta — HRIS izin takvimi ve dijital olayların saat/durum eşleşmesi gerekir  
**ÖRNEK METRIK:** İzinli İK uzmanı: 13:20'de payroll export + badge kaydı yok + 2 GB download

---

### F-078: Üçüncü Taraf/Yüklenici Kapsam Dışı Sistem Kullanımı

**KATEGORİ:** insan kaynakları ve personel yaşam döngüsü  
**VERİ KAYNAĞI:** Vendor/contractor registry, IAM entitlements, app audit, VPN logs  
**NE İZLENİYOR:** Danışman veya yüklenici hesabının sözleşme kapsamı dışındaki sistem, zaman aralığı, veri sınıfı veya departman alanlarını kullanması  
**NEDEN DEĞERLI:** Üçüncü taraf hesapları yüksek risklidir; kapsam dışı kullanım veri sızıntısı ve tedarik zinciri ihlali oluşturabilir  
**ANOMALİ SİNYALİ:** Sözleşme bitişi sonrası aktif oturum, kapsam dışı uygulama, gece erişim veya beklenmeyen veri çekişi  
**UYGULAMA ZORLUĞU:** Orta — sözleşme kapsamı makine-okunur hale getirilmelidir  
**ÖRNEK METRIK:** Network danışmanı: sadece VPN cihazları yetkisi varken HR file share üzerinde 600 MB read

---

## Zamanlama

---

### F-079: Mesai Dışı İnteraktif Oturum

**KATEGORİ:** zamanlama  
**VERİ KAYNAĞI:** AD logon, VPN, RDP gateway, fiziksel badge (opsiyonel)  
**NE İZLENİYOR:** İlk/son aktivite saati; hafta sonu oturum süresi; gece 00–06 login  
**NEDEN DEĞERLI:** Insider ve compromise için güçlü bağlam sinyali; gece aktivitesi saldırı window'u  
**ANOMALİ SİNYALİ:** Rol median çıkış 18:00 → 02:30 RDP 3+ saat; 3 yıl 09-18 çalışan kullanıcı → salı gecesi 03:15 2 saat kesintisiz  
**UYGULAMA ZORLUĞU:** Kolay  
**ÖRNEK METRIK:** Muhasebe: hiç gece login yok → Cuma 23:47 ERP erişim; haftalık gece aktivite skoru %0 → 02:00–05:00 arası 180 erişim

---

### F-080: Oturum Süresi vs Klavye/Fare Aktivitesi (Boş Oturum Suistimali)

**KATEGORİ:** zamanlama  
**VERİ KAYNAĞI:** EDR, Windows session telemetry  
**NE İZLENİYOR:** Unlock süresi ile input event oranı; uzun idle süresinin ardından ağ aktivitesi  
**NEDEN DEĞERLI:** Unattended session abuse (temizlik personeli, paylaşılan PC); oturum devralınması  
**ANOMALİ SİNYALİ:** 4 saat idle oturum + sürekli SMB okuma; 7 saat idle kalan oturumdan sonra 10 dk içinde hukuk klasörü erişimi  
**UYGULAMA ZORLUĞU:** Zor — input telemetry gizlilik dengesi gerekir  
**ÖRNEK METRIK:** Paylaşılan PC: unlock 8h, input 0.1h, SMB 2 GB; CEO oturumu 7h idle → hukuk klasörü

---

### F-081: Rol Bazlı Aktif Çalışma Penceresi Sapması

**KATEGORİ:** zamanlama  
**VERİ KAYNAĞI:** Windows etkinlik günlükleri, uygulama erişim logları  
**NE İZLENİYOR:** Kullanıcının aktif olduğu saatlerin standart dağılımı (Gaussian); gün/saat bazında sistemik sapma  
**NEDEN DEĞERLI:** Belirli bir departmanın çalışma kültürüne tamamen zıt zaman dilimlerinde gerçekleşen olağan dışı aktivite; bot veya hesap ele geçirme  
**ANOMALİ SİNYALİ:** İK/Satış kullanıcısı salı gecesi 03:15'te 2 saat kesintisiz işlem; İK pazar 6 saat özlük sistemi kullanımı  
**UYGULAMA ZORLUĞU:** Kolay — timestamp baseline LLM veya istatistiksel model ile çıkarılabilir  
**ÖRNEK METRIK:** Haftalık gece aktivite skoru %0 olan kullanıcı → 02:00–05:00 arası 180 ardışık sistem erişim isteği

---

*Bu katalog Watchtower UEBA sisteminin LangGraph pipeline'ına, baseline motoruna ve alert kurallarına girdi olarak kullanılacaktır. Her feature için veri kaynağı bağlantısı ve uygulama zorluğu tasarım önceliklendirmesini destekler.*
