import PyPDF2
import sqlite3
import json
from sentence_transformers import SentenceTransformer

# Model ilk çalışmada indirilir, sonrasında tamamen çevrimdışı ve yerel çalışır
print("Embedding modeli yükleniyor...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model başarıyla yüklendi!\n")

def extract_text_from_pdf(pdf_path):
    print(f"[{pdf_path}] dosyası okunuyor...")
    extracted_text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                extracted_text += page.extract_text() + "\n\n"
        return extracted_text
    except FileNotFoundError:
        print(f"HATA: '{pdf_path}' dosyası bulunamadı!")
        return None

def split_text_into_chunks(text):
    raw_chunks = text.split('\n\n')
    clean_chunks = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if len(chunk) > 20:
            clean_chunks.append(chunk)
    return clean_chunks

def save_to_database(chunks):
    conn = sqlite3.connect('rag_memory.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    
    # Eski sahte verileri temizleyelim ki veritabanımız pırıl pırıl olsun
    cursor.execute('DELETE FROM documents')

    inserted_count = 0
    for chunk in chunks:
        # magic part: metni al, modele ver, 384 boyutlu vektöre çevir!
        embedding = embedding_model.encode(chunk).tolist()
        
        # Bu sayı dizisini SQLite'a yazabilmek için JSON formatına (metne) çeviriyoruz
        embedding_json = json.dumps(embedding)

        cursor.execute('''
            INSERT INTO documents (content, embedding)
            VALUES (?, ?)
        ''', (chunk, embedding_json))
        inserted_count += 1

    conn.commit()
    conn.close()
    return inserted_count

if __name__ == "__main__":
    file_name = "staj-kilavuzu.pdf"
    text = extract_text_from_pdf(file_name)
    
    if text:
        chunks = split_text_into_chunks(text)
        print(f"Sistem: Metin {len(chunks)} adet anlamlı parçaya (chunk) bölündü. Vektörlere dönüştürülüyor...")
        
        record_count = save_to_database(chunks)
        print(f"\nSistem: {record_count} adet parça GERÇEK vektörlerle SQLite'a kaydedildi! İşlem Tamam!")