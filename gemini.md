İç ağ (Private LAN) simülasyon ortamınız için geliştirilen, 35 kullanıcıya ve belirtilen veri tiplerine göre özelleştirilmiş 100 adet gerçekçi UEBA test senaryosu aşağıda listelenmiştir.

---

### **Stajyer ve Yeni Çalışan Senaryoları (1 - 15)**

**1.**
SENARYO ADI: Stajyer Merakı
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Stajyer
OLAY: Yazılım stajyeri, ağ taraması yaparak erişim izni olmayan İK sunucusunun IP adresine bağlanmaya çalışıyor.
NEDEN ŞÜPHELİ: Rol tanımında olmayan bir sunucu segmentine erişim denemesi.
NORMAL BASELINE'DAN SAPMA: Haftalık 0 olan İK segmenti bağlantı denemesinin 1'e çıkması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Yeni başlayan stajyerler şirketin ağ yapısını ve sınırlarını test etmek için merakla tarama yaparlar.

**2.**
SENARYO ADI: Yanlış Klasör Paylaşımı
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Stajyer
OLAY: Stajyer, kendi bilgisayarındaki projeyi bitirmek için tüm yerel diskini ağdaki "Herkes" (Everyone) grubuna okuma/yazma açık şekilde paylaşıyor.
NEDEN ŞÜPHELİ: İç ağda kontrolsüz ve geniş yetkili yeni bir SMB paylaşımı açılması.
NORMAL BASELINE'DAN SAPMA: Ağ paylaşımlarında anlık değişiklik ve riskli yetkilendirme.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Teknik bilgi eksikliği nedeniyle işi kolaylaştırmak adına yerel klasörler ağa denetimsiz açılır.

**3.**
SENARYO ADI: Ortak Alandan Kod Çekme
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Stajyer
OLAY: Stajyer, yazılım geliştiricilerin ortak kullandığı test sunucusundan kendi yerel bilgisayarına 15 GB boyutunda ham log ve kaynak kod çekiyor.
NEDEN ŞÜPHELİ: Stajyer baselined değerinin çok üzerinde veri transferi yapılması.
NORMAL BASELINE'DAN SAPMA: Günlük ortalama 200 MB olan download miktarının 15 GB'a fırlaması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Ödev veya kişisel arşiv amacıyla şirket projelerinin ham halleri yerel makineye kopyalanır.

**4.**
SENARYO ADI: Eski Stajyer Hesabı Aktivitesi
KATEGORİ: credential ihlali
KULLANICI ROLÜ: Stajyer
OLAY: Sözleşmesi 2 gün önce biten stajyerin kullanıcı hesabı ile gece 03:00'te iç ağdaki GitLab sunucusuna login olunuyor.
NEDEN ŞÜPHELİ: Aktif olmaması gereken bir hesabın mesai dışı saatte sistemde oturum açması.
NORMAL BASELINE'DAN SAPMA: Pasif hesaptan gelen anomali login işlemi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: İK ve IT arasındaki kopukluk nedeniyle hesabı kapatılmayan eski çalışanlar ağa sızabilir.

**5.**
SENARYO ADI: İlk Gün Agresifliği
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Stajyer
OLAY: İşe yeni başlayan satış stajyeri, ortak ağ sürücüsündeki (File Server) tüm departman klasörlerini (Muhasebe, Hukuk vb.) tek tek açmaya çalışıyor.
NEDEN ŞÜPHELİ: Yetki hatası (Access Denied) üreten ardışık klasör erişim denemeleri.
NORMAL BASELINE'DAN SAPMA: Dakikada 25'ten fazla "Erişim Engellendi" logu üretilmesi.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Yeni çalışanlar ağdaki erişim sınırlarını bilmediğinden her klasöre tıklayarak keşif yapar.

**6.**
SENARYO ADI: USB ile Gelen Zararlı
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Stajyer
OLAY: Stajyer, sunum dosyasını getirmek için evden getirdiği şahsi USB belleği bilgisayarına takıyor ve iç ağdaki bir klasöre veri aktarıyor.
NEDEN ŞÜPHELİ: USB aygıt takılması ve ardından ağ klasörlerine hızlı dosya yazma aktivitesi.
NORMAL BASELINE'DAN SAPMA: Cihazda daha önce hiç görülmemiş Vendor ID'ye sahip USB kullanımı.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Güvenlik bilinci düşük çalışanlar virüslü şahsi USB'lerini şirket bilgisayarlarına takarlar.

**7.**
SENARYO ADI: Stajyer Hesabıyla API Kurcalama
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Stajyer
OLAY: Destek personeli stajyeri, şirketin iç test API'sine administrative (yönetici) parametreler ekleyerek istekler gönderiyor.
NEDEN ŞÜPHELİ: Yetkisiz bir rolden hassas API uç noktalarına (endpoints) çağrı yapılması.
NORMAL BASELINE'DAN SAPMA: 0 olan admin API çağrısının bir anda yükselmesi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Yazılıma meraklı stajyerler iç sistemlerdeki zafiyetleri manuel olarak test etmek isteyebilir.

**8.**
SENARYO ADI: Sosyal Mühendislik Tuzağına Düşen Yeni Başlayan
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Destek Personeli
OLAY: Şirkete yeni giren destek personeli, iç mailden gelen "IT Şifre Yenileme" görünümlü (aslında ele geçirilmiş başka bir çalışandan gelen) linke tıklayıp kimlik bilgilerini iç ağdaki sahte bir portala giriyor.
NEDEN ŞÜPHELİ: İç ağdaki güvenilmeyen bir IP adresine hassas form verisi gönderimi.
NORMAL BASELINE'DAN SAPMA: Yeni kullanıcının anormal HTTP POST aktivitesi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Yeni çalışanlar şirket kültürünü bilmediklerinden iç maillerden gelen sahte taleplere hızla güvenirler.

**9.**
SENARYO ADI: Stajyer Bilgisayarında Torrent Kullanımı
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Stajyer
OLAY: Yazılım stajyeri, yerel ağ üzerinden diğer bilgisayarlarla yüksek hacimli P2P (Peer-to-Peer) dosya paylaşım protokolü başlatıyor.
NEDEN ŞÜPHELİ: Şirket ağında yasaklı protokol ve uygulama kullanımı.
NORMAL BASELINE'DAN SAPMA: İç ağ portlarında alışılmadık P2P trafiği.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Genç çalışanlar şirket ağının yüksek hızını kullanarak kendi aralarında veri/oyun paylaşmaya çalışabilir.

**10.**
SENARYO ADI: İK Stajyerinin Maaş Merakı
KATEGORİ: insider threat
KULLANICI ROLÜ: Stajyer
OLAY: İK departmanındaki stajyer, amirinin bilgisayarı açık bırakıp yemeğe gitmesini fırsat bilerek ortak ağdaki "2026_Maaslar.xlsx" dosyasını okuyor.
NEDEN ŞÜPHELİ: Dosyaya erişen kullanıcının baseline saatleri dışında veya normal görev tanımının dışındaki bir dosyaya odaklanması (burada amirin hesabı kullanılıyor ancak LLM davranışsal olarak bunu olağanüstü hızlı dosya arama olarak yakalayabilir; eğer kendi hesabıyla girdiyse doğrudan yetki aşımı).
NORMAL BASELINE'DAN SAPMA: İK klasöründe derinlemesine arama ve kritik excel dosyasının okunması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Stajyerler veya alt kademe personel, şirket içi gizli bilgileri (özellikle maaşları) öğrenmek için anlık boşlukları kollar.

**11.**
SENARYO ADI: Yeni Yazılımcının Hatalı Scripti
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: İşe yeni başlayan yazılımcı, yazdığı hatalı bir test scripti yüzünden iç veri tabanı sunucusuna saniyede 5000 hatalı login isteği gönderiyor.
NEDEN ŞÜPHELİ: Bruteforce (kaba kuvvet) saldırısına benzer aşırı yoğun hatalı istek trafiği.
NORMAL BASELINE'DAN SAPMA: Saniyede 1 olan bağlantı isteğinin 5000'e çıkması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Sonsuz döngüye giren veya yanlış credential içeren otomasyon scriptleri ağda DoS veya bruteforce etkisi yaratır.

**12.**
SENARYO ADI: Stajyerin Wi-Fi Ağı Kurcalaması
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Stajyer
OLAY: Stajyer, iç ağa bağlı bilgisayarına kurduğu bir network analiz aracıyla yerel ağdaki paketleri dinlemeye (sniffing) çalışıyor.
NEDEN ŞÜPHELİ: Normal bir kullanıcı makinesinden ağa promiscuous modda paket istekleri gönderilmesi.
NORMAL BASELINE'DAN SAPMA: Ağ kartı modunun değişimi ve lokal ağda sıra dışı ARP trafiği.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Siber güvenlik alanında kendini geliştirmek isteyen stajyerler şirket ağını laboratuvar gibi kullanmaya kalkışırlar.

**13.**
SENARYO ADI: Yeni Muhasebecinin Yanlış Sunucu Seçimi
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Muhasebe
OLAY: Yeni işe başlayan muhasebe personeli, fatura yüklemek isterken yanlışlıkla yazılım departmanının kaynak kod deposunun (GitLab) IP'sine SMB üzerinden bağlanmaya çalışıyor.
NEDEN ŞÜPHELİ: Muhasebe departmanından yazılım altyapısına doğru anlamsız bağlantı isteği.
NORMAL BASELINE'DAN SAPMA: Departmanlar arası baseline dışı trafik denemesi.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: IP listesini veya sunucu isimlerini karıştıran yeni personeller tamamen alakasız sistemlerin kapısını çalar.

