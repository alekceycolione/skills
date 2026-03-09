import io
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(uploaded_file) -> str:
    """Extrai texto bruto de um arquivo submetido via st.file_uploader()."""
    if uploaded_file is None:
        return ""

    extension = uploaded_file.name.split(".")[-1].lower()
    
    try:
        if extension == "txt":
            # read as string
            return uploaded_file.getvalue().decode("utf-8")
        
        elif extension == "pdf":
            # parse with pypdf
            reader = PdfReader(uploaded_file)
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            return "\n".join(parts)
            
        elif extension == "docx":
            # parse with python-docx
            # file is a BytesIO-like object, docx can read directly
            doc = Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
            
        else:
            return f"[Erro: Formato '.{extension}' não suportado]"
            
    except Exception as e:
        return f"[Erro ao ler arquivo: {e}]"
