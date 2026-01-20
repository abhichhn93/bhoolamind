"""
BhoolamMind v1.5 - Emotion Tagger
Uses transformers to detect emotions, mood, and psychological states from text
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Install with: pip install transformers torch")

class EmotionTagger:
    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        """
        Initialize emotion detection pipeline
        Default model detects: anger, disgust, fear, joy, neutral, sadness, surprise
        """
        self.model_name = model_name
        self.emotion_pipeline = None
        self.sentiment_pipeline = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Emotion detection pipeline
                self.emotion_pipeline = pipeline(
                    "text-classification",
                    model=model_name,
                    tokenizer=model_name
                )
                
                # Sentiment analysis pipeline
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment"
                )
                
                print(f"✅ Emotion detection models loaded: {model_name}")
            except Exception as e:
                print(f"❌ Failed to load models: {e}")
                self.emotion_pipeline = None
                self.sentiment_pipeline = None
        
        # Bhoola-specific emotion mappings
        self.bhoola_emotions = {
            "high": ["euphoric", "creative", "philosophical", "giggly"],
            "anxious": ["nervous", "worried", "stressed", "overwhelmed"],
            "reflective": ["contemplative", "nostalgic", "introspective", "deep"],
            "horny": ["lustful", "romantic", "flirty", "attracted"],
            "sad": ["depressed", "melancholic", "lonely", "empty"],
            "confused": ["bewildered", "lost", "uncertain", "puzzled"],
            "excited": ["enthusiastic", "energetic", "pumped", "thrilled"],
            "tired": ["exhausted", "drained", "sleepy", "fatigued"]
        }
        
        # Hindi/Hinglish emotion indicators
        self.hinglish_emotions = {
            "khush": "joy",
            "udaas": "sadness", 
            "pareshan": "anxiety",
            "mast": "high",
            "confuse": "confusion",
            "excited": "excitement",
            "thak": "tired",
            "bore": "boredom",
            "romantic": "romantic",
            "horny": "horny"
        }
    
    def detect_emotions(self, text: str) -> Dict:
        """
        Analyze text for emotional content
        Returns comprehensive emotional analysis
        """
        analysis = {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "primary_emotion": "neutral",
            "emotion_scores": {},
            "sentiment": "neutral",
            "intensity": 1,
            "bhoola_mood": None,
            "hinglish_detected": False,
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for Hinglish emotion words
        text_lower = text.lower()
        for hinglish_word, emotion in self.hinglish_emotions.items():
            if hinglish_word in text_lower:
                analysis["hinglish_detected"] = True
                analysis["bhoola_mood"] = emotion
                break
        
        # Use transformer models if available
        if self.emotion_pipeline:
            try:
                # Get emotion predictions
                emotions = self.emotion_pipeline(text)
                
                if emotions:
                    # Primary emotion
                    primary = emotions[0]
                    analysis["primary_emotion"] = primary["label"]
                    analysis["confidence"] = primary["score"]
                    
                    # All emotion scores
                    analysis["emotion_scores"] = {
                        emotion["label"]: emotion["score"] 
                        for emotion in emotions
                    }
                    
                    # Map to Bhoola-specific moods
                    analysis["bhoola_mood"] = self._map_to_bhoola_mood(
                        analysis["primary_emotion"]
                    )
            
            except Exception as e:
                logging.warning(f"Emotion detection failed: {e}")
        
        # Sentiment analysis
        if self.sentiment_pipeline:
            try:
                sentiment_result = self.sentiment_pipeline(text)
                if sentiment_result:
                    analysis["sentiment"] = sentiment_result[0]["label"].lower()
            except Exception as e:
                logging.warning(f"Sentiment analysis failed: {e}")
        
        # Calculate intensity based on text patterns
        analysis["intensity"] = self._calculate_intensity(text)
        
        # Fallback emotion detection using keywords
        if not analysis["bhoola_mood"]:
            analysis["bhoola_mood"] = self._keyword_emotion_detection(text)
        
        return analysis
    
    def _map_to_bhoola_mood(self, standard_emotion: str) -> str:
        """Map standard emotions to Bhoola's specific mood categories"""
        emotion_mapping = {
            "joy": "khush",
            "happiness": "khush", 
            "sadness": "udaas",
            "anger": "gussa",
            "fear": "darr",
            "anxiety": "pareshan",
            "surprise": "shocked",
            "neutral": "normal",
            "disgust": "ghinn"
        }
        
        return emotion_mapping.get(standard_emotion.lower(), "normal")
    
    def _calculate_intensity(self, text: str) -> int:
        """Calculate emotional intensity from text patterns"""
        text_lower = text.lower()
        intensity = 1
        
        # High intensity indicators
        high_markers = [
            "!!!", "fucking", "amazing", "brilliant", "hilarious",
            "super", "extremely", "totally", "absolutely", "bahut",
            "bohat", "ekdum", "bilkul"
        ]
        
        # Medium intensity indicators  
        medium_markers = [
            "!!", "very", "quite", "really", "pretty", "kaafi", "thoda"
        ]
        
        # Count intensity markers
        high_count = sum(1 for marker in high_markers if marker in text_lower)
        medium_count = sum(1 for marker in medium_markers if marker in text_lower)
        
        if high_count >= 2 or "!!!" in text:
            intensity = 3
        elif high_count >= 1 or medium_count >= 2:
            intensity = 2
        
        # Check for ALL CAPS (indicates high intensity)
        caps_words = [word for word in text.split() if word.isupper() and len(word) > 2]
        if len(caps_words) >= 2:
            intensity = max(intensity, 3)
        elif len(caps_words) >= 1:
            intensity = max(intensity, 2)
        
        return intensity
    
    def _keyword_emotion_detection(self, text: str) -> str:
        """Fallback emotion detection using keyword matching"""
        text_lower = text.lower()
        
        emotion_keywords = {
            "anxious": ["nervous", "worried", "stressed", "anxiety", "pareshan", "tension"],
            "happy": ["happy", "good", "great", "awesome", "nice", "khush", "mast"],
            "sad": ["sad", "upset", "depressed", "down", "udaas", "dukhi"],
            "excited": ["excited", "thrilled", "pumped", "energy", "josh"],
            "tired": ["tired", "exhausted", "sleepy", "thak", "neend"],
            "confused": ["confused", "puzzled", "weird", "strange", "confuse"],
            "high": ["high", "stoned", "elevated", "philosophical", "deep"]
        }
        
        # Count matches for each emotion
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Return emotion with highest score
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        return "neutral"
    
    def analyze_mood_context(self, text: str, recent_history: List[str] = None) -> Dict:
        """
        Analyze mood considering recent conversation history
        Useful for detecting mood shifts and patterns
        """
        current_analysis = self.detect_emotions(text)
        
        if not recent_history:
            return current_analysis
        
        # Analyze recent emotions
        recent_emotions = []
        for hist_text in recent_history[-5:]:  # Last 5 interactions
            hist_emotion = self.detect_emotions(hist_text)
            recent_emotions.append(hist_emotion["bhoola_mood"])
        
        # Detect mood patterns
        mood_analysis = {
            **current_analysis,
            "mood_pattern": self._analyze_mood_pattern(recent_emotions),
            "mood_shift": self._detect_mood_shift(recent_emotions, current_analysis["bhoola_mood"]),
            "emotional_context": recent_emotions
        }
        
        return mood_analysis
    
    def _analyze_mood_pattern(self, recent_moods: List[str]) -> str:
        """Analyze patterns in recent moods"""
        if len(recent_moods) < 3:
            return "insufficient_data"
        
        # Check for consistency
        if len(set(recent_moods)) == 1:
            return "stable"
        
        # Check for escalation
        mood_values = {"sad": 1, "anxious": 2, "neutral": 3, "happy": 4, "excited": 5}
        values = [mood_values.get(mood, 3) for mood in recent_moods]
        
        if all(values[i] <= values[i+1] for i in range(len(values)-1)):
            return "improving"
        elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
            return "declining"
        else:
            return "fluctuating"
    
    def _detect_mood_shift(self, recent_moods: List[str], current_mood: str) -> Dict:
        """Detect significant mood shifts"""
        if not recent_moods:
            return {"shift_detected": False}
        
        last_mood = recent_moods[-1] if recent_moods else "neutral"
        
        # Define significant shifts
        significant_shifts = {
            ("sad", "excited"), ("anxious", "happy"), 
            ("happy", "sad"), ("excited", "anxious"),
            ("neutral", "high"), ("high", "sad")
        }
        
        shift_detected = (last_mood, current_mood) in significant_shifts
        
        return {
            "shift_detected": shift_detected,
            "from_mood": last_mood,
            "to_mood": current_mood,
            "shift_magnitude": abs(
                self._mood_to_numeric(current_mood) - self._mood_to_numeric(last_mood)
            )
        }
    
    def _mood_to_numeric(self, mood: str) -> int:
        """Convert mood to numeric value for comparison"""
        mood_scale = {
            "sad": 1, "anxious": 2, "confused": 3, "neutral": 4,
            "happy": 5, "excited": 6, "high": 7
        }
        return mood_scale.get(mood, 4)

