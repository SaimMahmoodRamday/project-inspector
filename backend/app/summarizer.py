# backend/app/summarizer.py

# import re
# import hashlib
# import json
# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# from groq import Groq
# from langchain_core.exceptions import OutputParserException

# # Load environment variables from backend/.env
# env_path = Path(__file__).resolve().parent.parent / ".env"
# load_dotenv(dotenv_path=env_path)

# # API keys
# google_api_key = os.getenv("GOOGLE_API_KEY")
# groq_api_key = os.getenv("GROQ_API_KEY")

# if not google_api_key:
#     raise ValueError("GOOGLE_API_KEY not found in .env file.")
# if not groq_api_key:
#     raise ValueError("GROQ_API_KEY not found in .env file.")

# # Cache file
# CACHE_FILE = Path(__file__).parent / "summary_cache.json"
# try:
#     cache = json.loads(CACHE_FILE.read_text())
# except FileNotFoundError:
#     cache = {}

# # gemini-2.5-flash-lite

# # Primary LLM (Gemini)
# llm_gemini = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash-lite",
#     temperature=0.3,
#     google_api_key=google_api_key
# )

# # Fallback LLM (Groq)
# llm_groq = Groq(api_key=groq_api_key)


# def clean_code_for_summary(code: str, max_chars: int = 4000) -> str:
#     """Remove sensitive patterns & trim size before sending to LLM."""
#     code = re.sub(
#         r'(?i)(api[_-]?key|secret|password)\s*=\s*["\'].*?["\']',
#         r'\1=***',
#         code
#     )
#     return code[:max_chars]


# backend/app/summarizer.py

import re
import hashlib
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from groq import Groq

# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chains.summarize import load_summarize_chain
# from langchain.schema import Document

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# API keys
google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in .env file.")

# Cache file
CACHE_FILE = Path(__file__).parent / "summary_cache.json"
try:
    cache = json.loads(CACHE_FILE.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    cache = {}

# LLM clients
llm_gemini = ChatGoogleGenerativeAI(
    # model="gemini-2.0-flash-exp",  # Using experimental flash for better performance
    model="gemini-2.5-flash-lite",  # Using experimental flash for better performance
    temperature=0.1,  # Lower temperature for more consistent output
    google_api_key=google_api_key
)

llm_groq = Groq(api_key=groq_api_key)


def clean_code_for_summary(code: str, max_chars: int = 3000) -> str:
    """Remove sensitive patterns & trim size efficiently."""
    # Remove comments and docstrings to reduce token count
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)  # Remove single line comments
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)  # Remove docstrings
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    
    # Remove sensitive data
    code = re.sub(
        r'(?i)(api[_-]?key|secret|password|token)\s*=\s*["\'].*?["\']',
        r'\1=***',
        code
    )
    
    # Remove extra whitespace
    code = re.sub(r'\n\s*\n', '\n\n', code)
    
    return code.strip()[:max_chars]


def should_summarize_file(file_path: str, code: str) -> bool:
    """Check if file is worth summarizing to save LLM calls."""
    # Skip very short files
    if len(code.strip()) < 50:
        return False
    
    # Skip files that are mostly configuration
    if any(ext in file_path.lower() for ext in ['config', 'settings', 'setup', 'requirements']):
        return len(code.strip()) > 200  # Only summarize if substantial content
    
    return True


def summarize_with_llm(file_path: str, code: str) -> str:
    """Optimized LLM summarization with better prompt engineering."""
    
    if not should_summarize_file(file_path, code):
        return "Configuration or minimal code file - no summary generated."
    
    cleaned_code = clean_code_for_summary(code)
    
    print(f"\n[SUMMARY] Processing: {file_path} ({len(cleaned_code)} chars)")

    if len(cleaned_code) > 2500:
        print(f"[SUMMARY] Using chunking for large file: {file_path}")
        return summarize_large_file(file_path, cleaned_code)

    # More efficient prompt
    prompt = f"""
    Analyze this code file briefly:
    
    File: {file_path}
    
    Code:
    {cleaned_code}
    
    Provide a VERY concise summary in this exact format:
    SUMMARY: [2-sentence overview]
    IMPORTS: [comma-separated project-specific imports or "none"]
    
    Rules:
    - SUMMARY: Maximum 50 words, focus on main purpose
    - IMPORTS: Only imports(imported functions) from other files in this project (not stdlib)
    - Be factual, no explanations
    - If no project imports, write "none"
    """

    # Try Gemini first (faster and cheaper)
    try:
        print(f"[SUMMARY] Calling Gemini for {file_path}")
        resp = llm_gemini.invoke(prompt)
        content = resp.content.strip()
        
        # Validate response format
        if "SUMMARY:" in content and "IMPORTS:" in content:
            return content
        else:
            # Fallback parsing
            return f"SUMMARY: {content}\nIMPORTS: none"
            
    except Exception as e:
        print(f"[SUMMARY] Gemini failed: {e}")
    
    # Groq fallback
    try:
        print(f"[SUMMARY] Calling Groq fallback for {file_path}")
        resp = llm_groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150  # Much shorter response
        )
        content = resp.choices[0].message.content.strip()
        
        if "SUMMARY:" in content and "IMPORTS:" in content:
            return content
        else:
            return f"SUMMARY: {content}\nIMPORTS: none"
            
    except Exception as e:
        print(f"[SUMMARY] Groq failed: {e}")
        return "SUMMARY: Could not generate summary\nIMPORTS: none"
    
