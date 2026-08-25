import json
import os
import chromadb
from chromadb.utils import embedding_functions

def run_indexing():
    print("🚀 Starting vector database ingestion...")

    db_path = "./bis_vector_db"
    client = chromadb.PersistentClient(path=db_path)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(name="bis_standards", embedding_function=emb_fn)

    data_path = "dataset/real_bis_standards.json"
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found! Run 'python scripts/fetch_real_bis_dataset.py' first.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        standards = json.load(f)

    docs, metadatas, ids = [], [], []
    for idx, item in enumerate(standards):
        text_chunk = (
            f"Standard: {item['is_number']}. Title: {item['title']}. "
            f"Category: {item['category']}. Scheme: {item['scheme']}. "
            f"Scope: {item['scope_summary']}. Testing: {', '.join(item['key_testing_parameters'])}."
        )
        docs.append(text_chunk)
        metadatas.append({
            "is_number": item["is_number"],
            "title": item["title"],
            "scheme": item["scheme"],
            "citation": item.get("certification_route", "BIS Official Gazette")
        })
        ids.append(f"is_doc_{idx}")

    collection.add(documents=docs, metadatas=metadatas, ids=ids)
    print(f"✅ Successfully indexed {len(docs)} official standards into Vector DB at '{db_path}'!")

if __name__ == "__main__":
    run_indexing()