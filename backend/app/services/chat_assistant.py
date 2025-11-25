"""
AgroSentinel AI Chat Assistant
Multi-language agricultural knowledge assistant for Indian farmers
"""

from typing import Dict, List, Optional
import re
from datetime import datetime

# Knowledge base for crop diseases and farming
KNOWLEDGE_BASE = {
    # Disease information
    "diseases": {
        "bacterial_spot": {
            "symptoms": "Small, water-soaked spots on leaves that turn brown with yellow halos. Spots may merge causing leaf drop.",
            "causes": "Caused by Xanthomonas bacteria, spreads through rain splash, contaminated seeds, and tools.",
            "prevention": "Use disease-free seeds, avoid overhead irrigation, maintain plant spacing, remove infected debris.",
            "crops_affected": ["tomato", "pepper", "chili"]
        },
        "early_blight": {
            "symptoms": "Dark brown to black spots with concentric rings (target-like pattern) on lower leaves first.",
            "causes": "Fungus Alternaria solani, favored by warm humid conditions (24-29°C), spreads by wind and rain.",
            "prevention": "Crop rotation (3 years), remove plant debris, mulching, avoid overhead watering.",
            "crops_affected": ["tomato", "potato"]
        },
        "late_blight": {
            "symptoms": "Water-soaked spots that rapidly turn brown/black, white fuzzy growth underneath leaves in humid conditions.",
            "causes": "Phytophthora infestans oomycete, spreads very rapidly in cool wet weather (10-25°C).",
            "prevention": "CRITICAL: Act immediately! Remove infected plants, avoid overhead irrigation, use resistant varieties.",
            "crops_affected": ["tomato", "potato"]
        },
        "leaf_mold": {
            "symptoms": "Yellow spots on upper leaf surface, olive-green to grayish fuzzy growth on lower surface.",
            "causes": "Fungus Passalora fulva, thrives in high humidity (>85%) and moderate temperatures.",
            "prevention": "Improve air circulation, reduce humidity, use resistant varieties, remove infected leaves.",
            "crops_affected": ["tomato"]
        },
        "mosaic_virus": {
            "symptoms": "Mottled light and dark green pattern on leaves, leaf curling, stunted growth, reduced fruit size.",
            "causes": "Tobacco Mosaic Virus (TMV), spread by contact, contaminated tools, hands (especially smokers).",
            "prevention": "No cure! Remove infected plants, wash hands, disinfect tools, use resistant varieties.",
            "crops_affected": ["tomato", "pepper", "tobacco"]
        },
        "septoria_leaf_spot": {
            "symptoms": "Small circular spots with dark borders and gray centers with tiny black dots (pycnidia).",
            "causes": "Fungus Septoria lycopersici, survives in plant debris, spreads by rain splash.",
            "prevention": "Remove lower leaves, mulch soil, avoid overhead watering, crop rotation.",
            "crops_affected": ["tomato"]
        },
        "spider_mites": {
            "symptoms": "Tiny yellow or white speckles on leaves, fine webbing on undersides, leaves turn bronze and dry.",
            "causes": "Two-spotted spider mites, thrive in hot dry conditions, rapid reproduction.",
            "prevention": "Regular water spray on leaves, maintain humidity, introduce predatory mites.",
            "crops_affected": ["tomato", "pepper", "beans", "cucumber"]
        },
        "target_spot": {
            "symptoms": "Brown spots with concentric rings and yellow halos, can affect leaves, stems, and fruits.",
            "causes": "Fungus Corynespora cassiicola, favored by warm wet conditions.",
            "prevention": "Improve air circulation, avoid overhead irrigation, fungicide sprays.",
            "crops_affected": ["tomato", "cucumber", "cotton"]
        },
        "yellow_leaf_curl": {
            "symptoms": "Upward curling and yellowing of leaves, stunted growth, flower drop, very few fruits.",
            "causes": "Tomato Yellow Leaf Curl Virus (TYLCV), transmitted by whiteflies.",
            "prevention": "Control whiteflies! Use yellow sticky traps, neem oil, remove infected plants immediately.",
            "crops_affected": ["tomato"]
        }
    },
    
    # Crop information
    "crops": {
        "tomato": {
            "season": "Rabi (October-February) and Kharif (June-September) in India",
            "soil": "Well-drained loamy soil with pH 6.0-7.0",
            "spacing": "60cm x 45cm for field, 45cm x 30cm for hybrid",
            "water": "Regular watering, avoid water stress during flowering and fruit set",
            "fertilizer": "NPK 120:60:60 kg/ha, split application recommended",
            "harvest": "60-90 days after transplanting depending on variety"
        },
        "potato": {
            "season": "Rabi (October-December planting) in North India, Kharif in hills",
            "soil": "Sandy loam, well-drained, pH 5.5-6.5",
            "spacing": "60cm x 20cm, seed tuber 30-40g",
            "water": "Critical at stolon formation and tuber bulking",
            "fertilizer": "NPK 150:60:100 kg/ha",
            "harvest": "90-120 days, when vines start yellowing"
        },
        "pepper": {
            "season": "Kharif (June-July) and Rabi (September-October)",
            "soil": "Well-drained loamy soil, pH 6.0-6.5",
            "spacing": "45cm x 45cm",
            "water": "Regular irrigation, sensitive to water stress",
            "fertilizer": "NPK 100:50:50 kg/ha",
            "harvest": "60-90 days after transplanting"
        }
    },
    
    # Weather and risk information
    "weather_risks": {
        "high_humidity": "High humidity (>80%) increases risk of fungal diseases like late blight, leaf mold. Improve ventilation and reduce watering.",
        "hot_dry": "Hot dry weather favors spider mites. Increase humidity, water frequently, use shade nets.",
        "cool_wet": "Cool wet conditions are ideal for late blight and downy mildew. Apply preventive fungicides.",
        "monsoon": "During monsoon, ensure proper drainage, avoid water logging, increase fungicide applications."
    },
    
    # General farming tips
    "tips": {
        "organic_pest_control": "Use neem oil (5ml/L), garlic-chili spray, tobacco decoction for organic pest control.",
        "soil_health": "Add organic matter, practice crop rotation, use green manures, maintain soil pH.",
        "seed_treatment": "Treat seeds with Thiram/Captan @ 2-3g/kg seed before sowing for disease prevention.",
        "integrated_management": "Combine cultural, biological, and chemical methods for best results. Start with prevention."
    }
}

