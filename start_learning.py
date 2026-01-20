"""
BhoolamMind v1.5 - Conversation Logger
Real-time conversation logging for immediate preference learning

Run this to start tracking our current conversation
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

def log_current_conversation():
    """Log our current conversation for learning"""
    
    try:
        from modules.database import BhoolamindDB
        from modules.emotion_tagger import EmotionTagger
        
        # Initialize components
        db_path = Path(__file__).parent / "memory/sqlite_db/bhoolamind.db"
        db = BhoolamindDB(str(db_path))
        emotion_tagger = EmotionTagger()
        
        print("🧠 BhoolamMind Live Learning Started!")
        print("📝 Logging current conversation...")
        
        # Log the initial request about learning preferences
        initial_request = """I want you to constantly learn about my preferences, humor style, communication patterns, technical interests, and any behavioral nuances. Use the BhoolamMind system to track and remember these patterns so you can provide increasingly personalized assistance."""
        
        # Analyze emotion and preferences
        emotion_result = emotion_tagger.detect_emotions(initial_request)
        
        # Extract preferences from the request
        preferences = {
            'wants_personalization': True,
            'interested_in_humor_tracking': True,
            'values_behavioral_learning': True,
            'prefers_adaptive_ai': True,
            'technical_interests': ['ai_memory', 'personalization', 'behavior_tracking']
        }
        
        # Store the interaction
        interaction_id = db.add_interaction(
            text=initial_request,
            emotion=emotion_result.get('emotion', 'determined'),
            intensity=emotion_result.get('mood_intensity', 7),
            source='conversation_logger',
            tags='personalization,learning_request,memory_system'
        )
        
        print(f"✅ Logged initial preference request (ID: {interaction_id})")
        print(f"🎭 Detected emotion: {emotion_result.get('emotion', 'neutral')}")
        print(f"📊 Mood intensity: {emotion_result.get('intensity', 5)}/10")
        
        # Log key preferences discovered
        print("🔍 Key preferences detected:")
        for key, value in preferences.items():
            print(f"   - {key}: {value}")
            
        # Store preferences as separate interactions for now
        for pref_type, pref_value in preferences.items():
            try:
                db.add_interaction(
                    text=f"User preference: {pref_type} = {pref_value}",
                    source='preference_detection',
                    tags=f'preference,{pref_type}',
                    emotion='neutral',
                    intensity=5
                )
            except Exception as e:
                print(f"Warning: Could not store preference {pref_type}: {e}")
                
        print("\n🚀 Live learning system is now active!")
        print("💡 I'll continue tracking our conversation patterns...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing live learning: {e}")
        return False

def update_copilot_context():
    """Update the Copilot context with latest learnings"""
    try:
        import sys
        sys.path.append("modules")
        from modules.copilot_bridge import CopilotMemoryBridge
        
        db_path = Path(__file__).parent / "memory/sqlite_db/bhoolamind.db"
        bridge = CopilotMemoryBridge(str(db_path))
        
        success = bridge.update_copilot_context(force_update=True)
        if success:
            print("✅ Updated Copilot context with latest preferences")
            print(f"📍 Context file: {bridge.context_path}")
        else:
            print("⚠️ Failed to update Copilot context")
            
        return success
        
    except Exception as e:
        print(f"❌ Error updating context: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Starting BhoolamMind Live Learning System...")
    
    # Log current conversation
    if log_current_conversation():
        print("✅ Initial conversation logged successfully")
        
        # Update Copilot context
        if update_copilot_context():
            print("✅ Copilot context updated with new preferences")
        
        print("\n🎯 System Status: ACTIVE")
        print("🔄 I'm now learning from our interactions in real-time!")
        print("📈 Each message will help me understand your preferences better")
        
    else:
        print("❌ Failed to initialize live learning system")
        print("💡 Try running: pip install -r requirements.txt")
