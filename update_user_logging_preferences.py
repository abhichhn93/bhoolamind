#!/usr/bin/env python3
"""
BhoolaMind v1.5 - User Preference Learning Update
Updates the memory system with learned user preferences about logging behavior
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the modules directory to path
sys.path.append('/Users/abhichauhan/Desktop/Core_Project/bhoolamind_v1.5/modules')

def update_logging_preferences():
    """Update BhoolaMind with learned user preferences about logging behavior"""
    
    try:
        from database import BhoolamindDB
        
        # Initialize database
        db = BhoolamindDB()
        
        print("🧠 BhoolaMind v1.5 - Learning Update: User Logging Preferences")
        print("=" * 65)
        print("Date: July 19, 2025")
        print("Learning Session: User Feedback on Logging Quality")
        print()
        
        # Critical learning about user's logging preferences
        learning_updates = [
            {
                "text": "USER PREFERENCE CRITICAL: User strongly dislikes keyword-style logging like 'project status, polaris AI 95% complete'. Considers this 'fucking stupid' and wants comprehensive 1000+ word detailed summaries instead. Future AIs must write detailed, narrative-style progress reports with full context, not bullet points or keywords.",
                "source": "logging_preference_critical",
                "tags": "user_preferences,logging_style,detailed_summaries,no_keywords,critical_feedback",
                "emotion": "learning",
                "intensity": 10,
                "bit_worthy": True
            },
            {
                "text": "LEARNED BEHAVIOR: User expects comprehensive daily progress reports with: 1) Detailed executive summaries, 2) Complete technical achievements with file sizes and purposes, 3) Full problem documentation with error patterns, 4) Business value demonstrations, 5) Safety and compliance details, 6) Performance metrics and benchmarks, 7) Strategic insights, 8) Next steps clearly defined. Minimum 1000 words for proper documentation.",
                "source": "comprehensive_logging_requirements",
                "tags": "detailed_logging,comprehensive_reports,user_expectations,1000_words,professional_docs",
                "emotion": "systematic",
                "intensity": 9,
                "bit_worthy": True
            },
            {
                "text": "USER FRUSTRATION DOCUMENTED: Downloads folder access issues caused user frustration when AI collaboration files weren't visible. Future AIs should copy important files directly to Desktop where user can see them, not rely on Downloads folder which may have access restrictions. Always verify file visibility after copying.",
                "source": "file_access_learning",
                "tags": "downloads_folder_issues,desktop_copying,file_visibility,user_frustration,access_problems",
                "emotion": "problem_solving",
                "intensity": 8,
                "bit_worthy": True
            },
            {
                "text": "BhoolaMind v1.5 SYSTEM ROLE CONFIRMED: This is the official memory logging system for everyday activities. User wants BhoolaMind to learn and adapt to prevent future AIs from repeating mistakes. The system should capture: user preferences, behavior patterns, successful approaches, failed attempts, frustration points, and improvement suggestions.",
                "source": "bhoolamind_role_definition",
                "tags": "bhoolamind_official,memory_system,learning_adaptation,prevent_mistakes,user_behavior",
                "emotion": "systematic",
                "intensity": 9,
                "bit_worthy": True
            },
            {
                "text": "NAMING PREFERENCES REINFORCED: User prefers natural naming conventions (launch_bhoola.py vs enhanced_launch_bhoola.py). Dislikes 'enhanced' prefixes that make files harder to find. Wants simple, descriptive names that are easy to remember and locate.",
                "source": "naming_conventions",
                "tags": "natural_naming,no_enhanced_prefixes,simple_names,user_preferences,file_naming",
                "emotion": "understanding",
                "intensity": 7,
                "bit_worthy": True
            },
            {
                "text": "DOCUMENTATION QUALITY STANDARDS: User expects professional-level documentation suitable for sharing with other AI systems (ChatGPT, Claude, Gemini). Documentation should include: executive summaries, technical deep-dives, exact error messages, working code examples, business value demonstrations, and clear collaboration frameworks. Quality over quantity but comprehensive coverage required.",
                "source": "documentation_standards",
                "tags": "professional_docs,ai_collaboration,comprehensive_coverage,technical_quality,business_value",
                "emotion": "professional",
                "intensity": 9,
                "bit_worthy": True
            },
            {
                "text": "SAFETY-FIRST APPROACH CONFIRMED: User prioritizes ToS compliance and ethical practices over functionality. All implementations must maintain safety protocols, rate limiting, privacy protection, and emergency kill switches. User appreciates comprehensive safety documentation and transparency about compliance measures.",
                "source": "safety_first_priority",
                "tags": "safety_priority,tos_compliance,ethical_practices,transparency,user_values",
                "emotion": "responsible",
                "intensity": 8,
                "bit_worthy": True
            },
            {
                "text": "CROSS-AI MEMORY IMPORTANCE: User values persistent context across AI platforms. BhoolaMind v1.5 serves as the bridge between different AI sessions (Copilot, ChatGPT, Claude). Documentation should enable seamless handoffs and prevent loss of project context when switching between AI systems.",
                "source": "cross_ai_memory_value",
                "tags": "cross_ai_context,persistent_memory,seamless_handoffs,project_continuity,ai_switching",
                "emotion": "strategic",
                "intensity": 8,
                "bit_worthy": True
            },
            {
                "text": "TECHNICAL PROBLEM-SOLVING PREFERENCE: User appreciates systematic documentation of failed attempts, exact error messages, and comprehensive solution exploration. Wants future AIs to understand what has been tried, what failed, and why, to avoid repeating unsuccessful approaches.",
                "source": "problem_solving_approach",
                "tags": "systematic_documentation,failed_attempts,error_analysis,solution_exploration,avoid_repetition",
                "emotion": "analytical",
                "intensity": 8,
                "bit_worthy": True
            },
            {
                "text": "COMMUNICATION STYLE LEARNING: User uses direct, sometimes colorful language when frustrated ('fucking stupid', 'that's shit'). This indicates strong preferences that should be respected. User appreciates honesty about mistakes and expects immediate correction when problems are identified.",
                "source": "communication_style",
                "tags": "direct_communication,strong_preferences,honesty_appreciated,immediate_correction,user_personality",
                "emotion": "understanding",
                "intensity": 7,
                "bit_worthy": True
            },
            {
                "text": "CRITICAL FILE MANAGEMENT BEHAVIOR: User strongly dislikes date-specific temporary files (like 'daily_comprehensive_update_july19.py'). Considers this 'useless' and 'stupid'. Future AIs must: 1) Create ONE general reusable script for daily operations, NOT date-specific files, 2) Always clean up temporary files immediately after use, 3) Do not create files for 'very small time' - use existing systems instead. User expects common sense: if something is done daily, create ONE reusable solution.",
                "source": "file_management_critical",
                "tags": "file_management,no_date_specific_files,cleanup_temp_files,reusable_scripts,common_sense",
                "emotion": "frustrated",
                "intensity": 10,
                "bit_worthy": True
            },
            {
                "text": "FOLDER ORGANIZATION PREFERENCE: User frustrated by creation of duplicate folders on Desktop (like 'BhoolaReelsAI_for_AIs'). Core_Project folder is the MAIN project folder - everything should go there, NOT on Desktop. Future AIs must: 1) Never create duplicate project folders on Desktop, 2) Use existing folder structure in Core_Project, 3) Understand that Desktop is for final files only, not project organization, 4) Ask before creating any new folders. User expects logical folder organization, not scattered duplicates.",
                "source": "folder_organization_preference",
                "tags": "folder_organization,no_desktop_duplicates,core_project_main,logical_structure,no_scattered_files",
                "emotion": "organized",
                "intensity": 9,
                "bit_worthy": True
            }
        ]
        
        print("📝 Logging user preference learnings...")
        print()
        
        logged_count = 0
        for learning in learning_updates:
            try:
                interaction_id = db.add_interaction(
                    text=learning["text"],
                    source=learning["source"],
                    tags=learning["tags"],
                    emotion=learning["emotion"],
                    intensity=learning["intensity"],
                    bit_worthy=learning["bit_worthy"]
                )
                logged_count += 1
                print(f"✅ Logged Learning (ID: {interaction_id}): {learning['source']}")
            except Exception as e:
                print(f"❌ Failed to log {learning['source']}: {e}")
        
        # Create meta-learning entry
        meta_learning = f"""BhoolaMind v1.5 Learning Session Complete - July 19, 2025: Comprehensive user preference updates logged based on direct feedback about logging quality. User strongly prefers detailed 1000+ word comprehensive reports over keyword-style logging. Critical learnings include: documentation quality standards, file access preferences (Desktop over Downloads), naming conventions (natural vs enhanced), safety-first approach, cross-AI memory importance, and communication style preferences. Future AIs must reference these preferences to avoid repeating mistakes. {logged_count} learning entries logged for permanent memory."""
        
        try:
            meta_id = db.add_interaction(
                text=meta_learning,
                source="meta_learning_session",
                tags="meta_learning,user_preferences,logging_quality,future_ai_guidance,july_19_2025",
                emotion="systematic",
                intensity=10,
                bit_worthy=True
            )
            print(f"🎯 Meta-learning entry created (ID: {meta_id})")
        except Exception as e:
            print(f"❌ Meta-learning failed: {e}")
        
        print()
        print(f"📊 Successfully logged {logged_count}/{len(learning_updates)} preference learnings")
        print("🧠 BhoolaMind v1.5 updated with user behavior patterns!")
        print("🔄 Future AI sessions will have these preferences available")
        print()
        print("🚀 LEARNING COMPLETE - FUTURE AIs WILL KNOW:")
        print("   ✅ Write 1000+ word detailed progress reports")
        print("   ✅ Use comprehensive documentation, not keywords")
        print("   ✅ Copy files to Desktop for visibility")
        print("   ✅ Use natural naming conventions")
        print("   ✅ Prioritize safety and compliance")
        print("   ✅ Maintain cross-AI memory context")
        print("   ✅ Document failures systematically")
        print("   ✅ Respect direct communication style")
        print("   ✅ Manage files with common sense - no date-specific temp files")
        print("   ✅ Organize folders logically - no duplicates on Desktop")
        
        return True
        
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        print("📂 Checking BhoolaMind v1.5 installation...")
        return False
    except Exception as e:
        print(f"❌ Learning session failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Starting BhoolaMind v1.5 User Preference Learning Update...")
    print()
    
    success = update_logging_preferences()
    
    if success:
        print("\n🎉 SUCCESS: User preferences permanently logged to BhoolaMind v1.5!")
        print("📝 Future AI sessions will automatically know these preferences!")
        print("🔄 Cross-AI learning system updated!")
        print()
        print("🚀 Tomorrow's AI will not repeat today's logging mistakes!")
    else:
        print("\n❌ Learning update had issues")
        print("📝 Check BhoolaMind v1.5 setup and try again")
