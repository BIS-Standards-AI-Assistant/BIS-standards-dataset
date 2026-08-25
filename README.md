## 🏛️ BIS Standards AI Assistant — Dataset & Ingestion Pipeline

> **Smart India Hackathon 2026** | **Problem Statement:** SIH26107  
> **Ministry:** Ministry of Consumer Affairs, Food & Public Distribution  
> **Repository Purpose:** Verified Government Gazette Standards, Vector DB Ingestion, and Evaluation Benchmarks

---

## 📌 Project Overview
This repository serves as the core data layer and knowledge ingestion pipeline for the **BIS Standards AI Assistant**. It provides small enterprises (MSMEs), manufacturers, and consumers with accurate Indian Standards (IS Codes), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, Hallmarking), and key testing parameters—grounded in official Gazette notifications with zero hallucinations.

---

## 📂 Repository File Structure

```text
BIS-standards-dataset/
│
├── dataset/
│   ├── real_bis_standards.json       # 22+ Verified Gazette QCO standards with complete metadata
│   └── evaluation_benchmarks.json    # Gold-standard evaluation queries for accuracy & refusal testing
│
├── scripts/
│   ├── fetch_real_bis_dataset.py     # Script to compile and rebuild the authentic dataset
│   └── ingest_to_vectorstore.py      # ChromaDB vector embedding & metadata indexing pipeline
│
├── .gitignore                        # Ignores .venv, Python cache, and local vector database files
└── README.md

