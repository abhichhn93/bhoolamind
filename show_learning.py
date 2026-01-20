"""
BhoolamMind v1.5 - Quick Learning Dashboard
Shows what I'm learning about your preferences in real-time
"""

import sys
import sqlite3
from datetime import datetime
from pathlib import Path

def show_learning_dashboard():
    """Display what BhoolamMind has learned about the user"""
    
    print("🧠 BHOOLA'S AI LEARNING DASHBOARD")
    print("=" * 50)
    
    try:
        # Connect to database
        db_path = Path(__file__).parent / "memory/sqlite_db/bhoolamind.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get total interactions
        cursor.execute("SELECT COUNT(*) FROM interactions")
        total_interactions = cursor.fetchone()[0]
        
        print(f"📊 Total Interactions Logged: {total_interactions}")
        print()
        
        # Get preferences
        cursor.execute("""
            SELECT text FROM interactions 
            WHERE source = 'preference_detection' 
            ORDER BY timestamp DESC
        """)
        preferences = cursor.fetchall()
        
        if preferences:
            print("🎯 DETECTED PREFERENCES:")
            for i, (pref,) in enumerate(preferences[:5], 1):
                clean_pref = pref.replace("User preference: ", "")
                print(f"   {i}. {clean_pref}")
            print()
        
        # Get learning insights
        cursor.execute("""
            SELECT text FROM interactions 
            WHERE source = 'pattern_detection' 
            ORDER BY timestamp DESC LIMIT 5
        """)
        insights = cursor.fetchall()
        
        if insights:
            print("💡 LEARNING INSIGHTS:")
            for i, (insight,) in enumerate(insights, 1):
                clean_insight = insight.replace("Learning insight: ", "")
                print(f"   {i}. {clean_insight}")
            print()
        
        # Get recent emotions
        cursor.execute("""
            SELECT emotion, COUNT(*) as count 
            FROM interactions 
            WHERE emotion IS NOT NULL AND emotion != 'neutral'
            GROUP BY emotion 
            ORDER BY count DESC
        """)
        emotions = cursor.fetchall()
        
        if emotions:
            print("🎭 EMOTIONAL PATTERNS:")
            for emotion, count in emotions:
                print(f"   • {emotion.title()}: {count} times")
            print()
        
        # Get conversation topics
        cursor.execute("""
            SELECT tags FROM interactions 
            WHERE tags IS NOT NULL 
            ORDER BY timestamp DESC LIMIT 10
        """)
        tag_results = cursor.fetchall()
        
        all_tags = []
        for (tags,) in tag_results:
            all_tags.extend(tags.split(','))
        
        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag = tag.strip()
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        if tag_counts:
            print("🏷️  CONVERSATION TOPICS (Top 5):")
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            for tag, count in sorted_tags[:5]:
                print(f"   • {tag}: {count} mentions")
            print()
        
        # Get latest context
        cursor.execute("""
            SELECT text, timestamp FROM interactions 
            WHERE source = 'real_time_analysis' 
            ORDER BY timestamp DESC LIMIT 1
        """)
        latest_context = cursor.fetchone()
        
        if latest_context:
            context_text, timestamp = latest_context
            print("🔄 LATEST CONTEXT UPDATE:")
            print(f"   Time: {timestamp}")
            # Show first few lines of context
            lines = context_text.strip().split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")
            print()
        
        conn.close()
        
        print("🎯 LEARNING STATUS: ACTIVE")
        print("📈 System is continuously learning from our interactions")
        print("🔄 Context updates happen in real-time")
        print("💾 All insights stored for future sessions")
        
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")

if __name__ == "__main__":
    show_learning_dashboard()
