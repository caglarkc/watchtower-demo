# UEBA Simülasyon Ortamı İçin Gerçekçi Test Senaryoları

Aşağıdaki senaryolar, yalnızca şirketin iç ağı (private LAN) içinde gerçekleşen olayları kapsar. Her senaryo, LLM destekli UEBA sisteminin anormal davranış tespiti, bağlamsal korelasyon ve rol-temelli baseline sapmasını test etmek için tasarlanmıştır.

---

SENARYO ADI: Gece Yarısı Finans Paylaşımı

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: CFO

OLAY: CFO, normalde yalnızca mesai saatlerinde eriştiği finans sunucusuna gece 02:17’de bağlanır. Ardından son çeyrek bütçe klasöründen 18 GB veri çekip bunu iç ağdaki ortak bir yazıcı-tarama sunucusuna geçici olarak kopyalar.

NEDEN ŞÜPHELİ: Saat dışı erişim, alışılmadık veri hacmi ve CFO’nun rutininde olmayan ara sunucu kullanımı birlikte yüksek risk oluşturur.

NORMAL BASELINE'DAN SAPMA: CFO’nun tipik veri çekişi günde 300–800 MB iken olayda 18 GB’tır. Normal login penceresi 08:00–19:00 iken erişim 02:17’dedir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Üst düzey yöneticiler bazen geç saatlerde çalışabilir; ancak veri hacmi ve alışılmadık aktarım rotası gerçek hayatta veri dışarı çıkarma hazırlığına işaret edebilir.

---

SENARYO ADI: Yanlış Paylaşılan Bordro Klasörü

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, aylık bordro belgelerini ekip içi paylaşıma koymak isterken erişim izinlerini yanlış ayarlar ve klasörü şirket içindeki tüm kullanıcıların okuyabileceği şekilde yayınlar.

NEDEN ŞÜPHELİ: Hassas finans verisinin yetki seviyesi dışında geniş erişime açılması anlık olarak izlenmelidir.

NORMAL BASELINE'DAN SAPMA: Normalde bordro klasörleri yalnızca 4 muhasebe personeli ve CFO tarafından erişilebilirken erişim kapsamı 35 kullanıcıya açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Gerçek şirketlerde erişim kontrol listesi hataları sık görülür ve çoğu kasıtlı değil operasyonel dikkatsizlik kaynaklıdır.

---

SENARYO ADI: Stajyerin Kaynak Kod Aynası

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Stajyer

OLAY: Yeni başlayan stajyer, eğitim amaçlı incelemek için üretim kod deposunun tam kopyasını dahili dosya sunucusundaki kişisel çalışma alanına alır. Kopya içinde servis anahtarlarının eski versiyonları da bulunur.

NEDEN ŞÜPHELİ: Gerekenden fazla erişim, hacimli kopyalama ve gizli credential artığı bulunan içeriklerin kişisel alana taşınması risklidir.

NORMAL BASELINE'DAN SAPMA: Stajyerler normalde yalnızca eğitim reposuna erişir; olayda erişilen repo sayısı 1’den 7’ye, veri miktarı 150 MB’tan 9 GB’a çıkmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Yeni çalışanlar çoğu zaman “lokalde incelemek için kopyalama” davranışını masum görür; ama bu durum veri yayılımını ciddi biçimde artırır.

---

SENARYO ADI: IT Admin Yetki Zinciri

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin kullanıcısı, vardiya dışı saatte önce etki alanı denetleyicisine, sonra hukuk arşiv sunucusuna, ardından muhasebe veritabanı yedeğine erişir. Bu erişimler için resmi değişiklik kaydı bulunmaz.

NEDEN ŞÜPHELİ: Ayrı departmanlara ait yüksek hassasiyetli sistemlere kısa sürede ardışık erişim, yatay keşif veya hazırlık hareketi olabilir.

NORMAL BASELINE'DAN SAPMA: Admin’in günlük ortalama kritik sistem erişimi 2–3 hedef iken olayda 7 hedefe 23 dakika içinde erişilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Sistem yöneticileri geniş yetkiye sahiptir; bu yüzden kötüye kullanımın tespiti için bağlam, zaman ve erişim deseni hayati önem taşır.

---

SENARYO ADI: CEO Asistanı Gibi Davranan Arama Sonrası Erişim

KATEGORİ: sosyal mühendislik / dış saldırı destegi

KULLANICI ROLÜ: CEO

OLAY: CEO, şirket içi destek masasını arayan ve kendini yönetim ofisinden biri gibi tanıtan kişinin yönlendirmesiyle “sunum hazırlığı” bahanesiyle iç ağdaki proje klasörlerine normalde kullanmadığı terminal odasından giriş yapar.

NEDEN ŞÜPHELİ: CEO hesabının olağan dışı terminalden kullanılması, alışılmadık klasör erişimi ve kısa süreli çoklu belge açılışı sosyal mühendislik etkisini düşündürür.

NORMAL BASELINE'DAN SAPMA: CEO genelde yalnızca kendi dizüstünden erişirken olayda ilk kez ortak toplantı terminali kullanılmıştır; erişilen klasör sayısı 2’den 11’e çıkmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Saldırganlar internet yerine şirket içindeki fiziksel veya telefon tabanlı sosyal mühendislikle de kullanıcıları yanlış işlem yaptırabilir.

---

SENARYO ADI: Hukuk Belgelerine Meraklı Geliştirici

KATEGORİ: insider threat

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Bir geliştirici, görev alanıyla ilgisi olmadığı halde hukuk departmanının sözleşme arşivi sunucusunda dosya isimlerini tarar ve sonrasında üç birleşme sözleşmesini indirir.

NEDEN ŞÜPHELİ: İş rolü ile erişilen veri arasında bağ bulunmaması ve hassas klasörlerde hedefli gezinme önemli alarm sebebidir.

NORMAL BASELINE'DAN SAPMA: Geliştiricinin normal sunucu erişim profili yalnızca dev/test sistemleri iken ilk kez hukuk sunucusuna 41 dosya sorgusu yapılmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İçeriden bilgi ticareti veya merak kaynaklı yetkisiz erişim olayları gerçek hayatta sıkça görülebilir.

---

SENARYO ADI: Fazladan USB Yedekleme

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, bakım amacıyla aldığı veritabanı yedeğini şirket onaylı olmayan harici diske aktarır. Aktarım iç ağda yedekleme sunucusundan admin iş istasyonuna, oradan USB’ye yapılır.

NEDEN ŞÜPHELİ: Büyük hacimli hassas veri aktarımı ile eşzamanlı USB bağlantısı birleşince veri kaçırma riski oluşur.

NORMAL BASELINE'DAN SAPMA: Normal yedek işlemleri doğrudan backup appliance’a giderken olayda 240 GB veri admin PC’si üzerinden geçmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: “Geçici taşıma” bahanesiyle yerel istasyon ve USB kullanımı birçok iç tehdit vakasında görülür.

---

SENARYO ADI: İK’dan Yanlış Odaya Giden Hassas Mail

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: İK

OLAY: İK çalışanı, disiplin sürecine ait belgeleri iç ağ posta sistemi üzerinden yalnızca hukuk ekibine göndermek isterken “Legal-All” yerine benzer isimli “Leadership-All” grubunu seçer.

NEDEN ŞÜPHELİ: Hassas mail ekinin normal dışı geniş dahili dağıtım listesine gitmesi veri minimizasyonu ihlalidir.

NORMAL BASELINE'DAN SAPMA: Bu tip ekler normalde 2–4 alıcıya giderken olayda 11 kişiye ulaştırılmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Benzer grup isimleri ve otomatik tamamlama, iç mail sistemlerinde çok yaygın hata kaynaklarıdır.

---

SENARYO ADI: Güvenlik Görevlisinin Sunucu Odası Bilgisiyle Tetiklenen Erişim

KATEGORİ: dış saldırı destegi

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Güvenlik görevlisi, gece vardiyasında sunucu odasında bakım ekibi olduğunu söyleyen kişilere kapı açar. Aynı zaman aralığında içerideki bakım terminalinden çok sayıda kimlik doğrulama denemesi görülür.

NEDEN ŞÜPHELİ: Fiziksel erişim olayı ile iç ağda başarısız login patlamasının korele olması kritik sinyaldir.

NORMAL BASELINE'DAN SAPMA: Normalde bakım terminalinde saatte 5’ten az login varken olay saatinde 86 başarısız deneme oluşmuştur.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Fiziksel güvenlik zafiyeti çoğu zaman siber olayın başlangıç noktası olur; UEBA fiziksel ve dijital sinyali birlikte ele almalıdır.

---

SENARYO ADI: API Servis Hesabını İnsan Gibi Kullanan Analist

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Veri Analisti

OLAY: Veri analisti, rapor çıkarmayı hızlandırmak için bir servis hesabının API anahtarını paylaşımlı nottan alıp kendi makinesinden manuel sorgular yapar.

NEDEN ŞÜPHELİ: Servis credential’ının interaktif kullanıcı oturumunda kullanılması politika dışıdır ve iz bırakır.

NORMAL BASELINE'DAN SAPMA: İlgili servis anahtarı normalde yalnızca 1 entegrasyon sunucusundan çağrı yaparken olayda analist iş istasyonundan 430 API çağrısı gelmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İşleri hızlandırma baskısı altında çalışanlar bazen servis hesaplarını pratik çözüm gibi kullanır.

---

SENARYO ADI: Satış Ekibinden Sessiz CRM Dökümü

KATEGORİ: insider threat

KULLANICI ROLÜ: Satış

OLAY: Ayrılma sürecindeki satış çalışanı, müşteri CRM verilerini parça parça iç ağdaki bölgesel paylaşım klasörlerine çıkarır ve dosya adlarını toplantı notu gibi masum isimlerle değiştirir.

NEDEN ŞÜPHELİ: Küçük partiler halinde tekrarlı veri çıkarımı ve isim maskeleme davranışı tipik sızdırma taktiğidir.

NORMAL BASELINE'DAN SAPMA: Kullanıcının normal haftalık müşteri export toplamı 200 MB altındayken 3 günde toplam 12.6 GB aktarım yapmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Gerçek vakalarda çalışanlar toplu export yerine yavaş ve düşük görünürlükte veri toplama yöntemlerini tercih eder.

---

SENARYO ADI: PM’den Gereksiz Credential İstemi

KATEGORİ: sosyal mühendislik / politika ihlali

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: Proje yöneticisi, teslim tarihi baskısı nedeniyle geliştiricilerden test ortamı parolalarını iç ağ mesajlaşma aracı üzerinden ister ve bunları kendi notlarında saklar.

NEDEN ŞÜPHELİ: Paylaşılan credential kullanımı ve rol dışı erişim talebi organizasyonel risktir.