**14.**
SENARYO ADI: Stajyer Bilgisayarından Kaynak Kod Sızdırma Denemesi
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Stajyer
OLAY: Proje kodlarına erişimi olan stajyer, yerel repository'deki tüm kodları zipleyerek iç mail üzerinden şirketteki başka bir arkadaşına "yedek" açıklamasıyla gönderiyor.
NEDEN ŞÜPHELİ: İç mail ekinde büyük boyutlu şifreli zip ve kaynak kod blokları bulunması.
NORMAL BASELINE'DAN SAPMA: Mail eki boyutunun normalin %500 üzerine çıkması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Stajyerler yazdıkları kodları gelecekte referans göstermek için şirket dışına çıkarmak adına önce iç ağda taşımayı denerler.

**15.**
SENARYO ADI: Yeni Satışçının CRM Dökümü Alması
KATEGORİ: insider threat
KULLANICI ROLÜ: Satış
OLAY: Şirketteki ilk haftasını dolduran satış personeli, iç ağdaki CRM sunucusundan tüm müşteri listesini CSV olarak bilgisayarına indiriyor.
NEDEN ŞÜPHELİ: Yeni bir kullanıcının baseline oluşmadan kitlesel veri indirme (bulk export) işlemi yapması.
NORMAL BASELINE'DAN SAPMA: Tek seferde 50.000 satırlık veri çekilmesi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Rakip şirkete geçmeyi planlayan veya yeni gelen hırslı personeller portföy çalmak için ilk günlerde agresif veri toplar.

---

### **IT Admin ve CTO Senaryoları (16 - 35)**

**16.**
SENARYO ADI: Domain Admin Hesabıyla Sıra Dışı Giriş
KATEGORİ: credential ihlali
KULLANICI ROLÜ: IT Admin
OLAY: En yetkili IT Admin hesabı ile pazar günü saat 04:00'te, normalde hiç kullanmadığı bir muhasebe bilgisayarı üzerinden Active Directory sunucusuna login olunuyor.
NEDEN ŞÜPHELİ: Olağan dışı zaman, olağan dışı kaynak makine ve yüksek yetkili hesap kombinasyonu.
NORMAL BASELINE'DAN SAPMA: Hafta içi mesai saatleri dışına çıkılması ve kaynak makine baseline sapması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar ele geçirdikleri admin hesaplarını fark edilmemek için şirketin en ücra bilgisayarlarından birinde kullanırlar.

**17.**
SENARYO ADI: Yönetici Yetkisiyle Kitlesel Log Silme
KATEGORİ: insider threat
KULLANICI ROLÜ: IT Admin
OLAY: Bir IT Admin, iç ağdaki merkezi log sunucusuna bağlanarak son 24 saate ait sistem erişim loglarını siliyor.
NEDEN ŞÜPHELİ: Log temizleme komutlarının veya servis durdurma işlemlerinin admin tarafından tetiklenmesi.
NORMAL BASELINE'DAN SAPMA: Log hacminin bir anda sıfıra düşmesi ve temizlik komutu tespiti.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Kötü niyetli insiderlar veya sistemde iz bırakmak istemeyen saldırganlar ilk olarak log mekanizmalarını sabote eder.

**18.**
SENARYO ADI: CTO Hesabından Ağ Yapılandırma Değişikliği
KATEGORİ: credential ihlali
KULLANICI ROLÜ: CTO
OLAY: CTO'nun hesabı kullanılarak iç ağdaki omurga anahtarlayıcıya (Core Switch) bağlanılıyor ve tüm trafiği bir IT Admin bilgisayarına kopyalayan (SPAN/Mirror) kuralı ekleniyor.
NEDEN ŞÜPHELİ: CTO'nun operasyonel olarak switch yapılandırması yapmaması gerekir; ayrıca trafiğin izinsiz kopyalanması şüphelidir.
NORMAL BASELINE'DAN SAPMA: CTO hesabının network cihazlarında aktif komut çalıştırması (Baseline: 0).
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Üst düzey yöneticilerin hesapları çalındığında, saldırganlar bu hesapların "sorgulanmaz" otoritesini kullanarak kalıcılık sağlar.

**19.**
SENARYO ADI: Yetki Yükseltme (Privilege Escalation)
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: IT Admin
OLAY: 3 IT Admin'den en kıdemsiz olanı, iç ağdaki Active Directory üzerinde kendi kişisel hesabını "Domain Admins" grubuna ekliyor.
NEDEN ŞÜPHELİ: Hak etmeyen veya onay mekanizmasından geçmemiş bir hesaba kritik rol atanması.
NORMAL BASELINE'DAN SAPMA: Kullanıcı yetki matrisinde anlık ve onaylanmamış kritik değişiklik.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirketten ayrılmayı düşünen veya arkasından iş çevrilen sistem yöneticileri kendilerine gizli arka kapı yetkileri tanımlar.

**20.**
SENARYO ADI: Admin Bilgisayarından Agresif Port Taraması
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: IT Admin
OLAY: Bir IT Admin'in bilgisayarından, şirketin tüm iç subnetlerine (35 kişinin bağlı olduğu tüm bloklara) yönelik 22, 80, 443 ve 445 portlarını kapsayan agresif tarama başlatılıyor.
NEDEN ŞÜPHELİ: Normal bakım saatleri dışında ve habersiz yapılan kitlesel tarama faaliyeti.
NORMAL BASELINE'DAN SAPMA: Dakikadaki bağlantı isteği sayısının normal admin baseline'ını %2000 aşması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Ele geçirilen bir admin makinesi, saldırganlar tarafından iç ağda yanal ilerleme (lateral movement) öncesi haritalama için kullanılır.

**21.**
SENARYO ADI: Yedekleme Sunucusundan Olağan Dışı Veri Çekme
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: IT Admin
OLAY: IT Admin, şirketin ana yedekleme sunucusundan (Backup Server) pazar günü kendi bilgisayarına 120 GB veri çekiyor ve ardından yerel makinesine bir USB disk bağlıyor.
NEDEN ŞÜPHELİ: Büyük hacimli yedek verisinin production ortamı dışındaki son kullanıcı makinesine indirilmesi.
NORMAL BASELINE'DAN SAPMA: Çekilen veri miktarında 120 GB'lık anomaliler ve USB aktivitesi senkronizasyonu.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Veri sızdırmanın en kolay yolu, tüm verilerin zaten sıkıştırılmış halde bulunduğu yedekleri çalmaktır.

**22.**
SENARYO ADI: CTO'nun Gece Yarısı Veri Tabanı Sorgusu
KATEGORİ: politika ihlali
KULLANICI ROLÜ: CTO
OLAY: CTO, cuma gecesi saat 02:00'de iç ağdan üretim (production) veri tabanına doğrudan bağlanarak müşteri tablolarını "SELECT *" komutu ile sorguluyor.
NEDEN ŞÜPHELİ: Yönetici rolünün doğrudan DB sorgulaması yapması ve zamanlamanın uygunsuzluğu.
NORMAL BASELINE'DAN SAPMA: CTO'nun veri tabanına doğrudan erişim sıklığı sıfırken aniden kritik tablolara erişmesi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Şirket kurucuları veya CTO'lar acil bir analiz için bazen doğrudan veri tabanına girer ancak bu durum hesap güvenliği açısından büyük bir risktir.

**23.**
SENARYO ADI: Hizmet Hesabının (Service Account) Kötüye Kullanımı
KATEGORİ: credential ihlali
KULLANICI ROLÜ: IT Admin
OLAY: Sadece uygulamaların birbiriyle konuşması için ayrılmış yüksek yetkili bir SQL servis hesabı kullanılarak bir IT Admin'in masaüstü bilgisayarından SQL sunucusuna interaktif oturum açılıyor.
NEDEN ŞÜPHELİ: Non-interactive (etkileşimsiz) olması gereken bir hesabın insan tarafından manuel kullanılması.
NORMAL BASELINE'DAN SAPMA: Servis hesabının kaynak IP baseline'ının değişmesi ve interaktif shell açması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar veya tembel adminler, kişisel hesapları yerine şifresini bildikleri ve izlenmediğini düşündükleri servis hesaplarını kullanırlar.

**24.**
SENARYO ADI: Geçici Erişim Süresinin Aşılması
KATEGORİ: politika ihlali
KULLANICI ROLÜ: IT Admin
OLAY: IT Admin, bir dış danışmanın işi için açtığı geçici iç ağ erişim hesabını, iş bitmesine rağmen 2 hafta boyunca kapatmıyor ve hesap üzerinden ağda veri akışı devam ediyor.
NEDEN ŞÜPHELİ: Kapatılma tarihi geçmiş bir hesabın iç ağda aktif olması.
NORMAL BASELINE'DAN SAPMA: Politika dışı aktif hesap anomalisi.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Unutulan geçici hesaplar, saldırganların iç ağa sızdıktan sonra kullanmayı en çok sevdiği kalıcılık yöntemlerindendir.

**25.**
SENARYO ADI: IT Admin'in Şahsi Cihazını Ağa Bağlaması
KATEGORİ: politika ihlali
KULLANICI ROLÜ: IT Admin
OLAY: IT Admin, evden getirdiği kişisel dizüstü bilgisayarını ethernet kablosuyla şirketin iç LAN ağına dahil ediyor.
NEDEN ŞÜPHELİ: Şirket envanterinde (Asset Management) kayıtlı olmayan bir MAC adresinin iç ağdan IP alıp Active Directory'yi sorgulaması.
NORMAL BASELINE'DAN SAPMA: Bilinmeyen cihaz anomalisi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: IT personeli kendi cihazlarındaki araçları kullanmak için ağ güvenlik kurallarını (NAC) arkadan dolanarak delebilir.

