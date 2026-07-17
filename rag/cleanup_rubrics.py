import os

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

for filename in os.listdir(KNOWLEDGE_BASE_DIR):
    if filename.endswith(".md"):
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()

        original = content
        content = content.replace("\\_", "_")
        content = content.replace("\\-", "-")
        content = content.replace("\\*", "*")

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {filename}")
        else:
            print(f"No change: {filename}")