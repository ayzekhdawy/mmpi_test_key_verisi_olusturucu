import pandas as pd
import json
from scipy.stats import pointbiserialr
import numpy as np
from app import app
from models import db, UserData
import os
import sys

# UTF-8 kodlamasını ayarla
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def generate_scoring_keys():
    print("Yapay Zeka Ogrenme Modu Baslatiliyor...")

    with app.app_context():
        # 1. Veritabanindaki tum veriyi cek
        users = UserData.query.all()
        if len(users) < 10:
            print("Yetersiz Veri: En az 10 (onerilen 100) kullanici gerekli.")
            print(f"Mevcut veri sayisi: {len(users)}")
            return

        print(f"{len(users)} kullanicinin verisi analiz ediliyor...")

        # 2. Veriyi Pandas DataFrame'e cevir
        data_list = []
        for u in users:
            try:
                mmpi = json.loads(u.mmpi_answers)  # {'1': 'Evet', '2': 'Hayir'...}
                refs = json.loads(u.reference_scores) # {'Depresyon': 3, ...}

                # Tek bir satirda birlestir
                row = {}
                # MMPI Cevaplarini 0 ve 1'e cevir (Istatistik icin)
                for q_id, ans in mmpi.items():
                    row[f"Q_{q_id}"] = 1 if ans == 'Evet' else 0

                # Hedef Skorlari ekle
                for scale, score in refs.items():
                    row[f"TARGET_{scale}"] = score

                data_list.append(row)
            except json.JSONDecodeError as e:
                print(f"JSON decode hatasi: {e}")
                continue
            except Exception as e:
                print(f"Veri isleme hatasi: {e}")
                continue

        if not data_list:
            print("Islenebilir veri bulunamadi.")
            return

        df = pd.DataFrame(data_list)

        # DataFrame'in bos olup olmadigini kontrol et
        if df.empty:
            print("Veri cercevesi bos. Islemecek veri yok.")
            return

        print(f"DataFrame olusturuldu. Satir sayisi: {len(df)}, Sutun sayisi: {len(df.columns)}")

        # 3. KORELASYON ANALIZI (Mining)
        # Her olcek icin en iyi sorulari bul
        discovered_keys = {}
        target_scales = ['Depresyon', 'Paranoya', 'Anksiyete']

        for scale in target_scales:
            print(f"'{scale}' olcegi icin anahtarlar araniyor...")
            target_col = f"TARGET_{scale}"

            # Hedef sutunun varligini kontrol et
            if target_col not in df.columns:
                print(f"'{target_col}' sutunu bulunamadi. Atlaniyor...")
                continue

            scale_keys = {}

            # Tum sorulari (Q_1, Q_2...) tara
            question_cols = [c for c in df.columns if c.startswith('Q_')]

            if not question_cols:
                print(f"Soru sutunlari bulunamadi. '{scale}' icin atlaniyor...")
                continue

            valid_correlations = 0

            for q_col in question_cols:
                # Soru cevabi ile Hedef Skor arasindaki iliskiyi olc
                # Eger herkes ayni cevabi verdiyse hata vermesin diye try/except
                try:
                    corr, p_value = pointbiserialr(df[q_col], df[target_col])
                except Exception as e:
                    print(f"Korelasyon hesaplama hatasi ({q_col}): {e}")
                    corr = 0
                    p_value = 1.0

                if np.isnan(corr):
                    corr = 0

                # ESIK DEGERI: 0.25 ustundeki iliski anlamlidir ve p-value < 0.05
                if abs(corr) > 0.25 and p_value < 0.05:
                    # Pozitif iliski: Evet diyen yuksek skor alir -> Anahtar 'Evet'
                    # Negatif iliski: Hayir diyen yuksek skor alir -> Anahtar 'Hayir'
                    key_val = 'Evet' if corr > 0 else 'Hayir'
                    original_q_id = q_col.replace('Q_', '')
                    scale_keys[original_q_id] = {
                        'answer': key_val,
                        'correlation': round(corr, 3),
                        'p_value': round(p_value, 3)
                    }
                    valid_correlations += 1

            discovered_keys[scale] = scale_keys
            print(f"   {valid_correlations} adet ayirt edici soru bulundu. Toplam soru sayisi: {len(question_cols)}")

        # 4. Anahtarlari Dosyaya Kaydet
        if discovered_keys:
            output_file = 'generated_keys.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(discovered_keys, f, indent=4, ensure_ascii=False)

            print(f"ISLEM TAMAM! '{output_file}' dosyasi olusturuldu.")
            print("Artik sistem bu dosyayi kullanarak gercek tahminler yapabilir.")

            # Olusturulan dosyanin icerigini ozetle
            print("Olusturulan anahtarlar:")
            for scale, keys in discovered_keys.items():
                print(f"   {scale}: {len(keys)} anahtar")
        else:
            print("Anlamsiz korelasyon bulunamadi. Anahtar dosyasi olusturulmadi.")

if __name__ == "__main__":
    try:
        generate_scoring_keys()
    except Exception as e:
        print(f"Hata olustu: {e}")
        import traceback
        traceback.print_exc()