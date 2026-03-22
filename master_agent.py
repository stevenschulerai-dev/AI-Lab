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
    """Reads a PDF, chunks the text, and stores it in memory."""
    print(f"LOG: Reading and indexing PDF: {file_path}...")
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(pages)
        
        # Add to ChromaDB
        for i, chunk in enumerate(chunks):
            memory_collection.add(
                documents=[chunk.page_content],
                metadatas=[{"source": file_path, "page": i}],
                ids=[f"{file_path}_{i}_{time.time()}"]
            )
        print(f"SUCCESS: Indexed {len(chunks)} fragments from the document.")
        return True
    except Exception as e:
        print(f"ERROR: Could not process PDF: {e}")
        return False

# --- MAIN ORCHESTRATOR ---

print("\n--- AI-LAB ORCHESTRATION SYSTEM: ONLINE ---")
print("Developer: stevenschulerai-dev")
print("Capabilities: Local File I/O | Web Search | PDF Intelligence | Engine Tracking")

while True:
    user_input = input("\nAdmin > ")
    if user_input.lower() in ["exit", "quit", "stop"]:
        break

    try:
        # 1. CASE: PDF INGESTION
        if ".pdf" in user_input.lower() and ("read" in user_input.lower() or "learn" in user_input.lower()):
            words = user_input.split()
            pdf_file = next((w for w in words if w.lower().endswith(".pdf")), None)
            if pdf_file and os.path.exists(pdf_file):
                # [ENGINE: Local Logic]
                process_pdf(pdf_file)
            else:
                print(f"ERROR: File '{pdf_file}' not found.")

        # 2. CASE: AUTOMATED CODE GENERATION & DEBUGGING
        elif "file" in user_input.lower() or "create" in user_input.lower():
            # [ENGINE: Groq/Llama-3.1] - Routing the initial logic
            words = user_input.split()
            target_file = "output_script.py" # (Simplified parsing for brevity)
            
            attempts = 0
            max_retries = 3
            last_error = ""

            while attempts < max_retries:
                print(f"LOG: Generating version {attempts + 1} for '{target_file}'...")
                prompt = f"Generate only the Python code for: {user_input}. "
                if last_error:
                    prompt += f"Previous error: {last_error}."
                
                try:
                    # PRIMARY CODING ENGINE
                    print("[ENGINE: OpenAI/GPT-4o] Processing architectural logic...")
                    ai_response = critical_engine.invoke(prompt)
                except Exception as e:
                    # BACKUP CODING ENGINE
                    print(f"WARNING: OpenAI failed. [ENGINE: Gemini/2.5-Flash] Taking over...")
                    ai_response = context_engine.invoke(prompt)

                write_to_disk(target_file, ai_response.content)
                success, logs = execute_script(target_file)
                
                if success:
                    print("SUCCESS: Code validated.")
                    print(f"\n--- SCRIPT OUTPUT ---\n{logs}---------------------")
                    break
                else:
                    print("WARNING: Debugger required.")
                    last_error = logs
                    attempts += 1

        # 3. CASE: DEEP WEB RESEARCH
        elif any(trigger in user_input.lower() for trigger in ["search", "investigate", "web"]):
            print(f"LOG: Researching web data for: {user_input}...")
            search_results = tavily.search(query=user_input, max_results=3)
            raw_context = "\n".join([r['content'] for r in search_results['results']])
            
            print("[ENGINE: Gemini/2.5-Flash] Synthesizing web research and memory...")
            final_response = context_engine.invoke(f"Context: {raw_context}\nTask: {user_input}")
            print(f"\n[MASTER AGENT]\n{final_response.content}\n")

        # 4. CASE: GENERAL QUERY
        else:
            # Check memory
            results = memory_collection.query(query_texts=[user_input], n_results=2)
            local_context = "\n".join(results['documents'][0]) if results['documents'] else ""
            
            print("[ENGINE: Groq/Llama-3.1] Handling fast-response query...")
            full_prompt = f"Local Context: {local_context}\nQuestion: {user_input}"
            final_response = fast_engine.invoke(full_prompt)
            print(f"\n[MASTER AGENT]\n{final_response.content}\n")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")