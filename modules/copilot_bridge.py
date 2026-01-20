"""
BhoolamMind v1.5 - GitHub Copilot Memory Bridge
Automatically updates GitHub Copilot context with user preferences and behavioral patterns
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Local imports
from .database import BhoolamindDB
from .summarizer import WeeklySummarizer

class CopilotMemoryBridge:
    """
    Bridges BhoolamMind data with GitHub Copilot context files
    Automatically updates user preferences, behavioral patterns, and learned insights
    """
    
    def __init__(self, db_path: str = None, copilot_context_path: str = None):
        """
        Initialize the Copilot Memory Bridge
        
        Args:
            db_path: Path to BhoolamMind database
            copilot_context_path: Path to GitHub Copilot context file
        """
        self.logger = logging.getLogger(__name__)
        self.db = BhoolamindDB(db_path)
        self.summarizer = WeeklySummarizer(db_path)
        
        # Set context file path (can be in Core_Project root for easy access)
        if copilot_context_path is None:
            copilot_context_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "BHOOLA_COPILOT_CONTEXT.md"
            )
        self.context_path = copilot_context_path
        
        self.logger.info(f"CopilotMemoryBridge initialized with context: {self.context_path}")
    
    def extract_user_preferences(self) -> Dict[str, Any]:
        """Extract user preferences from interaction patterns"""
        preferences = {
            "communication_style": {},
            "humor_preferences": {},
            "emotional_patterns": {},
            "technical_preferences": {},
            "behavioral_rules": [],
            "learning_insights": []
        }
        
        try:
            # Get recent interactions for analysis
            raw_interactions = self.db.get_recent_interactions(limit=200)
            
            # Convert tuples to dictionaries
            recent_interactions = []
            for row in raw_interactions:
                interaction = {
                    'id': row[0],
                    'text': row[1],
                    'source': row[2],
                    'tags': row[3],
                    'emotion': row[4],
                    'mood': row[5],
                    'intensity': row[6],
                    'bit_worthy': row[7],
                    'timestamp': row[8],
                    'created_at': row[9]
                }
                recent_interactions.append(interaction)
            
            # Analyze communication style
            communication_patterns = self._analyze_communication_style(recent_interactions)
            preferences["communication_style"] = communication_patterns
            
            # Analyze humor preferences
            humor_patterns = self._analyze_humor_preferences(recent_interactions)
            preferences["humor_preferences"] = humor_patterns
            
            # Analyze emotional patterns
            emotional_patterns = self._analyze_emotional_patterns(recent_interactions)
            preferences["emotional_patterns"] = emotional_patterns
            
            # Extract technical preferences
            tech_patterns = self._analyze_technical_preferences(recent_interactions)
            preferences["technical_preferences"] = tech_patterns
            
            # Generate behavioral rules
            behavioral_rules = self._generate_behavioral_rules(recent_interactions)
            preferences["behavioral_rules"] = behavioral_rules
            
            # Extract learning insights
            learning_insights = self._extract_learning_insights(recent_interactions)
            preferences["learning_insights"] = learning_insights
            
        except Exception as e:
            self.logger.error(f"Failed to extract preferences: {e}")
        
        return preferences
    
    def _analyze_communication_style(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communication style patterns"""
        style_patterns = {
            "preferred_tone": "casual",
            "formality_level": "informal",
            "emoji_usage": "frequent",
            "language_mix": "hinglish",
            "explanation_style": "detailed_with_examples",
            "humor_integration": "high"
        }
        
        # Analyze actual patterns from interactions
        total_text = " ".join([i['text'] for i in interactions])
        
        # Check for emoji usage
        emoji_count = sum(1 for char in total_text if ord(char) > 127)
        if emoji_count > len(interactions) * 2:  # More than 2 emojis per interaction
            style_patterns["emoji_usage"] = "frequent"
        elif emoji_count > len(interactions):
            style_patterns["emoji_usage"] = "moderate"
        else:
            style_patterns["emoji_usage"] = "minimal"
        
        # Check for Hinglish patterns
        hinglish_indicators = ["yaar", "bhai", "hai", "kya", "toh", "matlab", "achha", "theek", "bas"]
        hinglish_count = sum(1 for word in hinglish_indicators if word in total_text.lower())
        
        if hinglish_count > 10:
            style_patterns["language_mix"] = "heavy_hinglish"
        elif hinglish_count > 5:
            style_patterns["language_mix"] = "moderate_hinglish"
        else:
            style_patterns["language_mix"] = "primarily_english"
        
        # Check for technical depth preference
        tech_words = ["code", "debug", "function", "variable", "algorithm", "implementation"]
        tech_count = sum(1 for word in tech_words if word in total_text.lower())
        
        if tech_count > len(interactions) * 0.3:
            style_patterns["explanation_style"] = "technical_detailed"
        elif tech_count > len(interactions) * 0.1:
            style_patterns["explanation_style"] = "balanced_technical"
        else:
            style_patterns["explanation_style"] = "simple_explanations"
        
        return style_patterns
    
    def _analyze_humor_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze humor and comedy preferences"""
        humor_prefs = {
            "primary_style": "observational",
            "secondary_styles": [],
            "tech_humor_preference": "high",
            "self_deprecating_tolerance": "high", 
            "wordplay_appreciation": "moderate",
            "cultural_references": "bollywood_tech_mix"
        }
        
        # Get humor patterns from memory - safe fallback since method doesn't exist yet
        humor_patterns = []
        try:
            humor_patterns = self.db.get_memory_patterns("humor", min_frequency=2)
        except AttributeError:
            # Method doesn't exist yet, use empty list
            humor_patterns = []
        
        if humor_patterns:
            # Analyze humor types from patterns
            humor_types = {}
            for pattern in humor_patterns:
                pattern_data = pattern.get('pattern_data', {})
                humor_type = pattern_data.get('type', 'general')
                humor_types[humor_type] = humor_types.get(humor_type, 0) + pattern['frequency']
            
            if humor_types:
                # Set primary style as most frequent
                humor_prefs["primary_style"] = max(humor_types, key=humor_types.get)
                
                # Set secondary styles
                sorted_types = sorted(humor_types.items(), key=lambda x: x[1], reverse=True)
                humor_prefs["secondary_styles"] = [t[0] for t in sorted_types[1:4]]
        
        return humor_prefs
    
    def _analyze_emotional_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze emotional patterns and triggers"""
        emotional_patterns = {
            "dominant_emotions": [],
            "emotional_triggers": {},
            "mood_stability": "moderate",
            "stress_indicators": [],
            "happiness_triggers": [],
            "preferred_support_style": "practical_with_humor"
        }
        
        # Analyze emotions from interactions
        emotions = [i['emotion'] for i in interactions if i.get('emotion')]
        intensities = [i['mood_intensity'] for i in interactions if i.get('mood_intensity')]
        
        if emotions:
            from collections import Counter
            emotion_counts = Counter(emotions)
            emotional_patterns["dominant_emotions"] = [
                emotion for emotion, count in emotion_counts.most_common(5)
            ]
        
        if intensities:
            # Calculate emotional stability
            avg_intensity = sum(intensities) / len(intensities)
            variance = sum((x - avg_intensity) ** 2 for x in intensities) / len(intensities)
            
            if variance < 2:
                emotional_patterns["mood_stability"] = "high"
            elif variance < 5:
                emotional_patterns["mood_stability"] = "moderate"
            else:
                emotional_patterns["mood_stability"] = "variable"
        
        # Identify triggers by analyzing text with extreme emotions
        happy_texts = [i['text'] for i in interactions if i.get('emotion') == 'happy' and i.get('mood_intensity', 0) > 7]
        stressed_texts = [i['text'] for i in interactions if i.get('emotion') in ['anxious', 'frustrated', 'stressed'] and i.get('mood_intensity', 0) > 6]
        
        # Extract keywords from happy and stressed moments
        if happy_texts:
            happiness_keywords = self._extract_keywords_from_texts(happy_texts)
            emotional_patterns["happiness_triggers"] = happiness_keywords[:5]
        
        if stressed_texts:
            stress_keywords = self._extract_keywords_from_texts(stressed_texts)
            emotional_patterns["stress_indicators"] = stress_keywords[:5]
        
        return emotional_patterns
    
    def _analyze_technical_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze technical preferences and patterns"""
        tech_prefs = {
            "preferred_languages": [],
            "learning_style": "hands_on",
            "documentation_preference": "examples_first",
            "debugging_approach": "systematic",
            "code_style_preference": "readable_over_clever"
        }
        
        # Analyze tech-related interactions
        tech_interactions = [
            i for i in interactions 
            if any(keyword in i['text'].lower() for keyword in 
                  ['code', 'programming', 'debug', 'function', 'api', 'python', 'javascript'])
        ]
        
        if tech_interactions:
            # Extract programming languages mentioned
            languages = ['python', 'javascript', 'java', 'c++', 'html', 'css', 'react', 'node']
            lang_mentions = {}
            
            for interaction in tech_interactions:
                text = interaction['text'].lower()
                for lang in languages:
                    if lang in text:
                        lang_mentions[lang] = lang_mentions.get(lang, 0) + 1
            
            # Sort by frequency
            if lang_mentions:
                sorted_langs = sorted(lang_mentions.items(), key=lambda x: x[1], reverse=True)
                tech_prefs["preferred_languages"] = [lang for lang, count in sorted_langs[:5]]
        
        return tech_prefs
    
    def _generate_behavioral_rules(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Generate behavioral rules based on patterns"""
        rules = []
        
        # Analyze correction patterns and preferences
        correction_keywords = ['actually', 'correction', 'instead', 'prefer', 'better', 'should']
        corrections = [
            i for i in interactions 
            if any(keyword in i['text'].lower() for keyword in correction_keywords)
        ]
        
        # Generate rules from patterns
        rules.extend([
            "Always explain technical concepts with practical examples",
            "Use Hinglish expressions when appropriate for comfort",
            "Include humor in explanations but keep it relevant",
            "Provide step-by-step breakdowns for complex tasks",
            "Ask clarifying questions before making assumptions",
            "Offer multiple solution approaches when possible"
        ])
        
        # Add specific rules based on user feedback patterns
        if any('detail' in i['text'].lower() for i in corrections):
            rules.append("Provide detailed explanations with context")
        
        if any('simple' in i['text'].lower() for i in corrections):
            rules.append("Start with simple explanations, then add complexity")
        
        return rules
    
    def _extract_learning_insights(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Extract key learning insights about the user"""
        insights = []
        
        # Get weekly summaries for broader insights
        recent_summaries = self.summarizer.get_summary_history(weeks_back=4)
        
        insights.extend([
            "User appreciates detailed technical explanations with examples",
            "Prefers casual, friendly communication style",
            "Responds well to humor integrated naturally in conversations",
            "Values practical, actionable advice over theoretical discussions",
            "Enjoys wordplay and tech-related humor",
            "Appreciates step-by-step guidance for complex problems"
        ])
        
        # Add insights from summaries
        for summary in recent_summaries:
            if summary.get('humor_analysis', {}).get('total_funny_moments', 0) > 5:
                insights.append("User has active sense of humor and creates funny content regularly")
            
            if summary.get('mood_analysis', {}).get('emotional_range', {}).get('variance', 0) > 3:
                insights.append("User experiences varied emotional states - be supportive")
        
        return insights[:10]  # Limit to top 10 insights
    
    def _extract_keywords_from_texts(self, texts: List[str]) -> List[str]:
        """Extract meaningful keywords from a list of texts"""
        import re
        from collections import Counter
        
        # Combine all texts
        combined_text = " ".join(texts).lower()
        
        # Extract words (excluding common stop words)
        words = re.findall(r'\b\w+\b', combined_text)
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 
            'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter out stop words and short words
        meaningful_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Count frequency and return top keywords
        word_counts = Counter(meaningful_words)
        return [word for word, count in word_counts.most_common(10)]
    
    def generate_copilot_context(self) -> str:
        """Generate comprehensive GitHub Copilot context"""
        preferences = self.extract_user_preferences()
        
        context_sections = []
        
        # Header
        context_sections.append("# 🧠 BHOOLA'S AI COPILOT CONTEXT")
        context_sections.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} via BhoolamMind v1.5*")
        context_sections.append("")
        
        # User Profile
        context_sections.append("## 👤 USER PROFILE")
        context_sections.append("**Name:** Abhishek 'Bhoola' Chauhan")
        context_sections.append("**Context:** 15-month sabbatical, comedy career development")
        context_sections.append("**Location:** India (IST timezone)")
        context_sections.append("")
        
        # Communication Style
        comm_style = preferences["communication_style"]
        context_sections.append("## 💬 COMMUNICATION PREFERENCES")
        context_sections.append(f"- **Tone:** {comm_style.get('preferred_tone', 'casual').title()}")
        context_sections.append(f"- **Language Mix:** {comm_style.get('language_mix', 'hinglish').replace('_', ' ').title()}")
        context_sections.append(f"- **Emoji Usage:** {comm_style.get('emoji_usage', 'moderate').title()}")
        context_sections.append(f"- **Explanation Style:** {comm_style.get('explanation_style', 'detailed').replace('_', ' ').title()}")
        context_sections.append("")
        
        # Humor Preferences
        humor_prefs = preferences["humor_preferences"]
        context_sections.append("## 😄 HUMOR & COMEDY STYLE")
        context_sections.append(f"- **Primary Style:** {humor_prefs.get('primary_style', 'observational').title()}")
        if humor_prefs.get('secondary_styles'):
            context_sections.append(f"- **Secondary Styles:** {', '.join(humor_prefs['secondary_styles']).title()}")
        context_sections.append(f"- **Tech Humor:** {humor_prefs.get('tech_humor_preference', 'high').title()}")
        context_sections.append("- **Note:** User creates and appreciates comedy content regularly")
        context_sections.append("")
        
        # Emotional Patterns
        emotional = preferences["emotional_patterns"]
        context_sections.append("## 🎭 EMOTIONAL INTELLIGENCE")
        if emotional.get('dominant_emotions'):
            context_sections.append(f"- **Common Emotions:** {', '.join(emotional['dominant_emotions'][:3]).title()}")
        context_sections.append(f"- **Mood Stability:** {emotional.get('mood_stability', 'moderate').title()}")
        if emotional.get('happiness_triggers'):
            context_sections.append(f"- **Happiness Triggers:** {', '.join(emotional['happiness_triggers'][:3])}")
        if emotional.get('stress_indicators'):
            context_sections.append(f"- **Stress Indicators:** {', '.join(emotional['stress_indicators'][:3])}")
        context_sections.append("")
        
        # Technical Preferences
        tech_prefs = preferences["technical_preferences"]
        context_sections.append("## 💻 TECHNICAL PREFERENCES")
        if tech_prefs.get('preferred_languages'):
            context_sections.append(f"- **Languages:** {', '.join(tech_prefs['preferred_languages'][:3]).title()}")
        context_sections.append(f"- **Learning Style:** {tech_prefs.get('learning_style', 'hands_on').replace('_', ' ').title()}")
        context_sections.append(f"- **Documentation:** {tech_prefs.get('documentation_preference', 'examples_first').replace('_', ' ').title()}")
        context_sections.append("")
        
        # Behavioral Rules
        rules = preferences["behavioral_rules"]
        context_sections.append("## 📋 BEHAVIORAL GUIDELINES")
        for i, rule in enumerate(rules[:8], 1):
            context_sections.append(f"{i}. {rule}")
        context_sections.append("")
        
        # Learning Insights
        insights = preferences["learning_insights"]
        context_sections.append("## 🧠 KEY INSIGHTS")
        for insight in insights[:6]:
            context_sections.append(f"- {insight}")
        context_sections.append("")
        
        # Recent Memory Context
        context_sections.append("## 💭 RECENT MEMORY CONTEXT")
        raw_recent = self.db.get_recent_interactions(limit=5)
        if raw_recent:
            context_sections.append("**Recent Activities:**")
            for row in raw_recent:
                # Convert tuple to dictionary
                interaction = {
                    'id': row[0],
                    'text': row[1],
                    'source': row[2],
                    'tags': row[3],
                    'emotion': row[4],
                    'mood': row[5],
                    'intensity': row[6],
                    'bit_worthy': row[7],
                    'timestamp': row[8],
                    'created_at': row[9]
                }
                
                timestamp = datetime.fromisoformat(interaction['timestamp']).strftime('%m/%d %H:%M')
                emotion = f" ({interaction['emotion']})" if interaction.get('emotion') else ""
                text_preview = interaction['text'][:80] + "..." if len(interaction['text']) > 80 else interaction['text']
                context_sections.append(f"- [{timestamp}] {text_preview}{emotion}")
        context_sections.append("")
        
        # Footer
        context_sections.append("---")
        context_sections.append("*This context is automatically updated by BhoolamMind v1.5*")
        context_sections.append("*For questions about context accuracy, check the BhoolamMind dashboard*")
        
        return "\n".join(context_sections)
    
    def update_copilot_context(self, force_update: bool = False) -> bool:
        """Update the GitHub Copilot context file"""
        try:
            # Check if update is needed (only update if significant changes or forced)
            if not force_update and os.path.exists(self.context_path):
                # Check last modification time
                last_modified = datetime.fromtimestamp(os.path.getmtime(self.context_path))
                if (datetime.now() - last_modified).hours < 6:  # Only update every 6 hours
                    self.logger.info("Context file recently updated, skipping")
                    return False
            
            # Generate new context
            context_content = self.generate_copilot_context()
            
            # Write to file
            with open(self.context_path, 'w', encoding='utf-8') as f:
                f.write(context_content)
            
            self.logger.info(f"Updated Copilot context file: {self.context_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Copilot context: {e}")
            return False
    
    def schedule_daily_update(self):
        """Schedule daily context updates (can be called by cron or task scheduler)"""
        self.logger.info("Running scheduled Copilot context update...")
        
        # Update context
        updated = self.update_copilot_context(force_update=True)
        
        if updated:
            print(f"✅ Copilot context updated at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"⚠️  Copilot context update failed at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return updated

# Standalone function for easy integration
def update_copilot_memory(db_path: str = None, context_path: str = None) -> bool:
    """
    Standalone function to update Copilot memory
    Can be called from cron jobs or other scripts
    """
    try:
        bridge = CopilotMemoryBridge(db_path, context_path)
        return bridge.update_copilot_context(force_update=True)
    except Exception as e:
        print(f"Failed to update Copilot memory: {e}")
        return False

if __name__ == "__main__":
    # Command line usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Update GitHub Copilot context from BhoolamMind")
    parser.add_argument("--db-path", help="Path to BhoolamMind database")
    parser.add_argument("--context-path", help="Path to Copilot context file")
    parser.add_argument("--force", action="store_true", help="Force update regardless of timing")
    
    args = parser.parse_args()
    
    bridge = CopilotMemoryBridge(args.db_path, args.context_path)
    
    if args.force:
        success = bridge.update_copilot_context(force_update=True)
    else:
        success = bridge.schedule_daily_update()
    
    exit(0 if success else 1)
