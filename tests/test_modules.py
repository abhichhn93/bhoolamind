"""
BhoolamMind v1.5 - Test Module
Unit tests for all modules to ensure functionality and reliability.
"""

import pytest
import os
import tempfile
import json
from datetime import datetime, timedelta
import sys

# Add modules to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))

try:
    from modules.database import BhoolamMindDB
    from modules.emotion_tagger import EmotionTagger
    from modules.bit_tracker import BitTracker
    from modules.memory_injector import MemoryInjector
    from modules.summarizer import WeeklySummarizer
    # Note: voice_transcriber and rag_engine may require additional setup
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")

class TestBhoolamMindDB:
    """Test cases for the database module"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = BhoolamMindDB(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test database"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test that database initializes correctly"""
        assert os.path.exists(self.temp_db.name)
        stats = self.db.get_stats()
        assert 'total_interactions' in stats
        assert stats['total_interactions'] == 0
    
    def test_add_interaction(self):
        """Test adding interactions to database"""
        interaction_id = self.db.add_interaction(
            text="Test interaction",
            source="test",
            tags=["test", "unit"],
            emotion="neutral",
            mood_intensity=5
        )
        
        assert interaction_id > 0
        
        # Verify interaction was added
        interactions = self.db.get_recent_interactions(limit=1)
        assert len(interactions) == 1
        assert interactions[0]['text'] == "Test interaction"
        assert interactions[0]['source'] == "test"
        assert interactions[0]['emotion'] == "neutral"
    
    def test_add_voice_metadata(self):
        """Test adding voice metadata"""
        voice_id = self.db.add_voice_metadata(
            file_path="/test/path.wav",
            transcription="Test transcription",
            detected_emotion="happy",
            language="english"
        )
        
        assert voice_id > 0
    
    def test_memory_patterns(self):
        """Test memory pattern storage and retrieval"""
        pattern_data = {"type": "humor", "keywords": ["funny", "joke"]}
        
        # Add pattern multiple times
        for _ in range(3):
            self.db.update_memory_pattern("humor", pattern_data)
        
        patterns = self.db.get_memory_patterns("humor")
        assert len(patterns) == 1
        assert patterns[0]['frequency'] == 3
        assert patterns[0]['pattern_data'] == pattern_data
    
    def test_search_interactions(self):
        """Test interaction search functionality"""
        # Add test interactions
        self.db.add_interaction("This is about programming", "text", ["coding"], "focused", 7)
        self.db.add_interaction("I love pizza", "text", ["food"], "happy", 8)
        self.db.add_interaction("Programming is fun", "text", ["coding"], "excited", 9)
        
        # Search for programming
        results = self.db.search_interactions("programming")
        assert len(results) == 2
        
        # Search for pizza
        results = self.db.search_interactions("pizza")
        assert len(results) == 1
        assert "pizza" in results[0]['text']

class TestEmotionTagger:
    """Test cases for emotion detection"""
    
    def setup_method(self):
        """Set up emotion tagger"""
        try:
            self.emotion_tagger = EmotionTagger()
        except Exception:
            pytest.skip("EmotionTagger requires additional dependencies")
    
    def test_basic_emotion_detection(self):
        """Test basic emotion detection"""
        # Happy text
        result = self.emotion_tagger.analyze_emotion("I am so happy and excited today!")
        assert result['primary_emotion'] in ['happy', 'excited', 'joy']
        assert result['intensity'] > 5
        
        # Sad text
        result = self.emotion_tagger.analyze_emotion("I feel really sad and disappointed")
        assert result['primary_emotion'] in ['sad', 'disappointed', 'grief']
        
        # Neutral text
        result = self.emotion_tagger.analyze_emotion("The weather is okay today")
        assert result['primary_emotion'] in ['neutral', 'calm']
    
    def test_hinglish_detection(self):
        """Test Hinglish emotion detection"""
        # Happy Hinglish
        result = self.emotion_tagger.analyze_emotion("Yaar, I'm so khush today!")
        assert result['intensity'] > 5
        
        # Sad Hinglish
        result = self.emotion_tagger.analyze_emotion("Bhai, main bohot udaas hun")
        assert result['primary_emotion'] in ['sad', 'disappointed']
    
    def test_batch_processing(self):
        """Test batch emotion processing"""
        texts = [
            "I'm so excited!",
            "This is terrible",
            "Just a normal day",
            "Yaar, maja aa gaya!"
        ]
        
        results = self.emotion_tagger.analyze_batch(texts)
        assert len(results) == 4
        
        for result in results:
            assert 'primary_emotion' in result
            assert 'intensity' in result
            assert 'confidence' in result