**26.**
SENARYO ADI: Güvenlik Duvarı Kurallarının Esnetilmesi
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: IT Admin
OLAY: Bir IT Admin, iç ağdaki kritik finans sunucusuna kendi bilgisayarından her porttan erişebilmek için yerel firewall üzerinde "Any-Any" izni veren bir kural tanımlıyor.
NEDEN ŞÜPHELİ: Sıkı korunan bir segmente yönelik kuralların güvensiz şekilde genişletilmesi.
NORMAL BASELINE'DAN SAPMA: Güvenlik politikasında baseline dışı gevşeme.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Adminler işlerini kolaylaştırmak veya bir sorunu hızlıca çözmek için kalıcı güvenlik zafiyetleri yaratacak kurallar açarlar.

**27.**
SENARYO ADI: CTO Odasından Gelen Görevli Olmayan Girişler
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: IT Admin
OLAY: CTO odasındaki boş duran ethernet portundan, bir IT Admin hesabı kullanılarak şirketin ana Switch yönetici arayüzüne brute force denemeleri yapılıyor.
NEDEN ŞÜPHELİ: Fiziksel lokasyon ile hesap sahibinin normal çalışma alanı uyuşmuyor.
NORMAL BASELINE'DAN SAPMA: Lokasyon bazlı erişim anomali skoru artışı.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar üst düzey yöneticilerin odalarındaki fiziksel ağ portlarının daha az denetlendiğini varsayarak buralara sızar.

**28.**
SENARYO ADI: Admin Hesaplarının Çapraz Kullanımı
KATEGORİ: credential ihlali
KULLANICI ROLÜ: IT Admin
OLAY: 1. IT Admin, o gün izinli olan 2. IT Admin'in bilgisayarına uzaktan (RDP) bağlanıp onun yerel kimlik bilgileriyle ağda işlemler gerçekleştiriyor.
NEDEN ŞÜPHELİ: İzinli olan personelin hesabının şirket içinden aktifleşmesi.
NORMAL BASELINE'DAN SAPMA: Personel devam takip sistemi (PDKS) verisiyle kullanıcı login durumunun çelişmesi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: İş arkadaşları işler yetişsin diye şifrelerini birbirine verebilir, bu durum hesap izlenebilirliğini yok eder.

**29.**
SENARYO ADI: CTO'nun Kritik API'yi Devre Dışı Bırakması
KATEGORİ: politika ihlali
KULLANICI ROLÜ: CTO
OLAY: CTO, iç ağdaki test sürecini hızlandırmak için güvenlik doğrulama adımlarını yürüten mikro servis API'sinin anahtarlarını geçici olarak boşa çıkarıyor.
NEDEN ŞÜPHELİ: Kritik bir güvenlik API'sine yönelik sıra dışı konfigürasyon değişikliği çağrısı.
NORMAL BASELINE'DAN SAPMA: API çağrı kalıplarında yapısal değişiklik.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Yöneticiler bazen canlıya çıkış baskısı altındayken güvenlik kontrollerini bypass edecek kararlar alabilirler.

**30.**
SENARYO ADI: Domain Controller Üzerinde Olağan Dışı PowerShell Çalıştırılması
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: IT Admin
OLAY: IT Admin hesabı ile Active Directory sunucusu üzerinde tüm kullanıcı şifre özetlerini (hashes) hafızadan çeken karmaşık bir PowerShell scripti çalıştırılıyor.
NEDEN ŞÜPHELİ: Normal yönetim aktivitelerinde kullanılmayan, şifre dökümü (credential dumping) odaklı script tespiti.
NORMAL BASELINE'DAN SAPMA: PowerShell komut geçmişinde baseline dışı argümanlar.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar iç ağda tam hakimiyet kurmak için Domain Controller üzerinde Mimikatz benzeri scriptler koştururlar.

**31.**
SENARYO ADI: Admin Bilgisayarında Kayıt Defteri Kurcalama
KATEGORİ: politika ihlali
KULLANICI ROLÜ: IT Admin
OLAY: IT Admin, kendi yerel bilgisayarında Windows yetkilendirme mekanizmalarını (LSA) zayıflatacak kayıt defteri (Registry) değişiklikleri yapıyor.
NEDEN ŞÜPHELİ: Güvenlik sıkılaştırma kurallarına aykırı lokal sistem manipülasyonu.
NORMAL BASELINE'DAN SAPMA: Sistem konfigürasyon baseline'ından sapma.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Bazı adminler eski araçları çalıştırabilmek için kendi bilgisayarlarındaki yerel güvenlik mekanizmalarını kapatırlar.

**32.**
SENARYO ADI: Süresi Dolan Şifrelerin Toplu Uzatılması
KATEGORİ: politika ihlali
KULLANICI ROLÜ: IT Admin
OLAY: IT Admin, şirketin şifre politikası gereği süresi dolan 10 kritik personelin şifre değişim zorunluluğunu script ile 180 gün daha erteliyor.
NEDEN ŞÜPHELİ: Kurumsal şifre rotasyon politikasının toplu olarak delinmesi.
NORMAL BASELINE'DAN SAPMA: Şifre geçerlilik sürelerinde toplu sapma manipülasyonu.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Kullanıcılardan gelen şifre değiştirme şikayetlerinden bıkan adminler kuralları esnetme eğilimindedir.

**33.**
SENARYO ADI: DNS Sunucu Ayarlarının Değiştirilmesi
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: IT Admin
OLAY: İç ağdaki yerel DNS sunucusunun ayarlarında değişiklik yapılarak, şirket içi maillerin döndüğü mail sunucusunun IP adresi sahte bir lokal IP'ye yönlendiriliyor.
NEDEN ŞÜPHELİ: Kritik ağ altyapısında yetkisiz veya gerekçesiz DNS yönlendirmesi.
NORMAL BASELINE'DAN SAPMA: DNS kayıtlarında ani değişiklik (Baseline: Sabit).
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar iç ağdaki trafiği kendi sahte sunucularına çekmek (Man-in-the-Middle) için DNS zehirlemesi veya manipülasyonu yapar.

**34.**
SENARYO ADI: Admin Tarafından Eski Yedeklerin Silinmesi
KATEGORİ: insider threat
KULLANICI ROLÜ: IT Admin
OLAY: İşten çıkarılacağını öğrenen bir IT Admin, şirketin son 6 aylık offline teyp (tape) veya ağ tabanlı arşiv yedeklerini kalıcı olarak sistemden temizliyor.
NEDEN ŞÜPHELİ: Normal rotasyon dışı, kitlesel ve geri döndürülemez yedek silme aktivitesi.
NORMAL BASELINE'DAN SAPMA: Günlük silme limitlerinin %1000 üzerine çıkılması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: İntikam almak isteyen insiderlar şirkete en büyük zararı yedekleri yok ederek verebileceklerini bilirler.

**35.**
SENARYO ADI: CTO Bilgisayarından SSH Anahtarı Hasadı
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: CTO
OLAY: CTO'nun yerel bilgisayarındaki tüm sunucu SSH private key dosyaları (.pem, .id_rsa) taranıyor ve iç ağdaki bir geliştirici bilgisayarına kopyalanıyor.
NEDEN ŞÜPHELİ: Kritik kimlik doğrulama dosyalarının ağ içinde yer değiştirmesi.
NORMAL BASELINE'DAN SAPMA: Anahtar dosyalarına erişim sıklığında anomaliler.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar ağa girdikten sonra yöneticilerin bilgisayarlarındaki korumasız SSH anahtarlarını toplayarak diğer sunuculara parolasız geçerler.

---

### **Yazılım Geliştirici Senaryoları (36 - 55)**

**36.**
SENARYO ADI: Kaynak Kod Deposunun Klonlanması
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Bir yazılımcı, normalde sadece üzerinde çalıştığı tek bir projeye erişmesi gerekirken, GitLab üzerindeki tüm şirkete ait 40 farklı kod deposunu (repositories) ardışık olarak bilgisayarına klonluyor.
NEDEN ŞÜPHELİ: Rolün normal proje odağını aşan, kitlesel kod indirme davranışı.
NORMAL BASELINE'DAN SAPMA: Haftalık ortalama 1 depo indirmeden tek günde 40 depoya çıkış.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirketten ayrılmayı düşünen yazılımcılar, şirketin tüm fikri mülkiyetini (IP) yanlarında götürmek için kod depolarını topluca indirir.

**37.**
SENARYO ADI: Üretim (Production) DB'sine Doğrudan SQL Injection Testi
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, kendi lokalinde denemesi gereken güvenlik zafiyet tarama aracını yanlışlıkla iç ağdaki canlı müşteri veri tabanına doğru çalıştırıyor.
NEDEN ŞÜPHELİ: Geliştirici IP'sinden canlı veri tabanına yönelik binlerce anomali içeren SQL sorgu hatası gelmesi.
NORMAL BASELINE'DAN SAPMA: Veri tabanı hata loglarında anlık patlama.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Dikkatsiz yazılımcılar test ortamı ile canlı ortam bağlantı dizelerini (connection strings) karıştırarak canlı sistemleri riske atarlar.

**38.**
SENARYO ADI: Sabit Şifrelerin (Hardcoded Credentials) Koda Eklenmesi
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, iç ağdaki test sunucusunun root şifresini ve API anahtarını açık metin (plain text) olarak kodun içine yazıyor ve bunu iç Git sunucusuna push ediyor.
NEDEN ŞÜPHELİ: LLM destekli UEBA'nın kod commit içeriğinde veya dosya transferinde açık şifre örüntüleri (regex/entropy) yakalaması.
NORMAL BASELINE'DAN SAPMA: Güvenli kod yazım baseline'ından sapma.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Geliştiriciler pratik olmak adına şifreleri vault sistemlerinde saklamak yerine kodun içine gömerler, bu da iç ağdaki herkesin bu şifreleri görmesine yol açar.

