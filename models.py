from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # MMPI 566 Cevapları (Öğrenilecek Veri) - JSON String olarak tutulur
    mmpi_answers = db.Column(db.Text, nullable=False)

    # Kalibrasyon Testi Sonuçları (Referans Gerçek / Ground Truth)
    # Örn: {'depresyon_skoru': 8, 'paranoya_skoru': 2}
    reference_scores = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'

    def to_dict(self):
        """Modeli sözlük formatına çevirir"""
        return {
            'id': self.id,
            'mmpi_answers': self.mmpi_answers,
            'reference_scores': self.reference_scores
        }

    @classmethod
    def from_dict(cls, data):
        """Sözlükten model oluşturur"""
        return cls(
            mmpi_answers=data.get('mmpi_answers'),
            reference_scores=data.get('reference_scores')
        )