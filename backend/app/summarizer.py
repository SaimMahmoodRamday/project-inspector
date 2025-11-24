# # backend/app/summarizer.py

# import re
# import hashlib
# import json
# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI

# # Load environment variables from backend/.env
# env_path = Path(__file__).resolve().parent.parent / ".env"
# load_dotenv(dotenv_path=env_path)

# # Read API key from .env
# google_api_key = os.getenv("GOOGLE_API_KEY")
# if not google_api_key:
#     raise ValueError("GOOGLE_API_KEY not found in .env file.")

# # Cache file (simple JSON)
# CACHE_FILE = Path(__file__).parent / "summary_cache.json"

# try:
#     cache = json.loads(CACHE_FILE.read_text())
# except FileNotFoundError:
#     cache = {}

# # Gemini model (switch to gemini-1.5-flash for faster & cheaper)
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     temperature=0.3,
#     google_api_key=google_api_key
# )

# def clean_code_for_summary(code: str, max_chars: int = 4000) -> str:
#     """Remove sensitive patterns & trim size before sending to LLM."""
#     code = re.sub(
#         r'(?i)(api[_-]?key|secret|password)\s*=\s*["\'].*?["\']',
#         r'\1=***',
#         code
#     )
#     return code[:max_chars]

# def summarize_with_llm(file_path: str, code: str) -> str:
#     """Ask Gemini to summarize the file purpose."""
#     prompt = f"""
#     Summarize the purpose of this file in 3-4 short sentences.
#     Include the main functionality, key components, and role in the project.
#     Avoid code listings, be concise.

#     File path: {file_path}
#     Code:
#     ```{code}```
#     """
#     resp = llm.invoke(prompt)
#     return resp.content.strip()

# def get_cached_summary(file_path: str, code: str) -> str:
#     """Check cache first, otherwise call Gemini and store."""
#     key = hashlib.md5((file_path + code).encode()).hexdigest()
#     if key in cache:
#         return cache[key]
#     summary = summarize_with_llm(file_path, code)
#     cache[key] = summary
#     CACHE_FILE.write_text(json.dumps(cache, indent=2))
#     return summary

# New 02

# # backend/app/summarizer.py
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

# # Primary LLM (Gemini)
# llm_gemini = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash-latest",
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

# def summarize_with_llm(file_path: str, code: str) -> str:
#     """Ask LLM (Gemini first, Groq fallback) to summarize the file purpose."""
#     prompt = f"""
#     Summarize the purpose of this file in 3-4 short sentences.
#     Include the main functionality, key components, and role in the project.
#     Avoid code listings, be concise.

#     File path: {file_path}
#     Code:
#     ```{code}```
#     """

#     # Try Gemini first
#     try:
#         resp = llm_gemini.invoke(prompt)
#         return resp.content.strip()
#     except Exception as e:
#         print(f"[WARN] Gemini failed, switching to Groq: {e}")

#     # Fallback to Groq
#     try:
#         resp = llm_groq.chat.completions.create(
#             model="mixtral-8x7b-32768",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3,
#             max_tokens=300
#         )
#         return resp.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"[ERROR] Groq also failed: {e}")
#         return "[ERROR] Could not summarize file."

# def get_cached_summary(file_path: str, code: str) -> str:
#     """Check cache first, otherwise call LLM and store."""
#     key = hashlib.md5((file_path + code).encode()).hexdigest()
#     if key in cache:
#         return cache[key]
#     summary = summarize_with_llm(file_path, code)
#     cache[key] = summary
#     CACHE_FILE.write_text(json.dumps(cache, indent=2))
#     return summary

# New 03

# backend/app/summarizer.py

import re
import hashlib
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from groq import Groq
from langchain_core.exceptions import OutputParserException

# Load environment variables from backend/.env
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
except FileNotFoundError:
    cache = {}

# Primary LLM (Gemini)
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=google_api_key
)

# Fallback LLM (Groq)
llm_groq = Groq(api_key=groq_api_key)


def clean_code_for_summary(code: str, max_chars: int = 4000) -> str:
    """Remove sensitive patterns & trim size before sending to LLM."""
    code = re.sub(
        r'(?i)(api[_-]?key|secret|password)\s*=\s*["\'].*?["\']',
        r'\1=***',
        code
    )
    return code[:max_chars]


# def summarize_with_llm(file_path: str, code: str) -> str:
#     """Ask LLM (Gemini first, Groq fallback) to summarize the file purpose."""

#     # Clean & measure
#     cleaned_code = clean_code_for_summary(code)

#     print("\n=======================")
#     print(f"[DEBUG] Summarizing file: {file_path}")
#     print(f"[DEBUG] Original length: {len(code)} chars")
#     print(f"[DEBUG] Cleaned length:  {len(cleaned_code)} chars")
#     if len(cleaned_code) >= 4000:
#         print("[WARNING] Cleaned code reached 4000-char limit → possible truncation.")
#     print("=======================\n")

#     prompt = f"""
#     Provide the output in the following structure:
#     summary: <1-2 sentence summary of the file's purpose and main functionality>
#     external_functions_used: <list external functions/classes imported from other project files , or "none">
#     Keep formatting exactly as shown above. Be concise , Do NOT bold text , Do NOT include code.
    
#     File path: {file_path}
#     Code:
#     ```{cleaned_code}```
#     """

#     #
#     # ---------------------------- TRY GEMINI ----------------------------
#     #
#     try:
#         print("[DEBUG] Calling Gemini...")
#         resp = llm_gemini.invoke(prompt)
#         print("[DEBUG] Gemini Success")
#         return resp.content.strip()

