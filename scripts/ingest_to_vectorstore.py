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

    for item in standards:
        legal_src = item.get("legal_source", {})
        materials_str = ", ".join(item.get("materials", []))
        keywords_str = ", ".join(item.get("keywords", []))
        tests_str = ", ".join(item.get("key_testing_parameters", []))
        part_str = f" Part: {item['part']}" if item.get("part") else ""
        section_str = f" Section: {item['section']}" if item.get("section") else ""

        # Rich text chunk embedded for accurate vector semantic matching
        text_chunk = (
            f"Standard: {item['standard_number']}:{item['year']}{part_str}{section_str} | "
            f"Title: {item['full_title']} ({item['short_title']}) | "
            f"Category: {item['product_category']} | Industry: {item['industry']} | "
            f"Scheme: {item['scheme']} | Route: {item['certification_route']} | "
            f"Status: {item['status']} | Mandatory QCO: {item['mandatory_qco']} | "
            f"Scope: {item['scope']} | Key Tests: {tests_str} | "
            f"Materials: {materials_str} | Keywords: {keywords_str} | "
            f"Gazette Order: {legal_src.get('gazette_order')} | "
            f"Notification No: {legal_src.get('notification_number')} | "
            f"Ministry: {legal_src.get('issuing_ministry')}"
        )

        docs.append(text_chunk)
        
        # Complete metadata attributes for the ML layer's citation engine
        metadatas.append({
            "standard_id": item["standard_id"],
            "standard_number": item["standard_number"],
            "year": str(item["year"]),
            "short_title": item["short_title"],
            "product_category": item["product_category"],
            "industry": item["industry"],
            "scheme": item["scheme"],
            "certification_route": item["certification_route"],
            "mandatory_qco": str(item["mandatory_qco"]),
            "status": item["status"],
            "gazette_order": legal_src.get("gazette_order", "Official Gazette Order"),
            "notification_no": legal_src.get("notification_number", "N/A"),
            "issuing_ministry": legal_src.get("issuing_ministry", "Ministry of Consumer Affairs"),
            "source_url": item.get("source_url", "https://www.bis.gov.in"),
            "document_url": item.get("document_url", "https://www.services.bis.gov.in"),
            "verification_status": item.get("verification_status", "verified_accurate")
        })
        ids.append(item["standard_id"])

    collection.add(documents=docs, metadatas=metadatas, ids=ids)
    print(f"🚀 Ingested all {len(docs)} master standards into ChromaDB at '{db_path}'!")

if __name__ == "__main__":
    run_indexing()