NORMAL BASELINE'DAN SAPMA: PM rolünün normalde doğrudan sistem login’i bulunmazken iki günde 6 farklı credential talebi kaydedilmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Sosyal baskı, özellikle proje teslim dönemlerinde güvenlik politikasının gevşetilmesine yol açar.

---

SENARYO ADI: Muhasebe Terminalinden Gece Loginleri

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanının hesabı, çalışanın binada olmadığı bir gecede muhasebe terminali yerine geliştirici alanındaki paylaşımlı bir cihazdan kullanılır.

NEDEN ŞÜPHELİ: Fiziksel konum ile kullanıcı erişim noktası uyuşmazlığı ve zaman dışı kullanım hesap paylaşımı veya ele geçirilmiş oturumu gösterebilir.

NORMAL BASELINE'DAN SAPMA: Kullanıcının önceki 90 günde hiç 21:00 sonrası oturumu yokken olayda 01:09’da login gerçekleşmiştir; cihaz tipi de ilk kez değişmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İç ağ olaylarında internet göstergesi olmayabilir; bu yüzden fiziksel yoklama ve cihaz profili korelasyonu önemlidir.

---

SENARYO ADI: CTO’nun Gizli Yedek Klasörü

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: CTO

OLAY: CTO, birleşme görüşmeleri sırasında teknik durum tespit dokümanlarını standart M&A kasası yerine kendi adında yeni bir dahili paylaşım klasörüne toplar ve erişim geçmişini temizlemeye çalışır.

NEDEN ŞÜPHELİ: Yeni oluşturulmuş kişisel klasöre hassas belgelerin konsolide edilmesi ve log temizleme girişimi ciddi alarm üretmelidir.

NORMAL BASELINE'DAN SAPMA: CTO normalde 2 paylaşımlı klasör kullanırken olay haftasında 1 yeni özel klasöre 74 belge taşımıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Yüksek ayrıcalıklı kişiler gölgede kalan kişisel alanları sık kullanabilir; UEBA bunun davranışsal anomalisini yakalamalıdır.

---

SENARYO ADI: Destek Personelinin Yardım Amaçlı Fazla Yetkisi

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek personeli, bir kullanıcının yazıcı sorununu çözmek için uzaktan bağlanır ve oturum açıkken kullanıcının yetkili klasörlerinde gezerek yanlışlıkla hassas İK belgelerini açar.

NEDEN ŞÜPHELİ: Sorunla ilgisiz dosya erişimi ve hassas bölümlere yan gezinme tespit edilmelidir.

NORMAL BASELINE'DAN SAPMA: Tipik destek oturumları 10–15 dakika sürerken olay 52 dakika sürmüş ve 27 hassas dosya açılmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Merak, deneyimsizlik veya yanlış pencere seçimiyle destek süreçlerinde istemeden veri görülmesi yaygındır.

---

SENARYO ADI: Hukuk Ekibine CFO Adına Gelen İç Mail

KATEGORİ: diğer

KULLANICI ROLÜ: Hukuk

OLAY: Hukuk çalışanı, CFO’dan gelmiş gibi görünen ama şirket içi mail sunucusunda farklı bir istemci imzası taşıyan bir dahili mail alır. Mail, sözleşme klasörlerinin acil paylaşılmasını ister.

NEDEN ŞÜPHELİ: İç mail sahteciliği, anormal istemci izi ve aciliyet dili birlikte sosyal mühendislik göstergesidir.

NORMAL BASELINE'DAN SAPMA: CFO iç maillerinin %95’i tek cihazdan gelirken bu iletide ilk kez farklı workstation kimliği görülür.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İnternet olmadan da şirket içi mail relay suistimali veya açık oturum kullanımıyla sahte dahili yazışmalar üretilebilir.

---

SENARYO ADI: Yeni Geliştiricinin Prod Merakı

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Yeni işe başlayan geliştirici, onboarding dokümanlarını yanlış yorumlayıp üretim veritabanına readonly erişim talep etmeksizin mevcut paylaşımlı credential ile bağlanır.

NEDEN ŞÜPHELİ: Yeni çalışan, rol dışı ortam erişimi ve paylaşımlı credential kullanımı birleşmiştir.

NORMAL BASELINE'DAN SAPMA: İlk 30 gün içindeki geliştiriciler için baseline yalnızca dev/test erişimidir; olayda ilk haftada prod DB sorgusu yapılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Onboarding belirsizliği ve ekip içi “şunu kullan” kültürü gerçek hayatta ciddi erişim hataları üretir.

---

SENARYO ADI: İK’dan Toplu CV Arşivi Kopyası

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: İK

OLAY: İK uzmanı, geçmiş aday havuzunu analiz etmek için tüm CV arşivini merkezi İK sunucusundan kendi departman paylaşım alanına kopyalar.

NEDEN ŞÜPHELİ: PII içeren verilerin gereksiz çoğaltılması ve büyük hacimli taşınması veri koruma riski doğurur.

NORMAL BASELINE'DAN SAPMA: Günlük ortalama 20–30 CV erişimi varken olayda 4.800 dosya tek oturumda kopyalanmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: “Analiz yapacağım” motivasyonu ile toplu kopya oluşturma sık görülür; çoğu zaman veri minimizasyonu düşünülmez.

---

SENARYO ADI: Çoklu Lokasyon Çakışması

KATEGORİ: credential ihlali

KULLANICI ROLÜ: CEO

OLAY: CEO hesabı aynı 20 dakikalık dilimde hem yönetim katındaki sabit cihazdan hem de bodrum kattaki toplantı odası terminalinden aktif işlem yapar.

NEDEN ŞÜPHELİ: Fiziksel olarak imkânsız eşzamanlılık hesap paylaşımı veya oturum ele geçirilmesini gösterir.

NORMAL BASELINE'DAN SAPMA: CEO hesabında tarihsel olarak paralel oturum görülmemiştir; olayda iki farklı cihaz ve iki farklı iç lokasyon vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İç ağda “impossible travel” yerine bina içi imkânsız konum çakışmaları güçlü bir göstergedir.

---

SENARYO ADI: Satıştan Muhasebeye Kesişen Erişim

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Satış

OLAY: Satış çalışanı, prim hesaplamasını kontrol etmek için muhasebe paylaşım klasöründe bordro tablolarını arar ve farklı çalışanların maaş sayfalarını açar.

NEDEN ŞÜPHELİ: Gerekçesi kişisel merak olan, departman sınırını aşan hassas belge erişimidir.

NORMAL BASELINE'DAN SAPMA: Satış çalışanının önceki 6 ayda muhasebe sunucusuna erişimi yokken olay günü 18 dosya açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Prim ve maaş dönemlerinde çalışanlar yetkisiz şekilde finans dosyalarını merak edebilir.

---

SENARYO ADI: Eski Credential ile API Kullanımı

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Ekipten ayrılmak üzere olan geliştirici, bir zamanlar kullandığı ama iptal edilmesi gereken eski test API token’ını iç ağdan hâlâ çalışır halde bulur ve bunu kullanarak kullanıcı veri setlerini sorgular.

NEDEN ŞÜPHELİ: Süresi dolması gereken credential’ın tekrar kullanılması ve veri sorgulaması hesap yaşam döngüsü zafiyetidir.

NORMAL BASELINE'DAN SAPMA: İlgili token 47 gündür kullanılmıyorken olayda bir saatte 1.200 çağrı yapmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Yetki deprovisioning gecikmeleri gerçek şirketlerde çok sık görülür.

---

SENARYO ADI: Hukuk Klasörünü Yedekleyen PM

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, sözleşme değişikliklerini kaçırmamak için hukuk paylaşım klasörünü kendi proje klasörüne periyodik olarak kopyalayan küçük bir iç script çalıştırır.

NEDEN ŞÜPHELİ: Yetkisiz otomasyon, departman verisinin çoğaltılması ve erişim kapsamının fiilen genişletilmesidir.

NORMAL BASELINE'DAN SAPMA: PM kullanıcılarında otomatik kopyalama script’i baseline’da yoktur; olayda günde 4 kez senkron çalışmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Verimlilik için oluşturulan küçük otomasyonlar çoğu zaman gölge BT riskine dönüşür.

---

SENARYO ADI: USB ile İçeri Veri Taşıyan Stajyer

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer, eğitim sunumunu hazırlamak için örnek müşteri verisini şirketin güvenli paylaşım alanı yerine USB belleğe kopyalar, sonra bunu toplantı odasındaki ortak cihaza takar.

NEDEN ŞÜPHELİ: Yetkisiz taşınabilir medya kullanımı ve örnek veri içinde gerçek müşteri kayıtlarının bulunması risklidir.

NORMAL BASELINE'DAN SAPMA: Stajyer cihazlarında USB bağlantısı normalde kapalıdır; olayda ilk kez dış depolama tanınmıştır ve 2.4 GB veri yazılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Eğitim veya demo hazırlığı için gerçek verinin “örnek” sanılması çok yaygın bir hatadır.

---

SENARYO ADI: CFO’dan Gelen Acil Onay Talebi Sonrası Yetki Verme

KATEGORİ: sosyal mühendislik / kazara ihlal

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, CFO adına dahili chat üzerinden gelen “hemen erişim aç” mesajına güvenerek geçici kullanıcıya muhasebe klasörü yetkisi verir; daha sonra mesajın CFO’nun açık kalan toplantı odası oturumundan gönderildiği anlaşılır.

NEDEN ŞÜPHELİ: Yönetici hesabından olağandışı kanal kullanımı, aciliyet ve yetki değişikliği kombinasyonu risklidir.

NORMAL BASELINE'DAN SAPMA: CFO normalde erişim talebini ticket sistemiyle iletirken olayda ilk kez chat üzerinden ve gece 21:40’ta talep gelmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İç ağ sosyal mühendisliği çoğu zaman dışarıdan değil, açık oturumların suistimaliyle gerçekleşir.

---

SENARYO ADI: Veri Analistinin Tüm Posta Kutusu Tarama İşlemi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Veri Analisti

OLAY: Veri analisti, müşteri duygu analizi projesi için yalnızca destek ekibi maillerini alması gerekirken dahili mail arşiv sunucusunda tüm departman kutularını tarar.

NEDEN ŞÜPHELİ: Veri kapsamının gereksiz biçimde genişletilmesi ve hassas kutulara erişim olması.

NORMAL BASELINE'DAN SAPMA: Analistin normal mail veri seti tek paylaşımlı kutu iken olayda 9 farklı departman kutusuna sorgu gitmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Veri projelerinde “önce hepsini alalım sonra filtreleriz” yaklaşımı ciddi gizlilik ihlallerine yol açar.

---

SENARYO ADI: Destek Personelinin Yönetici Terminali Kullanması

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek çalışanı, boş bulduğu yönetici katı cihazını kendi hesabıyla kullanarak bir kullanıcıya uzaktan yardım verir çünkü yakınındaki terminal bozulmuştur.

