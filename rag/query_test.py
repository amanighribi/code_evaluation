import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")
MODEL_NAME = "all-MiniLM-L6-v2"


def query(text, n_results=3):
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name="pedagogical_rubrics")

    query_embedding = model.encode([text]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    print(f"\nQuery: {text}\n")
    for i, (doc_id, metadata, distance) in enumerate(
        zip(results["ids"][0], results["metadatas"][0], results["distances"][0])
    ):
         print(f"{i+1}. {metadata.get('rule_id')} / {metadata.get('section')}  (distance: {distance:.4f})")


if __name__ == "__main__":
    query("this function has no explanation of what it does")
    query("the code catches all errors without saying which one")
    query("this variable is created but never used anywhere")