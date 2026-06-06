# Google Maps Nearby Scraper

Google Maps üzerinden İstanbul'un farklı ilçeleri ve mahalleleri için çeşitli kategorilerde (restoran, kafe, bar, vb.) yerleri asenkron ve paralel olarak tarayan, otomatikleştirilmiş bir web scraping aracıdır.

## 🚀 Özellikler

- **Asenkron & Paralel Çalışma**: Playwright ve asyncio kullanılarak yüksek performanslı veri çekimi. Maksimum hız için paralel worker mimarisi (varsayılan: 4 worker).
- **Akıllı Oturum Yönetimi**: Her ilçe için temiz bir tarayıcı bağlamı (browser context) oluşturulur.
- **Dinamik User-Agent**: Yakalanma riskini azaltmak için her mahalle geçişinde dinamik olarak User-Agent değiştirilir.
- **Kaldığı Yerden Devam Etme (Resume)**: İşlem kesintiye uğrarsa, kaydedilen ilerleme (progress) sayesinde `progress.json` üzerinden kaldığı noktadan devam edebilme özelliği.
- **Kapsamlı Konfigürasyon**: Tüm ilçe, mahalle, arama kelimeleri (keywords), bekleme süreleri ve tarayıcı ayarları merkezi bir `config.py` dosyasından yönetilir.
- **Otomatik Birleştirme & Tekilleştirme**: Toplanan verileri sonradan temizlemek ve aynı mekanların mükerrer kayıtlarını (duplicate) silmek için `merge_and_dedup.py` aracı içerir.

## 📁 Proje Yapısı

- `main.py`: Projenin ana orkestrasyon modülü. İlçeleri ve mahalleleri tarama işlemini başlatır ve yönetir.
- `scraper.py`: Playwright ile Google Maps sayfalarında arama yapma, sayfayı kaydırma ve yer detaylarını (isim, adres, puan, kategori, url vb.) çekme işlemlerini barındırır.
- `config.py`: Projedeki tüm sabitler (ilçeler, mahalleler, bekleme süreleri, User-Agent listesi, anahtar kelimeler) burada yer alır.
- `browser_manager.py`: Tarayıcı oturumlarını, User-Agent değişimlerini ve çerez (cookie) temizliklerini yönetir.
- `progress_manager.py`: İşlemlerin nerede kaldığını takip eder ve JSON tabanlı (progress.json) kayıt tutar.
- `merge_and_dedup.py`: Çıktı dosyalarındaki aynı sonuçları temizler ve verileri tek bir dosyada birleştirir.
- `log_config.py`: Loglama ayarlarını içerir.

## 🛠️ Kurulum

1. Depoyu klonlayın (veya indirin) ve proje dizinine gidin:
   ```bash
   cd mapsURL
   ```

2. Gerekli Python kütüphanelerini yükleyin:
   Projede temel olarak `playwright` kullanılmaktadır.
   ```bash
   pip install playwright
   ```

3. Playwright tarayıcılarını kurun:
   ```bash
   playwright install chromium
   ```

## ⚙️ Kullanım

Tarama işlemini başlatmak için sadece ana modülü çalıştırmanız yeterlidir:

```bash
python main.py
```

İşlem başlatıldığında:
- Çıktılar `output/` dizini altında tarih-saat damgalı JSON dosyaları olarak kaydedilir.
- İlerleme durumu `output/progress.json` içerisinde tutulur. Program kapatılıp tekrar açıldığında bu dosya üzerinden kaldığı yerden devam eder.
- İlgili loglar konsola ve `logs/` dizinine yazılır.

Mükerrer (duplicate) verileri temizlemek ve dosyaları birleştirmek için:
```bash
python merge_and_dedup.py
```

## 📝 Konfigürasyon Ayarları

`config.py` dosyası üzerinden tüm ayarları özelleştirebilirsiniz:
- **İlçeler ve Mahalleler**: `ISTANBUL_ILCELER` sözlüğünü güncelleyerek farklı yerleri tarayabilirsiniz.
- **Aranacak Kategoriler**: `KEYWORDS` listesini değiştirerek farklı işletme türlerini arayabilirsiniz.
- **Paralellik Limiti**: Aynı anda işlenecek mahalle sayısını `MAX_WORKERS` değişkeni ile ayarlayabilirsiniz.
- **Bekleme Süreleri**: Google'ın rate-limit'ine takılmamak için `SCROLL_WAIT_MIN`, `SCROLL_WAIT_MAX`, `BETWEEN_ILCE_WAIT` (varsayılan: 10 dk) gibi süreleri düzenleyebilirsiniz.

## ⚠️ Uyarılar ve Yasal Bilgilendirme

Bu proje eğitim, araştırma ve veri analizi amaçlıdır. Google Maps servislerini scrape ederken Google'ın Hizmet Şartları'nı (TOS) ihlal etmemeye ve platforma aşırı yük bindirmemeye özen gösterin. Sık ve yoğun istekler, IP adresinizin veya oturumunuzun geçici/kalıcı olarak engellenmesine neden olabilir.
