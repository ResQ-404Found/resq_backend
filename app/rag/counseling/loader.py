from langchain_community.document_loaders import PyPDFLoader

def load_counseling_docs(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    return loader.load()