**39.**
SENARYO ADI: Canlı Ortam Verisinin Lokal Makineye Çekilmesi
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, bir hatayı (bug) çözmek gerekçesiyle canlı veri tabanından 8 GB boyutundaki gerçek kullanıcı ve kredi kartı maskelenmemiş verisini kendi yerel bilgisayarına indiriyor.
NEDEN ŞÜPHELİ: KVKK/GDPR uyumsuz veri transferi ve geliştirici makinesine yüksek hacimli veri akışı.
NORMAL BASELINE'DAN SAPMA: Günlük veri çekme limitinin %800 aşılması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Yazılımcılar gerçek verilerle çalışmanın testi kolaylaştırdığını düşünerek müşteri gizliliğini ihlal ederler.

**40.**
SENARYO ADI: Geliştirici Makinesinde İzinsiz API Sunucusu Başlatılması
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, kendi yerel bilgisayarında iç ağdaki diğer bilgisayarların erişebileceği, şirket politikalarına aykırı yetkisiz bir proxy veya gölge API (Shadow IT) servisi çalıştırıyor.
NEDEN ŞÜPHELİ: Kullanıcı bilgisayarında alışılmadık portların (örn: 8080, 8888) iç ağa hizmet verecek şekilde dinlemeye geçmesi.
NORMAL BASELINE'DAN SAPMA: Ağ dinleme profilinde değişiklik.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Geliştiriciler kendi aralarında veri paylaşmak veya araçları test etmek için bilgi işlemden habersiz yerel servisler ayağa kaldırırlar.

**41.**
SENARYO ADI: Çapraz Departman API Yetki Testi
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, muhasebe departmanının kullandığı iç finans API'sine, parametre manipülasyonu (IDOR) yaparak diğer çalışanların maaş bilgilerini getirecek istekler gönderiyor.
NEDEN ŞÜPHELİ: Geliştirici hesabından finans API uç noktalarına mantıksal sınırları zorlayan ardışık istekler atılması.
NORMAL BASELINE'DAN SAPMA: API yanıt kodlarında 403/401 oranının artması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Yazılımcılar API tasarımlarındaki açıkları bildikleri için şirket içindeki diğer sistemlerin sınırlarını test etmek isteyebilirler.

**42.**
SENARYO ADI: Geliştirici Bilgisayarından Gece Yarısı Git Aktivitesi
KATEGORİ: insider threat
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Bir yazılımcı, istifa etmeden önceki gece saat 03:30'da iç ağdaki Git sunucusuna bağlanarak kritik ana modüllerin kaynak kodlarını tek tek bilgisayarına indiriyor.
NEDEN ŞÜPHELİ: Alışılmadık çalışma saatinde yüksek hacimli fikri mülkiyet erişimi.
NORMAL BASELINE'DAN SAPMA: Zaman ve veri tipi bazlı baseline sapması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Ayrılacak olan teknik personel, geliştirdikleri algoritmaları yeni işlerinde kullanmak üzere son günlerde gece operasyonlarıyla çalarlar.

**43.**
SENARYO ADI: Onaylanmamış Açık Kaynak Kütüphane Kullanımı
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Geliştirici, projeye hız kazandırmak için iç ağdaki paket sunucusuna (Nexus/Artifactory) bilinen ciddi zafiyetleri (örn: Log4j benzeri) olan eski bir kütüphaneyi indirip entegre ediyor.
NEDEN ŞÜPHELİ: İç paket deposuna güvenlik onayından geçmemiş, riskli bağımlılıkların eklenmesi.
NORMAL BASELINE'DAN SAPMA: Paket yönetim sisteminde anomali tespiti.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Yazılımcılar teslim tarihlerine yetişmek için kütüphanelerin güvenlik açıklarını kontrol etmeden kodlarına dahil ederler.

**44.**
SENARYO ADI: Geliştirici Bilgisayarına USB ile Kod Kopyalama
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Geliştirici, gün boyu üzerinde çalıştığı yeni yapay zeka modelinin ağırlık dosyalarını (weights) ve kaynak kodlarını bilgisayarına taktığı şifresiz harici diskine kopyalıyor.
NEDEN ŞÜPHELİ: DLP kuralları ve UEBA baseline'ına göre geliştiricinin USB kullanım sıklığının sıfıra yakın olması ve veri boyutu.
NORMAL BASELINE'DAN SAPMA: USB dosya transfer hacminde patlama.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Bulut depolama yasak olunca yazılımcılar kod çalmak için fiziksel depolama birimlerine yönelirler.

**45.**
SENARYO ADI: Paylaşılan Geliştirici Kimlik Bilgileri
KATEGORİ: credential ihlali
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Bir yazılımcının AWS iç erişim anahtarı (Access Key), aynı anda hem kendi bilgisayarından hem de yan masadaki diğer yazılımcının bilgisayarından iç ağ üzerinden API çağrısı yapmak için kullanılıyor.
NEDEN ŞÜPHELİ: Aynı kimlik bilgisinin (credential) farklı benzersiz MAC/IP adreslerinden eş zamanlı kullanımı (Concurrency Anomaly).
NORMAL BASELINE'DAN SAPMA: Benzersiz cihaz/hesap eşleşme baseline'ının bozulması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Takım arkadaşları yetki al süreçleriyle uğraşmamak için kendi aralarında API tokenlarını ve şifrelerini paylaşırlar.

**46.**
SENARYO ADI: Jenkins Sunucusunda Yetkisiz Komut Çalıştırma
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Kıdemsiz yazılımcı, iç ağdaki Jenkins CI/CD sunucusunun arayüzündeki bir açıktan faydalanarak sunucu üzerinde işletim sistemi komutları (reverse shell) çalıştırıyor.
NEDEN ŞÜPHELİ: Jenkins servisinin normal derleme (build) süreçleri dışında şüpheli alt süreçler (child processes) başlatması.
NORMAL BASELINE'DAN SAPMA: Uygulama davranışsal baseline sapması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Yazılımcılar sistem yetkilerini aşmak için kendi kullandıkları otomasyon araçlarının zafiyetlerini suistimal edebilirler.

**47.**
SENARYO ADI: İç Mail Üzerinden Şifreli Dosya Alışverişi
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: İki yazılımcı, iç ağdaki mail sunucusunu kullanarak birbirlerine içeriği incelenemeyen, güçlü şifrelemeye sahip .7z uzantılı dosyalar gönderiyor.
NEDEN ŞÜPHELİ: Kurumsal mail politikasına aykırı, denetlenemeyen şifreli arşiv transferi.
NORMAL BASELINE'DAN SAPMA: Mail ekleri tiplerinde anomali.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Güvenlik filtrelerine takılmak istemeyen personeller şirket içinde veri taşırken şifreli arşivler kullanırlar.

**48.**
SENARYO ADI: Geliştirici Bilgisayarından SSH Kaba Kuvvet Saldırısı
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Bir yazılımcının bilgisayarı, siber saldırganlar tarafından ele geçiriliyor ve bu bilgisayar üzerinden iç ağdaki ana veri tabanına dakikada 300 SSH login denemesi yapılıyor.
NEDEN ŞÜPHELİ: Yazılımcı bilgisayarından iç ağ sunucularına yönelik başarısız ve yoğun bağlantı serisi.
NORMAL BASELINE'DAN SAPMA: Başarısız SSH bağlantı baseline'ının radikal artışı.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar ağa sızdıktan sonra bir yazılımcı makinesini "zombi" olarak kullanarak iç ağda brute-force başlatırlar.

**49.**
SENARYO ADI: Veri Analisti Klasörüne Sızma
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, veri analistlerinin üzerinde çalıştığı ham pazar araştırma sonuçlarının ve kullanıcı analitiklerinin bulunduğu ağ sürücüsüne sızıp dosyaları kopyalıyor.
NEDEN ŞÜPHELİ: Rol dışı ağ klasörü erişimi ve yüksek hacimli okuma faaliyeti.
NORMAL BASELINE'DAN SAPMA: Dosya sunucusu erişim matrisi dışına çıkılması.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Yazılımcılar işleri olmamasına rağmen veri analistlerinin topladığı temizlenmiş verileri ticari merakla çekebilirler.

**50.**
SENARYO ADI: Test Ortamından Canlı Ağ Değişkenlerini Toplama
KATEGORİ: diğer
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, test ortamındaki bir uygulamaya gömdüğü kod parçasıyla, canlı ağdaki sunucuların IP listesini ve açık portlarını taratıp bir text dosyasına yazdırıyor.
NEDEN ŞÜPHELİ: Uygulama loglarında ağ keşif (discovery) faaliyetlerine dair şüpheli desenler.
NORMAL BASELINE'DAN SAPMA: Uygulamanın normal çevre birimi iletişim baseline'ından sapması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Akıllı insiderlar iz bırakmamak için tarama işlemlerini kendi bilgisayarlarından değil, yönettikleri test sunucuları üzerinden yaparlar.

**51.**
SENARYO ADI: Eski API Versiyonunun İstismarı
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, şirketin yayından kaldırmayı unuttuğu eski ve güvensiz bir iç API versiyonunu (v1) kullanarak normalde görmemesi gereken finansal logları çekiyor.
NEDEN ŞÜPHELİ: Uzun süredir kullanılmayan pasif bir API ucuna aniden yoğun istek gelmesi.
NORMAL BASELINE'DAN SAPMA: Eski API trafik baseline'ında ani sıçrama.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Sistemleri iyi bilen eski yazılımcılar, unutulmuş legacy (eski) servisleri arka kapı olarak kullanırlar.

