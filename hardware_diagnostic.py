import os
import time
import subprocess
import chromadb
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
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

# --- MAIN ORCHESTRATOR ---

print("\n--- AI-LAB ORCHESTRATION SYSTEM: ONLINE ---")
print("Developer: stevenschulerai-dev")
print("Capabilities: Local File I/O | Web Search | Self-Correction Loop")

while True:
    user_input = input("\nAdmin > ")
    if user_input.lower() in ["exit", "quit", "stop"]:
        break

    try:
        # 1. CASE: AUTOMATED CODE GENERATION & DEBUGGING
        if "file" in user_input.lower() or "create" in user_input.lower():
            words = user_input.split()
            
            # --- IMPROVED FILENAME PARSING ---
            try:
                if "file" in words:
                    idx = words.index("file")
                    if idx + 1 < len(words) and words[idx + 1].lower() in ["called", "named"]:
                        target_file = words[idx + 2]
                    else:
                        target_file = words[idx + 1]
                else:
                    target_file = "output_script.py"
            except (ValueError, IndexError):
                target_file = "output_script.py"

            attempts = 0
            max_retries = 3
            last_error = ""

            while attempts < max_retries:
                print(f"LOG: Generating version {attempts + 1} for '{target_file}'...")
                prompt = f"Generate only the Python code for: {user_input}. "
                if last_error:
                    prompt += f"The previous attempt failed with this error: {last_error}. Please debug and fix it."
                
                try:
                    ai_response = critical_engine.invoke(prompt)
                except:
                    ai_response = context_engine.invoke(prompt)

                write_to_disk(target_file, ai_response.content)
                
                # Auto-testing
                is_valid, logs = execute_script(target_file)
                
                if is_valid:
                    print("SUCCESS: Code validated and operational.")
                    print(f"\n--- SCRIPT OUTPUT ---\n{logs}---------------------")
                    break
                else:
                    print("WARNING: Execution error found. Retrying with debugger...")
                    last_error = logs
                    attempts += 1
            
            if attempts == max_retries:
                print(f"ERROR: Failed to self-correct after {max_