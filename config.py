class Config:
    MODEL_NAME = "phi-3.5-mini"
    DOCS_DIR = "docs"
    DB_PATH = "rag.db"
    
    # leestott projesinin standart değerleri
    CHUNK_SIZE = 100     # Her parçadaki kelime sayısı
    CHUNK_OVERLAP = 25   # Parçalar arası bağlam kopmasın diye ortak kelime sayısı
    TOP_K = 3            # Soruya en çok benzeyen kaç parçanın LLM'e gideceği