**52.**
SENARYO ADI: Kodun İçine Mantık Bombası (Logic Bomb) Yerleştirme
KATEGORİ: insider threat
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Şirketle sorun yaşayan yazılımcı, iç Git sunucusundaki koda "Eğer X kullanıcısı silinirse veri tabanını sıfırla" şeklinde gizli bir mantıksal koşul ekleyip commit ediyor.
NEDEN ŞÜPHELİ: UEBA'nın LLM motorunun, kod commit incelemesinde potansiyel olarak yıkıcı/tehlikeli kod blokları tespit etmesi.
NORMAL BASELINE'DAN SAPMA: Kod içeriğinde anomali skoru artışı.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Kovulacağını anlayan yazılımcılar, şirkete ileride zarar vermek için kod tabanına zamana veya koşula bağlı sabote edici kodlar bırakırlar.

**53.**
SENARYO ADI: Docker İmajı İçinde Gizli Madencilik (Cryptojacking)
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, şirketin iç ağdaki geliştirme sunucularında çalıştırdığı Docker imajlarının içine gizlice kripto para madenciliği scripti ekliyor.
NEDEN ŞÜPHELİ: Test sunucularında CPU kullanımının 7/24 %100'e vurması ve iç ağ üzerinden tanınmayan havuz (pool) IP'lerine bağlantı kurulmaya çalışılması.
NORMAL BASELINE'DAN SAPMA: Sunucu kaynak tüketim ve network bağlantı baseline sapması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Şirket kaynaklarını bedava bilgi işlem gücü olarak gören personeller, gizlice mining yazılımları koşturarak elektrik ve donanım tüketirler.

**54.**
SENARYO ADI: Sürekli Başarısız Derleme (Build) Döngüsüyle Ağ Boğma
KATEGORİ: diğer
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, Jenkins sunucusuna her 3 dakikada bir kasıtlı olarak devasa bağımlılıkları olan hatalı kodlar göndererek iç ağdaki paket sunucusunun kilitlenmesine yol açıyor.
NEDEN ŞÜPHELİ: Olağan dışı sıklıkta ve büyüklükte başarısız CI/CD tetiklemeleri.
NORMAL BASELINE'DAN SAPMA: Ağdaki otomasyon trafiğinin baseline'ı felç edecek şekilde şişmesi.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Şirkete kızgın olan teknik elemanlar, doğrudan hackleme yerine süreçleri sabote ederek işleyişi yavaşlatmayı denerler.

**55.**
SENARYO ADI: Geliştiricinin İK Maillerini Sızdırması
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Yazılım Geliştirici
OLAY: Yazılımcı, iç mail sunucusundaki (Exchange/IMAP) bir konfigürasyon açığından yararlanarak İK departmanının kendi arasındaki iç yazışmalarını dinlemeye alıyor.
NEDEN ŞÜPHELİ: Yazılımcı hesabının mail sunucusu üzerinde yetkisiz sorgular veya protokol manipülasyonları yapması.
NORMAL BASELINE'DAN SAPMA: Mail sunucusu loglarında sorgu tipi anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirkette kimlerin işten çıkarılacağını veya zam oranlarını öğrenmek isteyen teknik personel mail sunucularını hedef alır.

---

### **Muhasebe ve Finans (CFO) Senaryoları (56 - 70)**

**56.**
SENARYO ADI: CFO Bilgisayarından Toplu Fatura İndirme
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: CFO
OLAY: CFO'nun bilgisayarından cumartesi akşamı iç ağdaki mali arşive bağlanılıyor ve son 3 yıla ait tüm fatura ve vergi beyannameleri tek bir şifreli klasörde toplanarak USB'ye aktarılıyor.
NEDEN ŞÜPHELİ: CFO rolde de olsa hafta sonu bu hacimde ticari sır niteliğinde verinin lokalde arşivlenip dış ortama aktarılması şüphelidir.
NORMAL BASELINE'DAN SAPMA: Zaman ve veri hacmi baseline sapması (0 MB'tan 30 GB'a).
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Üst düzey finans yöneticileri, şirket içi yolsuzlukları ifşa etmek veya rakip firmaya koz olarak sunmak için finansal geçmişi kopyalayabilirler.

**57.**
SENARYO ADI: Muhasebecinin Yetkisiz Sunucu İletişimi
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Muhasebe
OLAY: Bir muhasebe personeli, şirketin kaynak kodlarının bulunduğu GitLab sunucusunun web arayüzüne giriş yapmayı deniyor.
NEDEN ŞÜPHELİ: Muhasebe departmanının teknik kaynak kod depolarıyla hiçbir iş ilişkisinin olmaması.
NORMAL BASELINE'DAN SAPMA: Departman bazlı erişim matrisinin ihlal edilmesi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Saldırganlar ele geçirdikleri muhasebe bilgisayarı üzerinden iç ağda yanal ilerleme yaparken önlerine çıkan her IP'ye sızmaya çalışırlar.

**58.**
SENARYO ADI: Gece Yarısı Muhasebe Girişi ve Veri Çekme
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe çalışanı, gece saat 23:30'da şirkete uzaktan VPN ile bağlanıp (veya iç ağdaki masasından) ERP sistemine giriyor ve şirket banka hesap dökümlerini CSV olarak indiriyor.
NEDEN ŞÜPHELİ: Muhasebe rolü için tamamen mesai saatleri dışı bir aktivite ve kritik veri dışa aktarımı.
NORMAL BASELINE'DAN SAPMA: Zaman baseline'ından tam sapma.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Finansal manipülasyon veya hırsızlık yapacak olan insiderlar, ofiste kimsenin olmadığı veya yöneticilerin uyuduğu saatleri tercih ederler.

**59.**
SENARYO ADI: Muhasebe Mailinden Sahte IBAN Gönderimi
KATEGORİ: insider threat
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe personeli, satın alma departmanına iç mail yoluyla "Tedarikçi X firmasının IBAN numarası güncellenmiştir" içerikli sahte bir resmi yazı gönderiyor.
NEDEN ŞÜPHELİ: LLM'in iç mail içeriğini analiz ettiğinde, belirtilen IBAN'ın şirket şüpheli hesap listesinde olması veya dildeki olağan dışı değişiklikleri yakalaması.
NORMAL BASELINE'DAN SAPMA: Mail içerik analiz anomali skoru artışı.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: İçeriden yapılan dolandırıcılıklarda muhasebe çalışanları tedarikçi hesaplarını kendi hesaplarıyla değiştirerek şirketi zarara uğratırlar.

**60.**
SENARYO ADI: CFO'nun Yetki Devri Hatası
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: CFO
OLAY: CFO, tatile çıkacağı için şirket içi haris harcama onay yetkisini ve ERP şifresini içeren metni iç maille düz yazı olarak asistanına ve muhasebe grubuna gönderiyor.
NEDEN ŞÜPHELİ: Hassas kurumsal kimlik ve onay bilgilerinin iç ağda şifresiz ve güvensiz yayılması.
NORMAL BASELINE'DAN SAPMA: Güvenlik politikası baseline ihlali.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Yöneticiler operasyonun aksamaması için acil durumlarda şifrelerini alt çalışanlarla paylaşarak büyük zafiyet yaratırlar.

**61.**
SENARYO ADI: Muhasebe Bilgisayarında Bankacılık Truva Atı (Banker Trojan)
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe çalışanının bilgisayarı, iç ağ üzerinden her 10 saniyede bir finans sunucusuna gizli API çağrıları yaparak veri sızdırmaya çalışıyor.
NEDEN ŞÜPHELİ: İnsan hızının çok üzerinde, periyodik ve otomatik hale getirilmiş (beaconing) API istekleri.
NORMAL BASELINE'DAN SAPMA: İstek sıklığı baseline'ında makineleşme tespiti.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Zararlı yazılımlar arka planda sürekli çalışarak sistemden düzenli veri toplar ve bunu ağ içindeki sızdırma noktalarına iletir.

**62.**
SENARYO ADI: Muhasebe Odasındaki Boş Porttan Sızma
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe departmanındaki boş bir masaüstü ağ portuna, bilinmeyen bir cihaz takılıyor ve doğrudan şirketin finansal veri tabanı sunucusuna kaba kuvvet (brute force) saldırısı başlıyor.
NEDEN ŞÜPHELİ: Tanımlanmamış MAC adresinden kritik bir sunucuya yönelik yoğun başarısız istekler.
NORMAL BASELINE'DAN SAPMA: Ağ topolojisinde yeni cihaz anomali uyarısı.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Ziyaretçi kılığındaki saldırganlar, fiziksel olarak en az korunan muhasebe veya misafir odalarındaki portlara mini bilgisayarlar (Raspberry Pi) takarak ağa sızarlar.

**63.**
SENARYO ADI: CFO Hesabıyla Maaş Listesi Değişikliği
KATEGORİ: credential ihlali
KULLANICI ROLÜ: CFO
OLAY: Ele geçirilen CFO hesabı ile iç ağdaki ERP sistemi üzerinde pazar günü sisteme girilerek bazı personellerin maaş katsayıları ve prim oranları değiştiriliyor.
NEDEN ŞÜPHELİ: CFO'nun pazar günü operasyonel veri girişi yapması baseline'ına tamamen aykırıdır.
NORMAL BASELINE'DAN SAPMA: Hafta sonu ERP veri manipülasyonu anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Finansal kazanç sağlamak isteyen siber suçlular üst düzey finans yetkililerinin hesaplarını manipülasyon için kullanırlar.

**64.**
SENARYO ADI: Muhasebe Personelinin Toplu USB Kullanımı
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebeci, denetim firmasına vermek gerekçesiyle şirketin son mali yılına ait tüm mizan ve bilanço kayıtlarını şifresiz bir USB belleğe yüklüyor.
NEDEN ŞÜPHELİ: Şirket politikasına göre hassas finansal verilerin şifresiz harici medyaya aktarılmasının yasak olması.
NORMAL BASELINE'DAN SAPMA: Veri sınıflandırma etiketli dosyaların USB'ye yazılması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Denetim veya resmi kurum süreçlerinde çalışanlar, pratiklik adına güvenlik prosedürlerini çiğneyerek verileri USB ile taşırlar.

