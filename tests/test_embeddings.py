import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def main():
    # Load environment variables from .env
    load_dotenv()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        # Fallback to GOOGLE_API_KEY
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key or api_key in ["YOUR_GEMINI_API_KEY", "YOUR_GOOGLE_API_KEY"]:
        print("Error: Please set your GEMINI_API_KEY or GOOGLE_API_KEY in the .env file.", file=sys.stderr)
        sys.exit(1)
        
    # We use gemini-embedding-001 as text-embedding-004 is retired/deprecated in AI Studio.
    # gemini-embedding-001 supports Matryoshka Representation Learning (MRL), allowing us to
    # request a 768-dimensional output vector using the output_dimensionality parameter.
    model_name = "gemini-embedding-001"
    
    print(f"Initializing GoogleGenerativeAIEmbeddings with model: {model_name}...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            task_type="retrieval_document",
            google_api_key=api_key,
            output_dimensionality=768
        )
        
        sample_text = "Testing langchain google gemini embeddings retrieval dimension"
        print(f"Embedding sample string: '{sample_text}'")
        
        # Test calling embed_query
        try:
            vector = embeddings.embed_query(sample_text)
        except TypeError:
            # If the installed version of langchain-google-genai doesn't support output_dimensionality
            # in the constructor, we can try passing it to embed_query directly or slice it.
            print("Constructor output_dimensionality not supported, trying direct call parameter...")
            vector = embeddings.embed_query(sample_text, output_dimensionality=768)
            
        print("Success!")
        print(f"Vector type: {type(vector)}")
        print(f"Vector dimension: {len(vector)}")
        
        if len(vector) == 768:
            print("Verified: Dimension is exactly 768.")
        else:
            print(f"Warning: Dimension is {len(vector)} (expected 768).")
            
    except Exception as e:
        print(f"An error occurred during embedding: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
