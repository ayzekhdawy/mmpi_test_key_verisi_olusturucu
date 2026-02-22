from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, UserData
import pandas as pd
import json
import os
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_buraya_degistirilmeli' # Production'da değiştirilmeli
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gercek_veri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- REFERANS TESTİ (GROUND TRUTH) ---
# Bu sorular bilimsel olarak neyi ölçtüğü bilinen kısa sorulardır.
# Senin 566 soruluk testin bu soruları referans alarak kendini eğitecek.
REFERANS_SORULAR = [
    # DEPRESYON REFERANSI (Örn: PHQ-9 Mantığı)
    {'id': 'ref_d1', 'text': 'Son iki haftadır kendinizi çökkün veya umutsuz hissediyor musunuz?', 'scale': 'Depresyon'},
    {'id': 'ref_d2', 'text': 'Hayattan zevk alma veya ilgi duyma konusunda azalma var mı?', 'scale': 'Depresyon'},
    {'id': 'ref_d3', 'text': 'Uykuya dalmakta zorlanıyor veya çok fazla mı uyuyorsunuz?', 'scale': 'Depresyon'},

    # PARANOYA REFERANSI
    {'id': 'ref_p1', 'text': 'İnsanların çoğunun güvenilmez olduğunu düşünür müsünüz?', 'scale': 'Paranoya'},
    {'id': 'ref_p2', 'text': 'Başkalarının sizi kullandığını veya izlediğini hissettiğiniz olur mu?', 'scale': 'Paranoya'},

    # ANKSİYETE (KAYGI) REFERANSI
    {'id': 'ref_a1', 'text': 'Sürekli diken üstünde veya gergin hissediyor musunuz?', 'scale': 'Anksiyete'},
    {'id': 'ref_a2', 'text': 'Endişelenmeyi durduramadığınız oluyor mu?', 'scale': 'Anksiyete'}
]

with app.app_context():
    try:
        db.create_all()
        logger.info("Veritabanı tabloları oluşturuldu veya zaten mevcut.")
    except Exception as e:
        logger.error(f"Veritabanı oluşturma hatası: {e}")

def get_mmpi_questions():
    try:
        df = pd.read_csv('mmpi_sorular.csv', encoding='utf-8')
        questions = df[['Question #', 'Question']].to_dict(orient='records')
        logger.info(f"{len(questions)} MMPI sorusu yüklendi.")
        return questions
    except FileNotFoundError:
        logger.error("mmpi_sorular.csv dosyası bulunamadı.")
        return []
    except Exception as e:
        logger.error(f"MMPI soruları yüklenirken hata oluştu: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-mmpi')
def test_mmpi():
    # 1. Aşama: 566 Soru
    questions = get_mmpi_questions()

    if not questions:
        return "<h1>Hata: Sorular yüklenemedi</h1><p>Lütfen sistem yöneticisiyle iletişime geçin.</p>", 500

    return render_template('test_mmpi.html', questions=questions, total=len(questions))

@app.route('/submit-mmpi', methods=['POST'])
def submit_mmpi():
    try:
        # MMPI cevaplarını geçici olarak session'a kaydet (henüz veritabanına değil)
        answers = request.form.to_dict()

        # Cevapların doğruluğunu kontrol et
        if not answers:
            logger.warning("Boş cevaplar alındı.")
            return redirect(url_for('test_mmpi'))

        session['mmpi_answers'] = json.dumps(answers)
        logger.info(f"MMPI cevapları session'a kaydedildi. Cevap sayısı: {len(answers)}")
        return redirect(url_for('calibration_test'))
    except Exception as e:
        logger.error(f"MMPI cevapları kaydedilirken hata oluştu: {e}")
        return "<h1>Hata: Cevaplar işlenirken bir sorun oluştu</h1>", 500

@app.route('/calibration')
def calibration_test():
    # 2. Aşama: Referans Testi
    return render_template('test_calibration.html', questions=REFERANS_SORULAR)

@app.route('/submit-final', methods=['POST'])
def submit_final():
    try:
        if 'mmpi_answers' not in session:
            logger.warning("Session'da MMPI cevapları bulunamadı.")
            return redirect(url_for('index'))

        # Referans Testi Cevaplarını Al (0-3 arası puanlama gibi düşünelim: Hayır=0, Evet=1)
        ref_answers = request.form.to_dict()
        logger.info(f"Referans testi cevapları alındı. Cevap sayısı: {len(ref_answers)}")

        # Referans Skorlarını Hesapla (Kullanıcıya sonuç göstermek için)
        scores = {'Depresyon': 0, 'Paranoya': 0, 'Anksiyete': 0}

        for q in REFERANS_SORULAR:
            ans = ref_answers.get(q['id'])
            if ans == 'Evet':
                scores[q['scale']] += 1

        logger.info(f"Hesaplanan skorlar: {scores}")

        # --- VERİTABANINA KAYIT (ALTIN DEĞERİNDEKİ KISIM) ---
        new_entry = UserData(
            mmpi_answers=session['mmpi_answers'],
            reference_scores=json.dumps(scores) # Gerçek tanıyı kaydediyoruz
        )

        db.session.add(new_entry)
        db.session.commit()

        logger.info("Kullanıcı verileri veritabanına kaydedildi.")

        # Session'ı temizle
        session.pop('mmpi_answers', None)

        return render_template('result_real.html', scores=scores)
    except Exception as e:
        logger.error(f"Veritabanı kaydı sırasında hata oluştu: {e}")
        db.session.rollback()
        return "<h1>Hata: Veriler kaydedilirken bir sorun oluştu</h1>", 500

# Sağlık kontrolü endpoint'i
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "MMPI Turkey",
        "timestamp": pd.Timestamp.now().isoformat()
    })

# Sistem istatistikleri endpoint'i
@app.route('/stats')
def stats():
    try:
        with app.app_context():
            user_count = UserData.query.count()
            return jsonify({
                "user_count": user_count,
                "ai_trained": os.path.exists('generated_keys.json'),
                "status": "operational"
            })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "degraded"
        }), 500

if __name__ == '__main__':
    app.run(debug=False)