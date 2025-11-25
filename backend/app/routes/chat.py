"""
AgroSentinel Chat API Routes
Multi-language AI chat assistant endpoints with Gemini AI
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.chat_assistant import generate_response, get_suggestions
from app.services.gemini_chat import get_gemini_service, GeminiChatService
from app.services.database import Database
from app.config import get_settings
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Initialize Gemini service
_gemini_service: Optional[GeminiChatService] = None

def get_chat_service():
    """Get the Gemini chat service (lazy initialization)"""
    global _gemini_service
    if _gemini_service is None:
        settings = get_settings()
        if settings.gemini_api_key:
            _gemini_service = get_gemini_service(settings.gemini_api_key)
    return _gemini_service


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    intent: str
    detected_disease: Optional[str]
    detected_crop: Optional[str]
    language: str
    timestamp: str


class ChatHistoryItem(BaseModel):
    role: str  # "user" or "assistant"
    message: str
    timestamp: str


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the AI chat assistant
    Uses Gemini AI for intelligent responses
    Supports multiple languages: en, hi, te, ta, kn
    """
    try:
        # Try Gemini first
        gemini = get_chat_service()
        
        if gemini and gemini.model:
            # Use Gemini AI
            result = await gemini.send_message(
                message=request.message,
                language=request.language,
                session_id=request.session_id
            )
        else:
            # Fallback to basic response
            result = generate_response(
                message=request.message,
                language=request.language,
                context=request.context
            )
        
        # Store chat in database (optional)
        try:
            chat_doc = {
                "session_id": request.session_id,
                "user_message": request.message,
                "assistant_response": result["response"],
                "language": request.language,
                "intent": result.get("intent", "unknown"),
                "model": result.get("model", "basic"),
                "timestamp": datetime.utcnow()
            }
            await Database.db.chat_history.insert_one(chat_doc)
        except Exception:
            pass  # Don't fail if DB storage fails
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/suggestions")
async def get_chat_suggestions(language: str = "en"):
    """
    Get suggested questions based on language
    """
    suggestions = get_suggestions(language)
    return {"suggestions": suggestions, "language": language}


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """
    Get chat history for a session
    """
    try:
        cursor = Database.db.chat_history.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(limit)
        
        history = []
        async for doc in cursor:
            history.append({
                "user_message": doc.get("user_message"),
                "assistant_response": doc.get("assistant_response"),
                "language": doc.get("language"),
                "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None
            })
        
        return {"history": list(reversed(history)), "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a session
    """
    try:
        result = await Database.db.chat_history.delete_many({"session_id": session_id})
        return {"deleted": result.deleted_count, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


# Quick questions for common issues
QUICK_QUESTIONS = {
    "en": [
        {"id": "q1", "text": "My tomato leaves have brown spots", "icon": "🍅"},
        {"id": "q2", "text": "How to prevent late blight?", "icon": "🛡️"},
        {"id": "q3", "text": "What spray for leaf curl?", "icon": "💊"},
        {"id": "q4", "text": "Organic pest control tips", "icon": "🌿"},
        {"id": "q5", "text": "Weather precautions for monsoon", "icon": "🌧️"},
        {"id": "q6", "text": "How to grow healthy tomatoes?", "icon": "📈"},
    ],
    "hi": [
        {"id": "q1", "text": "मेरे टमाटर की पत्तियों पर भूरे धब्बे हैं", "icon": "🍅"},
        {"id": "q2", "text": "झुलसा रोग से कैसे बचें?", "icon": "🛡️"},
        {"id": "q3", "text": "पत्ता मोड़ के लिए कौन सा स्प्रे?", "icon": "💊"},
        {"id": "q4", "text": "जैविक कीट नियंत्रण टिप्स", "icon": "🌿"},
        {"id": "q5", "text": "मानसून में सावधानियां", "icon": "🌧️"},
        {"id": "q6", "text": "स्वस्थ टमाटर कैसे उगाएं?", "icon": "📈"},
    ],
    "te": [
        {"id": "q1", "text": "నా టమాటా ఆకులపై గోధుమ రంగు మచ్చలు", "icon": "🍅"},
        {"id": "q2", "text": "ఆలస్య తుప్పును ఎలా నిరోధించాలి?", "icon": "🛡️"},
        {"id": "q3", "text": "ఆకు ముడతకు ఏ స్ప్రే?", "icon": "💊"},
        {"id": "q4", "text": "సేంద్రీయ పురుగు నియంత్రణ చిట్కాలు", "icon": "🌿"},
        {"id": "q5", "text": "వర్షాకాలం జాగ్రత్తలు", "icon": "🌧️"},
        {"id": "q6", "text": "ఆరోగ్యకరమైన టమాటాలు ఎలా పండించాలి?", "icon": "📈"},
    ],
    "ta": [
        {"id": "q1", "text": "என் தக்காளி இலைகளில் பழுப்பு புள்ளிகள்", "icon": "🍅"},
        {"id": "q2", "text": "தாமத கருகலை எவ்வாறு தடுப்பது?", "icon": "🛡️"},
        {"id": "q3", "text": "இலை சுருட்டைக்கு என்ன தெளிப்பு?", "icon": "💊"},
        {"id": "q4", "text": "இயற்கை பூச்சி கட்டுப்பாட்டு குறிப்புகள்", "icon": "🌿"},
        {"id": "q5", "text": "பருவமழை முன்னெச்சரிக்கைகள்", "icon": "🌧️"},
        {"id": "q6", "text": "ஆரோக்கியமான தக்காளி வளர்ப்பது எப்படி?", "icon": "📈"},
    ],
    "kn": [
        {"id": "q1", "text": "ನನ್ನ ಟೊಮೇಟೊ ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಕಲೆಗಳು", "icon": "🍅"},
        {"id": "q2", "text": "ತಡವಾದ ಬ್ಲೈಟ್ ತಡೆಯುವುದು ಹೇಗೆ?", "icon": "🛡️"},
        {"id": "q3", "text": "ಎಲೆ ಸುರುಳಿಗೆ ಯಾವ ಸ್ಪ್ರೇ?", "icon": "💊"},
        {"id": "q4", "text": "ಸಾವಯವ ಕೀಟ ನಿಯಂತ್ರಣ ಸಲಹೆಗಳು", "icon": "🌿"},
        {"id": "q5", "text": "ಮಳೆಗಾಲದ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು", "icon": "🌧️"},
        {"id": "q6", "text": "ಆರೋಗ್ಯಕರ ಟೊಮೇಟೊ ಬೆಳೆಯುವುದು ಹೇಗೆ?", "icon": "📈"},
    ]
}


@router.get("/quick-questions")
async def get_quick_questions(language: str = "en"):
    """
    Get quick question buttons for the chat interface
    """
    questions = QUICK_QUESTIONS.get(language, QUICK_QUESTIONS["en"])
    return {"questions": questions, "language": language}
