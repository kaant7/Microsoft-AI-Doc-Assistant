import PyPDF2
import sqlite3
import json
from sentence_transformers import SentenceTransformer

# Model ilk çalışmada indirilir, sonrasında tamamen çevrimdışı ve yerel çalışır
print("Embedding modeli yükleniyor...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model başarıyla yüklendi!\n")

def pdf_metnini_cikar(pdf_yolu):
    print(f"[{pdf_yolu}] dosyası okunuyor...")
    cikartilan_metin = ""
    try:
        with open(pdf_yolu, 'rb') as dosya:
            pdf_okuyucu = PyPDF2.PdfReader(dosya)
            for sayfa_no in range(len(pdf_okuyucu.pages)):
                sayfa = pdf_okuyucu.pages[sayfa_no]
                cikartilan_metin += sayfa.extract_text() + "\n\n"
        return cikartilan_metin
    except FileNotFoundError:
        print(f"HATA: '{pdf_yolu}' dosyası bulunamadı!")
        return None

def metni_parcalara_bol(metin):
    ham_parcalar = metin.split('\n\n')
    temiz_parcalar = []
    for parca in ham_parcalar:
        parca = parca.strip()
        if len(parca) > 20:
            temiz_parcalar.append(parca)
    return temiz_parcalar

def veritabanina_kaydet(parcalar):
    conn = sqlite3.connect('rag_hafiza.db')
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

    eklenen_sayi = 0
    for parca in parcalar:
        # magic part: metni al, modele ver, 384 boyutlu vektöre çevir!
        vektor = embedding_model.encode(parca).tolist()
        
        # Bu sayı dizisini SQLite'a yazabilmek için JSON formatına (metne) çeviriyoruz
        vektor_json = json.dumps(vektor)

        cursor.execute('''
            INSERT INTO documents (content, embedding)
            VALUES (?, ?)
        ''', (parca, vektor_json))
        eklenen_sayi += 1

    conn.commit()
    conn.close()
    return eklenen_sayi

if __name__ == "__main__":
    dosya_adi = "staj-kilavuzu.pdf"
    metin = pdf_metnini_cikar(dosya_adi)
    
    if metin:
        parcalar = metni_parcalara_bol(metin)
        print(f"Sistem: Metin {len(parcalar)} adet anlamlı parçaya (chunk) bölündü. Vektörlere dönüştürülüyor...")
        
        kayit_sayisi = veritabanina_kaydet(parcalar)
        print(f"\nSistem: {kayit_sayisi} adet parça GERÇEK vektörlerle SQLite'a kaydedildi! İşlem Tamam!")