NEDEN ŞÜPHELİ: Yetkili/özel lokasyondaki cihazların farklı rol tarafından kullanılması çevresel güvenlik riskidir.

NORMAL BASELINE'DAN SAPMA: Destek ekibi cihaz profili yalnızca helpdesk odası ile sınırlıyken olayda ilk kez yönetici segmentinde login vardır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Pratik çözüm amaçlı cihaz paylaşımı kurum içi güvenlikte sık görülen zayıf halkadır.

---

SENARYO ADI: Geçici Toplantı Dosyasında Gizlenen Veritabanı Dökümü

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, kullanıcı tablosundan aldığı büyük bir veri çıktısını “Sprint_Retrospective_Backup” adıyla ortak proje klasörüne kaydeder.

NEDEN ŞÜPHELİ: Maskelenmiş dosya adıyla hassas veri saklama ve rol dışı veri export’u tespit edilmelidir.

NORMAL BASELINE'DAN SAPMA: Kullanıcı dev ortamında tipik sorgu sonucu 5–20 MB iken olay dosyası 6.8 GB’tır ve prod kaynağından alınmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Sızdırma niyeti olan çalışanlar çoğu zaman dosya adlarını rutin iş çıktısı gibi göstermeye çalışır.

---

SENARYO ADI: Muhasebe ile İK Arasında Yanlış Yetki Kalıtımı

KATEGORİ: diğer

KULLANICI ROLÜ: İK

OLAY: İK çalışanı, önceki pozisyonundan kalan grup üyeliği nedeniyle bordro ve çalışan disiplin kayıtlarına aynı anda erişebilir durumdadır ve bu durum ilk kez yoğun kullanımla fark edilir.

NEDEN ŞÜPHELİ: Rol değişimi sonrası kalması gerekmeyen yetkiler ve çapraz hassas veri erişimi.

NORMAL BASELINE'DAN SAPMA: İK rolündeki kullanıcıların muhasebe sistemlerine erişimi normalde sıfırken olay kullanıcı 63 dosya açmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Pozisyon değişikliklerinde eski grup üyeliklerinin unutulması sık yaşanır.

---

SENARYO ADI: CFO Paylaşımlı Yazıcıdan Tarayıp Saklıyor

KATEGORİ: politika ihlali

KULLANICI ROLÜ: CFO

OLAY: CFO, imzalı satın alma sözleşmelerini hızlıca işlemek için paylaşımlı çok fonksiyonlu yazıcı üzerinde bırakılmış tarama klasöründe tutar.

NEDEN ŞÜPHELİ: Hassas belgelerin geçici ortak cihaz depolamasında kalması veri maruziyeti yaratır.

NORMAL BASELINE'DAN SAPMA: Finans belgeleri normalde güvenli belge kasasına giderken olayda 36 dosya yazıcı storage’ında 14 saat kalmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Operasyonel kolaylık için MFP cihazları geçici depo gibi kullanılabiliyor.

---

SENARYO ADI: Çift Vardiya Gibi Davranan Güvenlik Hesabı

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Bir güvenlik görevlisinin hesabı aynı vardiyada iki farklı kapı kontrol terminalinde dönüşümlü olarak kullanılır; eşzamanlı olarak iç ağ loglarında güvenlik ofisi PC’sinden erişimler vardır.

NEDEN ŞÜPHELİ: Hesap paylaşımı veya başkasının badge/oturum kullanımı göstergesidir.

NORMAL BASELINE'DAN SAPMA: Normalde tek vardiyada tek terminal paterni varken olayda 3 terminal ve 2 lokasyon görülür.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Fiziksel güvenlik personeli arasında kolaylık için hesap paylaşımı gerçek hayatta yaşanabilir.

---

SENARYO ADI: IT Admin’den Sessiz Mail Kutusu Erişimi

KATEGORİ: insider threat

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, arıza inceleme bahanesiyle bir satış yöneticisinin dahili mail kutusuna delegate erişim açar ve müşteri teklif yazışmalarını okur.

NEDEN ŞÜPHELİ: İdari yetkiyle içerik erişimi, teknik gerekçeyle açıklanamayacak ölçüde hedeflidir.

NORMAL BASELINE'DAN SAPMA: Admin’in normal mail müdahaleleri ayda 2–3 hesap sıfırlama iken olayda içerik okuma ve 117 mesaj açma vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Yetkili kullanıcı kötüye kullanımı UEBA’nın en kritik kullanım alanlarından biridir.

---

SENARYO ADI: CFO Onayı İçin Hazırlanan Sahte İç Form

KATEGORİ: sosyal mühendislik

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, intranet üzerindeki gerçek ödeme formuna benzeyen sahte bir iç form sayfasına şirket içi bağlantı alır ve CFO imzası için gerekli credential bilgisini bu forma girer.

NEDEN ŞÜPHELİ: Credential’ın alışılmadık dahili uygulamaya verilmesi ve sonraki erişim zinciri anomali üretmelidir.

NORMAL BASELINE'DAN SAPMA: Kullanıcı normalde tek finans uygulamasını kullanırken olayda ilk kez yeni dahili host’a giriş yapılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Sosyal mühendislik sadece internet phishing ile olmaz; iç portal kopyaları da etkili olabilir.

---

SENARYO ADI: Geliştiricinin Fazla Geniş Log Toplaması

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Performans hatasını incelemek isteyen geliştirici, merkezi log sisteminden kullanıcı oturum bilgileri ve mail başlıkları içeren geniş kapsamlı log export’u alır.

NEDEN ŞÜPHELİ: Teknik hata çözümü bahanesiyle kişisel verilerin gereksiz ölçekte toplanması.

NORMAL BASELINE'DAN SAPMA: Tipik log export’u 50–100 MB iken olayda 14 GB’lık çok alanlı log paketi çıkarılmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Geliştiriciler bazen “önce tüm logları alayım” yaklaşımını benimser; veri sınıflandırması gözden kaçabilir.

---

SENARYO ADI: Yönetici Toplantı Odasında Açık Kalan Oturum

KATEGORİ: diğer

KULLANICI ROLÜ: CEO

OLAY: CEO toplantı odasındaki terminalde oturumu kapatmadan ayrılır. Sonraki 12 dakikada bu oturumdan hukuk ve finans klasörlerine göz atılır.

NEDEN ŞÜPHELİ: Oturum sahibi fiziksel olarak cihazdan ayrılmışken hassas dosya erişimi oluşur.

NORMAL BASELINE'DAN SAPMA: CEO oturumları genelde 1 cihaz ve aktif input paterni gösterirken olayda cihaz etkileşim profili değişir ve kısa sürede alışılmadık klasörler açılır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Açık bırakılmış oturumlar kurum içi fırsatçı erişimlerin ana kaynaklarından biridir.

---

SENARYO ADI: Stajyerden Toplu Print Queue İncelemesi

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer, yazıcıda sıkışan işlerini bulmak için merkezi print queue sunucusuna girer ve farklı departmanların bekleyen belge adlarını inceler.

NEDEN ŞÜPHELİ: Rol dışı meta-veri keşfi; belge adları dahi hassas bilgi sızdırabilir.

NORMAL BASELINE'DAN SAPMA: Stajyer rolünün print admin arayüzüne erişimi baseline’da yoktur; olayda 9 departmanın kuyrukları listelenmiştir.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Meta-veri erişimi çoğu zaman önemsiz sanılır ama hassas bilgi açığa çıkarabilir.

---

SENARYO ADI: Satış Yöneticisinin İç Mail Arşivi Temizliği

KATEGORİ: insider threat

KULLANICI ROLÜ: Satış

OLAY: Satış yöneticisi, ayrılmadan önce müşteri pazarlık geçmişini içeren eski mail klasörlerini toplu biçimde siler ve ardından CRM export alır.

NEDEN ŞÜPHELİ: Delil temizleme benzeri davranış ile veri toplama davranışının peş peşe gelmesi risklidir.

NORMAL BASELINE'DAN SAPMA: Kullanıcının normal silme hacmi haftada 20–30 mail iken olayda 2 saatte 1.900 mail silinmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Ayrılan çalışanlar bazen izlerini azaltmak için geçmiş iletişimi temizlemeye çalışır.

---

SENARYO ADI: Destek Personelinden Yetkisiz Mail Attachments Kopyası

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek personeli, arşivleme sorunu bahanesiyle dahili mail sunucusundaki büyük ekleri ortak klasöre export eder; içinde hukuk ve İK belgeleri de vardır.

NEDEN ŞÜPHELİ: Görevle uyumsuz içerik export’u ve hassas eklere toplu erişim.

NORMAL BASELINE'DAN SAPMA: Normal destek işlemleri metadata seviyesinde olurken olayda 8.2 GB ek dosyası dışarı alınmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Teknik arıza incelemesi bahanesi, gereğinden fazla veri erişimini meşrulaştırmak için kullanılabilir.

---

SENARYO ADI: Veri Analistinin İnsan Kaynakları Verisini Model Eğitimi İçin Kullanması

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist, çalışan churn modeli denemesi için izin almadan İK performans notları, devamsızlık kayıtları ve bordro özetlerini aynı veri setinde birleştirir.

NEDEN ŞÜPHELİ: Farklı hassas veri tiplerinin rol dışında bir araya getirilmesi.

NORMAL BASELINE'DAN SAPMA: Analistin normal kaynakları satış ve destek verisi iken olayda 3 yeni hassas kaynak join edilmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Analitik değer arayışıyla veri kullanım sınırları kolayca aşılabilir.

---

SENARYO ADI: IT Admin’in Çok Sayıda Credential Reset’i

KATEGORİ: credential ihlali

KULLANICI ROLÜ: IT Admin

OLAY: Bir IT Admin, tek vardiyada 11 farklı kullanıcının şifresini resetler; ancak açılmış resmi destek kaydı sadece 2 adettir.

NEDEN ŞÜPHELİ: Açıklanamayan toplu credential müdahalesi hesap ele geçirme hazırlığı olabilir.

NORMAL BASELINE'DAN SAPMA: Admin’in günlük ortalama reset sayısı 1–3 iken olayda 11 reset vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İçeriden tehditlerde ilk adım genellikle erişim zinciri kurmak için kimlik bilgilerini yönetmektir.

---

SENARYO ADI: Hukuk Çalışanından Toplantı Odası Terminaline Belge İndirme

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Hukuk

OLAY: Hukuk çalışanı, sözleşme sunumu için belgeleri toplantı odası terminaline indirir ve toplantı sonrasında belgeler yerelde kalır.

NEDEN ŞÜPHELİ: Paylaşımlı cihazda hassas belge kalıcılığı veri maruziyetidir.

NORMAL BASELINE'DAN SAPMA: Hukuk belgeleri normalde şifreli paylaşımla görüntülenirken olayda 1.1 GB belge local cache’e yazılmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Toplantı hazırlığında kullanıcılar güvenli erişim yerine yerel indirmeyi tercih edebilir.

