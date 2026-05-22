# Watchtower UEBA — Tool Stack ve Altyapı Gereksinimleri

> [!IMPORTANT]
> **Klasör Ayrımı — Karıştırılmamalı**
>
> - **`watchtower-demo/`** = Bizzat inşa ettiğimiz **ürünün kendisi**. LLM destekli izleme ve uyarı CLI sistemi.
> - **`server-stack/`** = Bu ürünü test etmek için kurduğumuz **kapalı sunucu ortamı**. Simüle edilmiş şirket ağı.
>
> Bu dosya `server-stack` ortamını ayağa kaldırmak için gereken araç ve servisleri listeler.

**Amaç:** 83 senaryo ve 40 izleme kapasitesini karşılamak için gereken TÜM araç ve hizmetlerin sistematik listesi.  
**Ortam:** Kapalı iç ağ (Private LAN) — internet bağlantısı zorunlu değil.  
**İki boyut:** Her araç için (1) **Gerçek Dağıtım** ve (2) **Simülasyon (Docker)** seçeneği verilmiştir.

---

## Kurumsal Gerçeklik: Hibrit OS Mimarisi

Kurumsal ölçekte pratik gerçeklik tek işletim sistemi değil, **ikili yapı**dır. THY, banka, telekom ve benzeri yapılarda:

- **Kimlik ve kullanıcı yönetimi katmanı** çoğunlukla `Windows Server + Active Directory`
- **Uygulama, servis ve veri katmanı** çoğunlukla `Linux` (`RHEL`, `Ubuntu`, bazen `Rocky/CentOS`)

Bu ayrım Watchtower için teorik değil, doğrudan ürün tasarımı kararıdır. Çünkü aynı kurum içinde hem `Windows Event ID` tabanlı kimlik olayları hem de `auditd/syslog/JSON` tabanlı Linux servis olayları birlikte akar.

### Katman Bazlı OS Dağılımı

| Katman | Baskın OS | Watchtower açısından anlamı |
|--------|-----------|-----------------------------|
| Kimlik / Domain | Windows Server | AD logon, grup üyeliği, Kerberos, GPO ve ayrıcalıklı değişiklik olayları |
| Uygulama / Backend | Linux (RHEL/Ubuntu) | PostgreSQL, Nginx, Git, mail, API, container ve servis logları |
| Kullanıcı Uç Noktaları | Çoğunlukla Windows | Çalışan davranışı, USB, process, print, interactive login sinyalleri |
| Özel Roller | Mac / Linux | Geliştirici ve DevOps istasyonları için ek audit/journald/syslog yolları |

### Neden Kritik?

Watchtower tek tip log bekleyemez. Aynı kurum içinde:

- Domain Controller `4624`, `4625`, `4728`, `6416` gibi **Windows Event ID** üretir
- Linux servisleri `auditd`, `journald`, `syslog`, `JSON access log` üretir
- Kullanıcı davranışı korelasyonu bu iki veri ailesini aynı olay modelinde birleştirmeyi gerektirir

```
┌─────────────────────────────────────────────────────────────┐
│  GERÇEK KURUMSAL AĞ OS DAĞILIMI                             │
├──────────────────────┬──────────────────────────────────────┤
│  Windows Server      │  Active Directory Domain Controller   │
│  (Kimlik katmanı)    │  Neredeyse tüm kurumsal ortam         │
│                      │  → Event ID 4624/4625/4663/4728/6416  │
│                      │  → Kerberos TGT/TGS logları           │
├──────────────────────┼──────────────────────────────────────┤
│  Linux (RHEL/Ubuntu) │  Uygulama ve servis sunucuları        │
│  (Servis katmanı)    │  Endüstri standardı (RHEL, Ubuntu)    │
│                      │  → PostgreSQL, Nginx, Git, Mail, API  │
│                      │  → auditd, syslog, journald           │
├──────────────────────┼──────────────────────────────────────┤
│  Kullanıcı           │  Windows laptop/masaüstü → çoğunluk  │
│  Workstation'ları    │  Mac → geliştirici/tasarım ekipleri   │
│                      │  Linux → DevOps/sysadmin              │
└──────────────────────┴──────────────────────────────────────┘
```

**Watchtower için kritik çıkarım:** Log toplama katmanında **iki ayrı normalizasyon yolu** zorunludur:

- **Windows path:** DC'den gelen Windows Event XML → Event ID bazlı parse
- **Linux path:** App server'lardan gelen auditd/syslog/JSON → key bazlı parse

Bu iki yol LangGraph `EventNormalizer` node'unda birleşir ve ortak `WatchtowerEvent` schema'sına dönüştürülür. Detaylar → Bölüm 9 (UEBA Core) ve Bölüm 15 (Normalizasyon Tasarımı).

---

## Özet Tablo

