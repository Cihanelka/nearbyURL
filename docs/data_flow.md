---
description: MapsNearby Scraper projesinin teknik veri akış mimarisi
---

# 🛠 Teknik Veri Akışı (Data Flow)

Bu belge, uygulamanın başlatılmasından verinin nihai JSON formatında kaydedilmesine kadar geçen tüm aşamaları teknik detaylarıyla açıklar.

## 1. Hazırlık ve Başlatma (Initialization)
- **`main.py`** çalıştırıldığında ilk olarak **`progress_manager.loadProgress()`** ile mevcut durum kontrol edilir.
- Eğer daha önce yarım kalmış bir çalışma varsa, `progress.json` üzerinden hangi mahallelerin tamamlandığı ve hangi çıktı dosyasının kullanıldığı tespit edilir.
- **`config.py`** üzerindeki tüm sabitler (ilçeler, mahalleler, bekleme süreleri, keyword listesi) yüklenir.

## 2. İlçe Bazlı Oturum Yönetimi (District-level Context)
- Uygulama, her ilçeyi izole bir oturum (session) olarak ele alır.
- **`browser_manager.createFreshContext()`** çağrılarak her ilçe için temiz bir browser context oluşturulur.
- **Cookie Yönetimi**: `initGoogleCookies` ile önce Google ana sayfasına gidilir ve cookie onayı ("Tümünü kabul et") verilir. Bu, Maps sayfalarının bot engeline takılmadan yüklenmesini sağlar.

## 3. Mahalle ve İşçi (Worker) Orkestrasyonu
- İlçe içindeki işlenmemiş mahalleler listelenir.
- **`asyncio.Semaphore(MAX_WORKERS)`** (varsayılan: 4) ile paralel işleme kontrol edilir.
- Her worker bir mahalle için:
  1. **`maps_navigator.navigateToNearby()`** ile Google Maps'te ilgili mahallenin "Yakınında" (Nearby) görünümüne gider.
  2. Tanımlı tüm keyword'leri (`restaurant`, `cafe`, vb.) sırayla aratır.

## 4. Arama ve Kart Veri Çekimi (Scraping Phase)
- **Keyword Arama**: `scraper.scrapeKeywordResults` içinde arama kutusuna keyword yazılır ve Enter'a basılır.
- **Scroll Mekanizması**: Sol panel (`[role="feed"]`) dinamik olarak aşağı kaydırılır (`scrollFeedToBottom`). Yeni kart yüklenmediğinde (3 deneme başarısızsa) durur.
- **Veri Ayıklama (`_parseCardData`)**:
  - `div.W4Efsd` blokları analiz edilerek kategori ve adres ayrıştırılır.
  - Puan, yorum sayısı ve fiyat aralığı (`span.MW4etd`, `span.UY7F9`) gibi sınıflardan çekilir.
  - **Normalizasyon**: Çekilen kısa kategori isimleri (ör. "Et"), `config.GOOGLE_CATEGORY_MAP` üzerinden tam haline (ör. "Et Restoranı") dönüştürülür.

## 5. Veri Saklama ve Progress (Persistence)
- **Thread-safe Yazma**: Birden fazla worker aynı anda çalıştığı için `_FILE_LOCK` (asyncio.Lock) kullanılarak JSON dosyasına güvenli ekleme yapılır.
- **JSON Yapısı**: 
  ```json
  {
    "mahalle": "...",
    "ilce": "...",
    "searchTerm": "...",
    "keyword": "...",
    "results": [...]
  }
  ```
- Her mahalle bittiğinde `progress_manager.markMahalleProcessed` ile durum kalıcı hale getirilir.

## 6. Son İşleme (Post-processing)
- Toplanan veriler `merge_and_dedup.py` aracı kullanılarak:
  1. Düz bir listeye (`flatten`) çevrilir.
  2. `href` (URL) bazlı global tekilleştirme (`deduplication`) yapılarak temizlenmiş veri seti elde edilir.
