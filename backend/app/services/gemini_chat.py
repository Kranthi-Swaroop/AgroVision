"""
AgroSentinel Gemini AI Chat Service
Uses Google's Gemini API for intelligent agricultural assistance
"""

import google.generativeai as genai
from typing import Optional, Dict, List
from datetime import datetime
import json

# Agricultural context for the AI
SYSTEM_CONTEXT = """You are AgroSentinel AI Assistant, an expert agricultural advisor specializing in crop disease detection and management for Indian farmers. You have deep knowledge about:

## SUPPORTED CROPS & DISEASES:

### Tomato Diseases:
1. **Tomato Bacterial Spot** (Xanthomonas)
   - Symptoms: Small, water-soaked spots on leaves turning brown with yellow halos
   - Treatment: Copper hydroxide @ 2g/L or Streptomycin sulphate @ 0.5g/L every 7-10 days
   - Organic: Neem oil spray @ 5ml/L
   - Severity: Medium, 10-50% yield loss if untreated

2. **Tomato Early Blight** (Alternaria solani)
   - Symptoms: Dark brown spots with concentric rings (target-like) on lower leaves
   - Treatment: Mancozeb 75WP @ 2.5g/L or Chlorothalonil @ 2g/L every 7-10 days
   - Organic: Copper fungicide, compost tea
   - Severity: High, 20-50% yield loss

3. **Tomato Late Blight** (Phytophthora infestans) - CRITICAL!
   - Symptoms: Water-soaked spots rapidly turning brown/black, white fuzzy growth underneath
   - Treatment: Metalaxyl + Mancozeb @ 2.5g/L or Cymoxanil + Mancozeb @ 3g/L every 5-7 days
   - URGENT: Destroy infected plants immediately!
   - Severity: Critical, 70-100% yield loss, spreads rapidly in cool wet weather

4. **Tomato Leaf Mold** (Passalora fulva)
   - Symptoms: Yellow spots on upper leaf, olive-green fuzzy growth underneath
   - Treatment: Chlorothalonil @ 2g/L or Mancozeb @ 2.5g/L every 7-10 days
   - Improve ventilation, reduce humidity
   - Severity: Medium, 10-30% yield loss

5. **Tomato Mosaic Virus** (TMV)
   - Symptoms: Mottled light/dark green pattern, leaf curling, stunted growth
   - NO CURE! Remove and destroy infected plants
   - Spread by contact, tools, hands (especially smokers)
   - Use resistant varieties, disinfect tools
   - Severity: High, 20-70% yield loss

6. **Tomato Septoria Leaf Spot**
   - Symptoms: Small circular spots with dark borders, gray centers with black dots
   - Treatment: Chlorothalonil @ 2g/L or Mancozeb @ 2.5g/L
   - Remove lower leaves, mulch soil
   - Severity: Medium, 10-40% yield loss

7. **Tomato Spider Mites**
   - Symptoms: Yellow/white speckles, fine webbing, leaves turn bronze
   - Treatment: Dicofol @ 2ml/L or Abamectin @ 0.5ml/L
   - Organic: Neem oil, water spray, predatory mites
   - Severity: Medium, can be severe in hot dry conditions

8. **Tomato Target Spot** (Corynespora)
   - Symptoms: Brown spots with concentric rings and yellow halos
   - Treatment: Azoxystrobin @ 1ml/L or Difenoconazole @ 0.5ml/L
   - Severity: Medium, 15-40% yield loss

9. **Tomato Yellow Leaf Curl Virus** (TYLCV) - CRITICAL!
   - Symptoms: Upward curling and yellowing, stunted growth, flower drop
   - Transmitted by whiteflies - CONTROL WHITEFLIES!
   - Treatment: Yellow sticky traps, Imidacloprid @ 0.3ml/L for whiteflies
   - Remove infected plants immediately
   - Severity: Critical, 50-100% yield loss

### Potato Diseases:
1. **Potato Early Blight** - Same as tomato early blight
2. **Potato Late Blight** - Same as tomato, VERY CRITICAL for potato!

### Pepper/Chili Diseases:
1. **Pepper Bacterial Spot** - Similar to tomato bacterial spot

## CROP CULTIVATION GUIDES:

### Tomato Cultivation (India):
- Season: Rabi (Oct-Feb), Kharif (Jun-Sep)
- Soil: Well-drained loamy, pH 6.0-7.0
- Spacing: 60cm x 45cm
- Fertilizer: NPK 120:60:60 kg/ha
- Harvest: 60-90 days after transplanting

### Potato Cultivation:
- Season: Rabi (Oct-Dec planting) in North India
- Soil: Sandy loam, pH 5.5-6.5
- Spacing: 60cm x 20cm
- Fertilizer: NPK 150:60:100 kg/ha
- Harvest: 90-120 days

### Pepper Cultivation:
- Season: Kharif (Jun-Jul), Rabi (Sep-Oct)
- Soil: Well-drained loamy, pH 6.0-6.5
- Spacing: 45cm x 45cm
- Fertilizer: NPK 100:50:50 kg/ha

## WEATHER-BASED ADVICE:
- High humidity (>80%): Risk of fungal diseases, apply preventive fungicides
- Hot & dry: Watch for spider mites, increase watering
- Cool & wet: HIGH RISK of late blight, apply protective sprays
- Monsoon: Ensure drainage, increase fungicide frequency

## ORGANIC ALTERNATIVES:
- Neem oil: General pest/fungus control @ 5ml/L
- Trichoderma: Soil-borne disease prevention
- Pseudomonas: Bacterial disease control
- Bordeaux mixture: Traditional copper fungicide
- Cow urine spray: Traditional organic pesticide

## GUIDELINES FOR RESPONSES:
1. Always be helpful and practical for Indian farmers
2. Provide specific dosages and application frequencies
3. Mention both chemical and organic alternatives
4. Warn about critical diseases that need immediate action
5. Consider local Indian conditions and available products
6. Use simple language, avoid overly technical jargon
7. If asked in Hindi/Telugu/Tamil/Kannada, respond in that language
8. Always recommend consulting local agricultural officers for serious outbreaks
9. Provide preventive measures, not just treatments
10. Be encouraging and supportive to farmers

Remember: You are helping real farmers protect their livelihoods. Be accurate, helpful, and practical."""

