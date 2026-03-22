import os
import time
import subprocess
import chromadb
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# --- ENGINE CONFIGURATION ---
fast_engine = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

context_engine = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

critical_engine = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --- PERSISTENT MEMORY SETUP ---
chroma_client = chromadb.PersistentClient(path="./memory_db")
memory_collection = chroma_client.get_or_create_collection(name="agent_history")

# --- CORE UTILITIES ---

def execute_script(file_name):
    """Runs a Python script and captures output or errors."""
    print(f"DEBUG: Executing '{file_name}'...")
    try:
        result = subprocess.run(
            ["python", file_name],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def write_to_disk(file_name, code_content):
    """Saves sanitized code to the local file system."""
    sanitized = code_content.replace("```python", "").replace("```", "").strip()
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(sanitized)

def process_pdf(file_path):
    """Reads a PDF, chunks the text with increased size, and stores it in memory."""
    print(f"LOG: Reading and indexing PDF with Semantic Chunking: {file_path}...")
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Increased chunk_size to 1500 to keep headers and descriptions together
        # Increased chunk_overlap to 150 for better context continuity
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, 
            chunk_overlap=150
        )
        chunks = text_splitter.split_documents(pages)
        
        # Add to ChromaDB
        for i, chunk in enumerate(chunks):
            memory_collection.add(
                documents=[chunk.page_content],
                metadatas=[{"source": file_path, "page": i}],
                ids=[f"{file_path}_{i}_{time.time()}"]
            )
        print(f"SUCCESS: Indexed {len(chunks)} fragments with optimized chunking.")
        return True
    except Exception as e:
        print(f"ERROR: Could not process PDF: {e}")
        return False

# --- MAIN ORCHESTRATOR ---

print("\n--- AI-LAB ORCHESTRATION SYSTEM: ONLINE ---")
print("Developer: stevenschulerai-dev")
print("Capabilities: Local File I/O | Web Search | PDF Intelligence | Source Explorer")

while True:
    user_input = input("\nAdmin > ")
    if user_input.lower() in ["exit", "quit", "stop"]:
        break

    try:
        # 1. CASE: PDF INGESTION (Remains same)
        if ".pdf" in user_input.lower() and ("read" in user_input.lower() or "learn" in user_input.lower()):
            words = user_input.split()
            pdf_file = next((w for w in words if w.lower().endswith(".pdf")), None)
            if pdf_file and os.path.exists(pdf_file):
                process_pdf(pdf_file)
            else:
                print(f"ERROR: File '{pdf_file}' not found.")

        # 2. CASE: AUTOMATED CODE GENERATION (Remains same)
        elif "file" in user_input.lower() or "create" in user_input.lower():
            # ... (Code generation logic as before)
            pass 

        # 3. CASE: DEEP WEB RESEARCH (Remains same)
        elif any(trigger in user_input.lower() for trigger in ["search", "investigate", "web"]):
            # ... (Tavily search logic as before)
            pass

        # 4. CASE: GENERAL QUERY (WITH RECALL BOOST)
        else:
            print("LOG: Checking memory for relevant local data...")
            # Bumping to 10 results to bypass 'Foreword Interference'
            results = memory_collection.query(
                query_texts=[user_input], 
                n_results=10 
            )
            
            context_fragments = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    doc_text = results['documents'][0][i]
                    meta = results['metadatas'][0][i]
                    context_fragments.append(f"[Source: {meta.get('source')}, Page: {meta.get('page')}]\n{doc_text}")

            local_context = "\n\n".join(context_fragments) if context_fragments else "No local context found."
            
            print("[ENGINE: Groq/Llama-3.1] Analyzing deep context from manual...")
            
            full_prompt = (
                f"Use the following excerpts from the book to answer the question. "
                f"The book is structured into chapters (e.g., Chapter 5: Business Tenets). "
                f"Focus on specific guidelines and principles mentioned in the body chapters.\n\n"
                f"CONTEXT:\n{local_context}\n\n"
                f"QUESTION: {user_input}"
            )
            
            final_response = fast_engine.invoke(full_prompt)
            print(f"\n[MASTER AGENT]\n{final_response.content}\n")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")