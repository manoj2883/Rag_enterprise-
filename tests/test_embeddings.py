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
        
    print("Initializing GoogleGenerativeAIEmbeddings...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            task_type="retrieval_document",
            google_api_key=api_key
        )
        
        sample_text = "Testing langchain google gemini embeddings retrieval dimension"
        print(f"Embedding sample string: '{sample_text}'")
        
        vector = embeddings.embed_query(sample_text)
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