| Katman | Araç/Sistem | Öncelik | Docker Sim. | Ücretsiz? |
|--------|------------|---------|-------------|-----------|
| Mail | Postfix + Dovecot + Roundcube | **Kritik** | ✅ | ✅ |
| Identity | Samba4 AD / OpenLDAP | **Kritik** | ✅ | ✅ |
| File Server | Samba (SMB) + Audit | **Kritik** | ✅ | ✅ |
| Endpoint Agent | Wazuh Agent + Sysmon | **Kritik** | ✅ | ✅ |
| SIEM/UEBA | Wazuh Server + ELK Stack | **Kritik** | ✅ | ✅ |
| Ağ Capture | Zeek (Bro) | **Kritik** | ✅ | ✅ |
| NetFlow | ntopng / nfdump | Yüksek | ✅ | ✅ |
| DNS Server | BIND9 + Query Log | **Kritik** | ✅ | ✅ |
| Git / Kod Repo | Gitea | Yüksek | ✅ | ✅ |
| Veritabanı | PostgreSQL + pg_audit | **Kritik** | ✅ | ✅ |
| Secret/Vault | HashiCorp Vault | Yüksek | ✅ | ✅ |
| Print Server | CUPS + audit | Orta | ✅ | ✅ |
| Badge Sistemi | Mock REST API | Orta | ✅ | ✅ |
| CRM | SuiteCRM | Orta | ✅ | ✅ |
| Messaging | Mattermost (iç chat) | Orta | ✅ | ✅ |
| Hypervisor | Proxmox / KVM audit | Orta | Kısmi | ✅ |
| DHCP Server | ISC DHCP + log | Yüksek | ✅ | ✅ |
| Kullanıcı Simülatörü | Python event_generator | **Kritik** | ✅ | ✅ |
| Log Toplayıcı | Filebeat + Logstash | **Kritik** | ✅ | ✅ |
| API Gateway | nginx + access log | Yüksek | ✅ | ✅ |

---

## 1. KİMLİK VE ERİŞİM KATMANI

### 1.1 Samba4 Active Directory Domain Controller

> **Gerçek ortam karşılığı:** Windows Server + Active Directory Domain Services. Kurumsal ağlarda kimlik katmanı pratikte çoğunlukla bu yapıdadır. Samba4 bunu Docker'da simüle eder; log formatı ve Event ID mantığı korunur.

**Ne için:**
- Windows AD simülasyonu; kullanıcı hesapları, grup üyelikleri, OU yapısı
- Kerberos TGT logları (S-016, F-007)
- AD grup değişikliği tespiti (S-030, S-034, F-010)
- Logon Type 2/10 — servis hesabı interaktif kullanım (S-019, F-009)
- Event ID: 4624 (başarılı login), 4625 (başarısız), 4728/4729 (grup değişikliği), 4776

**Simülasyon:**
```yaml
# docker-compose.yml
samba-ad:
  image: nowsci/samba-domain
  environment:
    DOMAIN: CORP
    DOMAINPASS: Watchtower1!
  ports:
    - "389:389"   # LDAP
    - "636:636"   # LDAPS
    - "88:88"     # Kerberos
```

**Log formatı:** Windows Event Log (JSON via winlogbeat veya wazuh-agent)

**Gerçek ortamda:** Windows Server + Active Directory Domain Services

---

### 1.2 OpenLDAP (Hafif kimlik doğrulama)

**Ne için:**
- Samba yetersiz kaldığında ek LDAP sorgulama
- LDAP bulk bind anomalisi (S-011, F-007)
- Servis hesapları için ayrı OU

**Simülasyon:**
```yaml
openldap:
  image: osixia/openldap:latest
  environment:
    LDAP_ORGANISATION: "Corp"
    LDAP_DOMAIN: "corp.local"
```

---

### 1.3 HashiCorp Vault

**Ne için:**
- Secret store burst tespiti (F-012, S-017)
- API key ve token yaşam döngüsü izleme
- Eski/iptal edilmiş token kullanımı (S-021)
- Vault audit log → her read/write event JSON olarak yazılır

**Simülasyon:**
```yaml
vault:
  image: vault:latest
  cap_add: [IPC_LOCK]
  environment:
    VAULT_DEV_ROOT_TOKEN_ID: "root-token"
  ports:
    - "8200:8200"
```

**Kritik log:** `vault audit enable file file_path=/vault/logs/audit.log`

---

## 2. MAIL VE İLETİŞİM KATMANI

### 2.1 Postfix (SMTP) + Dovecot (IMAP/POP3) + Roundcube (Webmail)

**Ne için:**
- Kapalı LAN'da şirket içi mail sistemi
- Mail gönderim hacmi izleme (F-015)
- Forward/delegate kural tespiti (F-016, S-027)
- BCC anomalisi (F-019)
- Mail ek entropi analizi (F-018)
- Kutu dışı erişim (F-017)
- Sahte dahili mail (S-077, S-079)

**Simülasyon:**
```yaml
mailserver:
  image: docker.io/mailserver/docker-mailserver:latest
  hostname: mail.corp.local
  ports:
    - "25:25"    # SMTP
    - "143:143"  # IMAP
    - "587:587"  # Submission
  volumes:
    - ./mail-data:/var/mail
    - ./mail-logs:/var/log/mail
```

**Log kaynakları:**
- `/var/log/mail.log` — SMTP transaction log
- Dovecot IMAP audit: `mail_log_prefix`, `log_path`
- Exchange benzeri audit için: Postfix + custom log parser

