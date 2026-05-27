import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.ingest.chunker import split_documents
from src.ingest.uploader import upload_chunks
from src.rag.chain import get_rag_chain

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG Enterprise Chatbot API",
    description="A free-tier FastAPI backend for RAG using Gemini 2.0 and Pinecone.",
    version="1.0.0"
)

# CORS Middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Schemas
class DocumentInput(BaseModel):
    text: str = Field(..., description="The text content of the document to ingest.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata dictionary for the document.")

class IngestRequest(BaseModel):
    documents: List[DocumentInput]
    chunk_size: int = Field(1000, ge=100, le=5000)
    chunk_overlap: int = Field(200, ge=0, le=1000)

class IngestResponse(BaseModel):
    status: str
    message: str
    chunks_created: int

class QueryRequest(BaseModel):
    question: str = Field(..., description="The query/question to answer.")

class SourceDocumentResponse(BaseModel):
    page_content: str
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[SourceDocumentResponse]

# Endpoints
@app.get("/health", tags=["Health"])
async def health():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "gemini_configured": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
        "pinecone_configured": bool(os.environ.get("PINECONE_API_KEY") and os.environ.get("PINECONE_INDEX_NAME"))
    }

@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_documents(request: IngestRequest):
    """
    Chunk and ingest documents into the Pinecone vector database.
    """
    try:
        # Format input documents to dict format
        docs_to_chunk = [{"text": doc.text, "metadata": doc.metadata} for doc in request.documents]
        
        # Chunk documents
        chunks = split_documents(
            documents=docs_to_chunk,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks created from the input documents.")
            
        # Upload to Pinecone
        upload_chunks(chunks)
        
        return IngestResponse(
            status="success",
            message="Documents successfully ingested into Pinecone.",
            chunks_created=len(chunks)
        )
        
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_rag(request: QueryRequest):
    """
    Submit a query to the RAG pipeline. Retrieves context from Pinecone and generates an answer using Gemini 2.0 Flash.
    """
    try:
        # Initialize RAG chain
        rag_chain = get_rag_chain()
        
        # Run chain
        response = rag_chain.invoke(request.question)
        
        # Format response documents
        source_docs = [
            SourceDocumentResponse(
                page_content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in response.get("source_documents", [])
        ]
        
        return QueryResponse(
            answer=response.get("answer", "No answer generated."),
            source_documents=source_docs
        )
        
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query generation failed: {str(e)}")