# Multi-language responses
RESPONSES = {
    "en": {
        "greeting": "Hello! I'm AgroSentinel Assistant. I can help you with crop diseases, treatments, and farming tips. What would you like to know?",
        "not_understood": "I'm sorry, I didn't quite understand that. Could you please ask about crop diseases, treatments, or farming tips?",
        "disease_info": "Here's information about {disease}:",
        "crop_info": "Here's information about growing {crop}:",
        "treatment_info": "For {disease}, here's the recommended treatment:",
        "prevention_info": "To prevent {disease}:",
        "weather_advice": "Based on current weather conditions:",
        "helpful_tips": "Here are some helpful farming tips:",
        "ask_more": "Is there anything else you'd like to know?",
        "emergency": "⚠️ URGENT: This appears to be a serious disease outbreak. Take immediate action!",
    },
    "hi": {
        "greeting": "नमस्ते! मैं एग्रोसेंटिनेल असिस्टेंट हूं। मैं फसल रोगों, उपचार और खेती की जानकारी में आपकी मदद कर सकता हूं। आप क्या जानना चाहते हैं?",
        "not_understood": "क्षमा करें, मैं समझ नहीं पाया। कृपया फसल रोगों, उपचार या खेती के बारे में पूछें।",
        "disease_info": "{disease} के बारे में जानकारी:",
        "crop_info": "{crop} उगाने के बारे में जानकारी:",
        "treatment_info": "{disease} के लिए उपचार:",
        "prevention_info": "{disease} से बचाव के लिए:",
        "weather_advice": "मौसम की स्थिति के अनुसार:",
        "helpful_tips": "कुछ उपयोगी खेती के टिप्स:",
        "ask_more": "क्या आप कुछ और जानना चाहते हैं?",
        "emergency": "⚠️ तुरंत कार्रवाई करें! यह गंभीर रोग का प्रकोप है।",
    },
    "te": {
        "greeting": "నమస్కారం! నేను అగ్రోసెంటినెల్ అసిస్టెంట్. పంట వ్యాధులు, చికిత్సలు మరియు వ్యవసాయ చిట్కాలలో మీకు సహాయం చేయగలను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
        "not_understood": "క్షమించండి, నాకు అర్థం కాలేదు. దయచేసి పంట వ్యాధులు, చికిత్సలు లేదా వ్యవసాయం గురించి అడగండి.",
        "disease_info": "{disease} గురించి సమాచారం:",
        "crop_info": "{crop} సాగు గురించి సమాచారం:",
        "treatment_info": "{disease} కోసం చికిత్స:",
        "prevention_info": "{disease} నివారణ కోసం:",
        "weather_advice": "వాతావరణ పరిస్థితుల ఆధారంగా:",
        "helpful_tips": "కొన్ని ఉపయోగకరమైన వ్యవసాయ చిట్కాలు:",
        "ask_more": "మీరు ఇంకేమైనా తెలుసుకోవాలనుకుంటున్నారా?",
        "emergency": "⚠️ అత్యవసరం: ఇది తీవ్రమైన వ్యాధి ప్రకోపం. వెంటనే చర్య తీసుకోండి!",
    },
    "ta": {
        "greeting": "வணக்கம்! நான் அக்ரோசெண்டினெல் உதவியாளர். பயிர் நோய்கள், சிகிச்சைகள் மற்றும் விவசாய குறிப்புகளில் உங்களுக்கு உதவ முடியும். நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?",
        "not_understood": "மன்னிக்கவும், நான் புரிந்து கொள்ளவில்லை. தயவுசெய்து பயிர் நோய்கள், சிகிச்சைகள் அல்லது விவசாயம் பற்றி கேளுங்கள்.",
        "disease_info": "{disease} பற்றிய தகவல்:",
        "crop_info": "{crop} வளர்ப்பு பற்றிய தகவல்:",
        "treatment_info": "{disease} சிகிச்சை:",
        "prevention_info": "{disease} தடுப்பு:",
        "weather_advice": "தற்போதைய வானிலை நிலைமைகளின் அடிப்படையில்:",
        "helpful_tips": "சில பயனுள்ள விவசாய குறிப்புகள்:",
        "ask_more": "வேறு ஏதாவது தெரிந்து கொள்ள விரும்புகிறீர்களா?",
        "emergency": "⚠️ அவசரம்: இது தீவிர நோய் பரவல். உடனடியாக நடவடிக்கை எடுங்கள்!",
    },
    "kn": {
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ಅಗ್ರೋಸೆಂಟಿನೆಲ್ ಸಹಾಯಕ. ಬೆಳೆ ರೋಗಗಳು, ಚಿಕಿತ್ಸೆಗಳು ಮತ್ತು ಕೃಷಿ ಸಲಹೆಗಳಲ್ಲಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ನೀವು ಏನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ?",
        "not_understood": "ಕ್ಷಮಿಸಿ, ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಬೆಳೆ ರೋಗಗಳು, ಚಿಕಿತ್ಸೆಗಳು ಅಥವಾ ಕೃಷಿ ಬಗ್ಗೆ ಕೇಳಿ.",
        "disease_info": "{disease} ಬಗ್ಗೆ ಮಾಹಿತಿ:",
        "crop_info": "{crop} ಬೆಳೆಯುವ ಬಗ್ಗೆ ಮಾಹಿತಿ:",
        "treatment_info": "{disease} ಚಿಕಿತ್ಸೆ:",
        "prevention_info": "{disease} ತಡೆಗಟ್ಟುವಿಕೆ:",
        "weather_advice": "ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ:",
        "helpful_tips": "ಕೆಲವು ಉಪಯುಕ್ತ ಕೃಷಿ ಸಲಹೆಗಳು:",
        "ask_more": "ಬೇರೆ ಏನಾದರೂ ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಾ?",
        "emergency": "⚠️ ತುರ್ತು: ಇದು ತೀವ್ರ ರೋಗ ಹರಡುವಿಕೆ. ತಕ್ಷಣ ಕ್ರಮ ತೆಗೆದುಕೊಳ್ಳಿ!",
    }
}

