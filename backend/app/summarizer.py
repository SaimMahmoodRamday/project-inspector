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


def summarize_with_llm(file_path: str, code: str) -> str:
    """Ask LLM (Gemini first, Groq fallback) to summarize the file purpose."""

    # Clean & measure
    cleaned_code = clean_code_for_summary(code)

    print("\n=======================")
    print(f"[DEBUG] Summarizing file: {file_path}")
    print(f"[DEBUG] Original length: {len(code)} chars")
    print(f"[DEBUG] Cleaned length:  {len(cleaned_code)} chars")
    if len(cleaned_code) >= 4000:
        print("[WARNING] Cleaned code reached 4000-char limit → possible truncation.")
    print("=======================\n")

    prompt = f"""
    Summarize the purpose of this file in 3-4 short sentences.
    Include the main functionality, key components, and role in the project.
    Avoid code listings, be concise.

    File path: {file_path}
    Code:
    ```{cleaned_code}```
    """

    #
    # ---------------------------- TRY GEMINI ----------------------------
    #
    try:
        print("[DEBUG] Calling Gemini...")
        resp = llm_gemini.invoke(prompt)
        print("[DEBUG] Gemini Success")
        return resp.content.strip()

    except Exception as e:
        print(f"[ERROR] Gemini failed for file: {file_path}")
        print(f"[ERROR] Exception Type: {type(e).__name__}")
        print(f"[ERROR] Exception Message: {e}")
        print("[DEBUG] Switching to Groq fallback\n")

    #
    # ---------------------------- TRY GROQ ----------------------------
    #
    try:
        print("[DEBUG] Calling Groq...")
        resp = llm_groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        print("[DEBUG] Groq Success")
        return resp.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] Groq failed for file: {file_path}")
        print(f"[ERROR] Exception Type: {type(e).__name__}")
        print(f"[ERROR] Exception Message: {e}")
        print(f"[ERROR] Could not summarize file.\n")
        return "[ERROR] Could not summarize file."


def get_cached_summary(file_path: str, code: str) -> str:
    """Check cache first, otherwise call LLM and store."""
    key = hashlib.md5((file_path + code).encode()).hexdigest()

    if key in cache:
        print(f"[DEBUG] Cache hit for: {file_path}")
        return cache[key]

    print(f"[DEBUG] Cache miss → Summarizing: {file_path}")
    summary = summarize_with_llm(file_path, code)

    cache[key] = summary
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    print(f"[DEBUG] Cache updated for: {file_path}")

    return summary