**Roundcube (webmail arayüzü):**
```yaml
roundcube:
  image: roundcube/roundcubemail:latest
  environment:
    ROUNDCUBEMAIL_DEFAULT_HOST: mail.corp.local
  ports:
    - "8080:80"
```

**İzlenen event örnekleri:**
```
# Postfix mail.log
May 22 02:17:33 mail postfix/smtp[1234]: to=<all@corp.local>, 
  from=<ik@corp.local>, size=850234, status=sent
```

---

### 2.2 Mattermost (İç Ağ Mesajlaşma)

**Ne için:**
- PM'den credential isteği (S-061) — chat log izleme
- CFO'dan acil chat talebi (S-076) — anormal kanal/saat
- Credential paylaşımı tespiti

**Simülasyon:**
```yaml
mattermost:
  image: mattermost/mattermost-team-edition:latest
  ports:
    - "8065:8065"
  environment:
    MM_SQLSETTINGS_DRIVERNAME: postgres
```

**Log:** Mattermost audit log API → JSON events

---

## 3. DOSYA SİSTEMİ VE DEPOLAMA KATMANI

### 3.1 Samba File Server (SMB)

**Ne için:**
- Departman paylaşımları (muhasebe, hukuk, İK, satış, geliştirici)
- SMB veri çekim hacmi (F-001, S-001-S-015)
- Departman dışı erişim (F-020)
- Directory traversal (F-023)
- Kitlesel dosya rename/delete (F-022)
- ACL değişikliği (F-024)
- Everyone izin ihlali (S-051)

**Simülasyon:**
```yaml
fileserver:
  image: dperson/samba:latest
  environment:
    SHARE1: "finance;/shares/finance;no;no;no;muhasebe,cfo"
    SHARE2: "legal;/shares/legal;no;no;no;hukuk,cfo"
    SHARE3: "hr;/shares/hr;no;no;no;ik,cfo"
    SHARE4: "dev;/shares/dev;no;no;no;gelistirici"
    SHARE5: "sales;/shares/sales;no;no;no;satis"
  ports:
    - "445:445"
    - "139:139"
```

**Audit konfigürasyonu (smb.conf):**
```ini
[global]
  full_audit:success = open read write rename unlink mkdir rmdir
  full_audit:failure = open
  full_audit:prefix = %u|%I|%S
  full_audit:facility = LOCAL5
  full_audit:priority = NOTICE
  vfs objects = full_audit
```

**Log format:**
```
May22 09:15:23 fileserver smbd_audit: cfo|10.0.1.5|finance|open|ok|budget_Q2_2026.xlsx
```

---

### 3.2 MinIO (S3-uyumlu Object Storage)

**Ne için:**
- Yedekleme deposu (S-008, S-014)
- Admin VM snapshot depolama
- Prod veri restore tespiti (F-035b)

**Simülasyon:**
```yaml
minio:
  image: minio/minio:latest
  command: server /data --console-address ":9001"
  ports:
    - "9000:9000"
    - "9001:9001"
```

---

## 4. AĞ İZLEME KATMANI

### 4.1 Zeek (Bro) — Derin Paket Analizi

**Ne için:**
- East-west lateral traffic (F-002)
- SMB protocol versiyon tespiti (F-004) — SMBv1 downgrade
- DNS entropi analizi (F-003)
- DHCP/ARP anomalisi (F-005)
- SSH brute force (S-071)
- Ağ topolojisi haritalama

**Simülasyon:**
```yaml
zeek:
  image: zeek/zeek:latest
  network_mode: host
  volumes:
    - ./zeek-logs:/usr/local/zeek/logs
  command: zeek -i eth0 local
```

**Üretilen log dosyaları:**
```
conn.log     — tüm bağlantılar (src, dst, port, bytes)
dns.log      — DNS sorguları (query, qtype, answers)
smb_files.log — SMB dosya işlemleri
smb_mapping.log — SMB share bağlantıları
kerberos.log — Kerberos TGT/TGS istekleri
ntlm.log     — NTLM auth girişimleri
http.log     — HTTP istekleri
ssh.log      — SSH bağlantıları
```

---

### 4.2 NetFlow / nfdump + ntopng

**Ne için:**
- Kullanıcı bazlı veri transfer hacmi (F-001)
- Lateral movement haritası (F-002)
- Anomalous traffic baseline

**Simülasyon:**
```yaml
ntopng:
  image: ntop/ntopng:stable
  ports:
    - "3000:3000"
  command: -i eth0 --community
```

**Alternatif:** Zeek'in `conn.log`'u NetFlow yerine kullanılabilir.

---

### 4.3 DHCP Server (ISC DHCP / Kea)

**Ne için:**
- IP-to-user mapping (AD session korelasyonu için şart)
- Rogue DHCP tespiti (F-005)
- Bilinmeyen MAC adresi tespiti (S-025)

**Simülasyon:**
```yaml
dhcp:
  image: networkboot/dhcpd:latest
  network_mode: host
  volumes:
    - ./dhcpd.conf:/etc/dhcp/dhcpd.conf
    - ./dhcp-logs:/var/log
```

**KRITIK:** Her IP ataması loglanmalı → IP↔MAC↔hostname↔AD-user zinciri için.

---

### 4.4 DNS Server (BIND9)

