from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.kural_nlp import process_farmer_audio
import os

farmer_router = APIRouter()

@farmer_router.post("/chat/audio")
async def chat_with_kural_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("ta") # Default to Tamil
):
    """
    Endpoint for MARUDHAN farmer audio queries.
    Receives raw audio from the frontend, orchestrates STT -> LLM/RAG -> TTS.
    Returns synthesized audio response dynamically optimized for low-latency Edge networks.
    """
    temp_audio_path = f"temp_{audio_file.filename}"
    
    try:
        # 1. Save uploaded audio temporarily from the edge node
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(await audio_file.read())
            
        # 2. Process via KURAL NLP pipeline (STT -> RAG -> TTS)
        response_audio_path, explanation = await process_farmer_audio(temp_audio_path, language)
        
        # 3. Return the generated TTS audio file
        return FileResponse(
            path=response_audio_path, 
            media_type="audio/mpeg", 
            filename="advisory_response.mp3",
            headers={"X-UNMAI-Explanation": explanation}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KURAL Pipeline Error: {str(e)}")
    finally:
        # Cleanup temporary ingestion file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
