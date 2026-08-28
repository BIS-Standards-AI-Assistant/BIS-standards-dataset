import json
import os
import chromadb

def run_indexing():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "dataset", "real_bis_standards.json")
    db_path = os.path.join(base_dir, "bis_vector_db")

    if not os.path.exists(json_path):
        print(f"❌ Error: Dataset file not found at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        standards = json.load(f)

    # Initialize ChromaDB persistent client
    client = chromadb.PersistentClient(path=db_path)
    
    # Reset/recreate collection
    try:
        client.delete_collection(name="bis_standards")
    except Exception:
        pass

    collection = client.create_collection(
        name="bis_standards",
        metadata={"hnsw:space": "cosine"}
    )

    docs = []
    metadatas = []
    ids = []

    for idx, item in enumerate(standards):
        source_info = item.get("legal_source", {})
        tests_str = ", ".join(item.get("key_testing_parameters", []))
        is_mandatory = "Mandatory QCO" if item.get("mandatory_qco", False) else "Voluntary Standard"
        
        # Product title and category with fallbacks
        product_title = item.get("title") or item.get("product_name", "Unknown Product")
        category = item.get("category") or item.get("product_category", "General")
        cert_route = item.get("certification_route", "Standard Verification")
        doc_id = item.get("id") or f"BIS-QCO-{idx+1:03d}"

        # Rich text chunk embedded for vector semantic search
        text_chunk = (
            f"Product: {product_title} | Category: {category} | "
            f"Standard: {item['is_number']} | Scheme: {item['scheme']} | "
            f"Route: {cert_route} | Legal Status: {is_mandatory} | "
            f"Scope: {item['scope_summary']} | Key Tests: {tests_str} | "
            f"Gazette Order: {source_info.get('gazette_order', 'Official BIS Gazette')} | "
            f"Notification: {source_info.get('notification_number', 'N/A')} | "
            f"Ministry: {source_info.get('issuing_ministry', 'Government of India')}"
        )

        docs.append(text_chunk)
        
        # Metadata payload for ML model citation extraction
        metadatas.append({
            "is_number": item["is_number"],
            "title": product_title,
            "category": category,
            "scheme": item["scheme"],
            "certification_route": cert_route,
            "mandatory_qco": str(item.get("mandatory_qco", False)),
            "gazette_order": source_info.get("gazette_order", "Official BIS Notification"),
            "notification_no": source_info.get("notification_number", "N/A"),
            "issuing_ministry": source_info.get("issuing_ministry", "Ministry of Consumer Affairs"),
            "portal_url": source_info.get("portal_url", "https://www.bis.gov.in"),
            # Surfaced so retrieval-time code / prompts can tell an
            # unconfirmed legal_source citation apart from a spot-checked
            # one, instead of presenting both with equal confidence.
            "verification_status": item.get("verification_status", "unverified"),
            "legal_source_verified": str(item.get("legal_source_verified", False)),
        })
        ids.append(doc_id)

    collection.add(documents=docs, metadatas=metadatas, ids=ids)
    unverified_legal = sum(1 for s in standards if not s.get("legal_source_verified", False))
    print(f"Ingested {len(docs)} BIS standards into ChromaDB at '{db_path}'.")
    print(f"Note: {unverified_legal}/{len(docs)} entries have an unverified legal_source block "
          f"(legal_source_verified=false) — see README.md before treating those citations as fact.")

if __name__ == "__main__":
    run_indexing()