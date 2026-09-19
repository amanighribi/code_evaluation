from project_utils.text_extraction import extract_text_from_file

# Simulates uploading a real PDF — replace this path with an actual PDF you have,
# or we'll generate a tiny test PDF first if you don't have one handy.
with open("samples/exam_instructions.txt", "rb") as f:
    pass  # placeholder, see below

# Real test: point this at an actual .pdf file on your machine
pdf_path = input("Enter path to a real .pdf file to test: ")
with open(pdf_path, "rb") as f:
    content = f.read()

text = extract_text_from_file(pdf_path.split("\\")[-1], content)
print("Extracted text:")
print(text[:500])