---

SENARYO ADI: CFO Hesabıyla Yapılan API Rapor Çağrıları

KATEGORİ: credential ihlali

KULLANICI ROLÜ: CFO

OLAY: CFO hesabı, normalde GUI üzerinden kullanılan finans raporlama sistemine bu kez API üzerinden bağlanarak yüzlerce rapor çeker.

NEDEN ŞÜPHELİ: Kullanıcı profilinde daha önce görülmeyen programatik kullanım biçimi ve yüksek hacim.

NORMAL BASELINE'DAN SAPMA: CFO’nun son 180 günde API kullanımı sıfırken olayda 950 rapor çağrısı vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Çalınan ya da paylaşılan kullanıcı credential’ları çoğu zaman alışılmadık erişim kanallarıyla kullanılır.

---

SENARYO ADI: Geliştiriciden Test Verisi Diye Prod Veri Kullanımı

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, hata üretmek için test ortamı yerine üretimden alınmış kullanıcı verisini iç ağ test paylaşım klasörüne bırakır.

NEDEN ŞÜPHELİ: Prod verinin test alanına taşınması gizlilik ve uyum riskidir.

NORMAL BASELINE'DAN SAPMA: Test paylaşım klasöründe normal dosya boyutu 10–100 MB iken olay dosyası 4.3 GB’tır ve PII alanları içerir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Hız baskısı altında ekipler gerçek veriyi test verisi gibi kullanma hatasına düşebilir.

---

SENARYO ADI: İK Uzmanına Taklit Edilen İç Destek Talimatı

KATEGORİ: sosyal mühendislik

KULLANICI ROLÜ: İK

OLAY: İK çalışanı, iç destekten geldiğini düşündüğü bir mesajla performans değerlendirme klasörünü “sorun analizi için” geçici erişime açar.

NEDEN ŞÜPHELİ: Rol dışı destek talebi, hassas klasör yetkisinin anlık genişletilmesi ve mesaj kanalındaki anormallik önemli göstergelerdir.

NORMAL BASELINE'DAN SAPMA: İK klasörleri son 60 günde hiç geçici herkese açık yapılmamışken olayda 47 dakika boyunca geniş erişim açıktır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İç iletişim kanallarında taklit edilen destek istekleri çalışanları kolayca kandırabilir.

---

SENARYO ADI: Veri Analisti ile Muhasebe Arasında Kural Dışı Dosya Alışverişi

KATEGORİ: diğer

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist, gelir tahmin modeli için muhasebeden ham fatura satırlarını ister; muhasebe çalışanı da dosyaları kişisel analist klasörüne bırakır.

NEDEN ŞÜPHELİ: Resmi veri paylaşım akışının dışında, hassas finans verisinin bireysel klasöre verilmesi.

NORMAL BASELINE'DAN SAPMA: Muhasebe verisi normalde rapor seviyesinde paylaşılırken olayda 12 milyon satırlık ham veri aktarılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Departmanlar arası iş birliği iyi niyetli olsa da veri erişim kurallarını aşabilir.

---

SENARYO ADI: Güvenlik Görevlisinin USB ile Kamera Kayıt Kopyası

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Güvenlik görevlisi, olay incelemesi bahanesiyle iç ağ üzerindeki CCTV kayıt sunucusundan belirli kameraların görüntülerini USB cihaza alır.

NEDEN ŞÜPHELİ: Gözetim verisinin onaysız taşınabilir medya ile dışarı alınması yüksek risklidir.

NORMAL BASELINE'DAN SAPMA: Normal export işlemleri yalnızca merkezi olay odasına giderken olayda 28 GB video USB’ye yazılmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Kamera kayıtları içeriden kötüye kullanım veya şantaj amaçlı hedef olabilir.

---

SENARYO ADI: PM’nin Toplantı Hazırlığı İçin CEO Mailine Erişmesi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, yönetim sunumunu hazırlamak için CEO’nun paylaşımlı asistan klasöründe bulunan iç mail özetlerine bakar ve yetki sınırını aşar.

NEDEN ŞÜPHELİ: Üst yönetim yazışmalarına rol dışı erişim ve içerik keşfi.

NORMAL BASELINE'DAN SAPMA: PM rolü için yönetim mail özetlerine erişim baseline’da yoktur; olayda 63 öğe okunmuştur.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: “Sunumu anlamam lazım” gibi gerekçelerle sınır aşımı kolayca normalleştirilebilir.

---

SENARYO ADI: Yeni Çalışanın Fazla Uzun Oturumu

KATEGORİ: diğer

KULLANICI ROLÜ: Stajyer

OLAY: Yeni stajyer hesabı 19 saat boyunca aralıksız açık kalır, bu sürede farklı paylaşımlı klasörlerde kısa aralıklarla gezinme yapılır.

NEDEN ŞÜPHELİ: Unutulmuş açık oturum, hesabın başkası tarafından kullanılmasına veya otomatik keşfe işaret edebilir.

NORMAL BASELINE'DAN SAPMA: Stajyer oturumları normalde 6–8 saat sürerken olay 19 saattir ve 14 farklı klasör erişimi vardır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Yeni çalışanlar oturum kapatma alışkanlıklarını oturtamayabilir; bu durum ikincil risk yaratır.

---

SENARYO ADI: Departmanlar Arası Credentials Excel’i

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek personeli, “işler hızlansın” diye farklı servis hesaplarını ve geçici parolaları içeren bir Excel dosyasını dahili paylaşıma koyar. Dosya zamanla birçok ekip tarafından kullanılmaya başlar.

NEDEN ŞÜPHELİ: Credential’ların merkezi olmayan ve geniş erişimli biçimde tutulması büyük kurumsal risk oluşturur.

NORMAL BASELINE'DAN SAPMA: Önceden credential paylaşımı tekil ticket notlarında iken olayda 17 hesap tek dosyada toplanmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Kolaylık için yapılan böyle listeler gerçek ihlallerde çok sık kök neden olur.

---

SENARYO ADI: CTO’nun Gizli Proje Kodlarını Hukuk’a Toplu Göndermesi

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: CTO

OLAY: CTO, patent başvurusu için gerekli parçaları hukuk ekibine göndermek isterken tüm özel Ar-Ge deposunun tam arşivini iç mail eki olarak paylaşım sunucusuna bırakır.

NEDEN ŞÜPHELİ: Amaçla orantısız veri kapsamı ve hassas kodun geniş erişimli transfer alanına düşmesi.

NORMAL BASELINE'DAN SAPMA: Tipik teknik belge paylaşımı 20–50 MB iken olayda 11 GB kaynak kod arşivi taşınmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İyi niyetli ama aşırı kapsamlı belge gönderimi çok sık veri sızıntısı benzeri sonuç doğurur.

---

SENARYO ADI: Satış Çalışanının Boşta Kalan Hesabı Kullanması

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Satış

OLAY: Satış çalışanı, izinli bir arkadaşının açık kalan CRM oturumunu kullanarak bölgesi dışındaki müşteri kayıtlarını inceler.

NEDEN ŞÜPHELİ: Oturum sahibi ile fiziksel kullanıcı uyumsuzluğu ve yetki alanı dışı erişim vardır.

NORMAL BASELINE'DAN SAPMA: İzinli kullanıcının hesabında iş günü aktivitesi olmaması gerekirken 137 kayıt görüntülenmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Açık bırakılan oturumlar ve iş arkadaşı güveni iç tehditlere zemin hazırlar.

---

SENARYO ADI: Hukuk Arşivinde Dosya İsimleriyle Keşif

KATEGORİ: insider threat

KULLANICI ROLÜ: Hukuk

OLAY: Hukuk çalışanı, açıkça erişme yetkisi olmayan birleşme klasörlerine dosya içeriğini açmadan yalnızca isim ve meta-veri düzeyinde çok sayıda sorgu yapar.

NEDEN ŞÜPHELİ: Hedefli keşif davranışı, sonradan gelecek erişim için hazırlık olabilir.

NORMAL BASELINE'DAN SAPMA: Kullanıcının tipik belge araması günde 20 sorgu iken olayda 410 meta-veri sorgusu vardır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Saldırgan veya içeriden tehdit aktörleri önce sadece neyin nerede olduğunu anlamaya çalışır.

---

SENARYO ADI: İK’dan Stajyere Fazla Yetki Verilmesi

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: İK

OLAY: Onboarding sırasında İK çalışanı, stajyerin eğitim klasörü yerine çalışan rehberi ile aynı isimdeki çalışan özlük klasörüne erişim verir.

NEDEN ŞÜPHELİ: Yeni çalışan hesabına gereksiz hassas klasör yetkisi tanımlanması.

NORMAL BASELINE'DAN SAPMA: Stajyer erişimi normalde 6 klasörle sınırlıyken olayda 2 ek hassas personel klasörü açılmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Benzer klasör isimleri ve onboarding yoğunluğu erişim hatalarına yol açabilir.

---

SENARYO ADI: API Rate Deseninden Ayrılan CFO Asistanı

KATEGORİ: diğer

KULLANICI ROLÜ: CFO

OLAY: CFO ofisinde kullanılan bir otomasyon, dahili finans API’sine insan kullanımına benzer düzensiz aralıklarla ama çok uzun süreler boyunca çağrı yapar; hesabın gerçekte CFO yerine asistan tarafından scriptle kullanıldığı anlaşılır.

NEDEN ŞÜPHELİ: İnsan hesabının otomasyon gibi davranması ve görev devrinin izinsiz yapılması.

NORMAL BASELINE'DAN SAPMA: CFO hesabı normalde günde 20–40 etkileşim üretirken olayda 2.300 API çağrısı vardır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Yöneticilerin hesapları bazen yardımcı personelce fiilen paylaşılır; bu güvenlik ve denetlenebilirlik problemidir.

---

SENARYO ADI: Geliştiricinin Build Sunucusundan Mail Verisi Okuması

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, build sunucusunda test ederken yanlış yapılandırılmış mount sayesinde dahili mail arşivine erişir ve içerik incelemeye başlar.

NEDEN ŞÜPHELİ: Yanlış yapılandırılmış servis yoluyla rol dışı veri erişimi.

NORMAL BASELINE'DAN SAPMA: Build sunucularından mail arşivine erişim baseline’da sıfırdır; olayda 600 dosya listelenmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Konfigürasyon hataları, beklenmeyen yan erişim yolları oluşturabilir.

---

SENARYO ADI: Muhasebe Personelinin Kendine Ait Olmayan Fatura Havuzu

KATEGORİ: insider threat

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, performans kıyası için başka ekip arkadaşlarının işlediği tedarikçi klasörlerini açıp toplu şekilde inceler.

NEDEN ŞÜPHELİ: İş gereği olmayan çapraz inceleme ve görev ayrılığı ihlali.