# Keywords for intent detection (multi-language)
KEYWORDS = {
    "disease": ["disease", "blight", "spot", "virus", "mold", "infection", "problem", "issue",
                "रोग", "बीमारी", "संक्रमण", "समस्या",
                "వ్యాధి", "రోగం", "సమస్య",
                "நோய்", "தொற்று", "பிரச்சனை",
                "ರೋಗ", "ಸಮಸ್ಯೆ"],
    "treatment": ["treatment", "cure", "spray", "medicine", "remedy", "solve", "fix",
                  "उपचार", "इलाज", "दवाई", "स्प्रे",
                  "చికిత్స", "మందు", "స్ప్రే",
                  "சிகிச்சை", "மருந்து", "தீர்வு",
                  "ಚಿಕಿತ್ಸೆ", "ಔಷಧಿ"],
    "prevention": ["prevent", "protection", "avoid", "stop",
                   "बचाव", "रोकथाम", "सुरक्षा",
                   "నివారణ", "రక్షణ",
                   "தடுப்பு", "பாதுகாப்பு",
                   "ತಡೆಗಟ್ಟುವಿಕೆ", "ರಕ್ಷಣೆ"],
    "crop": ["tomato", "potato", "pepper", "chili", "crop", "plant",
             "टमाटर", "आलू", "मिर्च", "फसल", "पौधा",
             "టమాటా", "బంగాళాదుంప", "మిరప", "పంట",
             "தக்காளி", "உருளைக்கிழங்கு", "மிளகாய்", "பயிர்",
             "ಟೊಮೇಟೊ", "ಆಲೂಗಡ್ಡೆ", "ಮೆಣಸಿನಕಾಯಿ", "ಬೆಳೆ"],
    "weather": ["weather", "rain", "humidity", "temperature", "monsoon",
                "मौसम", "बारिश", "नमी", "तापमान",
                "వాతావరణం", "వర్షం", "తేమ",
                "வானிலை", "மழை", "ஈரப்பதம்",
                "ಹವಾಮಾನ", "ಮಳೆ", "ತೇವಾಂಶ"],
    "greeting": ["hello", "hi", "help", "start", "namaste",
                 "नमस्ते", "हेलो", "मदद",
                 "నమస్కారం", "హలో", "సహాయం",
                 "வணக்கம்", "ஹலோ", "உதவி",
                 "ನಮಸ್ಕಾರ", "ಹಲೋ", "ಸಹಾಯ"],
    "tips": ["tips", "advice", "suggestion", "help", "guide",
             "टिप्स", "सलाह", "सुझाव",
             "చిట్కాలు", "సలహా",
             "குறிப்புகள்", "ஆலோசனை",
             "ಸಲಹೆಗಳು", "ಸಲಹೆ"]
}

