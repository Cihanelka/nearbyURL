"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : Nearby scraper için tüm sabitler, ayarlar, keyword'ler ve ilçe/mahalle verileri.
              Tüm konfigürasyon merkezi olarak bu dosyadan yönetilir.
"""

import os
from datetime import datetime
from typing import Dict, List

# ── User-Agent Ayarları ──────────────────────────────────────────────────────
BASE_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 OPR/131.0.0.0"
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 OPR/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
]

# ── Arama Keyword'leri ───────────────────────────────────────────────────────
KEYWORDS = [
    "restaurant",
    "bar",
    "brewpub",
    "gastropub",
    "pub",
    "irish pub",
    "cafeteria",
    "cafe",
    "art cafe",
    "chocolate cafe",
    "restaurant or cafe",
    "coffee roasters",
    "coffee shop",
    "coffee stand",
    "coffee store",
    "coffee wholesaler",
    "school cafeteria",
    "pizza restaurant",
    "pizza delivery",
    "pizza takeaway",
    "pizza takeout",
    "bakery",
    "fast food",
    "fast food restaurant",
    "breakfast restaurant",
    "wine bar",
    "wine club",
    "sports bar",
    "bistro",
    "deli",
    "ice cream shop",
    "ice cream and drink shop",
    "dessert restaurant",
    "dessert shop",
    "italian restaurant",
    "chinese restaurant",
    "mexican restaurant",
    "indian restaurant",
    "thai restaurant",
    "japanese restaurant",
    "steak house",
    "doner kebab restaurant",
    "kebab shop",
    "turkish restaurant",
    "meyhane",
    "mediterranean restaurant",
    "american restaurant",
    "cocktail bar",
    "halal restaurant",
    "vegan restaurant",
    "vegetarian restaurant",
    "soup kitchen",
    "soup restaurant",
    "small plates restaurant",
    "brunch",
    "brunch restaurant",
    "lunch restaurant",
    "catering",
    "sweets and dessert buffet",
    "family restaurant",
    "hotel",
    "resort hotel",
    "night club",
    "tea and coffee shop",
]

# ── İstanbul İlçe ve Mahalleleri ────────────────────────────────────────────
ISTANBUL_ILCELER: Dict[str, List[str]] = {
    "Adalar": ["Burgazada", "Heybeliada", "Kınalıada", "Maden", "Nizam"],
    "Arnavutköy": ["Anadolu", "Arnavutköy Merkez", "Boğazköy Merkez", "Bolluca", "Çilingir", "Deliklikaya", "Dursunköy", "Durusu", "Fatih", "Hacımaşlı", "Hadımköy", "Haraççı", "Hastane", "Hicret", "İmrahor", "İslambey", "Karaburun", "Karlıbayır", "Mareşal Fevzi Çakmak", "Mavigöl", "Mehmet Akif Ersoy", "Mustafa Kemal Paşa", "Nenehatun", "Ömerli", "Sazlıbosna", "Taşoluk", "Tayakadın", "Terkos", "Yassıören", "Yavuz Selim", "Yeniköy", "Yeşilbayır", "Yunus Emre", "Zafer"],
    "Ataşehir": ["Aşık Veysel", "Ataşehir Atatürk", "Barbaros", "Esatpaşa", "Ferhatpaşa", "Fetih", "İçerenköy", "İnönü", "Kayışdağı", "Küçükbakkalköy", "Mevlana", "Mimar Sinan", "Mustafa Kemal", "Örnek", "Yeni Çamlıca", "Yeni Sahra", "Yenişehir"],
    "Avcılar": ["Ambarlı", "Cihangir", "Denizköşkler", "Firuzköy", "Gümüşpala", "Merkez", "Mustafa Kemal Paşa", "Tahtakale", "Üniversite", "Yeşilkent"],
    "Bağcılar": ["100. Yıl", "15 Temmuz", "Bağlar", "Barbaros", "Çınar", "Demirkapı", "Fatih", "Fevzi Çakmak", "Göztepe", "Güneşli", "Hürriyet", "İnönü", "Kazım Karabekir", "Kemalpaşa", "Kirazlı", "Mahmutbey", "Merkez", "Sancaktepe", "Yavuz Selim", "Yenigün", "Yenimahalle", "Yıldıztepe"],
    "Bahçelievler": ["Bahçelievler", "Cumhuriyet", "Çobançeşme", "Fevzi Çakmak", "Hürriyet", "Kocasinan Merkez", "Siyavuşpaşa", "Soğanlı", "Şirinevler", "Yenibosna Merkez", "Zafer"],
    "Bakırköy": ["Ataköy 1., 2., 5., 6. Kısım", "Ataköy 3., 4., 11. Kısım", "Ataköy 7., 8., 9., 10. Kısım", "Basınköy", "Cevizlik", "Kartaltepe", "Osmaniye", "Sakızağacı", "Şenlikköy", "Yenimahalle", "Yeşilköy", "Yeşilyurt", "Zeytinlik", "Zuhuratbaba"],
    "Başakşehir": ["Altınşehir", "Bahçeşehir 1. Kısım", "Bahçeşehir 2. Kısım", "Başak", "Başakşehir", "Güvercintepe", "İkitelli Osb", "Kayabaşı", "Şahintepe", "Şamlar", "Ziya Gökalp"],
    "Bayrampaşa": ["Altıntepsi", "Cevatpaşa", "İsmet Paşa", "Kartaltepe", "Kocatepe", "Muratpaşa", "Orta", "Terazidere", "Vatan", "Yenidoğan", "Yıldırım"],
    "Beşiktaş": ["Abbasağa", "Akat", "Arnavutköy", "Balmumcu", "Bebek", "Cihannüma", "Dikilitaş", "Etiler", "Gayrettepe", "Konaklar", "Kuruçeşme", "Kültür", "Levazım", "Levent", "Mecidiye", "Muradiye", "Nisbetiye", "Ortaköy", "Sinanpaşa", "Türkali", "Ulus", "Vişnezade", "Yıldız"],
    "Beykoz": ["Acarlar", "Akbaba", "Alibahadır", "Anadolu Feneri", "Anadolu Hisarı", "Anadolu Kavağı", "Baklacı", "Bozhane", "Cumhuriyet", "Çamlıbahçe", "Çengeldere", "Çiftlik", "Çiğdem", "Çubuklu", "Dereseki", "Elmalı", "Fatih", "Göksu", "Göllü", "Görele", "Göztepe", "Gümüşsuyu", "İncirköy", "İshaklı", "Kanlıca", "Kavacık", "Kaynarca", "Kılıçlı", "Mahmutşevketpaşa", "Merkez", "Örnekköy", "Öyümce", "Paşabahçe", "Paşamandıra", "Polonez", "Poyraz", "Riva", "Rüzgarlıbahçe", "Soğuksu", "Tokatköy", "Yalıköy", "Yavuz Selim", "Yeni Mahalle", "Zerzavatçı"],
    "Beylikdüzü": ["Adnan Kahveci", "Barış", "Büyükşehir", "Cumhuriyet", "Dereağzı", "Gürpınar", "Kavaklı", "Marmara", "Sahil", "Yakuplu"],
    "Beyoğlu": ["Arap Cami", "Asmalı Mescit", "Bedrettin", "Bereketzade", "Bostan", "Bülbül", "Camiikebir", "Cihangir", "Çatma Mescit", "Çukur", "Emekyemez", "Evliya Çelebi", "Fetihtepe", "Firuzağa", "Gümüşsuyu", "Hacıahmet", "Hacımimi", "Halıcıoğlu", "Hüseyinağa", "İstiklal", "Kadımehmet Efendi", "Kalyoncu Kulluğu", "Kamer Hatun", "Kaptanpaşa", "Katipmustafa Çelebi", "Keçeci Piri", "Kemankeş Karamustafa Paşa", "Kılıçali Paşa", "Kocatepe", "Kulaksız", "Kuloğlu", "Müeyyedzade", "Ömer Avni", "Piri Paşa", "Piyaleypaşa", "Pürtelaş Hasan Efendi", "Sururi Mehmet Efendi", "Sütlüce", "Şahkulu", "Şehit Muhtar", "Tomtom", "Yahya Kahya"],
    "Büyükçekmece": ["19 Mayıs", "Ahmediye", "Alkent 2000", "Atatürk", "Bahçelievler", "Celaliye", "Cumhuriyet", "Çakmaklı", "Dizdariye", "Ekinoba", "Fatih", "Güzelce", "Hürriyet", "Kamiloba", "Karaağaç", "Kumburgaz", "Mimaroba", "Mimarsinan", "Murat Çeşme", "Pınartepe", "Sinanoba", "Türkoba", "Ulus", "Yenimahalle"],
    "Çatalca": ["Akalan", "Atatürk", "Aydınlar", "Bahşayiş", "Başak", "Belgrat", "Celepköy", "Çakıl", "Çanakça", "Çiftlikköy Merkez", "Dağyenice", "Elbasan", "Fatih", "Ferhatpaşa", "Gökçeali", "Gümüşpınar", "Hallaçlı", "Hisarbeyli", "İhsaniye", "İnceğiz", "İzzettin", "Kabaağaç", "Kaleiçi", "Kalfa", "Karacaköy Merkez", "Karamandere", "Kestanelik", "Kızılcaali", "Oklalı", "Ormanlı", "Ovayenice", "Öırcınlı", "Örencik", "Subaşı", "Yalıköy", "Yaylacık", "Yazlık"],
    "Çekmeköy": ["Alemdağ", "Aydınlar", "Çamlık", "Çatalmeşe", "Cumhuriyet", "Ekşioğlu", "Güngören", "Hamidiye", "Hüseyinli", "Kirazlıdere", "Koçullu", "Mehmet Akif", "Merkez", "Mimar Sinan", "Nişantepe", "Ömerli", "Reşadiye", "Sırapınar", "Soğukpınar", "Taşdelen", "Sultançiftliği"],
    "Esenler": ["Birlik", "Çifte Havuzlar", "Davutpaşa", "Fatih", "Fevzi Çakmak", "Havaalanı", "Kazım Karabekir", "Kemer", "Menderes", "Mimar Sinan", "Nene Hatun", "Oruçreis", "Tuna", "Turgut Reis", "Yavuz Selim", "Nine Hatun"],
    "Esenyurt": ["Akçaburgaz", "Akevler", "Akşemseddin", "Ardıçlı", "Aşık Veysel", "Atatürk", "Bağlarçeşme", "Balıkyolu", "Barbaros Hayrettin Paşa", "Battalgazi", "Cumhuriyet", "Çınar", "Esenkent", "Fatih", "Gökevler", "Güzelyurt", "Hürriyet", "İncirtepe", "İnönü", "İstiklal", "Koza", "Körfez", "Mevlana", "Namık Kemal", "Necip Fazıl Kısakürek", "Orhan Gazi", "Osmangazi", "Örnek", "Pınar", "Piri Reis", "Saadetdere", "Selahaddin Eyyubi", "Süleymaniye", "Şehitler", "Talatpaşa", "Turgut Özal", "Üçevler", "Yenikent", "Yeşilkent", "Yunus Emre", "Zafer"],
    "Eyüpsultan": ["Ağaçlı", "Akpınar", "Alibeyköy", "Çiftalan", "Çırçır", "Defterdar", "Düğmeciler", "Emniyettepe", "Esentepe", "Eyüp Merkez", "Göktürk Merkez", "Güzeltepe", "Işıklar", "İhsaniye", "İslambey", "Karadolap", "Mimar Sinan", "Mithatpaşa", "Nişancı", "Odayeri", "Pirinççi", "Rami Cuma", "Rami Yeni", "Sakarya", "Silahtarağa", "Topçular", "Yeşilpınar", "Gökkubbe"],
    "Fatih": ["Aksaray", "Akşemsettin", "Alemdar", "Ali Kuşçu", "Atikali", "Ayvansaray", "Balabanağa", "Balat", "Beyazıt", "Binbirdirek", "Cankurtaran", "Cerrahpaşa", "Cibali", "Demirtaş", "Derviş Ali", "Eminsinan", "Hacıkadın", "Haseki Sultan", "Hırka-i Şerif", "Hobyar", "Hoca Gıyaseddin", "Hoca Paşa", "İskenderpaşa", "Kalenderhane", "Karagümrük", "Katip Kasım", "Kemalpaşa", "Kocamustafapaşa", "Küçük Ayasofya", "Mercan", "Mesih Paşa", "Mevlanakapı", "Mimar Hayrettin", "Mimar Kemalettin", "Molla Fenari", "Molla Gürani", "Molla Hüsrev", "Muhsine Hatun", "Nişanca", "Rüstem Paşa", "Seyyid Ömer", "Silivrikapı", "Sultan Ahmet", "Sururi", "Süleymaniye", "Sümbül Efendi", "Şehremini", "Şehsuvar Bey", "Tahtakale", "Taya Hatun", "Topkapı", "Yavuz Sinan", "Yavuz Sultan Selim", "Yedikule", "Zeyrek"],
    "Gaziosmanpaşa": ["Bağlarbaşı", "Barbaros Hayrettin Paşa", "Fevzi Çakmak", "Hürriyet", "Karadeniz", "Karayolları", "Karlıtepe", "Kazım Karabekir", "Merkez", "Mevlana", "Pazariçi", "Sarıgöl", "Şemsipaşa", "Yeni Mahalle", "Yenidoğan", "Yıldıztabya"],
    "Güngören": ["Abdurrahman Nafiz Gürman", "Akıncılar", "Gençosman", "Güneştepe", "Güven", "Haznedar", "Mareşal Çakmak", "Mehmet Nesih Özmen", "Merkez", "Sanayi", "Tozkoparan"],
    "Kadıköy": ["19 Mayıs", "Acıbadem", "Bostancı", "Caddebostan", "Caferağa", "Dumlupınar", "Eğitim", "Erenköy", "Fenerbahçe", "Feneryolu", "Fikirtepe", "Göztepe", "Hasanpaşa", "Koşuyolu", "Kozyatağı", "Merdivenköy", "Osmanağa", "Rasimpaşa", "Sahrayıcedit", "Suadiye", "Zühtüpaşa"],
    "Kağıthane": ["Çağlayan", "Çeliktepe", "Emniyetevleri", "Gültepe", "Gürsel", "Hamidiye", "Harmantepe", "Hürriyet", "Mehmet Akif Ersoy", "Merkez", "Nurtepe", "Ortabayır", "Seyrantepe", "Sirkeci", "Şirintepe", "Talatpaşa", "Telsizler", "Yahya Kemal", "Yeşilce"],
    "Kartal": ["Atalar", "Cevizli", "Cumhuriyet", "Çavuşoğlu", "Esentepe", "Gümüşpınar", "Hürriyet", "Karlıktepe", "Kordonboyu", "Orhantepe", "Orta", "Petrol İş", "Soğanlık Yeni", "Topselvi", "Uğur Mumcu", "Yakacık Çarşı", "Yakacık Yeni", "Yalı", "Yukarı", "Yunus"],
    "Küçükçekmece": ["Atakent", "Atatürk", "Beşyol", "Cennet", "Cumhuriyet", "Fatih", "Fevzi Çakmak", "Gültepe", "Halkalı Merkez", "İnönü", "İstasyon", "Kanarya", "Kartaltepe", "Kemalpaşa", "Mehmet Akif", "Söğütlü Çeşme", "Tevfik Bey", "Yarımburgaz", "Yeni Mahalle", "Yeşilova"],
    "Maltepe": ["Altayçeşme", "Altıntepe", "Aydınevler", "Bağlarbaşı", "Başıbüyük", "Büyükbakkalköy", "Cevizli", "Çınar", "Esenkent", "Feyzullah", "Fındıklı", "Girne", "Gülensu", "Gülsuyu", "İdealtepe", "Küçükyalı", "Yalı", "Zümrütevler"],
    "Pendik": ["Ahmet Yesevi", "Bahçelievler", "Ballıca", "Batı", "Çamçeşme", "Çamlık", "Çınardere", "Doğu", "Dumlupınar", "Emirli", "Ertuğrul Gazi", "Esenler", "Esenyalı", "Fatih", "Fevzi Çakmak", "Göçbeyli", "Güllü Bağlar", "Güzelyalı", "Harmandere", "Kavakpınar", "Kaynarca", "Kurna", "Kurtdoğmuş", "Kurtköy", "Orhangazi", "Orta", "Ramazanoğlu", "Sanayi", "Sapan Bağları", "Sülüntepe", "Şeyhli", "Veli Baba", "Yayalar", "Yeni Mahalle", "Yenişehir", "Yeşilbağlar"],
    "Sancaktepe": ["Abdurrahmangazi", "Akpınar", "Atatürk", "Emek", "Eyüp Sultan", "Fatih", "Hilal", "Kemal Türkler", "Meclis", "Merve", "Mevlana", "Osmangazi", "Paşaköy", "Safa", "Sarıgazi", "Veysel Karani", "Yenidoğan", "Yunus Emre", "Kemalpaşa"],
    "Sarıyer": ["Ayazağa", "Bahçeköy Kemer", "Bahçeköy Merkez", "Bahçeköy Yeni", "Baltalimanı", "Büyükdere", "Cumhuriyet", "Çamlıtepe", "Çayırbaşı", "Darüşşafaka", "Demirciköy", "Derbent", "Emirgan", "Fatih Sultan Mehmet", "Ferahevler", "Garipçe", "Gümüşdere", "Huzur", "İstinye", "Kazım Karabekir Paşa", "Kilyos", "Kireçburnu", "Kocataş", "Kumköy", "Maden", "Maslak", "Merkez", "Pınar", "Poligon", "PTT Evleri", "Reşitpaşa", "Rumelifeneri", "Rumelihisarı", "Rumelikavağı", "Tarabya", "Uskumruköy", "Yeniköy", "Yenimahalle", "Zekeriyaköy"],
    "Silivri": ["Alibey", "Alipaşa", "Balaban", "Bekirli", "Beyciler", "Büyükçavuşlu Merkez", "Büyükkılıçlı", "Cumhuriyet", "Çayırdere", "Çeltik", "Danamandıra", "Fatih", "Fener", "Gazitepe", "Gümüşyaka Merkez", "Kadıköy", "Kavaklı", "Kurfallı", "Küçük Kılıçlı", "Mimar Sinan", "Ortaköy Merkez", "Piri Mehmet Paşa", "Sancaktepe", "Sayalar", "Selimpaşa Merkez", "Semizkumlar", "Seymen", "Şirinevler", "Yolçatı"],
    "Sultanbeyli": ["Abdurrahmangazi", "Adil", "Ahmetyesevi", "Akşemsettin", "Battalgazi", "Fatih", "Hasanpaşa", "Mecidiye", "Mehmet Akif", "Mimar Sinan", "Necip Fazıl", "Orhangazi", "Turgut Reis", "Yavuz Selim", "Yurtdoğu"],
    "Sultangazi": ["50. Yıl", "75. Yıl", "Cebeci", "Cumhuriyet", "Esentepe", "Gazi", "Habipler", "Malkoçoğlu", "Sultançiftliği", "Uğur Mumcu", "Yayla", "Yunus Emre", "Zübeyde Hanım", "İsmetpaşa", "Eski Habipler"],
    "Şile": ["Ağaçdere", "Ağva Merkez", "Ahmetli", "Akçakese", "Alacalı", "Avcıkoru", "Balibey", "Belen", "Bıçkıdere", "Bozkoca", "Bucaklı", "Çataklı", "Çavuş", "Çayırbaşı", "Çelebi", "Çengilli", "Darlık", "Değirmençayırı", "Doğancılı", "Erenler", "Esenceli", "Geredeli", "Göçe", "Gökmaslı", "Göksu", "Hacı Kasım", "Hasanlı", "İmrendere", "İmrenli", "İsaköy", "Kabakoz", "Kadıköy", "Kalem", "Karabeyli", "Karacaköy", "Karamandere", "Kervansaray", "Kızılca", "Korucu", "Kömürlük", "Kumbaba", "Kurfallı", "Kurna", "Meşrutiyet", "Oruçoğlu", "Osmanköy", "Ovacık", "Sahilköy", "Satmazlı", "Sofular", "Soğullu", "Sortullu", "Şuayipli", "Tekke", "Ulupelit", "Üvezli", "Yaka", "Yayla", "Yeniköy", "Yeşilvadi"],
    "Şişli": ["19 Mayıs", "Bozkurt", "Cumhuriyet", "Duatepe", "Ergenekon", "Esentepe", "Eskişehir", "Feriköy", "Fulya", "Gülbahar", "Halaskargazi", "Halide Edip Adıvar", "Halil Rıfat Paşa", "Harbiye", "İnönü", "İzzetpaşa", "Kaptanpaşa", "Kuştepe", "Mahmut Şevket Paşa", "Mecidiyeköy", "Merkez", "Meşrutiyet", "Paşa", "Teşvikiye", "Yayla"],
    "Tuzla": ["Akfırat", "Anadolu", "Aydınlı", "Aydıntepe", "Cami", "Evliya Çelebi", "Fatih", "İçmeler", "İstasyon", "Mescit", "Mimar Sinan", "Orhanlı", "Orta", "Postane", "Şifa", "Tepeören", "Yayla"],
    "Ümraniye": ["Adem Yavuz", "Altınşehir", "Armağan Evler", "Aşağı Dudullu", "Atakent", "Atatürk", "Cemil Meriç", "Çakmak", "Çamlık", "Dumlupınar", "Elmalıkent", "Esenevler", "Esenkent", "Esenşehir", "Fatih Sultan Mehmet", "Finanskent", "Hekimbaşı", "Huzur", "Ihlamurkuyu", "İnkılap", "İstiklal", "Kazım Karabekir", "Madenler", "Mehmet Akif", "Namık Kemal", "Necip Fazıl", "Parseller", "Saray", "Site", "Şerifali", "Tantavi", "Tatlısu", "Tepeüstü", "Topağacı", "Yamanevler", "Yeni Sanayi", "Yukarı Dudullu"],
    "Üsküdar": ["Acıbadem", "Ahmediye", "Altunizade", "Ayazma", "Bahçelievler", "Barbaros", "Beylerbeyi", "Bulgurlu", "Burhaniye", "Cumhuriyet", "Çengelköy", "Ferah", "Güzeltepe", "İcadiye", "İhsaniye", "Kandilli", "Kısıklı", "Kirazlıtepe", "Kuleli", "Kuzguncuk", "Küçük Çamlıca", "Küçüksu", "Küplüce", "Mehmet Akif Ersoy", "Mimar Sinan", "Muratreis", "Salacak", "Selami Ali", "Selimiye", "Sultantepe", "Ünalan", "Valide-i Atik", "Yavuztürk", "Zeynep Kamil"],
    "Zeytinburnu": ["Beştelsiz", "Çırpıcı", "Gökalp", "Kazlıçeşme", "Maltepe", "Merkezefendi", "Nuripaşa", "Seyitnizam", "Sümer", "Telsiz", "Veliefendi", "Yenidoğan", "Yeşiltepe"]
}

# ── Worker & Zamanlama Ayarları ──────────────────────────────────────────────
MAX_WORKERS = 4

# Maps yükleme/bekleme süreleri (ms)
PAGE_LOAD_TIMEOUT = 40000
RESULTS_LOAD_WAIT = 3000
SCROLL_WAIT_MIN = 4000
SCROLL_WAIT_MAX = 6000
BETWEEN_KEYWORD_WAIT = 3000
BETWEEN_MAHALLE_WAIT = 5000
BETWEEN_ILCE_WAIT = 10 * 60  # saniye (10 dakika)

# ── Dosya Yolları ────────────────────────────────────────────────────────────
LOGS_DIR = "logs"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    f"nearby_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
)
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.json")

# ── URL ──────────────────────────────────────────────────────────────────────
GOOGLE_URL = "https://www.google.com"
GOOGLE_MAPS_URL = "https://www.google.com/maps"
GOOGLE_MAPS_SEARCH_URL = "https://www.google.com/maps/search/"
