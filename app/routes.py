from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import SummarizeRequest, SummaryResponse
from app.openai_service import summarize_text

router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
async def summarize(request: SummarizeRequest):
    # --- validation ---
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail={"error": "Text cannot be empty."})

    if len(request.text) > 5000:
        raise HTTPException(
            status_code=400,
            detail={"error": "Text exceeds the 5000-character limit."},
        )

    # --- call Gemini ---
    try:
        result = summarize_text(request.text)
        return result
    except Exception as exc:
        error_msg = str(exc) or "Error generating summary"
        fallback = SummaryResponse(
            summary="Error generating summary",
            key_points=[],
            word_count=0,
        )
        return JSONResponse(
            status_code=500,
            content={**fallback.model_dump(), "error": error_msg},
        )