# Disease name mappings
DISEASE_MAPPINGS = {
    "bacterial spot": "bacterial_spot",
    "early blight": "early_blight",
    "late blight": "late_blight",
    "leaf mold": "leaf_mold",
    "mosaic virus": "mosaic_virus",
    "mosaic": "mosaic_virus",
    "septoria": "septoria_leaf_spot",
    "septoria leaf spot": "septoria_leaf_spot",
    "spider mites": "spider_mites",
    "spider mite": "spider_mites",
    "mites": "spider_mites",
    "target spot": "target_spot",
    "yellow leaf curl": "yellow_leaf_curl",
    "leaf curl": "yellow_leaf_curl",
    "tylcv": "yellow_leaf_curl",
    "blight": "late_blight",
    "fungus": "early_blight",
    "virus": "mosaic_virus"
}

# Crop name mappings
CROP_MAPPINGS = {
    "tomato": "tomato",
    "टमाटर": "tomato",
    "టమాటా": "tomato",
    "தக்காளி": "tomato",
    "ಟೊಮೇಟೊ": "tomato",
    "potato": "potato",
    "आलू": "potato",
    "బంగాళాదుంప": "potato",
    "உருளைக்கிழங்கு": "potato",
    "ಆಲೂಗಡ್ಡೆ": "potato",
    "pepper": "pepper",
    "chili": "pepper",
    "मिर्च": "pepper",
    "మిరప": "pepper",
    "மிளகாய்": "pepper",
    "ಮೆಣಸಿನಕಾಯಿ": "pepper"
}


def detect_intent(message: str) -> str:
    """Detect the intent from user message"""
    message_lower = message.lower()
    
    # Check for greetings first
    for keyword in KEYWORDS["greeting"]:
        if keyword in message_lower:
            return "greeting"
    
    # Check for specific intents
    for intent, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent
    
    return "unknown"


def extract_disease(message: str) -> Optional[str]:
    """Extract disease name from message"""
    message_lower = message.lower()
    for name, key in DISEASE_MAPPINGS.items():
        if name in message_lower:
            return key
    return None


def extract_crop(message: str) -> Optional[str]:
    """Extract crop name from message"""
    message_lower = message.lower()
    for name, key in CROP_MAPPINGS.items():
        if name in message_lower:
            return key
    return None


