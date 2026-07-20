import os
import sqlite3
import json
import numpy as np
from config import Config
from sentence_transformers import SentenceTransformer
from foundry_local_sdk import Configuration, FoundryLocalManager
from prompts import SYSTEM_PROMPT 

print("System: Starting up the search engine...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def cosine_similarity(v1, v2):
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return np.dot(v1, v2) / (norm_v1 * norm_v2)

def retrieve_context(query, top_k):
    query_vector = embedding_model.encode(query).tolist()

    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT content, embedding, source FROM documents')
    records = cursor.fetchall()
    conn.close()

    results = []
    for record in records:
        content, embedding, source = record
        record_vector = json.loads(embedding)
        score = cosine_similarity(query_vector, record_vector)
        results.append((score, content, source))

    results.sort(key=lambda x: x[0], reverse=True)
    best_chunks = [f"[Source: {source}]\n{content}" for _, content, source in results[:top_k]]
    return "\n---\n".join(best_chunks)

def start_chat():
    config = Configuration(app_name="local_rag_app")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    
    print("\nSystem: Preparing Phi-3.5-mini...")
    model = manager.catalog.get_model(Config.MODEL_NAME)
    model.download(lambda p: None)
    model.load()
    client = model.get_chat_client()
    client.settings.max_tokens = Config.MAX_TOKENS
    client.settings.temperature = Config.TEMPERATURE

    print("\n--- AI ASSISTANT READY ---")
    print("(Type 'quit' or 'exit' to leave the app)")

    while True:
        user_query = input("\nYou: ").strip()
        if user_query.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break

        context = retrieve_context(user_query, Config.TOP_K)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"}
        ]

        print("Assistant:\n", end="", flush=True)
        try:
            for chunk in client.complete_streaming_chat(messages):
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content or ""
                    print(content, end="", flush=True)
            print("\n" + "-"*40)
        except Exception as e:
            print(f"\nModel generation error: {e}")
            
    model.unload()

if __name__ == "__main__":
    start_chat()