NORMAL BASELINE'DAN SAPMA: Kullanıcı normalde 3 tedarikçi portföyüyle çalışırken olayda 19 portföy klasörüne erişmiştir.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: İç rekabet veya merak, finans ekiplerinde yetkisiz görüntüleme davranışına yol açabilir.

---

SENARYO ADI: Gece Vardiyasında Toplu Badge Basımı Sonrası Sistem Erişimi

KATEGORİ: dış saldırı destegi

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Güvenlik görevlisi, gece acil misafir kartı bahanesiyle birden fazla geçici kart basar. Aynı zamanlarda bu kartlarla erişilen alanlardaki terminallerden çok sayıda dahili dosya erişimi başlar.

NEDEN ŞÜPHELİ: Fiziksel giriş anomalisi ile dijital erişim zincirinin örtüşmesi.

NORMAL BASELINE'DAN SAPMA: Gece vardiyasında ortalama 0–1 geçici kart basılırken olayda 6 kart basılmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Saldırganlar iç ağa sızmak için fiziksel giriş noktalarını kullanabilir.

---

SENARYO ADI: CEO’nun Stajyere Mail Delege Etmesi

KATEGORİ: politika ihlali

KULLANICI ROLÜ: CEO

OLAY: CEO, tatildeyken bazı mailleri ayıklasın diye stajyere kendi dahili mail kutusuna kısmi erişim verir.

NEDEN ŞÜPHELİ: Hiyerarşik güvene dayalı olsa da rol ve veri minimizasyonu ilkelerini ihlal eder.

NORMAL BASELINE'DAN SAPMA: Stajyerlerin üst yönetim posta kutularına erişimi baseline’da sıfırdır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Üst düzey yöneticiler operasyonel rahatlık için yanlış delege kararları verebilir.

---

SENARYO ADI: Destekten Finance Share’e Merak Amaçlı Göz Atma

KATEGORİ: insider threat

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek çalışanı, herkesin erişemediği finans paylaşımına yanlış kalmış bir izin sayesinde girip bonus listelerini arar.

NEDEN ŞÜPHELİ: Görevle ilişkisi olmayan hassas finans verisine hedefli arama yapılması.

NORMAL BASELINE'DAN SAPMA: Destek rolünün finans dosyalarına erişimi tarihsel olarak yoktur; olayda 22 arama sorgusu yapılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Yanlış kalmış izinler çoğu zaman ancak anormal kullanım başladığında fark edilir.

---

SENARYO ADI: IT Admin’in Audit Log Temizliği

KATEGORİ: insider threat

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, hukuk paylaşımına yaptığı olağan dışı erişimlerden sonra ilgili sistemlerin audit log retention ayarlarını geçici olarak azaltır.

NEDEN ŞÜPHELİ: İz silme davranışı, yüksek güvenliğe sahip kullanıcılarda kritik göstergedir.

NORMAL BASELINE'DAN SAPMA: Log retention ayarlarında son 120 günde değişiklik yokken olay gecesi 3 sistemde değişiklik yapılmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İçeriden tehdit aktörleri çoğu zaman iz bırakmamaya çalışır; admin hakları bunu mümkün kılabilir.

---

SENARYO ADI: Veri Analistinin HR ve Access Log Join’i

KATEGORİ: diğer

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist, verimlilik analizi bahanesiyle çalışanların kartlı geçiş kayıtlarını, login saatlerini ve İK performans puanlarını tek tabloda birleştirir.

NEDEN ŞÜPHELİ: Çalışan gözetimi boyutuna kayan, hassas verilerin beklenmedik korelasyonu.

NORMAL BASELINE'DAN SAPMA: Normal analizler tek veri alanında yürürken olayda 3 hassas kaynağın birleşimi vardır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Analitik ekipler iş değeri için veri kaynaklarını birleştirirken etik ve yetki sınırlarını aşabilir.

---

SENARYO ADI: Stajyerden Paylaşımlı Credential Kullanımı

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Stajyer

OLAY: Bir mentor, işleri kolaylaştırmak için stajyere ekip içi ortak test hesabını verir. Stajyer bu hesapla daha geniş sistemlere erişir.

NEDEN ŞÜPHELİ: Bireysel izlenebilirliği ortadan kaldıran ortak hesap kullanımı.

NORMAL BASELINE'DAN SAPMA: Stajyerler bireysel hesapla sınırlıyken olayda paylaşımlı hesap üzerinden 5 sisteme erişim vardır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Eğitim süreçlerinde “şimdilik bunu kullan” yaklaşımı çok yaygındır.

---

SENARYO ADI: CFO Terminalinden USB Takılıyken Bordro Export’u

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: CFO

OLAY: CFO terminaline onaysız bir USB depolama aygıtı takılır ve aynı 10 dakikalık pencere içinde bordro sisteminden toplu export alınır.

NEDEN ŞÜPHELİ: Hassas veri export’u ile taşınabilir medya olayının korelasyonu kritik alarm gerektirir.

NORMAL BASELINE'DAN SAPMA: CFO cihazında son 1 yılda USB kullanımı yokken olayda 8.9 GB bordro verisi export edilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Üst düzey yöneticiler bazen “offline çalışmak” veya “taşımak” için güvenlik dışı yöntemlere başvurabilir.

---

SENARYO ADI: PM’den Yetki Aşan Dashboard İsteği

KATEGORİ: sosyal mühendislik / politika ihlali

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, geliştiriciye “demo için gerekli” diyerek destek, satış ve finans verilerini tek dashboard’da toplatır.

NEDEN ŞÜPHELİ: Birden fazla departmandan gereksiz veri konsolidasyonu ve hiyerarşik baskı.

NORMAL BASELINE'DAN SAPMA: Demo dashboard’ları normalde anonim/özet veri içerirken olayda üç hassas kaynak canlı bağlanmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Proje baskısı altında veri kapsamı farkında olmadan aşırı genişletilebilir.

---

SENARYO ADI: Hukuk Departmanında Yanlış Grup Politikası

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: IT Admin

OLAY: Bir grup ilkesi güncellemesi sonrası hukuk paylaşım klasörü okunabilir izinle proje yöneticilerine de görünür hale gelir.

NEDEN ŞÜPHELİ: Hassas departman verisinin yetki dışı rol grubuna açılması.

NORMAL BASELINE'DAN SAPMA: Önceden 2 hukuk kullanıcısı erişirken olayla 5 PM hesabı görünürlük kazanır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: IAM ve grup politikası değişiklikleri kurumsal ihlallerin önemli kaynağıdır.

---

SENARYO ADI: Destek Personelinin Eski Disk İmajlarında Gezinmesi

KATEGORİ: insider threat

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek çalışanı, arızalı laptoplardan alınmış disk imajlarını inceleme yetkisini kullanarak eski kullanıcı belgelerinde gezinir.

NEDEN ŞÜPHELİ: Teknik inceleme yetkisinin içerik keşfi için kullanılması.

NORMAL BASELINE'DAN SAPMA: Normalde destek işlemleri hash/doğrulama düzeyinde iken olayda 300’den fazla kullanıcı dosyası açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Teknik personel veri kalıntılarına erişebilir; denetim olmazsa kötüye kullanım mümkün olur.

---

SENARYO ADI: Muhasebeden Hukuka Yanlış Dosya Senkronu

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, vergi dokümanlarını hukuk ile paylaşmak için klasör senkron script’i çalıştırır; fakat yanlış path nedeniyle tüm ödeme kayıtları da kopyalanır.

NEDEN ŞÜPHELİ: Kapsam dışı büyük veri kopyası ve departmanlar arası gereksiz görünürlük.

NORMAL BASELINE'DAN SAPMA: Normal paylaşım 50–100 dosya iken olayda 12.400 dosya taşınmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Küçük script hataları büyük veri maruziyeti doğurabilir.

---

SENARYO ADI: Güvenlik Kamerası Sunucusunda Anormal Gezinme

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, erişim kontrol uygulamasındaki entegrasyon hatasını test ederken CCTV sunucusunda klasörler arasında gezinmeye başlar.

NEDEN ŞÜPHELİ: Teknik test bahanesiyle görev alanı dışındaki fiziksel güvenlik verisine erişim.

NORMAL BASELINE'DAN SAPMA: Geliştiriciler normalde CCTV sunucusuna hiç bağlanmaz; olayda 88 dizin listelenmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Entegrasyon çalışan ekipler bazen hedef sistem sınırlarını aşabilir.

---

SENARYO ADI: CEO İçin Hazırlanan Sunumda Gerçek Personel Verisi

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, yönetim toplantısı için hazırladığı sunum paylaşım klasörüne gerçek maaş ve performans verilerini ham haliyle koyar.

NEDEN ŞÜPHELİ: Sunum amaçlı özet yerine ham hassas veri kullanımı ve paylaşımlı klasörde tutulması.

NORMAL BASELINE'DAN SAPMA: Yönetim sunum klasörlerinde genelde PDF/özet veri bulunurken olayda 3 ham Excel ve 2.1 GB kaynak veri vardır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Sunum baskısı, verinin uygun biçimde anonimleştirilmeden paylaşılmasına yol açar.

---

SENARYO ADI: Veri Analistinin Çok Hızlı Departman Taraması

KATEGORİ: insider threat

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist hesabı 30 dakika içinde muhasebe, İK, satış, hukuk ve destek klasörlerinde kısa süreli ama sistematik taramalar yapar.

NEDEN ŞÜPHELİ: Normal görev akışına uymayan geniş keşif davranışı.

NORMAL BASELINE'DAN SAPMA: Kullanıcı normalde 1–2 veri kaynağıyla çalışırken olayda 5 departman ve 280 dosya listelenmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İç tehdit aktörleri önce erişebildikleri alanların envanterini çıkarır.

---

SENARYO ADI: Stajyerin İç Mailde Yanlış Eki Herkese Göndermesi

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer, eğitim sunumunu göndermek isterken aynı klasörde bulunan çalışan iletişim listesini şirket geneline iç mail eki olarak yollar.

NEDEN ŞÜPHELİ: Geniş dağıtım listesine yanlış hassas ek gönderimi.

NORMAL BASELINE'DAN SAPMA: Stajyerin normal alıcı sayısı 3–5 iken olayda 35 alıcıya gönderim yapılmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Dizin karışıklığı ve benzer dosya adları yeni çalışanlarda sık hataya neden olur.

---

SENARYO ADI: IT Admin’den Gölge Yedek Sunucusu

KATEGORİ: insider threat

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, resmi backup sistemine ek olarak kendi kontrolündeki dahili bir NAS cihazına seçili departmanların yedeklerini almaya başlar.

NEDEN ŞÜPHELİ: Onaysız ikinci kopya, veri sahipliği ve görünürlük sorunları yaratır.

NORMAL BASELINE'DAN SAPMA: Backup hedef sayısı normalde 1 iken olayda 2’ye çıkar ve ikincisi kayıtlı envanterde yoktur.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Gölge yedekleme, teknik kolaylık bahanesiyle yapılan ama yüksek risk taşıyan bir pratiktir.

