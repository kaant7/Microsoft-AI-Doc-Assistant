import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer

print("Embedding modeli yükleniyor...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_cosine_similarity(vector1, vector2):
    """İki vektör arasındaki matematiksel benzerliği (Cosine Similarity) hesaplar."""
    v1 = np.array(vector1)
    v2 = np.array(vector2)
    # Formül: v1 • v2 / (|v1| * |v2|)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def vector_search(user_query, top_k=1):
    """Soruyu vektöre çevirir ve veritabanındaki en alakalı metinleri bulur."""
    
    # 1. Kullanıcının sorusunu aynı modelle vektöre dönüştür
    query_embedding = embedding_model.encode(user_query).tolist()
    
    # 2. Veritabanına bağlan ve tüm kayıtları çek
    conn = sqlite3.connect('rag_memory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, content, embedding FROM documents')
    records = cursor.fetchall()
    conn.close()
    
    results = []
    
    # 3. Her bir staj kılavuzu parçası ile sorunun benzerliğini ölç
    for record in records:
        record_id = record[0]
        content = record[1]
        
        # Veritabanındaki metin (JSON) formatındaki vektörü tekrar diziye çevir
        record_embedding = json.loads(record[2]) 
        
        # Benzerlik skorunu hesapla (1.0'a ne kadar yakınsa o kadar benzer)
        score = calculate_cosine_similarity(query_embedding, record_embedding)
        results.append({"id": record_id, "content": content, "score": score})
        
    # 4. Skorlara göre büyükten küçüğe sırala
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # En iyi sonucu döndür
    return results[:top_k]

# Sistemi Test Etme Alanı
if __name__ == "__main__":
    # Sisteme staj kuralları ile ilgili spesifik bir soru soruyoruz
    test_query = "Staj defteri ve raporları en son hangi aya kadar teslim edilmelidir?"
    print(f"\nSoru: '{test_query}'\n")
    
    # Fonksiyonu çalıştır ve en iyi 1 metni getir
    retrieved_chunks = vector_search(test_query, top_k=1)
    
    print("--- YAPAY ZEKA TARAFINDAN BULUNAN EN ALAKALI KILAVUZ METNİ ---")
    for i, result in enumerate(retrieved_chunks):
        print(f"\nBenzerlik Skoru: {result['score']:.4f}")
        print("Metin İçeriği:")
        print(result["content"])