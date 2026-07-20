import os
import sqlite3
import json
import re
from sentence_transformers import SentenceTransformer
from config import Config

def semantic_chunk_markdown(text):
    chunks = []
    # Split the text on markdown headings (#, ##, ###)
    sections = re.split(r'(?m)^(?=#{1,3} )', text)
    for section in sections:
        section = section.strip()
        # Skip very short or empty sections
        if len(section) > 20:
            chunks.append(section)
    return chunks

def run_ingest():
    print("System: Loading embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Connect to the database and clear out old data
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS documents')
    cursor.execute('''CREATE TABLE documents
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, embedding TEXT, source TEXT)''')

    if not os.path.exists(Config.DOCS_DIR):
        os.makedirs(Config.DOCS_DIR)
        print(f"\nSystem: '{Config.DOCS_DIR}' folder not found, created it.")
        return

    total_chunks = 0
    # Walk every subfolder under docs/ for .md files
    for root, dirs, files in os.walk(Config.DOCS_DIR):
        for filename in files:
            if not filename.lower().endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, Config.DOCS_DIR)
            print(f"Reading: {rel_path} (semantic chunking active)")

            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            chunks = semantic_chunk_markdown(text)
            for chunk in chunks:
                vector = embedding_model.encode(chunk).tolist()
                cursor.execute('INSERT INTO documents (content, embedding, source) VALUES (?, ?, ?)',
                               (chunk, json.dumps(vector), rel_path))
                total_chunks += 1
                
    conn.commit()
    conn.close()
    print(f"\nDone: {total_chunks} semantic chunks written to the database (rag.db).")

if __name__ == "__main__":
    run_ingest()