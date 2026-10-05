"""Load your master resume from PDF, .md or .txt."""
from pathlib import Path


def load_resume(path):
    path = Path(path)
    if not path.exists() and Path(str(path) + ".pdf").exists():
        path = Path(str(path) + ".pdf")  # e.g. master_resume.pdf.pdf
    if not path.exists():
        raise FileNotFoundError(
            f"Resume not found: {path}. Put your resume there or change 'resume_file' in config.yaml."
        )
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join((p.extract_text() or "") for p in reader.pages).strip()
        if len(text) < 100:
            raise ValueError(
                "Could not extract text from the PDF (it may be a scanned image). "
                "Export your resume as a text-based PDF from Word/Google Docs, or use a .md file."
            )
        return text
    return path.read_text(encoding="utf-8")
