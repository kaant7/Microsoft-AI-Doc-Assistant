class Config:
    MODEL_NAME = "phi-3.5-mini"
    DOCS_DIR = "docs"
    DB_PATH = "rag.db"

    CHUNK_SIZE = 200     # Word count per chunk
    CHUNK_OVERLAP = 25   # Shared word count between chunks so context doesn't break
    TOP_K = 3            # How many of the most relevant chunks go to the LLM

    MAX_TOKENS = 300     # Max tokens the model can generate in a single reply
    TEMPERATURE = 0.2    # Low temperature: stay grounded in the docs, fewer "hallucinated" answers