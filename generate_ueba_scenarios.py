#!/usr/bin/env python3
"""Generate Watchtower UEBA simulation test scenarios."""

from pathlib import Path

# (name, category, role, olay, neden_supheli, sapma, severity, gerceklik)
SCENARIOS: list[tuple[str, ...]] = [
    ("Gece Yedek Çekimi", "veri sızdırma", "Muhasebe",
     "Muhasebe çalışanı normalde gündüz 200-400 MB finans sunucusundan rapor çekerken Cuma 23:47'de aynı sunucudan 18.4 GB toplu dosya indiriyor; arşiv (.zip) ve CSV paketleri.",
     "Rol için olağandışı saat, tek oturumda 45x veri hacmi, arşiv formatı toplu dışa aktarım paterni.",
     "Günlük ort. 320 MB → 18.4 GB; saat 09-18 dışı ilk kez.", "CRITICAL",
     "İşten ayrılma öncesi veya rakibe veri taşıma girişimlerinde sık görülür."),
    ("USB Toplu Kopya", "veri sızdırma", "Satış",
     "Satış temsilcisi CRM sunucusundan 2.1 GB veriyi 14 dakikada USB'ye kopyalıyor.",
     "Satışta USB yasak; CRM toplu okuma + USB yazma korelasyonu.",
     "USB: ayda 0-1 → 2.1 GB tek sefer.", "ALERT", "Fuar öncesi offline sunum."),
    ("Payroll Dump", "veri sızdırma", "İK",
     "İK uzmanı payroll-db'den tüm maaş tablosunu 890 MB SQL export ile indiriyor.",
     "Tam tablo export; normal iş akışı tek çalışan sorgusu.",
     "Ort. 2-5 MB → 890 MB.", "CRITICAL", "Maaş bilgisi sızdırma/şantaj."),
    ("Kaynak Kod Arşivi", "veri sızdırma", "Yazılım Geliştirici",
     "Geliştirici git-mirror'dan 4.7 GB tüm repo ağacı çekiyor; projesi tek microservice.",
     "Yetkili repo dışı tüm branch çekimi; hafta sonu.",
     "150 MB/hafta → 4.7 GB; repo 1→47.", "ALERT", "Ayrılış öncesi IP biriktirme."),
    ("Hukuk Dava Arşivi", "veri sızdırma", "Hukuk",
     "Hukuk danışmanı dava-arsiv'ten 120 PDF'i ZIP ile 3.2 GB indiriyor.",
     "Toplu indirme; müşteri kodlu dosya adları.",
     "5-10 dosya/gün → 120 dosya.", "WARNING", "Mahkeme hazırlığı meşru olabilir."),
    ("BI Ham PII Export", "veri sızdırma", "Veri Analisti",
     "Analist DWH'den ham müşteri PII ile 12 GB parquet export alıyor.",
     "Dashboard sorgusu 50-200 MB; ham PII export nadir.",
     "12 GB vs ort. 180 MB.", "ALERT", "Yanlış tüm veri seçimi."),
    ("Stajyer CRM Export", "veri sızdırma", "Stajyer",
     "Stajyer 2. haftada CRM'den 45.000 satır müşteri kaydını Excel'e aktarıyor (220 MB).",
     "Stajyer yetkisi demo ortamı; prod export yok.",
     "İlk CRM export; 9x satır üst sınır.", "CRITICAL", "Görev yanlış anlaşılması."),
    ("CFO USB Kopya", "veri sızdırma", "CFO",
     "CFO bütçe sunucusundan 1.8 GB indirip ardından USB'ye kopyalıyor.",
     "İndirme meşru; USB CFO baseline'ında yılda 0.",
     "USB olayı: 0 → 1.8 GB.", "WARNING", "YK sunumu + politika ihlali."),
    ("Destek Ticket PII", "veri sızdırma", "Destek Personeli",
     "Destek attachment store'dan 800 ticket ekini 6.1 GB zip'liyor.",
     "Kimlik fotokopisi ve ekran görüntüsü içerebilir.",
     "50 MB/gün → 6.1 GB.", "ALERT", "Yedekleme bahanesi."),
    ("Admin Yanlış VM", "veri sızdırma", "IT Admin",
     "Admin prod-HR VM snapshot'ını workstation'a 90 GB çekiyor.",
     "Hedef workstation; backup job dışı saat.",
     "Tek sefer 90 GB.", "CRITICAL", "Operasyon hatası."),
]

OUT = Path(__file__).resolve().parent.parent / "watchtower-ueba-test-scenarios.md"

def render(scenarios: list[tuple[str, ...]]) -> str:
    lines = [
        "# Watchtower UEBA — Simülasyon Test Senaryoları",
        "",
        f"Toplam: **{len(scenarios)}** senaryo | İç ağ (private LAN) only | 35 çalışan profili",
        "",
        "Kategoriler: veri sızdırma, yetkisiz erişim, insider threat, credential ihlali,",
        "dış saldırı desteği, kazara ihlal, politika ihlali, diğer",
        "",
        "---",
        "",
    ]
    for i, s in enumerate(scenarios, 1):
        lines += [
            f"## {i}. {s[0]}",
            "",
            f"**SENARYO ADI:** {s[0]}",
            f"**KATEGORİ:** {s[1]}",
            f"**KULLANICI ROLÜ:** {s[2]}",
            f"**OLAY:** {s[3]}",
            f"**NEDEN ŞÜPHELİ:** {s[4]}",
            f"**NORMAL BASELINE'DAN SAPMA:** {s[5]}",
            f"**BEKLENEN SEVERITY:** {s[6]}",
            f"**GERÇEKÇİLİK NOTU:** {s[7]}",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)

if __name__ == "__main__":
    OUT.write_text(render(SCENARIOS), encoding="utf-8")
    print(len(SCENARIOS), "->", OUT)
