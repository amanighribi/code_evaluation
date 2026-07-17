import os
import chromadb

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")

client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = client.get_or_create_collection(name="pedagogical_rubrics")

results = collection.get(
    where={"rule_id": "missing_docstring"},
)

for doc_id, metadata, document in zip(results["ids"], results["metadatas"], results["documents"]):
    print(f"\n[{metadata['section']}]")
    print(document[:150] + "...")