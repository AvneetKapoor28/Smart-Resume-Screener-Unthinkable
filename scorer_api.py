# scorer_api.py

import os
import json
import fitz  # PyMuPDF
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# --- Configuration and Initialization ---

# Load environment variables from .env file
load_dotenv()

# Securely initialize the InferenceClient
HF_API_TOKEN = os.getenv("HF_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Hugging Face API token not found. Set it in your .env file.")

# We will use a powerful open-source instruction-tuned model.
# Mixtral is an excellent choice for this kind of structured output task.
MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"

try:
    client = InferenceClient(model=MODEL_ID, token=HF_API_TOKEN)
except Exception as e:
    raise RuntimeError(f"Failed to initialize InferenceClient: {e}")

# --- Core Functions ---

def parse_pdf_resume(pdf_path: str) -> str:
    """Parses a PDF file and extracts its text content."""
    try:
        with fitz.open(pdf_path) as doc:
            text = "".join(page.get_text() for page in doc)
        print(f"✅ Successfully parsed {pdf_path}\n")
        return text
    except Exception as e:
        print(f"❌ Error parsing PDF {pdf_path}: {e}")
        return ""

def analyze_with_hf_api(resume_text: str, job_description: str) -> dict:
    """
    Analyzes resume against a job description using the Hugging Face Inference API.
    Returns a dictionary with the analysis.
    """
    # This system prompt is crucial for getting reliable JSON output.
    system_prompt = """
    You are an expert HR AI assistant. Your task is to analyze a candidate's resume
    against a job description and provide a structured analysis in a single, valid JSON object.
    
    Evaluate the resume based ONLY on the information it contains. Calculate a match score from 0 to 100.
    
    Your response MUST be a single JSON object with the following keys:
    - "match_score": An integer from 0 to 100.
    - "summary": A concise 2-3 sentence summary explaining the score.
    - "matching_skills": A list of skills from the resume that match the job description.
    """
    
    # The user prompt contains the actual data to be analyzed.
    user_prompt = f"""
    **JOB DESCRIPTION:**
    ---
    {job_description}
    ---

    **RESUME TEXT:**
    ---
    {resume_text}
    ---
    """
    
    messages_for_api = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    print("🤖 Calling the Hugging Face Inference API...")
    try:
        response = client.chat_completion(
            messages=messages_for_api,
            max_tokens=500,
            temperature=0.1, # Lower temperature for more deterministic, factual output
            # The following arguments help enforce JSON output with some models
            response_format={"type": "json_object"},
        )
        # Extract the content and parse it as JSON
        analysis_str = response.choices[0].message.content
        return json.loads(analysis_str)
    
    except Exception as e:
        print(f"❌ Error calling the inference model: {e}")
        return None

# --- Main Execution Block ---

if __name__ == "__main__":
    # --- DEFINE YOUR INPUTS HERE ---
    
    # 1. Path to the resume file
    resume_file_path = "resumes/sample_resume.pdf"
    
    # 2. The job description
    job_desc = """
    We are hiring a Senior Python Backend Developer with at least 5 years of experience.
    Key requirements include expert-level knowledge of Python, FastAPI, and Docker.
    The candidate must have hands-on experience deploying applications to AWS (EC2, S3, RDS).
    Strong SQL skills and experience with PostgreSQL are mandatory.
    """
    
    # --- SCRIPT EXECUTION ---
    
    print("--- 🚀 Starting Resume Screening (API Version) ---")
    
    resume_content = parse_pdf_resume(resume_file_path)
    
    if resume_content:
        analysis_result = analyze_with_hf_api(resume_content, job_desc)
        
        if analysis_result:
            print("\n--- ✅ ANALYSIS COMPLETE ---")
            print(f"📊 Match Score: {analysis_result.get('match_score', 'N/A')}")
            print(f"📝 Summary: {analysis_result.get('summary', 'N/A')}")
            print(f"🛠️ Matching Skills: {', '.join(analysis_result.get('matching_skills', []))}")
            print("---------------------------\n")