#!/usr/bin/env python3
"""
scripts/ingest_to_vectorstore.py

Ingestion pipeline for SIH 2026 Problem Statement SIH26107:
AI-Powered BIS Standards Assistant.

Loads the 50 verified Indian Standards from data/bis_standards_dataset.json,
constructs rich semantic compliance chunks, and embeds them into ChromaDB 
with deterministic metadata filtering support.
"""

import json
import os
import sys
from typing import List, Dict, Any

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Error: chromadb is not installed. Run: pip install chromadb sentence-transformers")
    sys.exit(1)


DATASET_PATH = "dataset/real_bis_standards.json"
CHROMA_PERSIST_DIR = "vectorstore/chroma_db"
COLLECTION_NAME = "bis_standards_collection"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_dataset(filepath: str) -> List[Dict[str, Any]]:
    """Loads the consolidated BIS JSON dataset."""
    if not os.path.exists(filepath):
        print(f"Dataset file not found at {filepath}. Running fetch script fallback...")
        try:
            from scripts.fetch_real_bis_dataset import export_dataset
            export_dataset(filepath)
        except ImportError:
            raise FileNotFoundError(f"Could not find {filepath} and fetch script is unavailable.")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} standards from {filepath}")
    return data


def format_document_chunk(item: Dict[str, Any]) -> str:
    """
    Constructs an information-dense semantic document string for dense vector indexing.
    Structured to optimize cosine similarity for natural language queries from MSMEs.
    """
    std_num = item.get("standard_number", "")
    part = f" ({item['part']})" if item.get("part") else ""
    sec = f" {item['section']}" if item.get("section") else ""
    full_standard_code = f"{std_num}{part}{sec}:{item.get('year', '')}"
    
    testing_bullets = "\n".join([f"- {test}" for test in item.get("key_testing_parameters", [])])
    materials_list = ", ".join(item.get("materials", []))
    keywords_list = ", ".join(item.get("keywords", []))
    legal = item.get("legal_source", {})
    
    chunk = (
        f"Indian Standard: {full_standard_code}\n"
        f"Product Title: {item.get('full_title', '')}\n"
        f"Common Product Name: {item.get('short_title', '')}\n"
        f"Category: {item.get('product_category', '')} | Industry: {item.get('industry', '')}\n"
        f"Certification Scheme: {item.get('scheme', '')}\n"
        f"Certification Route: {item.get('certification_route', '')}\n"
        f"Mandatory QCO Status: {'Mandatory' if item.get('mandatory_qco') else 'Voluntary'}\n"
        f"Legal Status: {item.get('status', '')}\n"
        f"Regulatory Authority: {legal.get('issuing_ministry', '')}\n"
        f"Gazette Order: {legal.get('gazette_order', '')} ({legal.get('notification_number', '')})\n"
        f"Enactment Date: {legal.get('enactment_date', '')}\n"
        f"Scope of Standard:\n{item.get('scope', '')}\n"
        f"Mandatory Key Testing Parameters:\n{testing_bullets}\n"
        f"Applicable Materials & Components: {materials_list}\n"
        f"Search Keywords & Aliases: {keywords_list}"
    )
    return chunk


def build_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts flat, filterable metadata fields compatible with ChromaDB constraints.
    """
    legal = item.get("legal_source", {})
    return {
        "standard_id": str(item.get("standard_id", "")),
        "standard_number": str(item.get("standard_number", "")),
        "year": str(item.get("year", "")),
        "short_title": str(item.get("short_title", "")),
        "product_category": str(item.get("product_category", "")),
        "industry": str(item.get("industry", "")),
        "scheme": str(item.get("scheme", "")),
        "mandatory_qco": bool(item.get("mandatory_qco", False)),
        "status": str(item.get("status", "")),
        "issuing_ministry": str(legal.get("issuing_ministry", "")),
        "gazette_order": str(legal.get("gazette_order", "")),
        "notification_number": str(legal.get("notification_number", "")),
        "document_url": str(item.get("document_url", "")),
        "verification_status": str(item.get("verification_status", "verified_accurate"))
    }


def ingest():
    """Initializes ChromaDB vector store, embeds data chunks, and creates the collection."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    dataset = load_dataset(DATASET_PATH)

    print(f"Initializing persistent ChromaDB client at: {CHROMA_PERSIST_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )

    # Recreate collection to ensure clean state
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Removed existing collection: {COLLECTION_NAME}")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "BIS Indian Standards & QCOs Vector Index for SIH 2026"}
    )

    ids = []
    documents = []
    metadatas = []

    print("Building document embeddings and metadata chunks...")
    for item in dataset:
        doc_id = item["standard_id"]
        doc_text = format_document_chunk(item)
        doc_meta = build_metadata(item)

        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append(doc_meta)

    # Ingest in batches of 25
    batch_size = 25
    total_docs = len(ids)
    for i in range(0, total_docs, batch_size):
        end_idx = min(i + batch_size, total_docs)
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        print(f"Ingested batch {i + 1} - {end_idx} of {total_docs} standards.")

    print(f"\nIngestion Complete: {collection.count()} verified BIS standards successfully indexed in ChromaDB.")


def run_sanity_query(query: str = "What tests are required for domestic pressure cookers?"):
    """Validates vector store retrieval accuracy."""
    print(f"\n--- Running Sanity Query: '{query}' ---")
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)

    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    for idx, (doc_id, dist, meta) in enumerate(zip(results["ids"][0], results["distances"][0], results["metadatas"][0])):
        print(f"\nResult {idx + 1} [Score Distance: {dist:.4f}]:")
        print(f"Standard ID : {doc_id}")
        print(f"Standard No : {meta.get('standard_number')}")
        print(f"Title       : {meta.get('short_title')}")
        print(f"Scheme      : {meta.get('scheme')}")
        print(f"QCO Status  : {'Mandatory' if meta.get('mandatory_qco') else 'Voluntary'}")


if __name__ == "__main__":
    ingest()
    run_sanity_query()