#     except Exception as e:
#         print(f"[ERROR] Gemini failed for file: {file_path}")
#         print(f"[ERROR] Exception Type: {type(e).__name__}")
#         print(f"[ERROR] Exception Message: {e}")
#         print("[DEBUG] Switching to Groq fallback\n")

#     #
#     # ---------------------------- TRY GROQ ----------------------------
#     #
#     try:
#         print("[DEBUG] Calling Groq...")
#         resp = llm_groq.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3,
#             max_tokens=300
#         )
#         print("[DEBUG] Groq Success")
#         return resp.choices[0].message.content.strip()

#     except Exception as e:
#         print(f"[ERROR] Groq failed for file: {file_path}")
#         print(f"[ERROR] Exception Type: {type(e).__name__}")
#         print(f"[ERROR] Exception Message: {e}")
#         print(f"[ERROR] Could not summarize file.\n")
#         return "[ERROR] Could not summarize file."

# backend/app/summarizer.py

# def summarize_with_llm(file_path: str, code: str) -> dict:
#     """Ask LLM to summarize the file purpose and return structured data."""
    
#     cleaned_code = clean_code_for_summary(code)

#     print("\n=======================")
#     print(f"[DEBUG] Summarizing file: {file_path}")
#     print(f"[DEBUG] Cleaned length:  {len(cleaned_code)} chars")
#     print("=======================\n")

#     prompt = f"""
#     Analyze this code file and provide a structured summary.
    
#     File: {file_path}
    
#     Code:
#     ```{cleaned_code}```
    
#     Provide output in EXACTLY this JSON format:
#     {{
#         "summary": "1-2 sentence summary of the file's purpose",
#         "external_imports": ["list", "of", "specific", "imports", "from", "other", "project", "files"],
#         "main_functionality": "brief description of what the file does"
#     }}
    
#     Rules:
#     - "external_imports": Only include imports from other files in THIS project (not standard library)
#     - "summary": Focus on the overall purpose
#     - "main_functionality": Describe key operations
#     - If no project-specific imports, use empty array []
#     - Be concise and factual
#     """

#     # Try Gemini first
#     try:
#         print("[DEBUG] Calling Gemini...")
#         resp = llm_gemini.invoke(prompt)
#         content = resp.content.strip()
        
#         # Extract JSON from response
#         json_match = re.search(r'\{.*\}', content, re.DOTALL)
#         if json_match:
#             json_str = json_match.group()
#             result = json.loads(json_str)
#             print("[DEBUG] Gemini Success - JSON parsed")
#             return result
#         else:
#             print("[DEBUG] Gemini Success - No JSON found, using fallback")
#             return {
#                 "summary": content,
#                 "external_imports": [],
#                 "main_functionality": "See summary"
#             }

#     except Exception as e:
#         print(f"[ERROR] Gemini failed: {e}")
    
#     # Groq fallback with same logic
#     try:
#         print("[DEBUG] Calling Groq...")
#         resp = llm_groq.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3,
#             max_tokens=400
#         )
#         content = resp.choices[0].message.content.strip()
        
#         json_match = re.search(r'\{.*\}', content, re.DOTALL)
#         if json_match:
#             json_str = json_match.group()
#             result = json.loads(json_str)
#             print("[DEBUG] Groq Success - JSON parsed")
#             return result
#         else:
#             print("[DEBUG] Groq Success - No JSON found, using fallback")
#             return {
#                 "summary": content,
#                 "external_imports": [],
#                 "main_functionality": "See summary"
#             }

#     except Exception as e:
#         print(f"[ERROR] Groq failed: {e}")
#         return {
#             "summary": "Could not generate summary",
#             "external_imports": [],
#             "main_functionality": "Analysis failed"
#         }

# # def get_cached_summary(file_path: str, code: str) -> str:
# #     """Check cache first, otherwise call LLM and store."""
# #     key = hashlib.md5((file_path + code).encode()).hexdigest()

# #     if key in cache:
# #         print(f"[DEBUG] Cache hit for: {file_path}")
# #         return cache[key]

# #     print(f"[DEBUG] Cache miss → Summarizing: {file_path}")
# #     summary = summarize_with_llm(file_path, code)

# #     cache[key] = summary
# #     CACHE_FILE.write_text(json.dumps(cache, indent=2))
# #     print(f"[DEBUG] Cache updated for: {file_path}")

# #     return summary

# def get_cached_summary(file_path: str, code: str) -> dict:
#     """Check cache first, otherwise call LLM and store structured data."""
#     key = hashlib.md5((file_path + code).encode()).hexdigest()

#     if key in cache:
#         print(f"[DEBUG] Cache hit for: {file_path}")
#         # Handle both old string format and new dict format
#         cached = cache[key]
#         if isinstance(cached, str):
#             # Convert old format to new format
#             return {
#                 "summary": cached,
#                 "external_imports": [],
#                 "main_functionality": "See summary"
#             }
#         return cached

#     print(f"[DEBUG] Cache miss → Summarizing: {file_path}")
#     summary_data = summarize_with_llm(file_path, code)

#     cache[key] = summary_data
#     CACHE_FILE.write_text(json.dumps(cache, indent=2))
#     print(f"[DEBUG] Cache updated for: {file_path}")

#     return summary_data

# backend/app/summarizer.py

import re
import hashlib
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from groq import Groq

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
    model="gemini-2.0-flash-exp",  # Using experimental flash for better performance
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