---

SENARYO ADI: CFO’nun Bordroya Erişen Geliştirici Hesabı Fark Etmeden Onaylaması

KATEGORİ: sosyal mühendislik / kazara ihlal

KULLANICI ROLÜ: CFO

OLAY: CFO, “rapor otomasyonu için gerekli” denilerek önüne getirilen dahili yetki onayını detay okumadan kabul eder; bu onayla geliştirici hesabı bordro klasörüne erişir.

NEDEN ŞÜPHELİ: Yönetici onayı ile rol uyumsuz yetki genişlemesi oluşmuştur.

NORMAL BASELINE'DAN SAPMA: Geliştirici rollerinin bordro erişimi baseline’da sıfırdır; olayla 1 hesap erişim kazanır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Yetki onayları çoğu zaman iş yükü altında detay incelenmeden verilebilir.

---

SENARYO ADI: Muhasebe Çalışanının Kendi USB’siyle Fatura Arşivi Alması

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, evde çalışmak için geçmiş fatura arşivini kişisel USB’sine alır.

NEDEN ŞÜPHELİ: Onaysız taşınabilir medya kullanımı ve geniş finans veri kopyası.

NORMAL BASELINE'DAN SAPMA: Finans cihazlarında USB yazımı normalde kapalıyken olayda 16 GB veri yazma denemesi kaydedilir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Çalışanlar bazen iyi niyetle işleri eve taşımaya çalışır; bu ciddi veri koruma riskidir.

---

SENARYO ADI: Hukuk Asistanı Gibi Davranan İç Çağrı

KATEGORİ: sosyal mühendislik

KULLANICI ROLÜ: Hukuk

OLAY: Hukuk çalışanı, kendini hukuk asistanı olarak tanıtan bir dahili arama sonrası bir dava klasörünün yolunu ve erişim mekanizmasını paylaşır.

NEDEN ŞÜPHELİ: Kimlik doğrulanmamış iç arama sonrası hassas bilgi paylaşımı.

NORMAL BASELINE'DAN SAPMA: Hassas dava klasörü bilgisi normalde yalnızca yüz yüze ya da kayıtlı ticket ile paylaşılırken olay telefon üzerinden verilmiştir.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: İçerideymiş gibi davranan kişiler çalışan güvenini daha kolay kazanabilir.

---

SENARYO ADI: Veri Analistinin Credential Notunu Ortak Wiki’ye Koyması

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist, veri pipeline çalışsın diye servis anahtarını dahili wiki sayfasına not eder.

NEDEN ŞÜPHELİ: Credential’ın insan okunur ve geniş erişimli ortamda tutulması.

NORMAL BASELINE'DAN SAPMA: Önceden wiki’de hiç secret bulunmazken olayda aktif bir API key metin olarak kaydedilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Bilgi paylaşımı kültürü bazen sırların yanlış yerde tutulmasına neden olur.

---

SENARYO ADI: Stajyerin Fazla Meraklı API Çağrıları

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer, dahili geliştirici portalında gördüğü örnek endpoint’leri kendi hesabıyla denemeye başlar ve farklı departman verilerini döndüren API’lere istek atar.

NEDEN ŞÜPHELİ: Öğrenme motivasyonu olsa da rol dışı API denemeleri ve yetki sınırı test etme davranışı vardır.

NORMAL BASELINE'DAN SAPMA: Stajyer hesabının normal API çağrısı günde 20’nin altındayken olayda 480 farklı istek oluşmuştur.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Meraklı yeni çalışanlar sınırları bilmeden tehlikeli denemeler yapabilir.

---

SENARYO ADI: IT Admin’den CEO Mail Kutusuna Kendine Delege

KATEGORİ: insider threat

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, “senkronizasyon sorunu incelemesi” bahanesiyle CEO mail kutusuna geçici delege erişimi açar ve sonra kaldırır.

NEDEN ŞÜPHELİ: Kısa süreli fakat yüksek hassasiyetli içerik erişimi ve sonradan izin temizleme davranışı.

NORMAL BASELINE'DAN SAPMA: CEO mailbox müdahaleleri yılda 0–1 iken olayda 23 dakika boyunca delege erişim vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Kısa süreli ayrıcalık kötüye kullanımı log korelasyonu yapılmazsa gözden kaçabilir.

---

SENARYO ADI: Satıştan Toplu Müşteri Ekleri Arşivi

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: Satış

OLAY: Satış çalışanı, geçmiş teklif eklerini ve sözleşmeleri dahili mail arşivinden toplu olarak klasöre export eder.

NEDEN ŞÜPHELİ: Toplu müşteri dokümanı biriktirme ve görevle orantısız hacim.

NORMAL BASELINE'DAN SAPMA: Günlük ortalama 10–15 teklif dosyası yerine olayda 2.700 ek dosyası export edilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Müşteri portföyüyle ayrılmak isteyen satış çalışanları bu tip davranış gösterebilir.

---

SENARYO ADI: Destek Personelinin HR Bilgilerini Ekran Paylaşımıyla Açması

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek çalışanı, ortak toplantı ekranına bağlandığını fark etmeden bir İK kullanıcısının cihazında açık olan personel dosyalarını troubleshooting sırasında görüntüler.

NEDEN ŞÜPHELİ: Hassas içeriğin gereksiz görünürlüğü ve paylaşımlı ortamda açılması.

NORMAL BASELINE'DAN SAPMA: Standart destek seanslarında büyük ekrana yayın yokken olayda 17 dakika boyunca açık paylaşım vardır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Toplantı odası ve uzaktan yardım kombinasyonlarında bu tip maruziyetler yaşanabilir.

---

SENARYO ADI: CTO’dan Anormal Kod Repo Kopyası

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: CTO

OLAY: CTO hesabı, normalde tekil repo incelemesi yaparken bir gecede tüm özel repositorileri iç ağ mirror sunucusuna tam clone eder.

NEDEN ŞÜPHELİ: Toplu fikri mülkiyet toplama davranışı ve saat dışı kullanım.

NORMAL BASELINE'DAN SAPMA: Normalde günde 2–4 repo erişimi varken olayda 39 repo tam kopyalanmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Üst düzey teknik rol sahipleri en değerli IP’ye erişir; bu yüzden davranış sapması kritiktir.

---

SENARYO ADI: Muhasebe’den Yanlış Departmana Gönderilen Vergi Dosyaları

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, vergi danışmanlığı için hazırladığı iç paketleri hukuk yerine satış ortak klasörüne bırakır.

NEDEN ŞÜPHELİ: Hassas finans dosyalarının yanlış departman paylaşımına düşmesi.

NORMAL BASELINE'DAN SAPMA: Bu dosya tipi daha önce hiç satış klasörlerinde görülmemiştir; olayda 620 dosya taşınmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Benzer klasör isimleri ve sürükle-bırak hataları operasyon yoğunluğunda yaşanır.

---

SENARYO ADI: Güvenlik Personelinin Ağ Haritası Dosyalarını Açması

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Fiziksel güvenlik görevlisi, sunucu odası turu sonrası iç ağ topoloji diyagramlarını içeren BT klasörünü açar.

NEDEN ŞÜPHELİ: Fiziksel erişim bilgisi ile ağ mimarisi bilgisinin birleşmesi risklidir.

NORMAL BASELINE'DAN SAPMA: Güvenlik görevlilerinin BT klasörlerine erişimi yoktur; olayda 14 belge açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Saldırganlara içeriden destek veren kişiler hem fiziksel hem mantıksal bilgi toplamaya çalışabilir.

---

SENARYO ADI: Proje Yöneticisinin Çok Sayıda Kullanıcıdan Ekran Görüntüsü İstemesi

KATEGORİ: sosyal mühendislik

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, “durum raporu” bahanesiyle farklı ekiplerden uygulama ekran görüntüleri ister; görüntülerde hassas müşteri, finans ve İK bilgileri görünür.

NEDEN ŞÜPHELİ: Gereksiz veri toplama ve rol temelli veri kapsamının aşılması.

NORMAL BASELINE'DAN SAPMA: Normal raporlama özet metrik düzeyindeyken olayda 19 ham ekran görüntüsü toplanmıştır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Sosyal baskı ile çalışanlardan gereksiz veri talep edilmesi sık rastlanan bir iç risk biçimidir.

---

SENARYO ADI: Veri Analisti Hesabından Gece HR API Sorguları

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist hesabı, mesai dışı saatte İK API’sine seri sorgular gönderir; analistin ofiste olmadığı bilinmektedir.

NEDEN ŞÜPHELİ: Zaman dışı davranış, rol dışı veri kaynağı ve sahip olunan fiziksel bağlamla uyumsuzluk.

NORMAL BASELINE'DAN SAPMA: Analistin önceki 60 günde hiç 20:00 sonrası aktivitesi yokken olayda 700 sorgu vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İç ağda da kimlik bilgileri çalınabilir veya paylaşılabilir; UEBA bağlamsal anomaliyi görmelidir.

---

SENARYO ADI: IT Admin’in Sessiz Grup Üyeliği Eklemesi

KATEGORİ: insider threat

KULLANICI ROLÜ: IT Admin

OLAY: IT Admin, destek gerekçesi olmadan kendi ikinci hesabını finans-oku grubuna ekler ve kısa süre sonra bütçe dosyalarına erişir.

NEDEN ŞÜPHELİ: Kendi lehine yetki genişletme ve ardından kullanım.

NORMAL BASELINE'DAN SAPMA: İkinci hesap normalde temel kullanıcı grubundayken olay günü 1 hassas gruba eklenmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Yetkili kullanıcılar doğrudan kendi erişimlerini artırabilir; denetim olmadan fark edilmez.

---

SENARYO ADI: Stajyerin İç Ağa Bağlı Kişisel Cihazı

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer, şirket laptopu yerine kişisel cihazını dahili ağa bağlayarak paylaşımlı eğitim klasörüne erişir.

NEDEN ŞÜPHELİ: Onaysız uç nokta kullanımı ve kurumsal denetim dışı cihazdan veri erişimi.

NORMAL BASELINE'DAN SAPMA: Stajyer için yetkili cihaz sayısı 1 iken olayda yeni, yönetilmeyen cihaz görünür.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Özellikle yeni çalışanlar kurumsal cihaz politikalarını tam anlamayabilir.

---

SENARYO ADI: İK Çalışanının Toplu Disiplin Notu Export’u

KATEGORİ: insider threat

KULLANICI ROLÜ: İK

OLAY: İK çalışanı, şirket içi anlaşmazlık sonrası son 3 yıla ait disiplin notlarını topluca dışa aktarır ve kendi departman klasöründe ayrı bir arşiv oluşturur.

NEDEN ŞÜPHELİ: Görev anında gerekmeyen, toplu hassas personel verisi toplama davranışı.