**Ne için:**
- DNS entropi izleme (F-003)
- DNS tunneling tespiti
- İç hostname çözümleme

**Simülasyon:**
```yaml
bind9:
  image: internetsystemsconsortium/bind9:9.18
  ports:
    - "53:53/udp"
    - "53:53/tcp"
  volumes:
    - ./bind-config:/etc/bind
    - ./bind-logs:/var/log/named
```

**Log aktivasyonu (named.conf):**
```
logging {
  channel query_log {
    file "/var/log/named/query.log" versions 5 size 20m;
    severity dynamic;
    print-time yes;
  };
  category queries { query_log; };
};
```

---

## 5. ENDPOINT VE AGENT KATMANI

### 5.1 Wazuh Agent (HIDS/EDR)

**En kritik araç — 30+ feature doğrudan Wazuh'tan beslenir.**

**Ne için:**
- Windows Event Log toplama (4624, 4625, 4663, 4728, 6416...)
- File integrity monitoring (FIM) — dosya değişiklik tespiti
- USB device insertion (Event ID 6416)
- Process monitoring — powershell, psexec, mimikatz pattern
- Log temizleme tespiti (S-044)
- Registry değişikliği (S-031)
- Rootkit tespiti

**Simülasyon:**
```yaml
wazuh-agent:
  image: wazuh/wazuh-agent:4.7.0
  environment:
    WAZUH_MANAGER: "wazuh-manager"
  volumes:
    - /var/ossec/logs:/var/ossec/logs
```

**Kritik event ID'leri Wazuh'un izlediği:**
```xml
<!-- ossec.conf -->
<localfile>
  <location>Security</location>
  <log_format>eventchannel</log_format>
</localfile>
<localfile>
  <location>Microsoft-Windows-Sysmon/Operational</location>
  <log_format>eventchannel</log_format>
</localfile>
<localfile>
  <location>Microsoft-Windows-PrintService/Operational</location>
  <log_format>eventchannel</log_format>
</localfile>
```

---

### 5.2 Sysmon (Windows Endpoint Telemetry)

**Ne için:**
- Process creation (Event ID 1) — psexec, powershell, cmd child process
- Network connection (Event ID 3) — process bazlı ağ bağlantısı
- File create (Event ID 11) — hassas dosya oluşturma
- Registry modify (Event ID 12/13)
- Pipe event (Event ID 17/18)
- Clipboard capture (Event ID 24) — F-037
- Process tree anomalisi (F-027) — Excel→powershell chain

**Config önerisi:** SwiftOnSecurity/sysmon-config (GitHub)

**Log format:**
```
EventID=1: Image=C:\Windows\System32\psexec.exe 
  ParentImage=C:\Users\user\Desktop\tool.exe
  CommandLine=psexec \\dc01 cmd.exe
```

---

### 5.3 osquery (Cross-platform Endpoint)

**Ne için:**
- Installed software inventory — shadow IT tespiti (F-031)
- Process bazlı ağ bağlantısı
- Local user listesi

**Simülasyon:** Linux container'larda osquery daemon olarak çalışır.

---

## 6. SIEM VE LOG TOPLAMA KATMANI

### 6.1 Wazuh Server (Ana SIEM)

**Ne için:**
- Tüm agent loglarının merkezi toplanması
- Kural bazlı alert üretimi
- Wazuh Manager → Elasticsearch → Kibana pipeline
- UEBA motorunun ana veri beslemesi

**Simülasyon:**
```yaml
wazuh-manager:
  image: wazuh/wazuh-manager:4.7.0
  ports:
    - "1514:1514"   # Agent communication
    - "1515:1515"   # Agent enrollment
    - "55000:55000" # REST API
  volumes:
    - wazuh_data:/var/ossec/data
    - ./rules:/var/ossec/etc/rules
```

---

### 6.2 Elasticsearch + Kibana (Log Depolama ve Görselleştirme)

**Ne için:**
- Tüm log verisinin indexlenmesi
- Kibana dashboards
- UEBA sisteminin REST API üzerinden sorgu atacağı backend

**Simülasyon:**
```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.12.0
  ports:
    - "5601:5601"
```

---

### 6.3 Filebeat + Logstash (Log Pipeline)

**Ne için:**
- Samba, Postfix, BIND9, CUPS, Zeek loglarını Elasticsearch'e taşıma
- Log normalizasyonu (farklı format → ortak schema)
- IP→user enrichment (DHCP lease tablosu ile)

**Simülasyon:**
```yaml
logstash:
  image: docker.elastic.co/logstash/logstash:8.12.0
  volumes:
    - ./logstash-pipeline:/usr/share/logstash/pipeline
  ports:
    - "5044:5044"   # Filebeat input
    - "5000:5000"   # Syslog input
```

**Pipeline örneği:**
```ruby
# samba-audit.conf
filter {
  if [type] == "samba_audit" {
    grok {
      match => { "message" => "%{USER:username}|%{IP:client_ip}|%{WORD:share}|%{WORD:operation}|%{WORD:status}|%{GREEDYDATA:filename}" }
    }
    # IP → AD user enrich
    translate {
      field => "client_ip"
      destination => "ad_user"
      dictionary_path => "/etc/logstash/ip_user_map.yml"
    }
  }
}
```

