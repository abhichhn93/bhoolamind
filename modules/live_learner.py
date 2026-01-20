"""
BhoolamMind v1.5 - Live Learning System
Real-time preference tracking and conversation analysis for immediate AI adaptation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from .database import BhoolamindDB
from .emotion_tagger import EmotionTagger
from .copilot_bridge import CopilotMemoryBridge

class LiveLearner:
    """
    Real-time learning system that tracks preferences and patterns
    Updates AI context immediately for better conversation continuity
    """
    
    def __init__(self, db_path: str = None):
        """Initialize live learning system"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        if db_path is None:
            db_path = Path(__file__).parent.parent / "memory/sqlite_db/bhoolamind.db"
        
        self.db = BhoolamindDB(str(db_path))
        self.emotion_tagger = EmotionTagger()
        self.bridge = CopilotMemoryBridge(str(db_path))
        
        # Session tracking
        self.session_id = f"session_{int(time.time())}"
        self.conversation_log = []
        self.preference_updates = []
        
        self.logger.info(f"LiveLearner initialized for session: {self.session_id}")
    
    def log_user_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Log user message and extract learning insights
        
        Args:
            message: User's message text
            context: Additional context (platform, tone, etc.)
            
        Returns:
            Extracted insights for immediate use
        """
        timestamp = datetime.now().isoformat()
        
        # Analyze message
        analysis = self._analyze_message(message, context or {})
        
        # Store in database
        interaction_data = {
            'session_id': self.session_id,
            'timestamp': timestamp,
            'message': message,
            'context': context or {},
            'analysis': analysis
        }
        
        # Add to conversation log
        self.conversation_log.append(interaction_data)
        
        # Store in database
        self.db.add_interaction(
            text=message,
            emotion=analysis.get('emotion', 'neutral'),
            mood_intensity=analysis.get('mood_intensity', 5),
            interaction_type='user_message',
            tags=analysis.get('tags', []),
            metadata=analysis
        )
        
        # Update preferences if significant patterns detected
        if analysis.get('preference_updates'):
            self._update_preferences(analysis['preference_updates'])
        
        # Return insights for immediate use
        return self._format_insights(analysis)
    
    def log_ai_response(self, response: str, user_feedback: str = None) -> Dict[str, Any]:
        """
        Log AI response and any user feedback
        
        Args:
            response: AI's response text
            user_feedback: User's feedback/reaction (optional)
            
        Returns:
            Learning insights from the interaction
        """
        timestamp = datetime.now().isoformat()
        
        # Analyze response effectiveness
        effectiveness = self._analyze_response_effectiveness(response, user_feedback)
        
        # Store interaction
        interaction_data = {
            'session_id': self.session_id,
            'timestamp': timestamp,
            'ai_response': response,
            'user_feedback': user_feedback,
            'effectiveness': effectiveness
        }
        
        self.conversation_log.append(interaction_data)
        
        # Store in database
        self.db.add_interaction(
            text=f"AI: {response}",
            emotion='neutral',
            mood_intensity=5,
            interaction_type='ai_response',
            tags=['ai_response'],
            metadata=effectiveness
        )
        
        return effectiveness
    
    def detect_preferences(self, text: str) -> Dict[str, Any]:
        """
        Detect user preferences from text
        
        Args:
            text: User's text to analyze
            
        Returns:
            Detected preferences and patterns
        """
        preferences = {
            'communication_style': {},
            'technical_preferences': {},
            'humor_style': {},
            'emotional_patterns': {},
            'content_interests': []
        }
        
        text_lower = text.lower()
        
        # Communication style detection
        if any(word in text_lower for word in ['yaar', 'bhai', 'hai', 'matlab', 'achha']):
            preferences['communication_style']['hinglish_usage'] = 'frequent'
        
        if '😂' in text or '🤣' in text or 'lol' in text_lower or 'haha' in text_lower:
            preferences['communication_style']['humor_response'] = 'positive'
        
        # Technical preferences
        tech_keywords = ['code', 'python', 'ai', 'machine learning', 'api', 'database', 'github']
        tech_mentions = [word for word in tech_keywords if word in text_lower]
        if tech_mentions:
            preferences['technical_preferences']['interests'] = tech_mentions
        
        # Learning style indicators
        if any(phrase in text_lower for phrase in ['show me', 'example', 'how to', 'step by step']):
            preferences['technical_preferences']['learning_style'] = 'hands_on'
        
        if any(phrase in text_lower for phrase in ['explain', 'why', 'what is', 'understand']):
            preferences['technical_preferences']['explanation_preference'] = 'detailed'
        
        # Content interests
        interest_keywords = ['comedy', 'reels', 'youtube', 'content', 'creative', 'video', 'editing']
        interests = [word for word in interest_keywords if word in text_lower]
        if interests:
            preferences['content_interests'] = interests
        
        # Filter out empty preferences
        return {k: v for k, v in preferences.items() if v}
    
    def update_copilot_context(self, immediate: bool = True) -> bool:
        """
        Update Copilot context with latest learnings
        
        Args:
            immediate: Whether to update immediately or wait for batch
            
        Returns:
            Success status
        """
        if immediate:
            return self.bridge.update_copilot_context(force_update=True)
        else:
            # Schedule for next batch update
            return True
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session learnings"""
        return {
            'session_id': self.session_id,
            'start_time': self.conversation_log[0]['timestamp'] if self.conversation_log else None,
            'message_count': len([log for log in self.conversation_log if 'message' in log]),
            'preference_updates': len(self.preference_updates),
            'key_insights': self._extract_session_insights(),
            'conversation_log': self.conversation_log[-5:]  # Last 5 interactions
        }
    
    def _analyze_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user message for patterns and preferences"""
        analysis = {
            'length': len(message),
            'word_count': len(message.split()),
            'timestamp': datetime.now().isoformat(),
            'tags': [],
            'preference_updates': {}
        }
        
        # Emotion analysis
        try:
            emotion_result = self.emotion_tagger.analyze_emotion(message)
            analysis.update(emotion_result)
        except Exception as e:
            self.logger.warning(f"Emotion analysis failed: {e}")
            analysis['emotion'] = 'neutral'
            analysis['mood_intensity'] = 5
        
        # Preference detection
        detected_prefs = self.detect_preferences(message)
        if detected_prefs:
            analysis['preference_updates'] = detected_prefs
            analysis['tags'].append('preference_indicator')
        
        # Communication pattern analysis
        if '?' in message:
            analysis['tags'].append('question')
        if '!' in message:
            analysis['tags'].append('exclamation')
        if any(word in message.lower() for word in ['please', 'thanks', 'thank you']):
            analysis['tags'].append('polite')
        
        return analysis
    
    def _analyze_response_effectiveness(self, response: str, feedback: str = None) -> Dict[str, Any]:
        """Analyze how effective the AI response was"""
        effectiveness = {
            'response_length': len(response),
            'has_code': '```' in response,
            'has_emoji': any(ord(char) > 127 for char in response),
            'tone': 'formal' if any(word in response.lower() for word in ['please', 'would', 'shall']) else 'casual'
        }
        
        if feedback:
            feedback_lower = feedback.lower()
            if any(word in feedback_lower for word in ['good', 'great', 'perfect', 'exactly', 'thanks']):
                effectiveness['user_satisfaction'] = 'positive'
            elif any(word in feedback_lower for word in ['wrong', 'not', "doesn't", 'issue', 'error']):
                effectiveness['user_satisfaction'] = 'negative'
            else:
                effectiveness['user_satisfaction'] = 'neutral'
        
        return effectiveness
    
    def _update_preferences(self, preferences: Dict[str, Any]):
        """Update stored preferences with new learnings"""
        self.preference_updates.append({
            'timestamp': datetime.now().isoformat(),
            'preferences': preferences
        })
        
        # Store as memory pattern
        try:
            for category, data in preferences.items():
                self.db.add_memory_pattern(
                    pattern_type='preference',
                    pattern_data={'category': category, 'data': data},
                    frequency=1,
                    last_seen=datetime.now().isoformat()
                )
        except Exception as e:
            self.logger.error(f"Failed to store preference update: {e}")
    
    def _format_insights(self, analysis: Dict[str, Any]) -> str:
        """Format analysis insights for immediate use"""
        insights = []
        
        if analysis.get('emotion') and analysis['emotion'] != 'neutral':
            insights.append(f"Emotion: {analysis['emotion']}")
        
        if analysis.get('preference_updates'):
            prefs = analysis['preference_updates']
            if 'communication_style' in prefs:
                insights.append(f"Communication: {prefs['communication_style']}")
            if 'technical_preferences' in prefs:
                insights.append(f"Tech interests: {prefs['technical_preferences']}")
        
        if analysis.get('tags'):
            insights.append(f"Patterns: {', '.join(analysis['tags'])}")
        
        return " | ".join(insights) if insights else "Standard interaction"
    
    def _extract_session_insights(self) -> List[str]:
        """Extract key insights from current session"""
        insights = []
        
        if len(self.conversation_log) > 0:
            # Communication patterns
            questions = len([log for log in self.conversation_log if 'question' in log.get('analysis', {}).get('tags', [])])
            if questions > 3:
                insights.append("High question frequency - prefers interactive learning")
            
            # Preference patterns
            if len(self.preference_updates) > 2:
                insights.append("Multiple preference indicators detected")
            
            # Emotional patterns
            emotions = [log.get('analysis', {}).get('emotion', 'neutral') for log in self.conversation_log]
            if emotions.count('excited') > emotions.count('frustrated'):
                insights.append("Generally positive emotional tone")
        
        return insights

# Convenience function for quick logging
def log_interaction(user_message: str, ai_response: str = None, feedback: str = None) -> Dict[str, Any]:
    """
    Quick function to log an interaction and get insights
    
    Args:
        user_message: What the user said
        ai_response: What the AI responded (optional)
        feedback: User's feedback on AI response (optional)
        
    Returns:
        Learning insights and recommendations
    """
    learner = LiveLearner()
    
    # Log user message
    user_insights = learner.log_user_message(user_message)
    
    result = {
        'user_insights': user_insights,
        'session_summary': learner.get_session_summary()
    }
    
    # Log AI response if provided
    if ai_response:
        ai_insights = learner.log_ai_response(ai_response, feedback)
        result['ai_insights'] = ai_insights
        
        # Update Copilot context
        learner.update_copilot_context(immediate=True)
    
    return result

if __name__ == "__main__":
    # Test the live learner
    learner = LiveLearner()
    
    # Simulate a conversation
    test_message = "Hey! Can you help me understand how to build a better AI memory system? I'm working on comedy content and need something that remembers my preferences."
    
    insights = learner.log_user_message(test_message)
    print(f"User insights: {insights}")
    
    # Test response logging
    test_response = "I'd be happy to help! Let me show you how to build a persistent memory system with Python and SQLite..."
    ai_insights = learner.log_ai_response(test_response)
    print(f"AI insights: {ai_insights}")
    
    # Get session summary
    summary = learner.get_session_summary()
    print(f"Session summary: {json.dumps(summary, indent=2)}")
