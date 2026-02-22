# MMPI - Kişilik Envanteri

Bu proje, MMPI (Minnesota Multiphasic Personality Inventory) testini uygulayan ve yapay zeka ile analiz eden deneysel bir web uygulamasıdır.

## Özellikler

- 566 soruluk MMPI testi
- Referans testi ile kalibrasyon
- Veritabanına sonuçların kaydedilmesi
- Yapay zeka ile analiz (veri toplandıkça aktif hale gelir)

## Kurulum

1. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Veritabanını oluşturun:
   ```
   python init_db.py
   ```

3. Test verilerini ekleyin (isteğe bağlı):
   ```
   python add_test_data.py
   ```

4. Yapay zeka eğitimi yapın:
   ```
   python train_ai.py
   ```

5. Uygulamayı başlatın:
   ```
   python app.py
   ```

6. Tarayıcınızda `http://localhost:5000` adresine gidin

## Dosya Yapısı

- `app.py`: Ana uygulama dosyası
- `models.py`: Veritabanı modelleri
- `scoring.py`: Skor hesaplama motoru
- `train_ai.py`: Yapay zeka eğitimi için veri analizi
- `mmpi_sorular.csv`: MMPI soruları
- `templates/`: HTML şablonları
- `instance/`: SQLite veritabanı dosyaları
- `generated_keys.json`: Yapay zeka tarafından üretilen anahtarlar

## Katkıda Bulunma

1. Fork edin
2. Yeni bir branch oluşturun (`git checkout -b ozellik/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik ekle'`)
4. Branch'inizi push edin (`git push origin ozellik/yeni-ozellik`)
5. Yeni bir Pull Request oluşturun

## Lisans

Bu proje sıfırdan öğrenim yoluyla key üretilmiştir ve bağımsız bir projedir.