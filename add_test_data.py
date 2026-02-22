from app import app
from models import db, UserData
import json
import random

def add_test_data():
    with app.app_context():
        # 15 test verisi ekle
        for user_num in range(15):
            # Test verisi oluştur
            test_mmpi_answers = {}
            for i in range(1, 567):  # 566 soru
                # Rastgele evet/hayır dağıtımı
                test_mmpi_answers[str(i)] = 'Evet' if random.random() > 0.5 else 'Hayır'

            # Referans skorları rastgele oluştur (0-3 arası)
            test_reference_scores = {
                'Depresyon': random.randint(0, 3),
                'Paranoya': random.randint(0, 3),
                'Anksiyete': random.randint(0, 3)
            }

            # Veritabanına ekle
            new_user = UserData(
                mmpi_answers=json.dumps(test_mmpi_answers),
                reference_scores=json.dumps(test_reference_scores)
            )
            db.session.add(new_user)

        db.session.commit()
        print("15 adet test verisi başarıyla eklendi.")

if __name__ == "__main__":
    add_test_data()