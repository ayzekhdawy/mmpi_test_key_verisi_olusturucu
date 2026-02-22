import random

class MMPIEngine:
    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode

        # --- KLİNİK ÖLÇEKLER VE YORUMLARI ---
        # Bu veriler yüklediğin PDF'lerin analizinden derlenmiştir.
        self.scales = {
            'L': {
                'name': 'L (Yalan) Ölçeği',
                'question_ids': [], # GÖREV Gerçek soru numaralarını buraya gir (Örn [15, 30, 45...])
                'desc_high': 'Kişi kendini olduğundan iyi göstermeye çalışmış (Sahte İyi). Sonuçlar şüpheli.',
                'desc_normal': 'Samimi ve açık sözlü yaklaşım.',
                'threshold': 7
            },
            'F': {
                'name': 'F (Sıklık) Ölçeği',
                'question_ids': [],
                'desc_high': 'Yardım çağrısı veya abartılı sıkıntı ifadesi. Kişi zor bir dönemden geçiyor olabilir.',
                'desc_normal': 'Uyumlu ve rasyonel cevaplar.',
                'threshold': 15
            },
            'K': {
                'name': 'K (Savunma) Ölçeği',
                'question_ids': [],
                'desc_high': 'Savunmacı tutum, zayıflıkları gizleme ve inkar eğilimi.',
                'desc_normal': 'Ruhsal kaynaklar dengeli.',
                'threshold': 18
            },
            '1-Hs': {
                'name': 'Hipokondriazis',
                'question_ids': [],
                'desc_high': 'Bedensel işlevlerle aşırı uğraş, sürekli hastalık şikayetleri, bencil ve talepkar tutum.',
                'desc_normal': 'Bedensel kaygı düzeyi normal.',
                'threshold': 19
            },
            '2-D': {
                'name': 'Depresyon',
                'question_ids': [],
                'desc_high': 'Mutsuzluk, umutsuzluk, enerji düşüklüğü ve değersizlik hisleri.',
                'desc_normal': 'Duygudurum dengeli, yaşama ilgili.',
                'threshold': 24
            },
            '3-Hy': {
                'name': 'Histeri',
                'question_ids': [],
                'desc_high': 'Stres altında bedensel tepkiler verme, ilgi beklentisi ve duygusal sığlık.',
                'desc_normal': 'Sosyal ilişkilerde uyumlu.',
                'threshold': 24
            },
            '4-Pd': {
                'name': 'Psikopatik Sapma',
                'question_ids': [],
                'desc_high': 'Toplumsal kurallara uyumsuzluk, dürtüsellik, öfke ve otorite sorunları.',
                'desc_normal': 'Kurallara saygılı ve uyumlu.',
                'threshold': 24
            },
            '6-Pa': {
                'name': 'Paranoya',
                'question_ids': [],
                'desc_high': 'Aşırı şüphecilik, alınganlık, başkalarına güvenmeme.',
                'desc_normal': 'İnsanlara güvenen yaklaşım.',
                'threshold': 15
            },
            '7-Pt': {
                'name': 'Psikasteni (Takıntı)',
                'question_ids': [],
                'desc_high': 'Takıntılı düşünceler, anksiyete, korkular ve kararsızlık.',
                'desc_normal': 'Organize ve planlı yapı.',
                'threshold': 25
            },
            '8-Sc': {
                'name': 'Şizofreni',
                'question_ids': [],
                'desc_high': 'Gerçeklikten kopuk düşünceler, tuhaf algılar, sosyal izolasyon.',
                'desc_normal': 'Mantıklı düşünme yetisi.',
                'threshold': 25
            },
            '9-Ma': {
                'name': 'Hipomani',
                'question_ids': [],
                'desc_high': 'Aşırı enerji, düşünce uçuşması, dürtüsel davranışlar.',
                'desc_normal': 'Enerji düzeyi amaca yönelik.',
                'threshold': 20
            },
            '0-Si': {
                'name': 'Sosyal İçe Dönüklük',
                'question_ids': [],
                'desc_high': 'İnsanlardan uzak durma isteği, utangaçlık ve içe kapanıklık.',
                'desc_normal': 'Sosyal ve dışa dönük.',
                'threshold': 25
            }
        }

    def calculate_scores(self, user_answers_dict):
        """
        Kullanıcı cevaplarını alır (Dict {'1': 'Evet', '2': 'Hayır'...})
        ve sonuçları hesaplar.
        """
        results = {}

        for code, scale in self.scales.items():
            raw_score = 0

            # 1. Gerçek Hesaplama
            if not self.demo_mode and scale['question_ids']:
                for q_id in scale['question_ids']:
                    # CSV'deki soru numaraları string gelebilir, int'e çeviriyoruz
                    ans = user_answers_dict.get(str(q_id))
                    # NOT Normalde hangi cevabın puan getirdiği de bilinmelidir.
                    # Şimdilik varsayılan olarak 'Evet' puan getirir mantığıyla yazıldı.
                    if ans == 'Evet':
                        raw_score += 1

            # 2. Demo Modu (Pazarlama için Rastgele Veri)
            elif self.demo_mode:
                # Rastgele ama mantıklı sınırlar içinde puan üret
                raw_score = random.randint(10, 35)

            # Durum Belirleme
            status = 'Normal'
            interpretation = scale['desc_normal']
            is_high = False

            if raw_score >= scale['threshold']:
                status = 'YÜKSEK'
                interpretation = scale['desc_high']
                is_high = True

            results[code] = {
                'name': scale['name'],
                'score': raw_score,
                'status': status,
                'desc': interpretation,
                'is_high': is_high
            }

        return results