class TestBitTracker:
    """Test cases for humor/bit detection"""
    
    def setup_method(self):
        """Set up bit tracker"""
        self.bit_tracker = BitTracker()
    
    def test_humor_detection(self):
        """Test basic humor detection"""
        # Obvious joke
        result = self.bit_tracker.analyze_text("Why did the chicken cross the road? To get to the other side!")
        assert result['is_bit_worthy'] == True
        assert result['confidence'] > 0.5
        
        # Self-deprecating humor
        result = self.bit_tracker.analyze_text("My code is so bad, even the bugs have bugs")
        assert result['is_bit_worthy'] == True
        
        # Non-funny text
        result = self.bit_tracker.analyze_text("I went to the store to buy groceries")
        assert result['is_bit_worthy'] == False
    
    def test_bhoola_style_detection(self):
        """Test Bhoola-specific humor patterns"""
        # Tech humor
        result = self.bit_tracker.analyze_text("Debugging is like being a detective in a crime movie where you're also the murderer")
        assert result['is_bit_worthy'] == True
        assert result['bit_type'] in ['observational', 'tech-humor']
        
        # Wordplay
        result = self.bit_tracker.analyze_text("I'm reading a book about anti-gravity. It's impossible to put down!")
        assert result['is_bit_worthy'] == True
        assert result['bit_type'] == 'wordplay'
    
    def test_extract_patterns(self):
        """Test humor pattern extraction"""
        funny_texts = [
            "My computer has a virus. I think it caught it from my code.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't scientists trust atoms? Because they make up everything!"
        ]
        
        patterns = self.bit_tracker.extract_humor_patterns(funny_texts)
        assert len(patterns) > 0
        
        for pattern in patterns:
            assert 'pattern' in pattern
            assert 'frequency' in pattern

class TestMemoryInjector:
    """Test cases for memory injection and retrieval"""
    
    def setup_method(self):
        """Set up memory injector with test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        try:
            self.memory_injector = MemoryInjector(self.temp_db.name)
        except Exception:
            pytest.skip("MemoryInjector requires additional dependencies")
    
    def teardown_method(self):
        """Clean up"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_memory_storage(self):
        """Test storing memories"""
        result = self.memory_injector.store_memory(
            "I love programming in Python",
            emotion="excited",
            tags=["programming", "python"]
        )
        assert result == True
    
    def test_memory_retrieval(self):
        """Test retrieving relevant memories"""
        # Store some test memories
        self.memory_injector.store_memory("Python is great", emotion="happy", tags=["python"])
        self.memory_injector.store_memory("I like JavaScript too", emotion="neutral", tags=["javascript"])
        self.memory_injector.store_memory("Coding at night is peaceful", emotion="calm", tags=["coding"])
        
        # Retrieve memories about programming
        memories = self.memory_injector.retrieve_memories("programming python")
        assert len(memories) > 0
    
    def test_emotion_based_retrieval(self):
        """Test emotion-based memory retrieval"""
        # Store memories with different emotions
        self.memory_injector.store_memory("Great day at work", emotion="happy", tags=["work"])
        self.memory_injector.store_memory("Stressful deadline", emotion="anxious", tags=["work"])
        
        # Retrieve happy memories
        happy_memories = self.memory_injector.get_memories_by_emotion("happy")
        assert len(happy_memories) > 0

class TestWeeklySummarizer:
    """Test cases for weekly summary generation"""
    
    def setup_method(self):
        """Set up summarizer with test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.summarizer = WeeklySummarizer(self.temp_db.name)
        
        # Add test data
        self.add_test_data()
    
    def teardown_method(self):
        """Clean up"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def add_test_data(self):
        """Add test interactions for the current week"""
        test_interactions = [
            ("Today I realized my code is like my love life - full of bugs!", "text", ["BhoolaMoment"], "amused", 8),
            ("Feeling really productive today", "text", ["work"], "focused", 7),
            ("Had a great dinner with friends", "text", ["social"], "happy", 8),
            ("Stressed about upcoming deadline", "text", ["work"], "anxious", 4),
            ("Watched a funny movie tonight", "text", ["entertainment"], "relaxed", 6)
        ]
        
        for text, source, tags, emotion, intensity in test_interactions:
            self.summarizer.db.add_interaction(text, source, tags, emotion, intensity)
    
    def test_week_boundaries(self):
        """Test week boundary calculation"""
        test_date = datetime(2025, 7, 17)  # Thursday
        start, end = self.summarizer.get_week_boundaries(test_date)
        
        # Should be Monday to Sunday
        assert start.weekday() == 0  # Monday
        assert end.weekday() == 6   # Sunday
        assert (end - start).days == 6
    
    def test_weekly_summary_generation(self):
        """Test complete weekly summary generation"""
        summary = self.summarizer.generate_weekly_summary()
        
        assert 'week_start' in summary
        assert 'week_end' in summary
        assert 'stats' in summary
        assert 'humor_analysis' in summary
        assert 'mood_analysis' in summary
        assert 'summary_text' in summary
        
        # Check stats
        assert summary['stats']['total_interactions'] > 0
        
        # Check humor analysis
        assert 'total_funny_moments' in summary['humor_analysis']
        
        # Check mood analysis
        assert 'daily_moods' in summary['mood_analysis']
    
    def test_humor_pattern_analysis(self):
        """Test humor pattern detection in summary"""
        # Get recent interactions
        interactions = self.summarizer.db.get_recent_interactions(limit=100)
        
        humor_analysis = self.summarizer.analyze_humor_patterns(interactions)
        
        assert 'total_funny_moments' in humor_analysis
        assert 'humor_types' in humor_analysis
        assert 'best_bits' in humor_analysis
    
    def test_mood_trend_analysis(self):
        """Test mood trend analysis"""
        interactions = self.summarizer.db.get_recent_interactions(limit=100)
        
        mood_analysis = self.summarizer.analyze_mood_trends(interactions)
        
        assert 'daily_moods' in mood_analysis
        assert 'dominant_emotions' in mood_analysis
        assert 'emotional_range' in mood_analysis