**65.**
SENARYO ADI: Muhasebe Maillerinde Phishing Belirtileri
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe şefinin bilgisayarından, şirket içindeki diğer 34 kişiye "Acil Ödeme Onayı - Ekli Belgeyi İnceleyin" konulu ve makro içeren excel ekli iç mailler atılıyor.
NEDEN ŞÜPHELİ: Muhasebeden tüm şirkete durduk yere makrolu dosya içeren toplu mail gönderimi.
NORMAL BASELINE'DAN SAPMA: İç mail gönderim hacmi ve ek türü anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Ele geçirilen muhasebe hesapları, şirket içinde yüksek güvene sahip olduklarından siber saldırganlar tarafından iç oltalama (internal phishing) için biçilmiş kaftandır.

**66.**
SENARYO ADI: CFO Bilgisayarında Kayıp Süreçler
KATEGORİ: diğer
KULLANICI ROLÜ: CFO
OLAY: CFO'nun bilgisayarında arka planda çalışan ve normal ofis programları (Word, Excel) dışında ağda sürekli tarama yapan izinsiz bir komut satırı (cmd.exe) süreci tespit ediliyor.
NEDEN ŞÜPHELİ: Yönetici profilindeki bilgisayarda teknik/yönetimsel süreçlerin çalışması.
NORMAL BASELINE'DAN SAPMA: İşletim sistemi süreç baseline sapması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Gelişmiş kalıcı tehditler (APT), yöneticilerin bilgisayarlarına sızdıktan sonra arka planda sessizce ağ keşif araçları çalıştırır.

**67.**
SENARYO ADI: Mizan Verisinin İç Ağda Yayılması
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe memuru, yanlışlıkla tüm şirketin karlılık ve borç durumunu içeren mizan dosyasını iç mail grubunda "Herkes" listesine gönderiyor.
NEDEN ŞÜPHELİ: LLM'in mail ekini ve alıcı listesini tarayarak gizlilik derecesi yüksek verinin yetkisiz geniş bir kitleye gönderildiğini anlaması.
NORMAL BASELINE'DAN SAPMA: Veri yayılım rotası anomali skoru.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Mail programlarındaki otomatik tamamlama kurbanı olan çalışanlar, gizli belgeleri yanlışlıkla genel listelere mail atarlar.

**68.**
SENARYO ADI: Muhasebe Departmanında Çoklu Başarısız Oturum Açma
KATEGORİ: credential ihlali
KULLANICI ROLÜ: Muhasebe
OLAY: Bir muhasebe çalışanının bilgisayarından, yan masadaki diğer muhasebecinin ERP hesabına yönelik ardışık 15 kez hatalı şifre denemesi yapılıyor.
NEDEN ŞÜPHELİ: Aynı departman içinde yatayda şifre tahmin/çalma faaliyeti.
NORMAL BASELINE'DAN SAPMA: Başarısız login baseline'ının ani yükselişi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: İş arkadaşının ne kadar maaş aldığını veya hangi işlemleri yaptığını merak eden personeller şifre tahmin etmeye çalışırlar.

**69.**
SENARYO ADI: ERP API'sine Aşırı Yüklenme
KATEGORİ: diğer
KULLANICI ROLÜ: Muhasebe
OLAY: Muhasebe bilgisayarından iç ağdaki ERP API'sine dakikada 10.000 istek gönderilerek sistem kilitlenmeye çalışılıyor.
NEDEN ŞÜPHELİ: Uygulama katmanında hizmet dışı bırakma (DoS) eğilimi.
NORMAL BASELINE'DAN SAPMA: API çağrı yoğunluğunda norm dışı patlama.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Şirkete zarar vermek isteyen bir personel, işlerin en yoğun olduğu an finansal sistemleri kilitleyerek operasyonu durdurabilir.

**70.**
SENARYO ADI: CFO'nun Kayıtlı Kimlik Bilgilerinin Çalınması
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: CFO
OLAY: CFO'nun bilgisayarındaki tarayıcıda kayıtlı olan iç ağ şifreleri, yerel bir betik vasıtasıyla okunuyor ve iç ağdaki bir geliştirici makinesine aktarılıyor.
NEDEN ŞÜPHELİ: CFO bilgisayarından hassas sistem dosyalarının okunması ve ağda taşınması.
NORMAL BASELINE'DAN SAPMA: Dosya okuma davranışsal anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar şifre girmekle uğraşmamak için tarayıcı belleklerinde veya credential manager'larda saklanan şifreleri hedef alırlar.

---

### **Satış ve Pazarlama Senaryoları (71 - 85)**

**71.**
SENARYO ADI: Satışçının İstifa Öncesi CRM Temizliği
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Satış
OLAY: İstifa etmeyi planlayan kıdemli satış temsilcisi, CRM sunucusundan erişebildiği tüm müşteri kontak listelerini ve fiyat tekliflerini CSV formatında lokal bilgisayarına indirip iç maille kişisel görünümlü bir adrese taşımaya çalışıyor (veya yerel ağdaki bir klasörde topluyor).
NEDEN ŞÜPHELİ: Kullanıcının normal günlük veri çekme miktarının 50 katını tek seferde çekmesi.
NORMAL BASELINE'DAN SAPMA: Günlük 10 müşteri kaydı inceleyen kullanıcının 5000 kaydı export etmesi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Satış personeli ayrılırken müşteri portföyünü de beraberinde götürmek ister ve bu verileri agresif şekilde toplar.

**72.**
SENARYO ADI: Satışçının İK Klasörünü Zorlaması
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Satış
OLAY: Satış personeli, iç ağdaki dosya sunucusunda açık unutulmuş bir İK klasörünü fark ederek içerideki prim ve komisyon dağıtım listelerini okuyor.
NEDEN ŞÜPHELİ: Satış rolünün İK ve bordro klasörleriyle etkileşime girmesi.
NORMAL BASELINE'DAN SAPMA: Erişim matrisi dışı klasör okuma aktivitesi.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Ortak ağlarda unutulan veya yanlış yetkilendirilen klasörler diğer departmanlar tarafından hızla keşfedilir ve sızdırılır.

**73.**
SENARYO ADI: Satış Bilgisayarında Ağ Tarama Yazılımı
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Satış
OLAY: Bir satış personelinin bilgisayarında, şirket politikalarına aykırı olan Advanced IP Scanner yazılımı kuruluyor ve iç LAN üzerinde tarama başlatılıyor.
NEDEN ŞÜPHELİ: Teknik olmayan bir rolde ağ haritalama ve tarama yazılımı çalıştırılması.
NORMAL BASELINE'DAN SAPMA: Uygulama envanteri baseline ihlali ve ağ anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar tarafından ele geçirilen satışçı bilgisayarları, teknik personel kadar göze batmadığı düşünülerek iç ağ taramalarında piyon olarak kullanılır.

**74.**
SENARYO ADI: Rakip Firmadan Gelen Satışçı Anomalisi
KATEGORİ: insider threat
KULLANICI ROLÜ: Satış
OLAY: Rakip firmadan yeni transfer edilen satış personeli, iç ağdaki ortak klasöre kendi getirdiği ve eski şirketine ait olan şifreli müşteri veri tabanını yüklüyor ve şirket ağında analiz etmeye çalışıyor.
NEDEN ŞÜPHELİ: Ağ sürücüsüne kaynağı belirsiz, şifreli ve büyük boyutlu veri bloklarının yüklenmesi.
NORMAL BASELINE'DAN SAPMA: Veri yükleme hacmi ve dosya türü anomalisi.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Yeni gelen çalışanlar eski iş yerlerinden veri getirerek kurumsal casusluk veya yasal risk doğuracak durumlar yaratabilirler.

**75.**
SENARYO ADI: Satış Maillerinde Fiyat Değişikliği
KATEGORİ: insider threat
KULLANICI ROLÜ: Satış
OLAY: Bir satış temsilcisi, iç ağ üzerinden teknik ekibe attığı maillerde, müşteriye onaylanan resmi fiyatın çok altında fiyatlar belirterek şirketi zarara uğratacak el altından anlaşmalar organize ediyor.
NEDEN ŞÜPHELİ: LLM'in iç yazışmaları analiz ederek onaylanan fiyat politikası ile mail içeriğindeki tutarsızlığı / şüpheli dille pazarlığı tespit etmesi.
NORMAL BASELINE'DAN SAPMA: Mail içerik semantik baseline sapması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Kötü niyetli satışçılar, rüşvet veya komisyon karşılığı şirket içi onay mekanizmalarını arkadan dolanarak fiyat manipülasyonu yaparlar.

**76.**
SENARYO ADI: Satışçının Sunucuya Sürekli Başarısız RDP Denemesi
KATEGORİ: credential ihlali
KULLANICI ROLÜ: Satış
OLAY: Satış personelinin bilgisayarından, muhasebe departmanının ana bilgisayarına uzak masaüstü (RDP) ile bağlanılmaya çalışılıyor ve üst üste yanlış şifreler giriliyor.
NEDEN ŞÜPHELİ: Teknik ve yetkisel olarak alakasız bir rolden RDP kaba kuvvet denemesi gelmesi.
NORMAL BASELINE'DAN SAPMA: Satış -> Muhasebe yönlü RDP baseline'ı 0'dır.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar ele geçirdikleri kullanıcı bilgisayarlarından iç ağdaki diğer bilgisayarlara parolasız veya zayıf parolaları tahmin ederek geçmek isterler.

