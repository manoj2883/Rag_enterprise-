from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split a single string into chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)

def split_documents(documents: List[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[dict]:
    """
    Split list of document dicts (containing 'text' and optional 'metadata') into chunks.
    Returns a list of dicts with chunked text and inherited metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunked_docs = []
    for doc in documents:
        text = doc.get("text", "")
        metadata = doc.get("metadata", {})
        chunks = text_splitter.split_text(text)
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunked_docs.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
            
    return chunked_docs
