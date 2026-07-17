import os
import chromadb

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")


def get_rubric_for_rule(rule_id: str) -> dict:
    """Retrieve all rubric chunks for a given analyzer rule_id.
    Returns a dict of {section_name: text}, or empty dict if not found."""
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name="pedagogical_rubrics")

    results = collection.get(where={"rule_id": rule_id})

    rubric = {}
    for metadata, document in zip(results["metadatas"], results["documents"]):
        rubric[metadata["section"]] = document

    return rubric


def get_rubrics_for_issues(issue_rule_ids: list[str]) -> dict:
    """Retrieve rubrics for multiple rule_ids at once (e.g. all issues found in one file)."""
    return {rule_id: get_rubric_for_rule(rule_id) for rule_id in issue_rule_ids}


if __name__ == "__main__":
    # quick manual test
    rubric = get_rubric_for_rule("bare_except")
    for section, text in rubric.items():
        print(f"\n[{section}]\n{text[:120]}...")