import PyPDF2
import sqlite3
import json

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
    """Metni paragraflara böler ve çok kısa anlamsız parçaları temizler."""
    ham_parcalar = metin.split('\n\n')
    temiz_parcalar = []
    
    for parca in ham_parcalar:
        parca = parca.strip()
        # Sadece 20 karakterden uzun olan (sayfa numarası vb. olmayan) parçaları al
        if len(parca) > 20:
            temiz_parcalar.append(parca)
            
    return temiz_parcalar

def veritabanina_kaydet(parcalar):
    """Parçaları SQLite veritabanına kaydeder."""
    conn = sqlite3.connect('rag_hafiza.db')
    cursor = conn.cursor()

    # Tablo yoksa oluşturuyoruz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')

    eklenen_sayi = 0
    for parca in parcalar:
        # DİKKAT: Şimdilik Foundry Local embedding modelini bağlamadık.
        # Test amaçlı sahte bir vektör ekliyoruz. Sonraki adımda burası gerçek yapay zeka olacak!
        sahte_vektor = json.dumps([0.0, 0.0, 0.0])

        cursor.execute('''
            INSERT INTO documents (content, embedding)
            VALUES (?, ?)
        ''', (parca, sahte_vektor))
        eklenen_sayi += 1

    conn.commit()
    conn.close()
    return eklenen_sayi

if __name__ == "__main__":
    dosya_adi = "staj-kilavuzu.pdf"
    metin = pdf_metnini_cikar(dosya_adi)
    
    if metin:
        # 1. Adım: Metni parçalara böl
        parcalar = metni_parcalara_bol(metin)
        print(f"\nSistem: Metin {len(parcalar)} adet anlamlı parçaya (chunk) bölündü.")
        
        # 2. Adım: Veritabanına kaydet
        kayit_sayisi = veritabanina_kaydet(parcalar)
        print(f"Sistem: {kayit_sayisi} adet parça SQLite veritabanına başarıyla kaydedildi!")