NORMAL BASELINE'DAN SAPMA: Tipik kullanım tekil vaka bazlı iken olayda 1.200 kayıt export edilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Duygusal veya kurumsal çatışma yaşayan çalışanlar hassas veriyle misilleme hazırlığı yapabilir.

---

SENARYO ADI: CFO ve Muhasebe Arasında Ortak Hesap Kullanımı

KATEGORİ: credential ihlali

KULLANICI ROLÜ: CFO

OLAY: CFO, yoğunluk nedeniyle rapor sistemindeki kendi hesabını muhasebe müdürüne verir; aynı hesap iki farklı cihazda dönüşümlü kullanılır.

NEDEN ŞÜPHELİ: Yönetici hesabının paylaşılması, denetlenebilirliği ve erişim sınırlarını bozar.

NORMAL BASELINE'DAN SAPMA: CFO hesabında önce tek cihaz paterni varken olay haftasında 4 cihaz kullanılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Üst düzey hesap paylaşımı pratikte olabiliyor ve çoğu zaman uzun süre fark edilmiyor.

---

SENARYO ADI: Yazılım Geliştiriciden Çoklu Credential Denemesi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, eski entegrasyon dokümanlarında gördüğü birkaç servis hesabını iç ağ üzerinde sırayla deneyerek erişim kapsamını test eder.

NEDEN ŞÜPHELİ: Farklı credential’larla art arda deneme, keşif ve yetki genişletme niyetini gösterir.

NORMAL BASELINE'DAN SAPMA: Kullanıcı normalde tek geliştirici hesabı kullanırken olayda 6 ayrı servis kimliği denenmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Teknik merak veya kasıtlı deneme, çoğu zaman “bakayım çalışıyor mu” şeklinde başlar.

---

SENARYO ADI: Destek Personelinin Çok Geniş Mail Araması

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek çalışanı, sorun araştırması bahanesiyle dahili mail arşivinde “salary”, “discipline”, “termination” gibi anahtar kelimelerle arama yapar.

NEDEN ŞÜPHELİ: Teknik destek göreviyle ilgisiz, hassas içerik odaklı anahtar kelime taraması.

NORMAL BASELINE'DAN SAPMA: Normal destek mail aramaları hata kodu odaklıyken olayda 12 hassas anahtar kelime kullanılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İç tehditlerde anahtar kelime tabanlı keşif çok yaygın bir taktiktir.

---

SENARYO ADI: Veri Analisti Tarafından Oluşturulan Gölge Veri Martı

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist, sürekli beklemekten kaçınmak için satış, finans ve İK verilerini kendi kontrolündeki dahili SQLite sunucusunda toplar.

NEDEN ŞÜPHELİ: Onaysız veri kopyası, merkezi denetimin dışında yeni hassas depo oluşturulması.

NORMAL BASELINE'DAN SAPMA: Kurumda kayıtlı veri martı sayısı 1 iken olayda belgelenmemiş ikinci depo ortaya çıkar.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Analitik ekipler çeviklik için gölge veri altyapısı kurabilir.

---

SENARYO ADI: Güvenlik Ofisi PC’sinden HR Erişimi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Güvenlik ofisindeki bilgisayardan bir güvenlik görevlisi hesabıyla çalışan özlük klasörlerine erişim olur.

NEDEN ŞÜPHELİ: Rol ve cihaz profilinin tamamen dışında veri erişimidir.

NORMAL BASELINE'DAN SAPMA: Güvenlik ofisi cihazlarının HR sistemlerine erişimi baseline’da sıfırdır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Fiziksel güvenlik personelinin böyle bir veriye ihtiyaç duyması çoğu durumda meşru değildir.

---

SENARYO ADI: PM’nin Yazılımcıdan Geçici Prod Erişimi İstemesi

KATEGORİ: sosyal mühendislik / yetkisiz erişim

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, kritik demo bahanesiyle geliştiriciden kendi hesabına geçici prod erişimi açmasını ister ve bu erişimi sonrasında da kapattırmaz.

NEDEN ŞÜPHELİ: Hiyerarşik baskıyla rol dışı yetki kazanılması.

NORMAL BASELINE'DAN SAPMA: PM rolleri için prod erişimi baseline’da yoktur; olayda 9 saatlik erişim açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Teslim baskısı, en sık rol dışı erişim gerekçelerinden biridir.

---

SENARYO ADI: İK’dan Çoklu USB Takma Denemesi

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: İK

OLAY: İK kullanıcısı, personel dosyalarını farklı USB cihazlarına kopyalamaya çalışır; ilk iki cihaz engellenince üçüncü cihaz tanınır.

NEDEN ŞÜPHELİ: Tekrarlı çıkarma girişimi ve hedeflenen hassas dosyalar.

NORMAL BASELINE'DAN SAPMA: Kullanıcının cihaz geçmişinde hiç USB olayı yokken 1 saatte 3 cihaz denenmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Bilinçli veri çıkarma girişimlerinde kullanıcılar birden fazla fiziksel aygıt deneyebilir.

---

SENARYO ADI: CFO Onayı Görünümlü Yanlış Dahili Workflow

KATEGORİ: sosyal mühendislik

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, intranet iş akışında CFO onayı gibi görünen fakat aslında yeni bir paylaşım kuralı oluşturan formu onaylar; bununla finans klasörü geniş erişime açılır.

NEDEN ŞÜPHELİ: Form tipi değişikliği, anormal workflow yolu ve yetki sonucunun beklenmedik olması.

NORMAL BASELINE'DAN SAPMA: Muhasebe kullanıcıları normalde paylaşım politikası değiştirmez; olayda 1 kritik ACL değişikliği oluşmuştur.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İç sistemlerdeki karmaşık form ve workflow’lar çalışanları kolayca yanıltabilir.

---

SENARYO ADI: CTO’nun Tüm API Credential Envanterini Çekmesi

KATEGORİ: insider threat

KULLANICI ROLÜ: CTO

OLAY: CTO, altyapı denetimi gerekçesiyle vault içeriğinin tam listesini export eder; export içinde aktif servis credential’ları da vardır.

NEDEN ŞÜPHELİ: Tüm sırların toplu envanteri çok yüksek değerde hedef oluşturur.

NORMAL BASELINE'DAN SAPMA: Normalde tekil secret erişimi yapılırken olayda 430 secret meta-verisi ve 80 değer export edilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Yüksek ayrıcalıklı rollerin toplu secret erişimi nadir ama çok kritik bir olaydır.

---

SENARYO ADI: Satış Çalışanının Hukuk Sözleşmelerini İncelemesi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Satış

OLAY: Satış çalışanı, müşteriye sunacağı indirimi öğrenmek için hukuk tarafındaki ana sözleşme şablonlarını ve istisna maddelerini açar.

NEDEN ŞÜPHELİ: Rol dışı hassas belge erişimi ve ticari avantaj amaçlı keşif.

NORMAL BASELINE'DAN SAPMA: Satış rolünün hukuk şablonlarına erişimi önceki 12 ayda hiç görülmemiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Ticari baskı, çalışanları sınır dışı belge erişimine itebilir.

---

SENARYO ADI: Geliştiricinin Loglarda Parola Araması

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, merkezi log sisteminde “password=”, “token=”, “secret” gibi ifadelerle arama yaparak yanlışlıkla dökülmüş sırları toplamaya çalışır.

NEDEN ŞÜPHELİ: Secret avı niteliğinde hedefli anahtar kelime araması.

NORMAL BASELINE'DAN SAPMA: Normal log aramaları hata kodu odaklıyken olayda 15 credential ifadesi aranmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Geliştiriciler sızmış sırları bazen “debug” için ararken, bu davranış kötüye kullanıma da dönüşebilir.

---

SENARYO ADI: Hukuk ve İK Verisini Aynı Toplantı Klasörüne Toplama

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Hukuk

OLAY: Hukuk çalışanı, çalışan anlaşmazlığı vakası için belge toplarken İK performans dosyalarını ve dava notlarını aynı ortak klasöre koyar.

NEDEN ŞÜPHELİ: Farklı hassas veri türlerinin gereksiz ortak depolanması.

NORMAL BASELINE'DAN SAPMA: Normalde vaka klasörleri tek departman erişimli iken olay klasörü 6 kişilik proje grubuna açıktır.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Departmanlar arası koordinasyonda veri ayrımı bozulabilir.

---

SENARYO ADI: Gece Boyu Süren Sessiz CRM Export’u

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: Satış

OLAY: Satış çalışanı, CRM’den her 15 dakikada küçük parçalar halinde müşteri kayıtlarını iç ağ dosya paylaşımına export eder; işlem tüm gece sürer.

NEDEN ŞÜPHELİ: Yavaş ve düşük profilli veri toplama paterni tipik sızdırma davranışıdır.

NORMAL BASELINE'DAN SAPMA: Gece kullanım baseline’da yoktur; toplam export hacmi 9.4 GB’a ulaşır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: DLP eşiklerinden kaçmak için veri sızdırma küçük parçalarla yapılabilir.

---

SENARYO ADI: CEO Adına Toplantı Terminalinden ACL Değişikliği

KATEGORİ: credential ihlali

KULLANICI ROLÜ: CEO

OLAY: CEO hesabı ile toplantı odası terminalinden ortak finans klasörünün erişim izinleri değiştirilir; CEO’nun böyle teknik işlem geçmişi yoktur.

NEDEN ŞÜPHELİ: Kullanıcı rolüyle uyumsuz teknik işlem ve alışılmadık cihaz kullanımı.

NORMAL BASELINE'DAN SAPMA: CEO geçmişinde ACL değişikliği 0 iken olayda 1 kritik klasör herkese okunur hale getirilmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Çalınan yönetici oturumları çoğu zaman güvenilir görünmek için kullanılır.

---

SENARYO ADI: Stajyerin Çok Sayıda Başarısız Login Sonrası Başarılı Girişi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer hesabı, muhasebe ve İK sistemlerine çok sayıda başarısız giriş denemesinden sonra hukuk paylaşımlarından birine erişmeyi başarır.

NEDEN ŞÜPHELİ: Sınırları test eden deneme-yanılma ve rol dışı hedefler.

NORMAL BASELINE'DAN SAPMA: Normalde stajyerde günlük 0–2 başarısız login varken olayda 47 başarısız deneme görülür.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Merak, yanlış yönlendirme veya kasıtlı keşif bu davranışı doğurabilir.

---

SENARYO ADI: Muhasebe Çalışanının API Anahtarını Kopyalayıp Script Yazdırması

KATEGORİ: sosyal mühendislik / credential ihlali

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, “raporunu otomatikleştireyim” diyen dahili bir geliştiriciye kendi finans API anahtarını verir; geliştirici bununla geniş veri çeker.

NEDEN ŞÜPHELİ: Sosyal etki ile credential paylaşımı ve sonrasında hacimli API kullanımı.

