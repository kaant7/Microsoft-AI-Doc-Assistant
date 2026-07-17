class Config:
    MODEL_NAME = "phi-3.5-mini"
    DOCS_DIR = "docs"
    DB_PATH = "rag.db"
    
    CHUNK_SIZE = 200     # Her parçadaki kelime sayısı #200
    CHUNK_OVERLAP = 25   # Parçalar arası bağlam kopmasın diye ortak kelime sayısı #25
    TOP_K = 1            # Soruya en çok benzeyen kaç parçanın LLM'e gideceği #3