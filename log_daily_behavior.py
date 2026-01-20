#!/usr/bin/env python3
"""
Daily Behavior Memory Logger
Logs user behavior patterns for cross-AI memory injection
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

try:
    from memory_injector import MemoryInjector
except ImportError:
    print("❌ Memory injector not found")
    sys.exit(1)

def log_daily_behavior():
    """Log today's behavioral observations"""
    
    injector = MemoryInjector()
    
    # Today's observations
    behavior_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "communication_patterns": {
            "direct_feedback": "User prefers direct communication, no AI sugarcoating",
            "naming_preferences": "Hates 'enhanced', 'optimized' prefix naming - wants natural names",
            "technical_approach": "Wants real implementation, not demos or proof-of-concepts"
        },
        "frustration_triggers": [
            "artificial file naming with prefixes",
            "AI over-enthusiasm and sugarcoating", 
            "systems that don't actually persist",
            "demo-only solutions"
        ],
        "project_preferences": {
            "organization": "Clean folder structure in Core_Project",
            "file_naming": "Natural conventions - telegram_bot.py not enhanced_telegram_bot.py",
            "memory_systems": "Real persistence across AI platforms"
        },
        "humor_insights": {
            "rating_system": "3-4 stars is good, 1-2 needs work",
            "preference": "authentic over clever",
            "successful_bits": ["AIs fighting like bitches", "tech bro rap battle"]
        }
    }
    
    # Log to memory system
    session_text = f"""Daily Behavior Log {behavior_data['date']}:
- Communication: {behavior_data['communication_patterns']['direct_feedback']}
- Naming: {behavior_data['communication_patterns']['naming_preferences']} 
- Technical: {behavior_data['communication_patterns']['technical_approach']}
- Humor: {behavior_data['humor_insights']['preference']} style preferred
- Organization: {behavior_data['project_preferences']['organization']}
"""
    
    success = injector.add_memory(
        text=session_text,
        emotion="analytical", 
        tags="daily_behavior,user_preferences,communication_patterns",
        interaction_id=None
    )
    
    if success:
        print("✅ Daily behavior logged to memory system")
    else:
        print("❌ Failed to log behavior")
    
    return behavior_data

if __name__ == "__main__":
    behavior_data = log_daily_behavior()
    print(f"📊 Logged behavior patterns for {behavior_data['date']}")
