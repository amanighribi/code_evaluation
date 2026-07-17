import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = client.get_or_create_collection(name="pedagogical_rubrics")

query_text = "this function has no explanation of what it does"
query_embedding = model.encode([query_text]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=50,  # get ALL chunks, ranked
)

for i, (doc_id, metadata, distance) in enumerate(
    zip(results["ids"][0], results["metadatas"][0], results["distances"][0])
):
    marker = " <-- missing_docstring" if metadata.get("rule_id") == "missing_docstring" else ""
    print(f"{i+1}. {metadata.get('rule_id')} / {metadata.get('section')}  (distance: {distance:.4f}){marker}")