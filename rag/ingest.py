import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_BASE_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "rubrics.json")
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")

MODEL_NAME = "all-MiniLM-L6-v2"


def load_rubric_chunks():
    with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
        rules = json.load(f)

    all_chunks = []
    for rule in rules:
        rule_id = rule["rule_id"]
        base_metadata = {
            "rule_id": rule_id,
            "category": rule.get("category", ""),
            "severity": rule.get("severity", ""),
            "source": rule.get("source", ""),
            "analyzer_check": rule.get("analyzer_check", ""),
        }

        for section_name, section_text in rule["chunks"].items():
            chunk_metadata = dict(base_metadata)
            chunk_metadata["section"] = section_name
            all_chunks.append({
                "id": f"{rule_id}::{section_name}",
                "text": section_text,
                "metadata": chunk_metadata,
            })

        print(f"  {rule_id}: {len(rule['chunks'])} chunks")

    return all_chunks


def ingest():
    print("Loading rubric JSON...")
    chunks = load_rubric_chunks()
    print(f"Total chunks to embed: {len(chunks)}")

    print(f"Loading embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Connecting to ChromaDB (local, persistent)...")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    existing_collections = [c.name for c in client.list_collections()]
    if "pedagogical_rubrics" in existing_collections:
        client.delete_collection(name="pedagogical_rubrics")

    collection = client.get_or_create_collection(name="pedagogical_rubrics")

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    print("Generating embeddings...")
    embeddings = model.encode(documents).tolist()

    print("Storing in ChromaDB...")
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Done. {len(ids)} chunks embedded and stored in '{CHROMA_DB_DIR}'.")


if __name__ == "__main__":
    ingest()