---

## 7. UYGULAMA KATMANI (Senaryo Ortamı)

### 7.1 Gitea (Self-hosted Git)

**Ne için:**
- Kaynak kod deposu (S-006, S-007, S-047)
- Tüm repo klonlama tespiti (F-030)
- Hardcoded credential push (S-062)
- Gece saati git aktivitesi (S-016 benzeri)

**Simülasyon:**
```yaml
gitea:
  image: gitea/gitea:latest
  ports:
    - "3001:3000"  # Web UI
    - "222:22"     # SSH
  volumes:
    - ./gitea-data:/data
  environment:
    GITEA__database__DB_TYPE: sqlite3
```

**Log:** Gitea audit log → `gitea/log/gitea.log`; git push/clone event'leri

---

### 7.2 PostgreSQL + pg_audit

**Ne için:**
- Production veritabanı (S-022, S-026, S-032)
- Payroll dump tespiti (S-015, F-026)
- SELECT * anomalisi
- Sorgu satır sayısı / response size izleme

**Simülasyon:**
```yaml
postgres:
  image: postgres:16
  environment:
    POSTGRES_DB: corpdb
    POSTGRES_USER: dbadmin
    POSTGRES_PASSWORD: secret
  ports:
    - "5432:5432"
  command: >
    postgres
    -c shared_preload_libraries=pgaudit
    -c pgaudit.log=all
    -c log_destination=csvlog
    -c log_directory=/var/log/postgresql
```

**pg_audit log örneği:**
```
2026-05-22 02:17:45 UTC,"ik_user","corpdb",42,"client_addr=10.0.1.12",
AUDIT: SESSION,1,1,READ,SELECT,TABLE,public.employees,
"SELECT * FROM employees",<not logged>
```

---

### 7.3 SuiteCRM (Müşteri İlişkileri Yönetimi)

**Ne için:**
- CRM toplu export tespiti (S-003, S-007, S-012)
- Satış çalışanı müşteri verisi (S-050)
- API çağrı anomalisi

**Simülasyon:**
```yaml
suitecrm:
  image: bitnami/suitecrm:latest
  ports:
    - "8082:8080"
  environment:
    SUITECRM_DATABASE_HOST: postgres
```

---

### 7.4 Nginx API Gateway + Access Log

**Ne için:**
- İç API çağrı deseni sapması (F-028)
- HTTP 4xx yoğunlaşması (F-029)
- IDOR deneme tespiti (S-041 benzeri)
- Servis hesabı API abuse (S-022)

**Simülasyon:**
```yaml
nginx:
  image: nginx:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx-conf:/etc/nginx/conf.d
    - ./nginx-logs:/var/log/nginx
```

**Log format (JSON):**
```nginx
log_format json_combined escape=json
  '{"time":"$time_iso8601",'
  '"remote_addr":"$remote_addr",'
  '"request":"$request",'
  '"status":$status,'
  '"body_bytes_sent":$body_bytes_sent,'
  '"http_user_agent":"$http_user_agent"}';
```

---

### 7.5 Jira (Proje/Ticket Yönetimi)

**Ne için:**
- Change ticket doğrulaması (S-028, S-040, S-044 — change ticket yok pattern)
- Helpdesk ticket ile AD reset korelasyonu (F-013)
- PM ticket sensitive alan görüntüleme (F-031b)

**Simülasyon:**
```yaml
jira:
  image: atlassian/jira-software:latest
  ports:
    - "8083:8080"
  environment:
    JVM_MINIMUM_MEMORY: 512m
```

**Not:** Hafif alternatif → **Plane** (open source Jira) veya basit mock REST API.

---

### 7.6 CUPS Print Server

**Ne için:**
- Yazıcı iş hacmi izleme (F-033b / F-034)
- Hassas belge kağıt çıktısı tespiti (S-067 benzeri)
- Scan-to-share pipeline (F-034)

**Simülasyon:**
```yaml
cups:
  image: olbat/cupsd:latest
  ports:
    - "631:631"
  volumes:
    - ./cups-logs:/var/log/cups
```

**Log:** `/var/log/cups/access_log` — her print job: kullanıcı, dosya adı, sayfa sayısı, yazıcı

---

### 7.7 Mattermost (İç Mesajlaşma)

**Ne için:**
- Credential paylaşımı chat üzerinden (S-024, S-061)
- CFO acil mesaj anomalisi (S-076)
- PM credential istemi (S-061)

(Üstte detaylandırıldı — bkz. 2.2)

---

## 8. FİZİKSEL GÜVENLİK SİMÜLASYONU

### 8.1 Badge/Fiziksel Erişim Mock API

**Ne için:**
- Badge geçişi ↔ AD login korelasyonu (F-036b, F-044)
- Fiziksel yokluk + dijital aktivite (S-022, S-056, S-067)
- Güvenlik görevlisi erişim olayı (S-067)

**Gerçek ortamda:** HID, Bosch, Paxton access control sistemleri → SQL veritabanı export

