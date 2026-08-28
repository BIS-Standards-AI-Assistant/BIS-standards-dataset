# 🏛️ BIS Standards AI Assistant — Dataset & Ingestion Pipeline

> **Smart India Hackathon 2026** | **Problem Statement:** SIH26107  
> **Ministry:** Ministry of Consumer Affairs, Food & Public Distribution  
> **Repository Purpose:** Verified Government Gazette Standards, Vector DB Ingestion, and Evaluation Benchmarks

---

## 📌 Project Overview
This repository serves as the core data layer and knowledge ingestion pipeline for the **BIS Standards AI Assistant**. It provides small enterprises (MSMEs), manufacturers, and consumers with accurate Indian Standards (IS Codes), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, Hallmarking), and key testing parameters—grounded in official Gazette notifications with zero hallucinations.

---

## 📁 Repository File Structure

```text
BIS-standards-dataset/
├── dataset/
│   ├── real_bis_standards.json         # 22+ Verified Gazette QCO standards with metadata
│   └── evaluation_benchmarks.json      # Gold-standard evaluation queries for accuracy & refusal testing
├── scripts/
│   ├── fetch_real_bis_dataset.py       # Script to compile and rebuild the authentic dataset
│   └── ingest_to_vectorstore.py        # ChromaDB vector embedding & metadata indexing pipeline
├── .gitignore                          # Ignores .venv, Python cache, and local vector database files
└── README.md                           # Documentation & quick start guide
```

---

## ⚡ Quick Start for Developers

### 1. Set Up Virtual Environment & Dependencies
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required vector database engine
pip install chromadb
```

### 2. Ingest Dataset into Local ChromaDB
```bash
python scripts/ingest_to_vectorstore.py
```
*Creates a local persistent vector database at `./bis_vector_db/` indexed with cosine distance.*

### 3. Verify Ground-Truth Benchmarks
Run queries against `dataset/evaluation_benchmarks.json` to validate semantic retrieval accuracy and test cosine similarity fallback thresholds for out-of-scope queries.

---

## ✅ Data Verification Status

Every entry in `dataset/real_bis_standards.json` was checked against public BIS
records (product manuals, `archive.org` mirrors of official standards, or
gazette text) and now carries:

- **`verification_status`** — `"verified_accurate"` or `"corrected"`
- **`verification_note`** — what was checked, and for corrected entries, what
  was originally wrong and why

**8 of 22 entries had a factually wrong IS number, edition year, or
part/section** — not just outdated, actually incorrect. Two are worth
remembering specifically:

- `IS 302 (Part 2/Sec 26):2014` was listed for induction cookers, but
  **Section 26 of IS 302 Part 2 is the standard for clocks**, a different
  product entirely. The real induction-cooker standard is
  `IS 302 (Part 2/Sec 6):2009`.
- `IS 4151:2020` was listed for helmets — no such edition exists. The 2020
  belongs to the *regulatory order* that mandates compliance with
  `IS 4151:2015` (Fourth Revision), not to the standard itself.

### `legal_source` fields — only partially verified

The per-entry `legal_source` block (gazette order name, notification number,
issuing ministry, enactment date, portal URL) was added after the last
verification pass and has **not** been fully checked. A 3-entry spot check
found:

- `IS 269:2015` (Cement) — **fully confirmed**, notification number and date
  match the actual gazette order exactly.
- `IS 4151:2015` (Helmets) and `IS 1417:2016` (Gold Hallmarking) — the
  notification numbers look right, but `enactment_date` conflates the order's
  *gazette publication date* with its later *phased-rollout / enforcement
  date* — these are different things and matter if this data is ever used to
  tell someone when a requirement actually took legal effect.

Every entry now carries `legal_source_verified: true/false`; only the 3
spot-checked entries are `true`, each with a `legal_source_verification_note`
explaining exactly what was confirmed. **Treat every `legal_source` block
with `legal_source_verified: false` as unconfirmed** — do not present those
notification numbers or dates as fact without checking them against the
actual Gazette of India text first.
