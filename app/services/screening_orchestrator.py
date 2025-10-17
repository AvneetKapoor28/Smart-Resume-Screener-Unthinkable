from fastapi import UploadFile
from typing import List
import asyncio

from app.services.parser_service import parse_resume
from app.services.llm_service import get_llm_analysis
from app.schemas.screening import CandidateAnalysis

async def process_and_screen_resumes(job_description: str, resumes: List[UploadFile]) -> List[CandidateAnalysis]:
    """
    Orchestrates the entire screening process for a batch of resumes.
    It parses and analyzes each resume concurrently.
    """
    
    async def screen_single_resume(resume_file: UploadFile):
        """Helper function to process one resume."""
        print(f"Processing resume: {resume_file.filename}...")
        
        # 1. Parse resume text
        resume_text = await parse_resume(resume_file)
        if not resume_text:
            print(f"Could not parse text from {resume_file.filename}. Skipping.")
            return None

        # 2. Get LLM analysis
        analysis = get_llm_analysis(resume_text, job_description)
        if not analysis:
            print(f"LLM analysis failed for {resume_file.filename}. Skipping.")
            return None

        # 3. Structure the result using our Pydantic schema
        try:
            return CandidateAnalysis(
                file_name=resume_file.filename,
                **analysis
            )
        except Exception as e:
            print(f"Failed to validate LLM output for {resume_file.filename}: {e}")
            return None

    # Run the screening for all resumes concurrently using asyncio.gather
    tasks = [screen_single_resume(resume) for resume in resumes]
    results = await asyncio.gather(*tasks)
    
    # Filter out any resumes that failed during processing
    successful_results = [res for res in results if res is not None]
    
    # Sort the successful results by match_score in descending order
    successful_results.sort(key=lambda x: x.match_score, reverse=True)
    
    return successful_results