**77.**
SENARYO ADI: Pazarlama Planlarının Toplu İndirilmesi
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Satış
OLAY: Satış yöneticisi, şirketin önümüzdeki 2 yıla ait gizli pazarlama stratejilerini ve ürün yol haritalarını içeren sunum dosyalarını topluca yerel diskine çekiyor.
NEDEN ŞÜPHELİ: Normalde sadece güncel satış verilerine bakan personelin stratejik gelecek planlarına odaklanması.
NORMAL BASELINE'DAN SAPMA: Dosya erişim örüntülerinde yapısal sapma.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Rakip firmaya geçiş arefesindeki yöneticiler, yeni yerlerinde prim yapmak için şirketin gelecek planlarını kopyalarlar.

**78.**
SENARYO ADI: Satışçı Bilgisayarında USB Ağ Geçidi Oluşturma
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Satış
OLAY: Satış personeli, şirketin iç ağ kısıtlamalarını delmek için bilgisayarına bir 4G/5G USB modem takıyor ve iç ağdaki verileri bu hat üzerinden dışarı aktarma potansiyeli yaratıyor.
NEDEN ŞÜPHELİ: Bilgisayarda yeni bir ağ kartı (network interface) oluşması ve iç ağ yönlendirme tablosunun (routing table) manipüle edilmesi.
NORMAL BASELINE'DAN SAPMA: Ağ donanım baseline değişimi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: İnternet yasaklarını veya takibini aşmak isteyen çalışanlar, taşınabilir modemler kullanarak ağ güvenliğini tamamen bypass ederler.

**79.**
SENARYO ADI: Satış Grubuna Toplu Sahte Ek Gönderimi
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: Satış
OLAY: Bir satışçının hesabı ele geçiriliyor ve iç ağdaki "Satış Departmanı Toplu Mail Grubu"na "Yeni Prim Listesi.exe" isimli zararlı bir dosya gönderiliyor.
NEDEN ŞÜPHELİ: Satış personeli tarafından executable (.exe) uzantılı dosyaların iç ağda maille dağıtılması.
NORMAL BASELINE'DAN SAPMA: Mail eki standartlarının dışına çıkılması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Saldırganlar iç ağda hızla yayılmak (ransomware yayılımı vb.) için güvenilen bir departman içi toplu mail grubunu kullanırlar.

**80.**
SENARYO ADI: Satışçının Kaynak Kod Sunucusunda Açık Araması
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Satış
OLAY: Satış temsilcisi, yazılımcıların kullandığı iç Git sunucusunun web arayüzünde "admin/admin" veya "root/root" gibi zayıf varsayılan şifreleri deniyor.
NEDEN ŞÜPHELİ: Satış IP'sinden geliştirici araçlarına yönelik brute force / default credential denemeleri.
NORMAL BASELINE'DAN SAPMA: Sistem giriş loglarında rol dışı anomali puanı.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirket içi siber casusluk faaliyetlerinde, teknik görünmeyen roller üzerinden kritik altyapıların zayıf şifreleri test edilir.

**81.**
SENARYO ADI: Müşteri Bilgilerinin İç Maille Kişisel Hesaplara Sızdırılması
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Satış
OLAY: Satışçı, CRM'den çektiği müşteri telefon ve e-postalarını bir metin dosyasına kaydedip iç mail üzerinden şirkette çalışan yakın bir arkadaşına "buna bir bak" diyerek gönderiyor.
NEDEN ŞÜPHELİ: LLM'in mail içeriğindeki verinin KVKK kapsamında kritik müşteri kişisel verisi (KVKK/GDPR) olduğunu anlaması.
NORMAL BASELINE'DAN SAPMA: Veri koruma kurallarının iç mail segmentinde ihlali.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Çalışanlar dışarıya mail atamadıklarında, takibe takılmamak için verileri önce başka bir iç hesaba paslayarak iz kaybettirmeye çalışırlar.

**82.**
SENARYO ADI: Satışçının Gece Boyu CRM Verisi Otomasyonu
KATEGORİ: insider threat
KULLANICI ROLÜ: Satış
OLAY: Satış personeli, bilgisayarına kurduğu basit bir makro kaydedici (macro recorder) ile gece boyu CRM sistemindeki tüm müşteri sayfalarını tek tek açtırıp ekran görüntüsü aldırıyor veya veri topluyor.
NEDEN ŞÜPHELİ: Kullanıcının insanüstü bir hızla ve ritmik olarak saatlerce sayfa yenilemesi ve veri indirmesi.
NORMAL BASELINE'DAN SAPMA: Kullanıcı tıklama ve sayfa gezme hızı baseline sapması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Export yetkisi elinden alınan satışçılar, veriyi çalmak için ekranı tarayan veya sayfaları otomatik gezen makrolar kullanırlar.

**83.**
SENARYO ADI: Fiyat Listelerinin Rakip İncelemesine Hazırlanması
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Satış
OLAY: Satışçı, şirketin gizli maliyet ve kar marjlarını içeren ana fiyatlama tablosunu yerel bilgisayarında kopyalayıp adını "Yeni_Yemek_Menusu.xlsx" olarak değiştiriyor.
NEDEN ŞÜPHELİ: Dosya içeriği ile dosya uzantısı/adı arasındaki uyumsuzluk (LLM içerik analizi ile isimlendirme çelişkisi).
NORMAL BASELINE'DAN SAPMA: Dosya maskeleme anomalisi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Veri çalacak çalışanlar DLP sistemlerini atlatmak için hassas dosyaların isimlerini masum isimlerle değiştirirler.

**84.**
SENARYO ADI: Satışçının IT Admin Kimliğine Bürünmesi
KATEGORİ: credential ihlali
KULLANICI ROLÜ: Satış
OLAY: Satış personeli, bir IT Admin'in masasından kalkarken açık bıraktığı bilgisayarı kullanarak kendi kullanıcısına tam ağ erişim yetkisi tanımlıyor.
NEDEN ŞÜPHELİ: Admin bilgisayarından satış personeli hesabına yönelik sıra dışı yetki tanımlama aktivitesi.
NORMAL BASELINE'DAN SAPMA: Yetkilendirme loglarında anomali.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Sosyal mühendislik ve açık bırakılan ekranlar, içerideki kötü niyetli kişilerin en kolay yetki yükseltme yöntemidir.

**85.**
SENARYO ADI: Pazarlama Sunucusuna Zararlı Dosya Yükleme
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: Satış
OLAY: Satışçı, dışarıdan aldığı virüslü bir kampanya görselini (aslında içinde zararlı kod gömülü olan bir görsel dosyası) şirketin iç pazarlama sunucusuna yüklüyor.
NEDEN ŞÜPHELİ: Dosya sunucusuna yüklenen dosyanın imza ve davranış olarak anomali içermesi.
NORMAL BASELINE'DAN SAPMA: Sunucuya yazılan dosya bütünlüğü anomalisi.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Tedarikçilerden veya dış mecralardan gelen materyaller kontrol edilmeden iç sunuculara yüklendiğinde ağa virüs bulaşır.

---

### **İK ve Hukuk Departmanı Senaryoları (86 - 100)**

**86.**
SENARYO ADI: İK Müdürünün Toplu Özlük Dosyası İndirmesi
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: İK
OLAY: İK çalışanı, cuma günü mesai bitimine yakın iç ağdaki arşivden 35 çalışanın tümüne ait performans değerlendirmelerini, sabıka kayıtlarını ve sağlık raporlarını tek bir zip dosyasında topluyor.
NEDEN ŞÜPHELİ: İK rolü yetkili olsa dahi tüm şirketin hassas verilerinin toplu olarak arşivlenmesi sızdırma öncesi hazırlığa işaret eder.
NORMAL BASELINE'DAN SAPMA: Tekil özlük dosyası erişim sıklığından kitlesel dosya paketlemeye geçiş.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Şirketle mahkemelik olan veya ayrılan İK personelleri, koz olarak kullanmak üzere çalışanların gizli bilgilerini kopyalarlar.

**87.**
SENARYO ADI: Hukuk Müşavirinin Teknik Sunuculara İlgisi
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk departmanı çalışanı, şirketin kaynak kodlarının ve API anahtarlarının bulunduğu sunucu bloklarına ping atarak erişim yollarını tarıyor.
NEDEN ŞÜPHELİ: Hukuk rolünün altyapı ve network katmanında keşif faaliyeti yapması normal dışıdır.
NORMAL BASELINE'DAN SAPMA: Ağ iletişim matrisinde baseline dışı bağlantı isteği.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Ele geçirilen bilgisayarlarda saldırganlar kullanıcının kim olduğuna bakmaksızın ağda yanal ilerleme komutları çalıştırırlar.

**88.**
SENARYO ADI: İK Mailinden Gelen Şüpheli İstifa Duyurusu
KATEGORİ: credential ihlali
KULLANICI ROLÜ: İK
OLAY: İK personelinin hesabı kullanılarak tüm şirkete "CEO'muz istifa etmiştir, detaylar ekteki PDF'tedir" şeklinde sahte bir iç mail atılıyor.
NEDEN ŞÜPHELİ: LLM'in mail içeriğindeki panik ve kaos yaratacak dili, normal İK kurumsal iletişim dilindeki baseline ile karşılaştırıp anomali bulması.
NORMAL BASELINE'DAN SAPMA: Mail dil ve üslup anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirket içinde panik yaratarak hisse değerini düşürmek veya kaos anında güvenlik açıklarından yararlanmakiçin sahte mailler atılır.