def generate_response(message: str, language: str = "en", context: Optional[Dict] = None) -> Dict:
    """Generate AI response based on user message"""
    
    # Get language responses, default to English
    lang_responses = RESPONSES.get(language, RESPONSES["en"])
    
    # Detect intent
    intent = detect_intent(message)
    disease = extract_disease(message)
    crop = extract_crop(message)
    
    response_text = ""
    suggestions = []
    
    if intent == "greeting":
        response_text = lang_responses["greeting"]
        suggestions = get_suggestions(language)
        
    elif intent == "disease" or disease:
        if disease:
            disease_info = KNOWLEDGE_BASE["diseases"].get(disease, {})
            if disease_info:
                disease_display = disease.replace("_", " ").title()
                response_text = f"{lang_responses['disease_info'].format(disease=disease_display)}\n\n"
                response_text += f"**Symptoms:** {disease_info.get('symptoms', 'N/A')}\n\n"
                response_text += f"**Causes:** {disease_info.get('causes', 'N/A')}\n\n"
                response_text += f"**Prevention:** {disease_info.get('prevention', 'N/A')}\n\n"
                response_text += f"**Affected Crops:** {', '.join(disease_info.get('crops_affected', []))}"
                
                # Add emergency warning for critical diseases
                if disease in ["late_blight", "yellow_leaf_curl"]:
                    response_text = lang_responses["emergency"] + "\n\n" + response_text
                    
                suggestions = ["How to treat this?", "Prevention tips", "Other diseases"]
        else:
            response_text = "Please specify which disease you'd like to know about:\n\n"
            response_text += "• Bacterial Spot\n• Early Blight\n• Late Blight\n• Leaf Mold\n"
            response_text += "• Mosaic Virus\n• Septoria Leaf Spot\n• Spider Mites\n"
            response_text += "• Target Spot\n• Yellow Leaf Curl Virus"
            suggestions = ["Early blight info", "Late blight treatment", "Mosaic virus"]
            
    elif intent == "treatment":
        if disease:
            disease_info = KNOWLEDGE_BASE["diseases"].get(disease, {})
            disease_display = disease.replace("_", " ").title()
            response_text = f"{lang_responses['treatment_info'].format(disease=disease_display)}\n\n"
            
            # Get treatment from disease_data
            from app.services.disease_data import REMEDIES
            remedy = REMEDIES.get(f"tomato_{disease}", REMEDIES.get(f"potato_{disease}", REMEDIES.get(f"pepper_{disease}", {})))
            
            if remedy:
                response_text += f"**Chemical Treatment:** {remedy.get('spray', 'Consult local expert')}\n\n"
                response_text += f"**Application:** Every {remedy.get('repeat', '7-10 days')}\n\n"
                response_text += f"**Organic Alternative:** {remedy.get('organic', 'Neem oil spray')}\n\n"
                response_text += f"**Precautions:** {remedy.get('precautions', 'Follow safety guidelines')}"
            else:
                response_text += "Please consult your local agricultural officer for specific treatment."
                
            suggestions = ["Prevention tips", "Organic options", "Application frequency"]
        else:
            response_text = "Which disease treatment are you looking for?\n\n"
            response_text += "I can help with treatments for bacterial spot, early blight, late blight, leaf mold, and more."
            suggestions = ["Late blight treatment", "Spider mites treatment", "Mosaic virus cure"]
            
    elif intent == "prevention":
        if disease:
            disease_info = KNOWLEDGE_BASE["diseases"].get(disease, {})
            disease_display = disease.replace("_", " ").title()
            response_text = f"{lang_responses['prevention_info'].format(disease=disease_display)}\n\n"
            response_text += disease_info.get('prevention', 'Practice crop rotation and maintain good field hygiene.')
            suggestions = ["Treatment options", "Organic methods", "Weather precautions"]
        else:
            response_text = "Here are general prevention tips:\n\n"
            response_text += "• Use disease-free certified seeds\n"
            response_text += "• Practice 3-year crop rotation\n"
            response_text += "• Remove infected plant debris\n"
            response_text += "• Avoid overhead irrigation\n"
            response_text += "• Maintain proper plant spacing\n"
            response_text += "• Apply preventive fungicides before monsoon"
            suggestions = ["Specific disease prevention", "Organic prevention", "Seed treatment"]
            
    elif intent == "crop" or crop:
        if crop:
            crop_info = KNOWLEDGE_BASE["crops"].get(crop, {})
            crop_display = crop.title()
            response_text = f"{lang_responses['crop_info'].format(crop=crop_display)}\n\n"
            response_text += f"**Season:** {crop_info.get('season', 'N/A')}\n\n"
            response_text += f"**Soil:** {crop_info.get('soil', 'N/A')}\n\n"
            response_text += f"**Spacing:** {crop_info.get('spacing', 'N/A')}\n\n"
            response_text += f"**Water:** {crop_info.get('water', 'N/A')}\n\n"
            response_text += f"**Fertilizer:** {crop_info.get('fertilizer', 'N/A')}\n\n"
            response_text += f"**Harvest:** {crop_info.get('harvest', 'N/A')}"
            suggestions = [f"{crop_display} diseases", f"{crop_display} pests", "Fertilizer schedule"]
        else:
            response_text = "I can help with information about:\n\n"
            response_text += "🍅 **Tomato** - Growing, diseases, treatments\n"
            response_text += "🥔 **Potato** - Cultivation, blight management\n"
            response_text += "🌶️ **Pepper/Chili** - Care and disease control"
            suggestions = ["Tomato growing tips", "Potato diseases", "Pepper care"]
            
    elif intent == "weather":
        response_text = f"{lang_responses['weather_advice']}\n\n"
        response_text += "**High Humidity (>80%):**\n"
        response_text += KNOWLEDGE_BASE["weather_risks"]["high_humidity"] + "\n\n"
        response_text += "**Hot & Dry:**\n"
        response_text += KNOWLEDGE_BASE["weather_risks"]["hot_dry"] + "\n\n"
        response_text += "**Monsoon Season:**\n"
        response_text += KNOWLEDGE_BASE["weather_risks"]["monsoon"]
        suggestions = ["Disease risk today", "Preventive sprays", "Weather forecast"]
        
    elif intent == "tips":
        response_text = f"{lang_responses['helpful_tips']}\n\n"
        response_text += "**Organic Pest Control:**\n"
        response_text += KNOWLEDGE_BASE["tips"]["organic_pest_control"] + "\n\n"
        response_text += "**Soil Health:**\n"
        response_text += KNOWLEDGE_BASE["tips"]["soil_health"] + "\n\n"
        response_text += "**Seed Treatment:**\n"
        response_text += KNOWLEDGE_BASE["tips"]["seed_treatment"] + "\n\n"
        response_text += "**Integrated Management:**\n"
        response_text += KNOWLEDGE_BASE["tips"]["integrated_management"]
        suggestions = ["Organic farming", "Pest control", "Fertilizer tips"]
        
    else:
        response_text = lang_responses["not_understood"]
        suggestions = get_suggestions(language)
    
    # Add follow-up
    if response_text and intent != "greeting" and intent != "unknown":
        response_text += f"\n\n{lang_responses['ask_more']}"
    
    return {
        "response": response_text,
        "suggestions": suggestions,
        "intent": intent,
        "detected_disease": disease,
        "detected_crop": crop,
        "language": language,
        "timestamp": datetime.now().isoformat()
    }


