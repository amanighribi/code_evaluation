from project_utils.text_extraction import extract_text_from_file

docx_path = input("Enter path to a real .docx file to test: ")
with open(docx_path, "rb") as f:
    content = f.read()

text = extract_text_from_file(docx_path.split("\\")[-1], content)
print("Extracted text:")
print(text[:500])