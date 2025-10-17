from pydantic import BaseModel, Field
from typing import List

# --- Schema for a Single Candidate's Analysis ---
class CandidateAnalysis(BaseModel):
    """
    Represents the structured analysis of a single resume.
    """
    match_score: int = Field(..., description="The match score from 0 to 100.", ge=0, le=100)
    summary: str = Field(..., description="A concise summary of the candidate's fit.")
    matching_skills: List[str] = Field(..., description="A list of skills that match the job description.")
    file_name: str = Field(..., description="The name of the resume file.")

# --- Schema for the overall API response ---
class ScreeningResponse(BaseModel):
    """
    The final response returned by the /screen endpoint, containing a ranked list of candidates.
    """
    job_description_summary: str = Field(..., description="A brief summary of the job description provided.")
    ranked_candidates: List[CandidateAnalysis] = Field([], description="A list of candidates, ranked by match score.")