**89.**
SENARYO ADI: Hukuk Departmanında Sözleşmelerin Toplu USB'ye Atılması
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk personeli, şirketin tüm gizlilik sözleşmelerini (NDA) ve müşteri ortaklık anlaşmalarını bilgisayarına taktığı bir harici diske kopyalıyor.
NEDEN ŞÜPHELİ: Hukuk departmanında baseline USB kullanım kurallarının ihlali ve yüksek gizlilik dereceli veri transferi.
NORMAL BASELINE'DAN SAPMA: Kritik belge sınıflarının harici medyaya yazılma hacmi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirketin ticari sırlarını ve yasal açıklarını bilen hukukçular, ayrılırken bu belgeleri yasal süreçlerde kullanmak üzere çalabilirler.

**90.**
SENARYO ADI: İK Bilgisayarında Yetkisiz Keylogger Çalışması
KATEGORİ: dış saldırı destegi
KULLANICI ROLÜ: İK
OLAY: İK çalışanının bilgisayarında, basılan tuşları kaydeden (keylogger) zararlı bir arka plan süreci çalışıyor ve toplanan verileri iç ağdaki sahte bir yerel paylaşım klasörüne yazıyor.
NEDEN ŞÜPHELİ: Kullanıcı bilgisayarında yetkisiz dosya yazma ve API dinleme süreçleri.
NORMAL BASELINE'DAN SAPMA: İşletim sistemi API çağrılarında anomali.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: İK çalışanlarının şifrelerini ele geçirmek, tüm şirketin özlük haklarına ve sistemlerine erişim kapısı aralar.

**91.**
SENARYO ADI: Hukukçunun Yazılımcı Bilgisayarına RDP Yapması
KATEGORİ: credential ihlali
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk personelinin bilgisayarından, bir yazılımcının test ortamındaki makinesine aktif RDP oturumu açılıyor.
NEDEN ŞÜPHELİ: Hukuk -> Yazılım yönünde kurumsal geçmişte hiç RDP bağlantısı olmaması.
NORMAL BASELINE'DAN SAPMA: Kaynak-Hedef RDP matrisinin dışına çıkılması.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Çalınan hesaplar ağda dolaşırken en zayıf korunan geliştirici bilgisayarlarını hedef seçerler.

**92.**
SENARYO ADI: İK Personelinin Yetkisiz Veri Tabanı Giriş Denemesi
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: İK
OLAY: İK uzmanı, şirketin ana üretim veri tabanına (Production DB) SQL istemci programı indirerek bağlanmayı deniyor.
NEDEN ŞÜPHELİ: Rol tanımında SQL veya veri tabanı yönetimi olmayan kullanıcının DB portuna (1433/3306) istek atması.
NORMAL BASELINE'DAN SAPMA: Port bazlı erişim anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Kullanıcılar bazen kendi yetkilerinin sınırını test etmek veya teknik sistemlerdeki bilgileri kurcalamak için doğrudan DB'ye erişmek isterler.

**93.**
SENARYO ADI: Hukuk Departmanında Şifreli Maillerin Artışı
KATEGORİ: politika ihlali
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk müşaviri, iç ağdaki mail sunucusu üzerinden şirket dışındaki veya içindeki alakasız kişilere içeriği DLP tarafından okunamayan PGP ile şifrelenmiş mailler gönderiyor.
NEDEN ŞÜPHELİ: Kurumsal ağda denetlenemeyen şifreli iletişim kanallarının kullanılması.
NORMAL BASELINE'DAN SAPMA: Mail şifreleme tiplerinde anomali puanı artışı.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Bilgi sızdıran köstebekler (whistleblower), yakalanmamak için şirket içinde PGP veya benzeri güçlü şifreleme araçları kullanırlar.

**94.**
SENARYO ADI: İK Uzmanının Mesai Dışı Yoğun Uygulama Kullanımı
KATEGORİ: politika ihlali
KULLANICI ROLÜ: İK
OLAY: İK uzmanı, pazar günü öğlen saatlerinde iç ağa bağlanıp normalde günde 1 saat kullandığı özlük işleri yazılımını kesintisiz 6 saat boyunca çalıştırıyor ve veri taraması yapıyor.
NEDEN ŞÜPHELİ: Zaman penceresi ve uygulama kullanım süresi baseline uyumsuzluğu.
NORMAL BASELINE'DAN SAPMA: Haftalık ortalama kullanım sürelerinin pazar gününde aşılması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: İş yükü altında ezilen veya gizlice veri toplayan çalışanlar, kimsenin rahatsız etmeyeceği hafta sonu saatlerinde sistemleri yoğun şekilde kullanırlar.

**95.**
SENARYO ADI: Hukuk Sekreterinin Yanlışlıkla Kimlik Paylaşması
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk sekreteri, yönetim kurulunun iç ağdaki toplantı erişim şifrelerini yanlışlıkla şirketin tüm destek ve stajyer kadrosunun da olduğu genel iç mail grubuna gönderiyor.
NEDEN ŞÜPHELİ: LLM'in mail içeriğini ve ekindeki şifre formatlarını analiz ederek "Hassas Bilgi İhlali" saptaması.
NORMAL BASELINE'DAN SAPMA: Veri sızıntısı risk skoru patlaması.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Dikkatsizlik ve aceleyle atılan iç mailler, şirket içindeki yetkisiz kişilerin kritik bilgilere zahmetsizce ulaşmasına neden olur.

**96.**
SENARYO ADI: İK Bilgisayarından Toplu API Çağrısı
KATEGORİ: veri sızdırma
KULLANICI ROLÜ: İK
OLAY: İK bilgisayarından, şirketin çalışan listesini dönen iç API'sine 1 dakika içinde 2000 ardışık istek gönderilerek tüm çalışanların ev adresleri ve telefonları çekiliyor.
NEDEN ŞÜPHELİ: Arayüz üzerinden tek tek bakılması gereken verilerin script yardımıyla kitlesel olarak çekilmesi (Scraping).
NORMAL BASELINE'DAN SAPMA: API çağrı hızı ve hacmi anomali tespiti.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Kötü niyetli kişiler veri tabanına erişemediklerinde, kullanıcı arayüzlerinin arkasındaki API'leri otomatize ederek verileri sızdırırlar.

**97.**
SENARYO ADI: Hukuk Departmanında Eski Çalışan Klasörlerinin Kurcalanması
KATEGORİ: yetkisiz erişim
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk çalışanı, ortak ağ sürücüsünde bulunan ve 3 yıl önce şirketten ayrılmış olan kurucu ortakların eski arşiv klasörlerini açıp içindeki belgeleri tek tek okuyor.
NEDEN ŞÜPHELİ: Güncel iş tanımıyla ilgisi olmayan, geçmişe dönük ve pasif dosya bloklarına yönelik ani ilgi.
NORMAL BASELINE'DAN SAPMA: Dosya erişim geçmişi baseline sapması.
BEKLENEN SEVERITY: WARNING
GERÇEKÇİLİK NOTU: Şirket içi geçmiş krizleri veya gizli anlaşmaları araştırarak şantaj malzemesi arayan çalışanlar eski arşivleri kurcalarlar.

**98.**
SENARYO ADI: İK Sisteminde Sahte Kullanıcı Oluşturma Denemesi
KATEGORİ: insider threat
KULLANICI ROLÜ: İK
OLAY: İK yöneticisi, şirkette gerçekte var olmayan "hayalet bir çalışan" profili oluşturup ERP sistemine kaydediyor ve ona maaş hesabı tanımlamaya çalışıyor.
NEDEN ŞÜPHELİ: LLM'in İK kayıt süreçlerindeki eksik belgeleri (sabıka kaydı yok, imza sirküsü yok) ve anormal veri giriş sırasını sistem loglarından yakalaması.
NORMAL BASELINE'DAN SAPMA: Süreç akış anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: İçeriden yapılan büyük dolandırıcılıklarda İK ve muhasebe ortaklaşa hayalet personeller yaratarak şirket bütçesini zimmetlerine geçirirler.

**99.**
SENARYO ADI: Hukuk Bilgisayarına Güvenli Olmayan USB Takılması
KATEGORİ: kazara ihlal
KULLANICI ROLÜ: Hukuk
OLAY: Hukuk müşaviri, bir davanın delillerini incelemek üzere müvekkilden veya dış taraftan gelen ve içinde ne olduğu bilinmeyen denetimsiz bir USB belleği bilgisayarına takıyor.
NEDEN ŞÜPHELİ: İç ağ güvenliğini tehlikeye atacak, envanter dışı harici depolama birimi aktivitesi.
NORMAL BASELINE'DAN SAPMA: Donanım baseline ihlali.
BEKLENEN SEVERITY: ALERT
GERÇEKÇİLİK NOTU: Hukukçular adli süreçlerde kendilerine teslim edilen dijital delilleri doğrudan şirket bilgisayarlarında açarak ağa zararlı yazılım bulaştırırlar.

**100.**
SENARYO ADI: İK ve Bilgi İşlem Çapraz Hesap Manipülasyonu
KATEGORİ: credential ihlali
KULLANICI ROLÜ: İK
OLAY: İK personeli, bir IT Admin ile iş birliği yaparak, işten çıkarılacak olan bir yazılımcının hesabının şifresini habersizce değiştiriyor ve hesaba İK bilgisayarından erişerek yazılımcının kendi arasındaki eski maillerini siliyor.
NEDEN ŞÜPHELİ: Bir kullanıcının hesabına ait şifrenin olağan dışı şekilde sıfırlanması ve hemen ardından farklı departmandaki bir IP'den oturum açılması.
NORMAL BASELINE'DAN SAPMA: Eş zamanlı hesap değişim ve lokasyon sapma anomalisi.
BEKLENEN SEVERITY: CRITICAL
GERÇEKÇİLİK NOTU: Şirket içi politikalarda veya yönetim kavgalarında departmanlar arası gizli ittifaklar kurularak hedef kişilerin dijital izleri ve delilleri yok edilmeye çalışılır.