def get_suggestions(language: str = "en") -> List[str]:
    """Get suggested questions based on language"""
    suggestions = {
        "en": ["What is late blight?", "How to grow tomatoes?", "Treatment for leaf curl", "Weather precautions"],
        "hi": ["झुलसा रोग क्या है?", "टमाटर कैसे उगाएं?", "पत्ता मोड़ का इलाज", "मौसम सावधानियां"],
        "te": ["ఆలస్య తుప్పు అంటే ఏమిటి?", "టమాటాలు ఎలా పండించాలి?", "ఆకు ముడత చికిత్స", "వాతావరణ జాగ్రత్తలు"],
        "ta": ["தாமத கருகல் என்றால் என்ன?", "தக்காளி எப்படி வளர்ப்பது?", "இலை சுருட்டை சிகிச்சை", "வானிலை முன்னெச்சரிக்கைகள்"],
        "kn": ["ತಡವಾದ ಬ್ಲೈಟ್ ಎಂದರೇನು?", "ಟೊಮೇಟೊ ಬೆಳೆಯುವುದು ಹೇಗೆ?", "ಎಲೆ ಸುರುಳಿ ಚಿಕಿತ್ಸೆ", "ಹವಾಮಾನ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು"]
    }
    return suggestions.get(language, suggestions["en"])


# Quick response for common questions
QUICK_RESPONSES = {
    "what is late blight": "late_blight",
    "what is early blight": "early_blight",
    "leaf curl": "yellow_leaf_curl",
    "my tomato leaves are curling": "yellow_leaf_curl",
    "brown spots on leaves": "early_blight",
    "white spots on leaves": "leaf_mold",
    "yellow spots": "bacterial_spot",
    "plant is dying": "late_blight"
}
