import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer

print("Embedding modeli yükleniyor...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def kosinus_benzerligi(vektor1, vektor2):
    """İki vektör arasındaki matematiksel benzerliği (Cosine Similarity) hesaplar."""
    v1 = np.array(vektor1)
    v2 = np.array(vektor2)
    # Formül: v1 • v2 / (|v1| * |v2|)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def veritabaninda_ara(kullanici_sorusu, getirecek_parca_sayisi=1):
    """Soruyu vektöre çevirir ve veritabanındaki en alakalı metinleri bulur."""
    
    # 1. Kullanıcının sorusunu aynı modelle vektöre dönüştür
    soru_vektoru = embedding_model.encode(kullanici_sorusu).tolist()
    
    # 2. Veritabanına bağlan ve tüm kayıtları çek
    conn = sqlite3.connect('rag_hafiza.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, content, embedding FROM documents')
    kayitlar = cursor.fetchall()
    conn.close()
    
    sonuclar = []
    
    # 3. Her bir staj kılavuzu parçası ile sorunun benzerliğini ölç
    for kayit in kayitlar:
        kayit_id = kayit[0]
        metin = kayit[1]
        
        # Veritabanındaki metin (JSON) formatındaki vektörü tekrar diziye çevir
        kayit_vektoru = json.loads(kayit[2]) 
        
        # Benzerlik skorunu hesapla (1.0'a ne kadar yakınsa o kadar benzer)
        skor = kosinus_benzerligi(soru_vektoru, kayit_vektoru)
        sonuclar.append({"id": kayit_id, "metin": metin, "skor": skor})
        
    # 4. Skorlara göre büyükten küçüğe sırala
    sonuclar = sorted(sonuclar, key=lambda x: x["skor"], reverse=True)
    
    # En iyi sonucu döndür
    return sonuclar[:getirecek_parca_sayisi]

# Sistemi Test Etme Alanı
if __name__ == "__main__":
    # Sisteme staj kuralları ile ilgili spesifik bir soru soruyoruz
    test_sorusu = "Staj defteri ve raporları en son hangi aya kadar teslim edilmelidir?"
    print(f"\nSoru: '{test_sorusu}'\n")
    
    # Fonksiyonu çalıştır ve en iyi 1 metni getir
    bulunan_parcalar = veritabaninda_ara(test_sorusu, getirecek_parca_sayisi=1)
    
    print("--- YAPAY ZEKA TARAFINDAN BULUNAN EN ALAKALI KILAVUZ METNİ ---")
    for i, sonuc in enumerate(bulunan_parcalar):
        print(f"\nBenzerlik Skoru: {sonuc['skor']:.4f}")
        print("Metin İçeriği:")
        print(sonuc["metin"])