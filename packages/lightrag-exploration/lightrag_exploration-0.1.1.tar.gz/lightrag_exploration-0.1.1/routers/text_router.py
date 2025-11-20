from fastapi import APIRouter, HTTPException

# local imports
from schemas import TextRequest
from utils import (
    get_ollama_models,
    get_ollama_summary
)

router = APIRouter(prefix="/text", tags=["text"])

@router.get("/models")
async def get_models():
    try:
        models = get_ollama_models()
        return {"models": [model.get("name") for model in models]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/summarize")
async def summarize_text(request: TextRequest):
    try:
        # If context is provided, prepend it to the text
        text = request.text
        if request.context:
            text = f"Context: {request.context}\nUser: {request.text}"
        summary = get_ollama_summary(text=text, model=request.chat_model)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))