NORMAL BASELINE'DAN SAPMA: Anahtar normalde CFO onaylı rapor ekranında kullanılırken olayda script üzerinden 1.500 çağrı yapılmıştır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Yardım teklifleri üzerinden credential elde etmek kurum içi en kolay sosyal mühendislik yöntemlerindendir.

---

SENARYO ADI: Destek Personelinin Ayrılan Çalışan Hesabını Geç Kapatması

KATEGORİ: diğer

KULLANICI ROLÜ: Destek Personeli

OLAY: Ayrılmış bir satış çalışanının hesabı 6 gün boyunca aktif kalır ve bu sürede iç ağ erişimleri devam eder.

NEDEN ŞÜPHELİ: Deprovisioning gecikmesi ve aktif olmaması gereken hesabın kullanımı.

NORMAL BASELINE'DAN SAPMA: Offboarding standardı aynı gün kapatma iken olayda 6 gün gecikme vardır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Hesap kapatma gecikmeleri gerçek şirketlerde yaygın ve tehlikelidir.

---

SENARYO ADI: İK Hesabından Gece Mail Arşiv Taraması

KATEGORİ: insider threat

KULLANICI ROLÜ: İK

OLAY: İK çalışanı, işten çıkarma planlarıyla ilgili bilgileri toplamak için yöneticilerin dahili mail arşivinde meta-veri araması yapar.

NEDEN ŞÜPHELİ: Görev alanını aşan yönetim iletişimi keşfi ve mesai dışı kullanım.

NORMAL BASELINE'DAN SAPMA: İK kullanıcısının normal mail erişimi kendi kutusu ve İK shared box iken olayda 4 yönetim kutusunda arama vardır.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: İş güvencesi kaygısı yaşayan çalışanlar içeriden bilgi toplamaya yönelebilir.

---

SENARYO ADI: Veri Analistinin Legal Hold Dosyalarını Dahil Etmesi

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Veri Analisti

OLAY: Analist, şirket verisini temizlerken hukuki saklama kapsamındaki dosyaları da kendi veri setine dahil eder.

NEDEN ŞÜPHELİ: Legal hold altındaki veriye uygunsuz erişim ve çoğaltma.

NORMAL BASELINE'DAN SAPMA: Legal hold klasörlerine analist erişimi baseline’da sıfırdır; olayda 3.200 dosya indekslenmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Veri temizleme veya arşivleme projelerinde hukuki saklama kuralları atlanabilir.

---

SENARYO ADI: Geliştiricinin CFO Terminalinde Kod Çalıştırması

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Yazılım Geliştirici

OLAY: Geliştirici, finans uygulamasındaki bir sorunu hızlı görmek için CFO’nun masasındaki cihazda kendi script’ini çalıştırır.

NEDEN ŞÜPHELİ: Hassas kullanıcı cihazında yönetimsiz kod çalıştırılması ve çapraz rol cihaz kullanımı.

NORMAL BASELINE'DAN SAPMA: Geliştiriciler yalnızca test cihazlarında script çalıştırırken olayda finans endpoint’ine bağlı workstation kullanılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Hızlı destek veya debug gerekçesiyle yapılan bu tür işler büyük güvenlik riski taşır.

---

SENARYO ADI: CEO Mail Kutusundan Toplu Arşiv Export’u

KATEGORİ: veri sızdırma

KULLANICI ROLÜ: CEO

OLAY: CEO hesabı, dahili mail sisteminde tüm ekleriyle birlikte arşiv export işlemi başlatır.

NEDEN ŞÜPHELİ: Yönetim iletişiminin toplu dışa aktarımı çok yüksek hassasiyetlidir.

NORMAL BASELINE'DAN SAPMA: CEO kutusunda daha önce hiç full export yapılmamışken olayda 14 yıllık içerik paketlenmiştir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Bu tür toplu export’lar kurum içi anlaşmazlık veya kişisel arşivleme bahanesiyle yapılabilir.

---

SENARYO ADI: Çoklu Departman Zincirli Olay

KATEGORİ: dış saldırı destegi

KULLANICI ROLÜ: Güvenlik Görevlisi

OLAY: Güvenlik görevlisi sunucu odasına doğrulanmamış bakım ekibini alır; kısa süre sonra IT Admin hesabından hukuk ve finans sistemlerine erişim başlar, ardından destek personeli cihazından log temizleme denenir.

NEDEN ŞÜPHELİ: Fiziksel olay, yüksek ayrıcalıklı erişim, çapraz departman hedefleme ve delil temizleme denemesi tek zincirde birleşmektedir.

NORMAL BASELINE'DAN SAPMA: Normalde bu üç olay tipi birbirinden bağımsızdır; burada 40 dakika içinde korele şekilde gerçekleşir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Gerçek ihlaller tekil sinyallerden çok çok aşamalı zincirler halinde gelişir; simülasyonda bu korelasyon özellikle değerlidir.

---

SENARYO ADI: Stajyerin Eski Çalışan Dosyalarını Merak Etmesi

KATEGORİ: yetkisiz erişim

KULLANICI ROLÜ: Stajyer

OLAY: Stajyer, onboarding klasöründe gezinirken eski çalışanların performans ve çıkış mülakatı belgelerine girer.

NEDEN ŞÜPHELİ: Eğitim alanı dışındaki hassas personel dosyalarına merak odaklı erişim.

NORMAL BASELINE'DAN SAPMA: Stajyer erişimi yalnızca eğitim içeriğiyle sınırlıyken olayda 58 HR dosyası açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Yeni çalışanlar klasör yapısını anlamadan ve sınırları bilmeden hassas alanlara girebilir.

---

SENARYO ADI: PM’nin Geçici Slack Benzeri İç Mesaj Kayıtlarını İstemesi

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Proje Yöneticisi

OLAY: PM, sprint retro için ekiplerin dahili mesaj geçmişlerini destek ekibinden export etmesini ister.

NEDEN ŞÜPHELİ: İş amacıyla orantısız içerik talebi ve çalışan iletişim mahremiyeti riski.

NORMAL BASELINE'DAN SAPMA: PM’ler normalde yalnızca özet aksiyon notu alırken olayda ham mesaj arşivi talep edilmiştir.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Süreç iyileştirme bahanesiyle fazla gözetime kayan talepler olabilir.

---

SENARYO ADI: Destek Personelinin CFO Dosyalarını Troubleshooting Paketine Katması

KATEGORİ: kazara ihlal

KULLANICI ROLÜ: Destek Personeli

OLAY: Destek çalışanı, uygulama hatasını göstermek için ekran görüntüsü ve log toplarken CFO’nun açık finans tablolarını da pakete dahil eder.

NEDEN ŞÜPHELİ: Sorun çözüm paketine ilgisiz hassas içeriğin karışması.

NORMAL BASELINE'DAN SAPMA: Normal diagnostic paketleri sistem loglarıyla sınırlıyken olayda 14 finans dosyası da eklenmiştir.

BEKLENEN SEVERITY: WARNING

GERÇEKÇİLİK NOTU: Troubleshooting sırasında ekran ve dosya kapsama alanı çoğu zaman gereğinden fazla olur.

---

SENARYO ADI: Hukuk Çalışanının Toplu PDF OCR Klasörü Oluşturması

KATEGORİ: politika ihlali

KULLANICI ROLÜ: Hukuk

OLAY: Hukuk çalışanı, arama kolaylığı için binlerce sözleşmeyi OCR işlemi yapmak üzere geçici ortak klasöre koyar; klasör BT ekibinin de erişimine açıktır.

NEDEN ŞÜPHELİ: Hassas belgelerin işleme bahanesiyle erişim yüzeyinin genişletilmesi.

NORMAL BASELINE'DAN SAPMA: Hukuk belgeleri normalde sadece 2 kullanıcıya açıkken olay klasörü 9 kullanıcı erişimine açılmıştır.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İşleme veya indeksleme amaçlı ara klasörler çoğu zaman güvenlik açısından unutulur.

---

SENARYO ADI: Muhasebe Kullanıcısının Toplu Login Saatleri İncelemesi

KATEGORİ: insider threat

KULLANICI ROLÜ: Muhasebe

OLAY: Muhasebe çalışanı, işten çıkarma söylentileri sonrası kimlerin geç kaldığını veya gece çalıştığını anlamak için erişim loglarını toplar.

NEDEN ŞÜPHELİ: Kişisel motivasyonla çalışan davranış verisi toplama.

NORMAL BASELINE'DAN SAPMA: Muhasebe rolünün access log görüntüleme ihtiyacı yokken olayda 35 kullanıcıya ait giriş kayıtları çekilmiştir.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: İç merak ve ofis politikası, çalışanların rol dışı verilere yönelmesine neden olabilir.

---

SENARYO ADI: İç Ağda Yetkisiz Dahili Posta Kuralı Oluşturma

KATEGORİ: credential ihlali

KULLANICI ROLÜ: Satış

OLAY: Satış çalışanı hesabında, belirli müşteri anahtar kelimelerini içeren dahili mailleri otomatik olarak gizli bir klasöre taşıyan kural oluşturulur.

NEDEN ŞÜPHELİ: Kalıcı veri toplama amacı taşıyan gizli mail kuralı davranışı.

NORMAL BASELINE'DAN SAPMA: Kullanıcının daha önce 0 kuralı varken olayda 3 yeni filtre kuralı oluşur.

BEKLENEN SEVERITY: ALERT

GERÇEKÇİLİK NOTU: Mail kuralları içeriden veri toplamada sessiz ve etkili araçlardır.

---

SENARYO ADI: Çok Kaynaklı Kademeli İhlal Simülasyonu

KATEGORİ: diğer

KULLANICI ROLÜ: IT Admin

OLAY: Önce stajyer yanlışlıkla ortak credential’ı wiki’ye koyar, sonra geliştirici bunu görüp test API’sine girer, ardından IT Admin anomaliyi gizlemek için log ayarlarını değiştirir; son aşamada satış çalışanı müşteri export’u yapar.

NEDEN ŞÜPHELİ: Birden çok düşük ve orta seviye olayın birbirini tetikleyerek tam ölçekli ihlale dönüşmesi.

NORMAL BASELINE'DAN SAPMA: Tekil olarak sıradan görünebilecek olaylar, 24 saat içinde birbirine bağlı 4 farklı departman aktörüyle koreledir.

BEKLENEN SEVERITY: CRITICAL

GERÇEKÇİLİK NOTU: Gerçek şirket ihlalleri çoğu zaman tek bir büyük olay değil, küçük ihlaller zinciri şeklinde gelişir.

---

Bu doküman 100+ adet, iç ağ odaklı, rol tabanlı ve çapraz departman etkileşimli UEBA test senaryosu içerir. İstenirse bir sonraki adımda bu senaryolar severity dağılımına, MITRE ATT&CK benzeri fazlara, veri kaynaklarına veya sentetik log formatına dönüştürülebilir.
