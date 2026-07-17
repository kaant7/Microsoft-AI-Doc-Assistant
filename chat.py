import sqlite3
import json
import numpy as np
from config import Config
from sentence_transformers import SentenceTransformer
from foundry_local_sdk import Configuration, FoundryLocalManager

print("Sistem: Arama motoru ayağa kaldırılıyor...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def retrieve_context(query, top_k):
    query_vector = embedding_model.encode(query).tolist()
    
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT content, embedding FROM documents')
    records = cursor.fetchall()
    conn.close()
    
    results = []
    for record in records:
        content = record[0]
        record_vector = json.loads(record[1])
        score = cosine_similarity(query_vector, record_vector)
        results.append((score, content))
        
    # En yüksek skorlu Top K kadar parçayı al ve birleştir
    results.sort(key=lambda x: x[0], reverse=True)
    best_chunks = [res[1] for res in results[:top_k]]
    return "\n---\n".join(best_chunks)

def start_chat():
    # Foundry Local entegrasyonu
    config = Configuration(app_name="local_rag_app")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    
    print("\nSistem: Phi-3.5-mini hazırlanıyor...")
    model = manager.catalog.get_model(Config.MODEL_NAME)
    model.download(lambda p: None) # İndirme çubuğunu gizledik
    model.load()
    client = model.get_chat_client()
    
    # Github projesiyle uyumlu sistem komutu
    system_prompt = (
        "You are an offline support agent. Rules:\n"
        "- Only answer using the retrieved context.\n"
        "- If the answer isn't in the context, say so.\n"
        "- Respond in the language of the user's prompt."
    )
    
    print("\n--- YAPAY ZEKA ASİSTANI HAZIR ---")
    print("(Uygulamadan çıkmak için 'quit' veya 'exit' yazabilirsiniz)")
    
    while True:
        user_query = input("\nSen: ").strip()
        if user_query.lower() in ['quit', 'exit']:
            print("Görüşmek üzere!")
            break
            
        context = retrieve_context(user_query, Config.TOP_K)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}\nAnswer:"}
        ]
        
        print("Asistan: ", end="", flush=True)
        try:
            for chunk in client.complete_streaming_chat(messages):
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content or ""
                    print(content, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nModel üretim hatası: {e}")
            
    # Döngü kırıldığında (quit yazıldığında) modeli bellekten at
    model.unload()

if __name__ == "__main__":
    start_chat()