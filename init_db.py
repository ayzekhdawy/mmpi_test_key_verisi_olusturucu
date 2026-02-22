from app import app
from models import db

def initialize_database():
    with app.app_context():
        db.create_all()
        print("Veritabanı tabloları başarıyla oluşturuldu.")

if __name__ == "__main__":
    initialize_database()