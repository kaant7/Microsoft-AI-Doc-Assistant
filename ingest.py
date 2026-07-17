import os
import sqlite3
import json
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from config import Config

def chunk_text(text, chunk_size, chunk_overlap):
    """Overlapping chunks mantığı: Bilgi kaybını önlemek için kaydırarak keser."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 0:
            chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

def extract_text_from_pdf(pdf_path):
    """PDF dosyasındaki tüm sayfaları okuyup tek bir metin haline getirir."""
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"PDF okuma hatası ({pdf_path}): {e}")
    return text

def run_ingest():
    print("Sistem: Embedding modeli yükleniyor...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, embedding TEXT)''')
    cursor.execute('DELETE FROM documents')
    
    # docs/ klasörü yoksa oluştur
    if not os.path.exists(Config.DOCS_DIR):
        os.makedirs(Config.DOCS_DIR)
        print(f"\nSistem: '{Config.DOCS_DIR}' adında bir klasör oluşturdum.")
        print("Lütfen kaynak PDF veya TXT belgelerinizi bu klasöre koyup kodu tekrar çalıştırın.")
        return

    total_chunks = 0
    # docs klasöründeki tüm PDF ve TXT dosyalarını tara
    for filename in os.listdir(Config.DOCS_DIR):
        filepath = os.path.join(Config.DOCS_DIR, filename)
        text = ""
        
        if filename.lower().endswith(".pdf"):
            print(f"Okunuyor: {filename} (PDF)")
            text = extract_text_from_pdf(filepath)
        elif filename.lower().endswith((".txt", ".md")):
            print(f"Okunuyor: {filename} (Metin)")
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
        if text:
            chunks = chunk_text(text, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
            for chunk in chunks:
                vector = embedding_model.encode(chunk).tolist()
                cursor.execute('INSERT INTO documents (content, embedding) VALUES (?, ?)', 
                               (chunk, json.dumps(vector)))
                total_chunks += 1
                
    conn.commit()
    conn.close()
    print(f"\nİşlem Tamamlandı: {total_chunks} veri parçası SQLite veritabanına yazıldı.")

if __name__ == "__main__":
    run_ingest()