# Test the emotion tagger
if __name__ == "__main__":
    tagger = EmotionTagger()
    
    test_texts = [
        "Yaar I'm feeling super anxious about tomorrow's performance",
        "Bhool gaya main kya bol raha tha... confused hu bilkul",
        "AMAZING set tonight!!! Audience was laughing throughout!!!",
        "Udaas feel kar raha hu... lonely vibes",
        "High hu thoda sa... philosophical thoughts aa rahe hai",
        "Mast day tha yaar, kaafi khush hu"
    ]
    
    print("🎭 BhoolamMind Emotion Analysis Test:\n")
    
    for text in test_texts:
        analysis = tagger.detect_emotions(text)
        print(f"Text: {text}")
        print(f"Primary Emotion: {analysis['primary_emotion']}")
        print(f"Bhoola Mood: {analysis['bhoola_mood']}")
        print(f"Intensity: {analysis['intensity']}/3")
        print(f"Hinglish: {'✅' if analysis['hinglish_detected'] else '❌'}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print("-" * 60)
    
    print("\n🧠 Testing mood pattern analysis...")
    history = ["I'm sad today", "Still feeling down", "Getting better now"]
    current = "Super excited about the show!"
    
    mood_context = tagger.analyze_mood_context(current, history)
    print(f"Mood Pattern: {mood_context['mood_pattern']}")
    print(f"Shift Detected: {mood_context['mood_shift']['shift_detected']}")
    if mood_context['mood_shift']['shift_detected']:
        print(f"Shift: {mood_context['mood_shift']['from_mood']} → {mood_context['mood_shift']['to_mood']}")
