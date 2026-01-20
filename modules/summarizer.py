"""
BhoolamMind v1.5 - Summarizer Module
Weekly summary generator for BhoolaLogs - compresses logs into patterns, trends, and insights.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import logging
import re

# Local imports
from .database import BhoolamindDB
from .emotion_tagger import EmotionTagger
from .bit_tracker import BitTracker

class WeeklySummarizer:
    def __init__(self, db_path: str = None):
        """
        Initialize the weekly summarizer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.logger = logging.getLogger(__name__)
        self.db = BhoolamindDB(db_path)
        self.emotion_tagger = EmotionTagger()
        self.bit_tracker = BitTracker()
        
        # Patterns for analysis
        self.humor_keywords = [
            'funny', 'hilarious', 'lol', 'haha', 'joke', 'humor', 'comedy',
            'sarcasm', 'wit', 'amusing', 'laughing', 'giggle', 'chuckle'
        ]
        
        self.reflection_keywords = [
            'think', 'realize', 'understand', 'learn', 'discover', 'insight',
            'reflection', 'thought', 'contemplating', 'wondering', 'ponder'
        ]
        
        self.mood_patterns = {
            'high_energy': ['excited', 'energetic', 'motivated', 'pumped', 'active'],
            'creative': ['creative', 'inspired', 'artistic', 'innovative', 'imaginative'],
            'relaxed': ['chill', 'relaxed', 'calm', 'peaceful', 'zen'],
            'focused': ['focused', 'concentrated', 'productive', 'working', 'busy'],
            'social': ['friends', 'people', 'social', 'party', 'hanging out'],
            'introspective': ['thinking', 'reflecting', 'alone', 'quiet', 'introspective']
        }
        
        self.logger.info("WeeklySummarizer initialized")
    
    def get_week_boundaries(self, target_date: datetime = None) -> Tuple[datetime, datetime]:
        """Get start and end dates for a week (Monday to Sunday)"""
        if target_date is None:
            target_date = datetime.now()
        
        # Find Monday of the week
        days_since_monday = target_date.weekday()
        week_start = target_date - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find Sunday of the week
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return week_start, week_end
    
    def get_weekly_interactions(self, week_start: datetime, week_end: datetime) -> List[Dict[str, Any]]:
        """Get all interactions for a specific week"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM interactions 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (week_start.isoformat(), week_end.isoformat()))
            
            columns = [desc[0] for desc in cursor.description]
            interactions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            # Parse JSON fields
            for interaction in interactions:
                if interaction['tags']:
                    try:
                        interaction['tags'] = json.loads(interaction['tags'])
                    except json.JSONDecodeError:
                        interaction['tags'] = []
            
            return interactions
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly interactions: {e}")
            return []
    
    def analyze_humor_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze humor patterns and evolution for the week"""
        humor_analysis = {
            'total_funny_moments': 0,
            'humor_types': Counter(),
            'best_bits': [],
            'humor_evolution': {},
            'recurring_themes': []
        }
        
        try:
            daily_humor = defaultdict(list)
            
            for interaction in interactions:
                text = interaction['text'].lower()
                tags = interaction.get('tags', [])
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                day = timestamp.strftime('%A')
                
                # Check for humor indicators
                is_funny = False
                humor_type = 'general'
                
                # Check tags for humor
                if any(tag in ['BhoolaMoment', 'Bit-worthy', 'funny', 'humor'] for tag in tags):
                    is_funny = True
                
                # Check text for humor keywords
                if any(keyword in text for keyword in self.humor_keywords):
                    is_funny = True
                
                # Use bit tracker to identify potential bits
                bit_analysis = self.bit_tracker.analyze_text(interaction['text'])
                if bit_analysis['is_bit_worthy']:
                    is_funny = True
                    humor_type = bit_analysis['bit_type']
                    humor_analysis['best_bits'].append({
                        'text': interaction['text'][:200] + '...' if len(interaction['text']) > 200 else interaction['text'],
                        'timestamp': interaction['timestamp'],
                        'type': humor_type,
                        'score': bit_analysis['confidence']
                    })
                
                if is_funny:
                    humor_analysis['total_funny_moments'] += 1
                    humor_analysis['humor_types'][humor_type] += 1
                    daily_humor[day].append(interaction['text'])
            
            # Analyze humor evolution through the week
            for day, humor_items in daily_humor.items():
                humor_analysis['humor_evolution'][day] = {
                    'count': len(humor_items),
                    'sample': humor_items[0][:100] + '...' if humor_items else ''
                }
            
            # Sort best bits by score
            humor_analysis['best_bits'] = sorted(
                humor_analysis['best_bits'], 
                key=lambda x: x['score'], 
                reverse=True
            )[:5]  # Top 5 bits
            
            # Find recurring themes
            all_humor_text = ' '.join([item['text'] for item in humor_analysis['best_bits']])
            words = re.findall(r'\w+', all_humor_text.lower())
            word_counts = Counter(words)
            # Filter out common words and keep meaningful themes
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cant', 'wont', 'dont', 'doesnt', 'didnt', 'wasnt', 'werent', 'havent', 'hasnt', 'hadnt', 'wouldnt', 'couldnt', 'shouldnt', 'mightnt', 'mustnt'}
            humor_analysis['recurring_themes'] = [
                word for word, count in word_counts.most_common(10) 
                if word not in stop_words and len(word) > 3 and count > 1
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to analyze humor patterns: {e}")
        
        return humor_analysis
    
    def analyze_mood_trends(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze mood and emotional trends for the week"""
        mood_analysis = {
            'daily_moods': {},
            'dominant_emotions': Counter(),
            'mood_swings': [],
            'emotional_range': {},
            'patterns': {}
        }
        
        try:
            daily_emotions = defaultdict(list)
            daily_intensities = defaultdict(list)
            
            for interaction in interactions:
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                day = timestamp.strftime('%A')
                
                emotion = interaction.get('emotion')
                intensity = interaction.get('mood_intensity', 5)
                
                if emotion:
                    daily_emotions[day].append(emotion)
                    mood_analysis['dominant_emotions'][emotion] += 1
                
                if intensity:
                    daily_intensities[day].append(intensity)
            
            # Analyze daily patterns
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                emotions = daily_emotions.get(day, [])
                intensities = daily_intensities.get(day, [])
                
                if emotions:
                    dominant_emotion = Counter(emotions).most_common(1)[0][0]
                    avg_intensity = sum(intensities) / len(intensities) if intensities else 5
                    
                    mood_analysis['daily_moods'][day] = {
                        'dominant_emotion': dominant_emotion,
                        'average_intensity': round(avg_intensity, 1),
                        'emotion_count': len(emotions),
                        'emotions': list(set(emotions))
                    }
                
                # Detect mood patterns
                for pattern_name, keywords in self.mood_patterns.items():
                    pattern_count = 0
                    for interaction in interactions:
                        if datetime.fromisoformat(interaction['timestamp']).strftime('%A') == day:
                            text = interaction['text'].lower()
                            if any(keyword in text for keyword in keywords):
                                pattern_count += 1
                    
                    if pattern_count > 0:
                        if pattern_name not in mood_analysis['patterns']:
                            mood_analysis['patterns'][pattern_name] = {}
                        mood_analysis['patterns'][pattern_name][day] = pattern_count
            
            # Calculate emotional range
            all_intensities = [i for intensities in daily_intensities.values() for i in intensities]
            if all_intensities:
                mood_analysis['emotional_range'] = {
                    'min': min(all_intensities),
                    'max': max(all_intensities),
                    'average': round(sum(all_intensities) / len(all_intensities), 1),
                    'variance': round(sum((x - sum(all_intensities) / len(all_intensities))**2 for x in all_intensities) / len(all_intensities), 1)
                }
            
            # Detect significant mood swings (intensity changes > 3 points)
            for day_idx, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
                if day in mood_analysis['daily_moods'] and day_idx > 0:
                    prev_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_idx - 1]
                    if prev_day in mood_analysis['daily_moods']:
                        intensity_diff = abs(
                            mood_analysis['daily_moods'][day]['average_intensity'] - 
                            mood_analysis['daily_moods'][prev_day]['average_intensity']
                        )
                        if intensity_diff > 3:
                            mood_analysis['mood_swings'].append({
                                'from_day': prev_day,
                                'to_day': day,
                                'intensity_change': round(intensity_diff, 1),
                                'from_emotion': mood_analysis['daily_moods'][prev_day]['dominant_emotion'],
                                'to_emotion': mood_analysis['daily_moods'][day]['dominant_emotion']
                            })
            
        except Exception as e:
            self.logger.error(f"Failed to analyze mood trends: {e}")
        
        return mood_analysis
    
    def identify_memory_loops(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify recurring thoughts, topics, or behavioral patterns"""
        memory_loops = []
        
        try:
            # Analyze recurring topics
            topic_mentions = defaultdict(list)
            
            # Common topics to track
            topics = {
                'work': ['work', 'job', 'office', 'meeting', 'project', 'deadline', 'coding', 'programming'],
                'relationships': ['friend', 'family', 'relationship', 'dating', 'love', 'breakup'],
                'health': ['gym', 'exercise', 'health', 'diet', 'sleep', 'tired', 'energy'],
                'creativity': ['creative', 'art', 'music', 'writing', 'idea', 'inspiration'],
                'anxiety': ['anxiety', 'worried', 'stress', 'nervous', 'overthinking'],
                'goals': ['goal', 'plan', 'future', 'dream', 'ambition', 'resolution'],
                'technology': ['tech', 'computer', 'phone', 'app', 'software', 'internet'],
                'entertainment': ['movie', 'show', 'book', 'game', 'music', 'netflix']
            }
            
            for interaction in interactions:
                text = interaction['text'].lower()
                timestamp = interaction['timestamp']
                
                for topic, keywords in topics.items():
                    if any(keyword in text for keyword in keywords):
                        topic_mentions[topic].append({
                            'timestamp': timestamp,
                            'text': interaction['text'][:100] + '...' if len(interaction['text']) > 100 else interaction['text'],
                            'emotion': interaction.get('emotion', 'neutral')
                        })
            
            # Identify loops (topics mentioned 3+ times)
            for topic, mentions in topic_mentions.items():
                if len(mentions) >= 3:
                    # Calculate time span
                    timestamps = [datetime.fromisoformat(m['timestamp']) for m in mentions]
                    time_span = (max(timestamps) - min(timestamps)).days
                    
                    # Analyze emotional pattern
                    emotions = [m['emotion'] for m in mentions if m['emotion']]
                    dominant_emotion = Counter(emotions).most_common(1)[0][0] if emotions else 'neutral'
                    
                    memory_loops.append({
                        'topic': topic,
                        'frequency': len(mentions),
                        'time_span_days': time_span,
                        'dominant_emotion': dominant_emotion,
                        'pattern_type': 'recurring_topic',
                        'examples': mentions[:3],  # First 3 examples
                        'strength': len(mentions) / 7  # Mentions per day
                    })
            
            # Sort by strength (frequency relative to week length)
            memory_loops.sort(key=lambda x: x['strength'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to identify memory loops: {e}")
        
        return memory_loops
    
    def generate_weekly_summary(self, target_date: datetime = None) -> Dict[str, Any]:
        """Generate complete weekly summary"""
        if target_date is None:
            target_date = datetime.now()
        
        week_start, week_end = self.get_week_boundaries(target_date)
        
        self.logger.info(f"Generating weekly summary for {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        
        # Get interactions for the week
        interactions = self.get_weekly_interactions(week_start, week_end)
        
        if not interactions:
            return {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'summary': 'No interactions recorded for this week',
                'stats': {'total_interactions': 0}
            }
        
        # Generate analyses
        humor_analysis = self.analyze_humor_patterns(interactions)
        mood_analysis = self.analyze_mood_trends(interactions)
        memory_loops = self.identify_memory_loops(interactions)
        
        # Calculate basic stats
        stats = {
            'total_interactions': len(interactions),
            'daily_average': round(len(interactions) / 7, 1),
            'sources': Counter(i['source'] for i in interactions),
            'total_characters': sum(len(i['text']) for i in interactions),
            'avg_length': round(sum(len(i['text']) for i in interactions) / len(interactions), 1)
        }
        
        # Generate narrative summary
        summary_text = self._generate_narrative_summary(
            week_start, week_end, stats, humor_analysis, mood_analysis, memory_loops
        )
        
        # Compile full summary
        weekly_summary = {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'stats': stats,
            'humor_analysis': humor_analysis,
            'mood_analysis': mood_analysis,
            'memory_loops': memory_loops,
            'summary_text': summary_text
        }
        
        # Save to database
        self._save_weekly_summary(weekly_summary)
        
        return weekly_summary
    
    def _generate_narrative_summary(self, 
                                  week_start: datetime, 
                                  week_end: datetime,
                                  stats: Dict[str, Any],
                                  humor_analysis: Dict[str, Any],
                                  mood_analysis: Dict[str, Any],
                                  memory_loops: List[Dict[str, Any]]) -> str:
        """Generate a narrative text summary of the week"""
        week_name = f"Week of {week_start.strftime('%B %d')}"
        
        narrative_parts = [f"# {week_name} - Bhoola's Weekly Digest\n"]
        
        # Activity summary
        narrative_parts.append(f"📊 **Activity Overview:**")
        narrative_parts.append(f"- Total interactions: {stats['total_interactions']}")
        narrative_parts.append(f"- Daily average: {stats['daily_average']} entries")
        
        if stats['sources']:
            sources_text = ", ".join([f"{source}: {count}" for source, count in stats['sources'].items()])
            narrative_parts.append(f"- Sources: {sources_text}")
        
        # Humor highlights
        if humor_analysis['total_funny_moments'] > 0:
            narrative_parts.append(f"\n😄 **Humor Highlights:**")
            narrative_parts.append(f"- {humor_analysis['total_funny_moments']} funny moments recorded")
            
            if humor_analysis['best_bits']:
                narrative_parts.append("- Top bits:")
                for i, bit in enumerate(humor_analysis['best_bits'][:3], 1):
                    narrative_parts.append(f"  {i}. \"{bit['text'][:80]}...\"")
            
            if humor_analysis['recurring_themes']:
                themes = ", ".join(humor_analysis['recurring_themes'][:5])
                narrative_parts.append(f"- Recurring themes: {themes}")
        
        # Mood insights
        if mood_analysis['daily_moods']:
            narrative_parts.append(f"\n🎭 **Mood Journey:**")
            
            # Highlight best and worst days
            days_with_intensity = [(day, data['average_intensity']) for day, data in mood_analysis['daily_moods'].items()]
            if days_with_intensity:
                best_day = max(days_with_intensity, key=lambda x: x[1])
                worst_day = min(days_with_intensity, key=lambda x: x[1])
                
                narrative_parts.append(f"- Best day: {best_day[0]} (intensity: {best_day[1]})")
                narrative_parts.append(f"- Challenging day: {worst_day[0]} (intensity: {worst_day[1]})")
            
            if mood_analysis['dominant_emotions']:
                top_emotions = mood_analysis['dominant_emotions'].most_common(3)
                emotions_text = ", ".join([f"{emotion} ({count}x)" for emotion, count in top_emotions])
                narrative_parts.append(f"- Top emotions: {emotions_text}")
            
            if mood_analysis['mood_swings']:
                narrative_parts.append(f"- Significant mood changes: {len(mood_analysis['mood_swings'])}")
        
        # Memory patterns
        if memory_loops:
            narrative_parts.append(f"\n🔄 **Recurring Patterns:**")
            for loop in memory_loops[:3]:
                narrative_parts.append(
                    f"- {loop['topic'].title()}: {loop['frequency']} mentions "
                    f"(avg {loop['strength']:.1f}/day, {loop['dominant_emotion']} mood)"
                )
        
        # Weekly reflection
        narrative_parts.append(f"\n🤔 **Week Reflection:**")
        
        if humor_analysis['total_funny_moments'] >= stats['total_interactions'] * 0.3:
            narrative_parts.append("This was a particularly humorous week - comedy was flowing! 😄")
        
        if mood_analysis.get('emotional_range', {}).get('variance', 0) > 5:
            narrative_parts.append("Emotional intensity varied significantly this week - quite the roller coaster! 🎢")
        
        if len(memory_loops) > 3:
            narrative_parts.append("Many recurring thoughts this week - lots on the mind! 🧠")
        
        return "\n".join(narrative_parts)
    
    def _save_weekly_summary(self, summary: Dict[str, Any]):
        """Save weekly summary to database"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO weekly_summaries 
                (week_start, week_end, funny_patterns, mood_trends, memory_loops, summary_text)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                summary['week_start'],
                summary['week_end'],
                json.dumps(summary['humor_analysis']),
                json.dumps(summary['mood_analysis']),
                json.dumps(summary['memory_loops']),
                summary['summary_text']
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info("Weekly summary saved to database")
            
        except Exception as e:
            self.logger.error(f"Failed to save weekly summary: {e}")
    
    def get_summary_history(self, weeks_back: int = 4) -> List[Dict[str, Any]]:
        """Get historical weekly summaries"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM weekly_summaries 
                ORDER BY week_start DESC 
                LIMIT ?
            ''', (weeks_back,))
            
            columns = [desc[0] for desc in cursor.description]
            summaries = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for summary in summaries:
                if summary['funny_patterns']:
                    summary['funny_patterns'] = json.loads(summary['funny_patterns'])
                if summary['mood_trends']:
                    summary['mood_trends'] = json.loads(summary['mood_trends'])
                if summary['memory_loops']:
                    summary['memory_loops'] = json.loads(summary['memory_loops'])
            
            conn.close()
            return summaries
            
        except Exception as e:
            self.logger.error(f"Failed to get summary history: {e}")
            return []

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize summarizer
    summarizer = WeeklySummarizer()
    
    # Add some test data
    db = summarizer.db
    
    # Add test interactions for the current week
    test_interactions = [
        ("Today I realized my code review comments are basically just me talking to my past self, and my past self is an idiot! 😂", "text", ["BhoolaMoment", "programming"], "amused", 8),
        ("Feeling really focused today. Got so much work done!", "text", ["productive"], "focused", 7),
        ("Watched a great movie tonight. Sometimes you need that creative inspiration.", "text", ["entertainment"], "inspired", 6),
        ("Overthinking again... why do I do this to myself?", "text", ["reflection"], "anxious", 4),
        ("Had an amazing idea for a new project! Can't wait to start working on it.", "text", ["creative", "Bit-worthy"], "excited", 9)
    ]
    
    for text, source, tags, emotion, intensity in test_interactions:
        db.add_interaction(text, source, tags, emotion, intensity)
    
    # Generate weekly summary
    summary = summarizer.generate_weekly_summary()
    
    print("Weekly Summary Generated:")
    print("=" * 50)
    print(summary['summary_text'])
    print("\nStats:", json.dumps(summary['stats'], indent=2))