class GeminiChatService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        self.chat_sessions: Dict[str, any] = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 1024,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
        except Exception as e:
            print(f"[GeminiChat] Failed to initialize: {e}")
            self.model = None
    
    def get_or_create_session(self, session_id: str):
        """Get existing chat session or create new one"""
        if session_id not in self.chat_sessions:
            if self.model:
                chat = self.model.start_chat(history=[])
                # Send system context as first message
                try:
                    chat.send_message(f"SYSTEM CONTEXT (remember this for all responses):\n{SYSTEM_CONTEXT}")
                    self.chat_sessions[session_id] = chat
                except Exception as e:
                    print(f"[GeminiChat] Failed to initialize session: {e}")
                    return None
        return self.chat_sessions.get(session_id)
    
    async def send_message(self, message: str, language: str = "en", session_id: str = None) -> Dict:
        """Send message to Gemini and get response"""
        
        if not self.model:
            return self._fallback_response(message, language)
        
        try:
            # Add language instruction if not English
            lang_instruction = ""
            if language == "hi":
                lang_instruction = "Please respond in Hindi (हिंदी में जवाब दें). "
            elif language == "te":
                lang_instruction = "Please respond in Telugu (తెలుగులో సమాధానం ఇవ్వండి). "
            elif language == "ta":
                lang_instruction = "Please respond in Tamil (தமிழில் பதிலளிக்கவும்). "
            elif language == "kn":
                lang_instruction = "Please respond in Kannada (ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ). "
            
            full_message = f"{lang_instruction}{message}"
            
            # Get or create session
            chat = self.get_or_create_session(session_id or "default")
            
            if chat:
                response = chat.send_message(full_message)
                response_text = response.text
            else:
                # Single message mode without session
                response = self.model.generate_content(
                    f"{SYSTEM_CONTEXT}\n\nUser question: {full_message}"
                )
                response_text = response.text
            
            # Generate suggestions based on response
            suggestions = self._generate_suggestions(message, language)
            
            return {
                "response": response_text,
                "suggestions": suggestions,
                "intent": "gemini_response",
                "detected_disease": None,
                "detected_crop": None,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "model": "gemini-2.0-flash"
            }
            
        except Exception as e:
            print(f"[GeminiChat] Error: {e}")
            return self._fallback_response(message, language)
    
    def _generate_suggestions(self, message: str, language: str) -> List[str]:
        """Generate follow-up suggestions based on conversation"""
        message_lower = message.lower()
        
        suggestions_map = {
            "en": {
                "disease": ["How to prevent this?", "Organic treatment options", "When to spray?"],
                "treatment": ["Application frequency?", "Safety precautions", "Cost-effective alternatives"],
                "crop": ["Common diseases", "Best varieties for my region", "Fertilizer schedule"],
                "default": ["Disease identification help", "Organic farming tips", "Weather precautions"]
            },
            "hi": {
                "disease": ["इसे कैसे रोकें?", "जैविक उपचार", "स्प्रे कब करें?"],
                "treatment": ["कितनी बार लगाएं?", "सुरक्षा सावधानियां", "सस्ते विकल्प"],
                "crop": ["आम रोग", "अच्छी किस्में", "खाद अनुसूची"],
                "default": ["रोग पहचान", "जैविक खेती टिप्स", "मौसम सावधानियां"]
            },
            "te": {
                "disease": ["దీన్ని ఎలా నివారించాలి?", "సేంద్రీయ చికిత్స", "స్ప్రే ఎప్పుడు?"],
                "treatment": ["ఎంత తరచుగా?", "భద్రతా జాగ్రత్తలు", "చౌకైన ప్రత్యామ్నాయాలు"],
                "default": ["వ్యాధి గుర్తింపు", "సేంద్రీయ వ్యవసాయం", "వాతావరణ జాగ్రత్తలు"]
            },
            "ta": {
                "disease": ["இதை எவ்வாறு தடுப்பது?", "இயற்கை சிகிச்சை", "எப்போது தெளிப்பது?"],
                "treatment": ["எத்தனை முறை?", "பாதுகாப்பு நடவடிக்கைகள்", "மலிவான மாற்றுகள்"],
                "default": ["நோய் அடையாளம்", "இயற்கை விவசாயம்", "வானிலை எச்சரிக்கைகள்"]
            },
            "kn": {
                "disease": ["ಇದನ್ನು ಹೇಗೆ ತಡೆಯುವುದು?", "ಸಾವಯವ ಚಿಕಿತ್ಸೆ", "ಯಾವಾಗ ಸಿಂಪಡಿಸುವುದು?"],
                "treatment": ["ಎಷ್ಟು ಬಾರಿ?", "ಸುರಕ್ಷತಾ ಕ್ರಮಗಳು", "ಅಗ್ಗದ ಪರ್ಯಾಯಗಳು"],
                "default": ["ರೋಗ ಗುರುತಿಸುವಿಕೆ", "ಸಾವಯವ ಕೃಷಿ", "ಹವಾಮಾನ ಎಚ್ಚರಿಕೆಗಳು"]
            }
        }
        
        lang_suggestions = suggestions_map.get(language, suggestions_map["en"])
        
        # Detect topic
        if any(word in message_lower for word in ["disease", "blight", "spot", "virus", "रोग", "వ్యాధి", "நோய்", "ರೋಗ"]):
            return lang_suggestions.get("disease", lang_suggestions["default"])
        elif any(word in message_lower for word in ["treatment", "spray", "medicine", "उपचार", "చికిత్స", "சிகிச்சை", "ಚಿಕಿತ್ಸೆ"]):
            return lang_suggestions.get("treatment", lang_suggestions["default"])
        elif any(word in message_lower for word in ["tomato", "potato", "pepper", "crop", "टमाटर", "టమాటా", "தக்காளி", "ಟೊಮೇಟೊ"]):
            return lang_suggestions.get("crop", lang_suggestions["default"])
        
        return lang_suggestions["default"]
    
    def _fallback_response(self, message: str, language: str) -> Dict:
        """Fallback response when Gemini is unavailable"""
        fallback_messages = {
            "en": "I'm currently unable to connect to my AI service. Please try again in a moment, or check your internet connection.",
            "hi": "मैं वर्तमान में अपनी AI सेवा से कनेक्ट करने में असमर्थ हूं। कृपया कुछ देर बाद पुनः प्रयास करें।",
            "te": "నేను ప్రస్తుతం నా AI సేవకు కనెక్ట్ కాలేకపోతున్నాను. దయచేసి కొద్దిసేపట్లో మళ్ళీ ప్రయత్నించండి.",
            "ta": "என்னால் தற்போது AI சேவையுடன் இணைக்க முடியவில்லை. சிறிது நேரத்தில் மீண்டும் முயற்சிக்கவும்.",
            "kn": "ನಾನು ಪ್ರಸ್ತುತ ನನ್ನ AI ಸೇವೆಗೆ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದಲ್ಲಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
        }
        
        return {
            "response": fallback_messages.get(language, fallback_messages["en"]),
            "suggestions": ["Try again", "Check connection"],
            "intent": "fallback",
            "detected_disease": None,
            "detected_crop": None,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "model": "fallback"
        }
    
    def clear_session(self, session_id: str):
        """Clear a chat session"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]


# Singleton instance
_gemini_service: Optional[GeminiChatService] = None

def get_gemini_service(api_key: str) -> GeminiChatService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiChatService(api_key)
    return _gemini_service
