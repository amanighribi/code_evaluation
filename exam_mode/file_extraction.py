import io
from pypdf import PdfReader
from docx import Document


class UnsupportedFileTypeError(Exception):
    pass


class TextExtractionError(Exception):
    pass


def extract_text_from_file(filename: str, content: bytes) -> str:
    """Extracts plain text from an uploaded instructions file.
    Supports .txt, .pdf, and .docx. Raises a clear error for anything else
    or if extraction produces no usable text."""

    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "txt":
        text = _extract_txt(content)
    elif ext == "pdf":
        text = _extract_pdf(content)
    elif ext == "docx":
        text = _extract_docx(content)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '.{ext}'. Supported: .txt, .pdf, .docx."
        )

    text = text.strip()
    if not text:
        raise TextExtractionError(
            f"No readable text could be extracted from this {ext.upper()} file. "
            "It may be empty, scanned as an image, or corrupted."
        )
    return text


def _extract_txt(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        raise TextExtractionError("The .txt file is not valid UTF-8 text.")


def _extract_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)
    except Exception as e:
        raise TextExtractionError(f"Could not read this PDF file: {e}")


def _extract_docx(content: bytes) -> str:
    try:
        doc = Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception as e:
        raise TextExtractionError(f"Could not read this .docx file: {e}")


if __name__ == "__main__":
    # Quick manual test with a plain .txt
    sample = b"Write a function that sorts a list. Do not use sort()."
    print(extract_text_from_file("instructions.txt", sample))