import PyPDF2

def pdf_metnini_cikar(pdf_yolu):
    print(f"[{pdf_yolu}] dosyası okunuyor...")
    cikartilan_metin = ""
    
    try:
        # Dosyayı ikili (binary) okuma modunda açıyoruz
        with open(pdf_yolu, 'rb') as dosya:
            pdf_okuyucu = PyPDF2.PdfReader(dosya)
            toplam_sayfa = len(pdf_okuyucu.pages)
            
            print(f"Sistem: Toplam {toplam_sayfa} sayfa bulundu. Metin ayıklanıyor...\n")
            
            for sayfa_no in range(toplam_sayfa):
                sayfa = pdf_okuyucu.pages[sayfa_no]
                # Her sayfanın metnini al ve aralarına boşluk koyarak birleştir
                cikartilan_metin += sayfa.extract_text() + "\n\n"
                
        return cikartilan_metin
        
    except FileNotFoundError:
        print(f"HATA: '{pdf_yolu}' dosyası bulunamadı. PDF ile Python dosyasının aynı klasörde olduğundan emin ol!")
        return None

# Sadece bu dosya çalıştırıldığında aşağıdaki test kodunu çalıştır
if __name__ == "__main__":
    dosya_adi = "staj-kilavuzu.pdf"
    
    # Fonksiyonumuzu çağırıyoruz
    saf_metin = pdf_metnini_cikar(dosya_adi)
    
    if saf_metin:
        print("--- Çıkarılan Metnin İlk 500 Karakteri ---")
        print(saf_metin[:500])
        print("------------------------------------------")
        print("İşlem Başarılı: Veri seti sisteme aktarılmaya hazır!")