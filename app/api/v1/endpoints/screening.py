from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List

from app.schemas.screening import ScreeningResponse
from app.services.screening_orchestrator import process_and_screen_resumes

router = APIRouter()

@router.post(
    "/",
    response_model=ScreeningResponse,
    summary="Screen Resumes Against a Job Description"
)
async def screen_resumes_endpoint(
    job_description: str = Form(
        ...,
        description="The full text of the job description."
    ), 
    resumes: List[UploadFile] = File(
        ...,
        description="A list of PDF resume files to be screened."
    )
):
    """
    Accepts a job description and one or more resume files, then returns a ranked
    list of candidates based on how well their resumes match the description.
    
    - **job_description**: The job posting to screen against.
    - **resumes**: The candidate resumes (PDF format).
    """
    # Basic validation
    if len(resumes) > 10:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="You can upload a maximum of 10 resumes at a time."
        )
    for resume in resumes:
        if resume.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{resume.filename}' is not a PDF. Only PDF files are accepted."
            )

    # Call the orchestrator to do the heavy lifting
    ranked_candidates = await process_and_screen_resumes(job_description, resumes)
    
    # For the response, we'll just summarize the JD
    jd_summary = (job_description[:75] + '...') if len(job_description) > 75 else job_description

    return ScreeningResponse(
        job_description_summary=jd_summary,
        ranked_candidates=ranked_candidates
    )