def split_code_into_chunks(code: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """Simple code chunking without langchain dependency."""
    chunks = []
    start = 0
    
    while start < len(code):
        end = start + chunk_size
        
        # Try to split at a logical boundary
        if end < len(code):
            # Look for the last newline within the last 100 chars
            split_pos = code.rfind('\n', end - 100, end)
            if split_pos != -1 and split_pos > start:
                end = split_pos + 1
        
        chunks.append(code[start:end])
        start = end - overlap  # Apply overlap
        
        if start >= len(code):
            break
    
    return chunks

def summarize_large_file(file_path: str, code: str) -> str:
    """Handle large files using manual chunking with both Gemini and Groq support."""
    
    chunks = split_code_into_chunks(code)
    print(f"[SUMMARY] Large file {file_path}, splitting into {len(chunks)} chunks")
    
    # First pass: Summarize each chunk with Gemini
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"[SUMMARY] Processing chunk {i+1}/{len(chunks)} with Gemini")
        
        chunk_prompt = f"""
        Analyze this code chunk from {file_path} (part {i+1}/{len(chunks)}):
        
        {chunk}
        
        Provide a brief summary of this specific part.
        """
        
        try:
            resp = llm_gemini.invoke(chunk_prompt)
            chunk_summaries.append(resp.content.strip())
        except Exception as e:
            print(f"[SUMMARY] Gemini failed on chunk {i+1}: {e}")
            # Try Groq for this chunk
            try:
                print(f"[SUMMARY] Trying Groq for chunk {i+1}")
                resp = llm_groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": chunk_prompt}],
                    temperature=0.1,
                    max_tokens=200
                )
                chunk_summaries.append(resp.choices[0].message.content.strip())
            except Exception as groq_error:
                print(f"[SUMMARY] Both failed on chunk {i+1}: {groq_error}")
                chunk_summaries.append(f"Chunk {i+1}: Processing failed")
    
    # Combine all chunk summaries for final analysis
    combined_summaries = "\n\n".join([
        f"Chunk {i+1}:\n{summary}" 
        for i, summary in enumerate(chunk_summaries)
    ])
    
    combine_prompt = f"""
    Analyze these summaries from different parts of {file_path}:
    
    {combined_summaries}
    
    Provide a VERY concise final summary in this exact format:
    
    SUMMARY: [2-sentence overview of the entire file]
    IMPORTS: [comma-separated project-specific imports from ANY part or "none"]
    
    Rules:
    - SUMMARY: Maximum 50 words, focus on main purpose
    - IMPORTS: Only imports from other files in this project (not stdlib)
    - Be factual, no explanations
    - If no project imports, write "none"
    """
    
    # Try final combination with Gemini first
    try:
        print(f"[SUMMARY] Final combination with Gemini")
        resp = llm_gemini.invoke(combine_prompt)
        content = resp.content.strip()
        
        if "SUMMARY:" in content and "IMPORTS:" in content:
            return content
        else:
            return f"SUMMARY: {content}\nIMPORTS: none"
            
    except Exception as e:
        print(f"[SUMMARY] Gemini final combination failed: {e}, trying Groq...")
        
        # Fallback to Groq for final combination
        try:
            print(f"[SUMMARY] Final combination with Groq")
            resp = llm_groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": combine_prompt}],
                temperature=0.1,
                max_tokens=200
            )
            content = resp.choices[0].message.content.strip()
            
            if "SUMMARY:" in content and "IMPORTS:" in content:
                return content
            else:
                return f"SUMMARY: {content}\nIMPORTS: none"
                
        except Exception as groq_error:
            print(f"[SUMMARY] All chunking methods failed: {groq_error}")
            return summarize_with_llm(file_path, code)


def parse_summary_response(response: str) -> dict:
    """Parse the LLM response into structured data."""
    summary = "No summary available"
    imports = []
    
    try:
        # Extract SUMMARY
        summary_match = re.search(r'SUMMARY:\s*(.+)', response)
        if summary_match:
            summary = summary_match.group(1).strip()
        
        # Extract IMPORTS
        imports_match = re.search(r'IMPORTS:\s*(.+)', response)
        if imports_match:
            imports_str = imports_match.group(1).strip()
            if imports_str.lower() != "none":
                # Split by comma and clean up
                imports = [imp.strip() for imp in imports_str.split(',') if imp.strip()]
    
    except Exception as e:
        print(f"[ERROR] Failed to parse summary response: {e}")
        summary = "Error parsing summary"
    
    return {
        "summary": summary,
        "external_imports": imports
    }


def get_cached_summary(file_path: str, code: str) -> dict:
    """Optimized cache handling with structured data."""
    key = hashlib.md5((file_path + code).encode()).hexdigest()

    if key in cache:
        print(f"[CACHE] Hit for: {file_path}")
        cached = cache[key]
        
        # Handle both string and dict formats
        if isinstance(cached, str):
            return parse_summary_response(cached)
        elif isinstance(cached, dict):
            return cached
        else:
            # Invalid cache entry, regenerate
            del cache[key]
    
    print(f"[CACHE] Miss for: {file_path}")
    
    # Get new summary
    summary_response = summarize_with_llm(file_path, code)
    summary_data = parse_summary_response(summary_response)
    
    # Cache the structured data
    cache[key] = summary_data
    
    # Save cache (with error handling)
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2))
    except Exception as e:
        print(f"[ERROR] Failed to save cache: {e}")
    
    return summary_data