**Simülasyon:**
```python
# badge_api.py — Mock fiziksel erişim sistemi
from fastapi import FastAPI
from datetime import datetime
import sqlite3

app = FastAPI()

@app.post("/api/badge/entry")
def record_entry(user_id: str, door_id: str, timestamp: str = None):
    ts = timestamp or datetime.now().isoformat()
    db = sqlite3.connect("badge.db")
    db.execute("INSERT INTO access_log VALUES (?,?,?,?)", 
               (user_id, door_id, ts, "ENTRY"))
    db.commit()
    return {"status": "recorded"}

@app.get("/api/badge/presence/{user_id}")
def check_presence(user_id: str):
    # Returns whether user is physically in building
    ...
```

---

## 9. WATCHTOWER UEBA CORE SİSTEMİ

### 9.1 LangGraph Pipeline (UEBA Motoru)

**Bağlı olduğu araçlar:** Wazuh API, Elasticsearch API, PostgreSQL, Samba audit, DHCP lease, Badge API

**LLM çağrı noktaları:**
- Hızlı sınıflandırıcı (Gemini Flash / Claude Haiku) — raw event → schema detection
- Güçlü fallback (Claude Sonnet / Opus) — rule generation, korelasyon analizi

**Pipeline akışı:**
```
[Log Sources] → [Filebeat/Logstash] → [Elasticsearch]
                                            ↓
                                    [Wazuh Alerts]
                                            ↓
                              [LangGraph UEBA Pipeline]
                              ├── Node: EventNormalizer
                              ├── Node: BaselineComparator
                              ├── Node: AnomalyClassifier (LLM-1)
                              ├── Node: CorrelationEngine
                              ├── Node: RuleGenerator (LLM-2)
                              └── Node: AlertDispatcher
                                            ↓
                              [Rule Store: SQLite]
                              [Alert Store: PostgreSQL]
```

---

### 9.2 Baseline ve Kural Store

```
rule_store.sqlite
├── user_baselines      (kullanıcı × metrik × rolling 90-day window)
├── dept_baselines      (departman bazlı norm)
├── active_rules        (LLM üretimi + onaylı kurallar)
├── pending_rules       (yeni, henüz doğrulanmamış)
└── suppressed_rules    (false positive olarak kapatılmış)
```

---

## 10. SİMÜLASYON MOTORu

### 10.1 Python Kullanıcı Simülatörü

**Ne için:** Tüm 83 senaryoyu gerçekçi şekilde üretmek.

**Bileşenler:**
```
simulation/
├── users.yaml          — 35 kullanıcı profili (rol, mesai saati, normal davranış)
├── event_generator.py  — senaryo → log üretici
├── scenarios/
│   ├── s001_cfo_night_download.py
│   ├── s006_bulk_repo_clone.py
│   ├── s016_admin_kerberos_chain.py
│   └── ... (83 senaryo)
└── scheduler.py        — zaman çizelgesi yönetimi
```

**users.yaml örneği:**
```yaml
users:
  - id: cfo_user
    name: "Ali Yılmaz"
    role: CFO
    department: Finance
    normal_hours: "08:00-19:00"
    normal_daily_download_mb: 400
    accessible_shares:
      - finance
      - board
    accessible_dbs:
      - finance_db
    
  - id: intern_user_01
    name: "Zeynep Kaya"
    role: Stajyer
    department: Development
    normal_hours: "09:00-18:00"
    normal_daily_download_mb: 50
    accessible_shares:
      - dev-training
```

---

## 11. DOCKER COMPOSE — TAM STACK

```yaml
# watchtower-demo/docker-compose.yml
version: "3.9"

networks:
  corp-lan:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.0.0/16

services:
  # ─── IDENTITY ─────────────────────────────
  samba-ad:
    image: nowsci/samba-domain
    networks:
      corp-lan:
        ipv4_address: 10.0.0.2
    
  dhcp-server:
    image: networkboot/dhcpd
    network_mode: host
  
  vault:
    image: vault:latest
    networks:
      corp-lan:
        ipv4_address: 10.0.0.3

  # ─── MAIL ─────────────────────────────────
  mailserver:
    image: docker.io/mailserver/docker-mailserver
    networks:
      corp-lan:
        ipv4_address: 10.0.1.10

  roundcube:
    image: roundcube/roundcubemail
    networks:
      corp-lan:
        ipv4_address: 10.0.1.11

  mattermost:
    image: mattermost/mattermost-team-edition
    networks:
      corp-lan:
        ipv4_address: 10.0.1.12

  # ─── FILE SERVER ──────────────────────────
  fileserver:
    image: dperson/samba
    networks:
      corp-lan:
        ipv4_address: 10.0.2.10

  minio:
    image: minio/minio
    networks:
      corp-lan:
        ipv4_address: 10.0.2.11

  # ─── NETWORK MONITORING ───────────────────
  zeek:
    image: zeek/zeek
    network_mode: host
    
  bind9:
    image: internetsystemsconsortium/bind9:9.18
    networks:
      corp-lan:
        ipv4_address: 10.0.0.53

  ntopng:
    image: ntop/ntopng:stable
    network_mode: host

  # ─── APPLICATIONS ─────────────────────────
  postgres:
    image: postgres:16
    networks:
      corp-lan:
        ipv4_address: 10.0.3.10

  gitea:
    image: gitea/gitea
    networks:
      corp-lan:
        ipv4_address: 10.0.3.11

  suitecrm:
    image: bitnami/suitecrm
    networks:
      corp-lan:
        ipv4_address: 10.0.3.12

  nginx-gateway:
    image: nginx
    networks:
      corp-lan:
        ipv4_address: 10.0.3.13

  cups:
    image: olbat/cupsd
    networks:
      corp-lan:
        ipv4_address: 10.0.3.14

  # ─── SIEM ─────────────────────────────────
  wazuh-manager:
    image: wazuh/wazuh-manager:4.7.0
    networks:
      corp-lan:
        ipv4_address: 10.0.4.10

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    networks:
      corp-lan:
        ipv4_address: 10.0.4.11

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    networks:
      corp-lan:
        ipv4_address: 10.0.4.12

  logstash:
    image: docker.elastic.co/logstash/logstash:8.12.0
    networks:
      corp-lan:
        ipv4_address: 10.0.4.13

  # ─── UEBA ─────────────────────────────────
  watchtower-core:
    build: ./watchtower
    networks:
      corp-lan:
        ipv4_address: 10.0.5.10
    environment:
      ELASTICSEARCH_URL: http://10.0.4.11:9200
      WAZUH_API_URL: https://10.0.4.10:55000
      POSTGRES_URL: postgresql://10.0.3.10/watchtower
      LLM_FAST_MODEL: gemini-flash
      LLM_POWER_MODEL: claude-sonnet
    
  badge-api:
    build: ./simulation/badge_api
    networks:
      corp-lan:
        ipv4_address: 10.0.5.11

  user-simulator:
    build: ./simulation
    networks:
      corp-lan:
        ipv4_address: 10.0.5.20
```

