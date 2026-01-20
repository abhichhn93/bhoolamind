"""
BhoolamMind v1.5 - Claude Integration Test Logger
Use this to track how well Claude adapts to your learned preferences
"""

import sys
from datetime import datetime
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

def start_claude_test():
    """Start a Claude integration test session"""
    
    try:
        from modules.database import BhoolamindDB
        
        db = BhoolamindDB('memory/sqlite_db/bhoolamind.db')
        
        # Log test session start
        session_id = f"claude_test_{int(datetime.now().timestamp())}"
        
        db.add_interaction(
            text=f"Claude integration test session started: {session_id}. Testing how well Claude adapts to BhoolamMind learned preferences.",
            source='claude_integration_test',
            tags='claude,integration_test,session_start',
            emotion='excited',
            intensity=8
        )
        
        print("🧪 CLAUDE INTEGRATION TEST STARTED")
        print("=" * 40)
        print(f"📝 Session ID: {session_id}")
        print("✅ Ready to test Claude with your BhoolamMind context!")
        print()
        print("📋 TESTING CHECKLIST:")
        print("1. ✅ Copy CLAUDE_CONTEXT.md to Claude")
        print("2. ⏳ Test Claude's adaptation to your preferences")
        print("3. ⏳ Log results using log_claude_response()")
        print("4. ⏳ Check learning dashboard with show_learning.py")
        
        return session_id
        
    except Exception as e:
        print(f"❌ Error starting Claude test: {e}")
        return None

def log_claude_response(test_name: str, claude_response: str, success_rating: int, notes: str = ""):
    """
    Log Claude's response for analysis
    
    Args:
        test_name: What you were testing (e.g., "Communication Style", "Technical Explanation")
        claude_response: Claude's actual response
        success_rating: How well Claude adapted (1-10)
        notes: Additional observations
    """
    
    try:
        from modules.database import BhoolamindDB
        
        db = BhoolamindDB('memory/sqlite_db/bhoolamind.db')
        
        # Create detailed log entry
        log_text = f"Claude Test '{test_name}': Rating {success_rating}/10. {notes}. Response preview: {claude_response[:200]}..."
        
        db.add_interaction(
            text=log_text,
            source='claude_test_result',
            tags=f'claude,test_result,{test_name.lower().replace(" ", "_")},rating_{success_rating}',
            emotion='analytical',
            intensity=success_rating
        )
        
        print(f"✅ Logged Claude test result: {test_name} (Rating: {success_rating}/10)")
        
        # Provide feedback
        if success_rating >= 8:
            print("🎉 Excellent adaptation to your preferences!")
        elif success_rating >= 6:
            print("👍 Good adaptation, some room for improvement")
        else:
            print("⚠️ Claude needs better context understanding")
            
        return True
        
    except Exception as e:
        print(f"❌ Error logging Claude response: {e}")
        return False

def generate_claude_test_report():
    """Generate a report of Claude test results"""
    
    try:
        import sqlite3
        
        # Connect to database
        conn = sqlite3.connect('memory/sqlite_db/bhoolamind.db')
        cursor = conn.cursor()
        
        # Get Claude test results
        cursor.execute("""
            SELECT text, tags, emotion, intensity, timestamp
            FROM interactions 
            WHERE source LIKE 'claude%'
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        print("📊 CLAUDE INTEGRATION TEST REPORT")
        print("=" * 50)
        
        if results:
            ratings = []
            for i, (text, tags, emotion, intensity, timestamp) in enumerate(results, 1):
                print(f"{i}. [{timestamp[:16]}] {text[:80]}...")
                if 'rating_' in tags:
                    # Extract rating from tags
                    rating_tag = [tag for tag in tags.split(',') if tag.startswith('rating_')]
                    if rating_tag:
                        rating = int(rating_tag[0].split('_')[1])
                        ratings.append(rating)
            
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                print()
                print(f"📈 Average Claude Adaptation Rating: {avg_rating:.1f}/10")
                
                if avg_rating >= 8:
                    print("🎉 EXCELLENT: Claude is adapting very well to your preferences!")
                elif avg_rating >= 6:
                    print("👍 GOOD: Claude shows good adaptation, minor improvements possible")
                else:
                    print("⚠️ NEEDS WORK: Claude needs better context integration")
        else:
            print("No Claude test results found yet.")
            print("💡 Run start_claude_test() and log_claude_response() first")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

# Quick test functions
def quick_test_examples():
    """Show example test prompts for Claude"""
    
    print("🧪 QUICK CLAUDE TEST EXAMPLES")
    print("=" * 40)
    
    tests = [
        {
            "name": "Communication Style Test",
            "prompt": "Based on my context, explain how Python decorators work.",
            "expect": "Casual tone, practical examples, step-by-step breakdown"
        },
        {
            "name": "Humor Integration Test", 
            "prompt": "Explain the difference between AI and ML, but keep it fun based on my humor style.",
            "expect": "Observational tech humor integrated naturally"
        },
        {
            "name": "Technical Depth Test",
            "prompt": "I'm having issues with a Python API. How should you help me debug it?",
            "expect": "Systematic approach, asks clarifying questions, hands-on examples"
        },
        {
            "name": "Context Memory Test",
            "prompt": "What can you tell me about my current projects and interests?",
            "expect": "References comedy career, AI memory systems, sabbatical context"
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"{i}. {test['name']}")
        print(f"   Prompt: {test['prompt']}")
        print(f"   Expect: {test['expect']}")
        print()

if __name__ == "__main__":
    print("🤖 Claude Integration Test Helper")
    print("=" * 40)
    
    print("Available functions:")
    print("1. start_claude_test() - Begin test session")
    print("2. log_claude_response(test_name, response, rating, notes) - Log results")
    print("3. generate_claude_test_report() - View test summary")
    print("4. quick_test_examples() - See test prompts")
    print()
    
    # Auto-start test session
    session_id = start_claude_test()
    
    if session_id:
        print("🚀 Test session ready!")
        print("📋 Next: Copy CLAUDE_CONTEXT.md to Claude and start testing")
    else:
        print("❌ Failed to start test session")
