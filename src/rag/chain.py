import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from src.rag.retriever import get_retriever

# Load environment variables
load_dotenv()

def get_llm() -> ChatGoogleGenerativeAI:
    """
    Initialize ChatGoogleGenerativeAI using gemini-2.0-flash.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set in environment variables.")
        
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_key,
        temperature=0.2
    )

def format_docs(docs) -> str:
    """
    Format list of Documents into a single string context.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """
    Constructs and returns the full RAG pipeline.
    The chain returns a dict: {"answer": str, "source_documents": List[Document]}
    """
    llm = get_llm()
    retriever = get_retriever()
    
    # Prompt template for grounded generation
    system_prompt = (
        "You are a helpful, enterprise-grade AI assistant.\n"
        "Answer the user's question using ONLY the provided context below. "
        "If the answer cannot be found in the context, say 'I cannot find the answer in the provided context.' "
        "Do not make up facts or use external knowledge. Keep answers concise and factual.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])
    
    # Inner generation chain
    generation_chain = (
        {
            "context": lambda x: format_docs(x["context"]),
            "question": lambda x: x["question"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Full pipeline combining retrieval and generation
    rag_chain = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ) | {
        "answer": generation_chain,
        "source_documents": lambda x: x["context"]
    }
    
    return rag_chain