---

## 12. SENARYO → TOOL MATRISI

Her senaryo kategorisi için hangi tool'un devrede olduğu:

| Kategori | Birincil Tool | Destekleyici |
|----------|--------------|--------------|
| Veri Sızdırma | Samba audit + Zeek conn.log | Wazuh FIM, Elasticsearch |
| Credential İhlali | Wazuh (AD events) + Samba AD | Vault audit, Zeek kerberos.log |
| Yetkisiz Erişim | Wazuh (4663, 4624) + Samba AD | Nginx 401/403, Postgres pg_audit |
| Insider Threat | Zeek + Samba + Gitea audit | Wazuh, DHCP lease map |
| Kazara İhlal | Samba ACL log + Postfix log | CUPS print log |
| Politika İhlali | Sysmon + Wazuh | Gitea (hardcoded creds) |
| Dış Saldırı | Zeek + Wazuh + Samba AD | ntopng, DNS log |
| Sosyal Mühendislik | Postfix log + Wazuh + Mattermost | Badge API korelasyon |
| Çapraz Korelasyon | Elasticsearch (tüm indexler) + LangGraph | Badge API, DHCP map |

---

## 13. LOG KAYNAĞI → ELASTICSEARCH INDEX ŞEMASI

```
watchtower-samba-*        smb_user, smb_share, smb_op, bytes, filename
watchtower-ad-*           event_id, user, source_ip, logon_type, target
watchtower-mail-*         from, to, bcc, subject_hash, attachment_size, rule_changes
watchtower-dns-*          client_ip, query, qtype, response, entropy_score
watchtower-zeek-conn-*    src_ip, dst_ip, dst_port, proto, bytes, duration
watchtower-zeek-kerberos-* user, src_ip, service, success
watchtower-process-*      user, image, cmdline, parent_image, event_id
watchtower-db-*           user, db, table, operation, rows_returned, bytes
watchtower-git-*          user, repo, operation (clone/push/pull), bytes
watchtower-usb-*          user, device_id, vendor, bytes_written
watchtower-print-*        user, printer, document, pages, queue_type
watchtower-badge-*        user, door, timestamp, direction
watchtower-vault-*        user, path, operation, timestamp
watchtower-api-*          user, endpoint, method, status_code, response_size
```

**Korelasyon için zorunlu ortak alan:** `user`, `timestamp`, `source_ip`  
**IP→user mapping için:** DHCP lease tablosu + AD logon korelasyonu

---

## 14. KURULUM ÖNCELİK SIRASI

**Faz 1 — Temel İzleme (MVP):**
1. Samba AD + File Server
2. Wazuh Manager + Agent
3. Elasticsearch + Kibana
4. DHCP Server
5. User Simulator (temel)
6. LangGraph core pipeline

**Faz 2 — Mail ve Uygulama:**
7. Postfix + Dovecot + Roundcube
8. PostgreSQL + pg_audit
9. Gitea
10. Nginx Gateway
11. Zeek

**Faz 3 — Gelişmiş İzleme:**
12. HashiCorp Vault
13. Mattermost
14. CUPS Print Server
15. Badge Mock API
16. ntopng / NetFlow
17. SuiteCRM

**Faz 4 — Tam Senaryo Kütüphanesi:**
18. 83 senaryonun tamamı için simülasyon scriptleri
19. Composite risk score engine
20. Offboarding HRIS entegrasyonu

---

