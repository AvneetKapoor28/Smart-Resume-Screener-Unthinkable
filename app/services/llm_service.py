import json
import google.generativeai as genai
from app.core.config import settings

# --- Configure the Gemini Client ---
# This configures the library with your API key
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to configure Gemini client: {e}")

# --- System Prompt ---
# This guides the model on its role and the *schema* of the JSON we want.
SYSTEM_PROMPT = """
You are an expert HR AI assistant. Your task is to analyze a candidate's resume
against a job description and provide a structured analysis.

Evaluate the resume based ONLY on the information it contains. Calculate a match score from 0 to 100.

Your response MUST be a single JSON object with the following keys:
- "match_score": An integer from 0 to 100.
- "summary": A concise, professional summary (2-3 sentences) explaining the score.
- "matching_skills": A list of skills (up to 5) from the resume that match the job description.
"""

# --- Generation Configuration ---
# We explicitly tell Gemini to only output JSON. This is extremely reliable.
generation_config = genai.types.GenerationConfig(
    response_mime_type="application/json"
)

# --- Initialize the Model ---
# We initialize the model once here.
try:
    model = genai.GenerativeModel(
        model_name=settings.MODEL_ID,
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini model '{settings.MODEL_ID}': {e}")


def get_llm_analysis(resume_text: str, job_description: str) -> dict | None:
    """
    Analyzes a resume against a job description using the Gemini API.
    Returns a dictionary parsed from the model's JSON response.
    """
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
    
    try:
        # Call the API, passing the user prompt and our JSON config
        response = model.generate_content(
            user_prompt,
            generation_config=generation_config
        )
        
        # The response.text will be a clean JSON string
        analysis_str = response.text
        
        # Print for debugging (you can remove this later)
        print(f"RAW Gemini Response:\n---\n{analysis_str}\n---")
        
        return json.loads(analysis_str)
    
    except json.JSONDecodeError:
        print(f"Error: Failed to decode Gemini response into JSON.")
        return None
    except Exception as e:
        # Handle API errors (e.g., auth failure, quota issues)
        print(f"Error calling Gemini API: {e}")
        return None