class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Set up complete system for integration testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db = BhoolamMindDB(self.temp_db.name)
        self.emotion_tagger = EmotionTagger() if 'EmotionTagger' in globals() else None
        self.bit_tracker = BitTracker()
        self.summarizer = WeeklySummarizer(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_complete_workflow(self):
        """Test complete workflow from input to summary"""
        # Step 1: Add interaction with analysis
        text = "Today I discovered that my debugging skills are like my cooking - I follow the recipe but somehow everything still burns! 😂"
        
        # Analyze humor
        bit_analysis = self.bit_tracker.analyze_text(text)
        tags = ["BhoolaMoment"] if bit_analysis['is_bit_worthy'] else []
        
        # Analyze emotion (if available)
        emotion = "amused"
        intensity = 8
        if self.emotion_tagger:
            emotion_analysis = self.emotion_tagger.analyze_emotion(text)
            emotion = emotion_analysis['primary_emotion']
            intensity = emotion_analysis['intensity']
        
        # Store interaction
        interaction_id = self.db.add_interaction(
            text=text,
            source="text",
            tags=tags,
            emotion=emotion,
            mood_intensity=intensity
        )
        
        assert interaction_id > 0
        
        # Step 2: Verify storage
        interactions = self.db.get_recent_interactions(limit=1)
        assert len(interactions) == 1
        assert interactions[0]['text'] == text
        
        # Step 3: Generate summary
        summary = self.summarizer.generate_weekly_summary()
        assert summary['stats']['total_interactions'] >= 1
        
        # Step 4: Check humor detection
        if bit_analysis['is_bit_worthy']:
            assert summary['humor_analysis']['total_funny_moments'] >= 1
    
    def test_data_consistency(self):
        """Test data consistency across modules"""
        # Add multiple interactions
        interactions = [
            ("Happy coding session today!", "excited", 8),
            ("Debugging marathon continues...", "frustrated", 3),
            ("Finally fixed that bug! Victory!", "triumphant", 9),
            ("Time for a coffee break", "relaxed", 6)
        ]
        
        interaction_ids = []
        for text, emotion, intensity in interactions:
            interaction_id = self.db.add_interaction(
                text=text,
                source="text",
                emotion=emotion,
                mood_intensity=intensity
            )
            interaction_ids.append(interaction_id)
        
        # Verify all interactions are stored
        all_interactions = self.db.get_recent_interactions(limit=10)
        assert len(all_interactions) >= len(interactions)
        
        # Verify stats are consistent
        stats = self.db.get_stats()
        assert stats['total_interactions'] >= len(interactions)
        
        # Verify summary includes all data
        summary = self.summarizer.generate_weekly_summary()
        assert summary['stats']['total_interactions'] >= len(interactions)

def run_tests():
    """Run all tests with pytest"""
    # Run tests with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    return pytest.main(pytest_args)

if __name__ == "__main__":
    print("🧪 Running BhoolamMind v1.5 Test Suite...")
    print("=" * 50)
    
    # Run individual test classes if pytest is not available
    try:
        import pytest
        exit_code = run_tests()
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {exit_code})")
    except ImportError:
        print("pytest not available, running basic tests...")
        
        # Basic manual testing
        print("Testing database...")
        test_db = TestBhoolamMindDB()
        test_db.setup_method()
        test_db.test_database_initialization()
        test_db.test_add_interaction()
        test_db.teardown_method()
        print("✅ Database tests passed")
        
        print("Testing bit tracker...")
        test_bit = TestBitTracker()
        test_bit.setup_method()
        test_bit.test_humor_detection()
        print("✅ Bit tracker tests passed")
        
        print("\n✅ Basic tests completed!")