*Bu stack ile 40 izleme kapasitesinin tamamı ve 83 senaryonun %95'i karşılanmaktadır. Kalan %5 (clipboard, screenshot) için uç nokta DLP agent gerektirir ve gerçek OS hook yeteneği Docker'da simüle edilemez — bu kısım mock event injection ile test edilebilir.*

---

## 15. HİBRİT OS NORMALİZASYON TASARIMI

> Bu bölüm "Kurumsal Gerçeklik" bulgusundan (bkz. başlık) türeyen teknik tasarım kararlarını içerir.

### 15.1 İki Log Yolu

Gerçek kurumsal ağda log'lar iki farklı OS'tan gelir. LangGraph `EventNormalizer` node'u her ikisini de ortak schema'ya dönüştürmek zorundadır:

```
Windows Server DC          Linux App Servers (RHEL/Ubuntu)
      │                              │
      │  Windows Event XML           │  auditd / syslog / JSON
      ▼                              ▼
┌─────────────┐              ┌──────────────┐
│  EventID    │              │  type/msg    │
│  based      │              │  based parse │
│  parse      │              └──────┬───────┘
└──────┬──────┘                     │
       │                            │
       └──────────┬─────────────────┘
                  ▼
         WatchtowerEvent (ortak schema)
         {user, event_type, timestamp,
          source_ip, source_os, raw}
```

### 15.2 Windows Event ID → WatchtowerEvent Eşlemesi

| Windows Event ID | WatchtowerEvent.event_type | İlgili Feature |
|-----------------|---------------------------|----------------|
| 4624 | `login_success` | F-007, F-008 |
| 4625 | `login_failed` | F-006, F-007 |
| 4663 | `file_access` | F-020, F-021 |
| 4728/4729 | `group_change` | F-010, S-030 |
| 4670 | `acl_change` | F-024 |
| 6416 | `usb_connect` | F-033 |
| 7045 | `nic_promiscuous` | F-035 |
| 307 (Print) | `print_job` | F-034 |
| Sysmon 1 | `process_create` | F-027 |
| Sysmon 3 | `network_connect` | F-002 |
| Sysmon 24 | `clipboard_copy` | F-037 |

### 15.3 Linux auditd → WatchtowerEvent Eşlemesi

| auditd type | WatchtowerEvent.event_type | İlgili Feature |
|-------------|---------------------------|----------------|
| `USER_AUTH` | `login_success` | F-007, F-008 |
| `USER_LOGIN` / `FAILED_LOGIN` | `login_failed` | F-006 |
| `SYSCALL` (open/read) | `file_access` | F-020, F-021 |
| `ADD_GROUP` | `group_change` | F-010 |
| `PATH` + write | `file_write` | F-022 |
| `USER_CMD` (psexec/powershell equiv.) | `process_create` | F-027 |

### 15.4 Wazuh Agent Dağıtım Matrisi

| Sunucu Tipi | OS | Wazuh Konfigürasyonu |
|------------|----|--------------------|
| Domain Controller | Windows Server | WinAgent → Security event channel + Sysmon |
| File Server | Linux (Samba) | LinuxAgent → auditd + samba full_audit syslog |
| Mail Server | Linux (Postfix) | LinuxAgent → /var/log/mail.log filebeat |
| DB Server | Linux (PostgreSQL) | LinuxAgent → pg_audit CSV log |
| Git Server | Linux (Gitea) | LinuxAgent → gitea audit log |
| API Gateway | Linux (Nginx) | LinuxAgent → access.log JSON |
| Kullanıcı PC (Win) | Windows | WinAgent → Security + Sysmon + PrintService |
| Kullanıcı PC (Linux) | Ubuntu/RHEL | LinuxAgent → auditd + journald |
| Kullanıcı PC (Mac) | macOS | WazuhAgent → syslog (sınırlı) |

### 15.5 Simülasyonda Windows Event Bridge

Simülasyon ortamında tüm container'lar Linux tabanlıdır. Windows Event formatını üretmek için `windows-event-bridge` servisi Samba4 loglarını Event ID XML formatına çevirir:

```python
# simulation/windows_event_bridge.py
def samba_login_to_win_event(samba_log: dict) -> dict:
    """Samba4 login → Windows Event ID 4624 formatı"""
    return {
        "EventID": 4624,
        "TimeCreated": samba_log["timestamp"],
        "SubjectUserName": samba_log["user"],
        "IpAddress": samba_log["client_ip"],
        "LogonType": 3,           # Network logon
        "WorkstationName": samba_log.get("workstation", "UNKNOWN"),
        "AuthenticationPackageName": "Kerberos",
        "source_os": "windows"    # normalizatör için işaret
    }

def samba_file_to_win_event(audit_line: dict) -> dict:
    """Samba file audit → Windows Event ID 4663 formatı"""
    return {
        "EventID": 4663,
        "TimeCreated": audit_line["timestamp"],
        "SubjectUserName": audit_line["user"],
        "ObjectName": f"\\\\fileserver\\{audit_line['share']}\\{audit_line['filename']}",
        "AccessMask": "0x1" if audit_line["operation"] == "read" else "0x2",
        "source_os": "windows"
    }
```

---

*Son güncelleme: 22 Mayıs 2026 — Hibrit OS mimarisi kurumsal araştırma bulgusuna göre eklendi.*
