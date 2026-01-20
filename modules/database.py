"""
BhoolamMind v1.5 Database Schema & Initialization
Handles SQLite setup for emotional memory storage
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

class BhoolamindDB:
    def __init__(self, db_path="memory/sqlite_db/bhoolamind.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Interactions table - Core emotional & textual memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                tags TEXT,
                emotion TEXT,
                mood TEXT,
                intensity INTEGER DEFAULT 1,
                bit_worthy BOOLEAN DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Voice metadata table - Audio-specific data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                transcription TEXT,
                tone TEXT,
                detected_emotion TEXT,
                language TEXT DEFAULT 'hinglish',
                duration_seconds REAL,
                quality_score REAL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT 0
            )
        ''')
        
        # Memory patterns - Recurring themes & humor evolution
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_text TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                evolution_notes TEXT,
                humor_category TEXT
            )
        ''')
        
        # Weekly summaries - Compressed insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start TEXT NOT NULL,
                week_end TEXT NOT NULL,
                funny_patterns TEXT,
                mood_trends TEXT,
                memory_loops TEXT,
                bit_collection TEXT,
                insights TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Embedding metadata - Vector search references
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER,
                vector_id TEXT,
                model_used TEXT DEFAULT 'all-MiniLM-L6-v2',
                embedding_type TEXT DEFAULT 'text',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (interaction_id) REFERENCES interactions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ BhoolamMind database initialized at {self.db_path}")
    
    def add_interaction(self, text, source="manual", tags=None, emotion=None, 
                       mood=None, intensity=1, bit_worthy=False):
        """Add new interaction to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions 
            (text, source, tags, emotion, mood, intensity, bit_worthy, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (text, source, tags, emotion, mood, intensity, bit_worthy, 
              datetime.now().isoformat()))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return interaction_id
    
    def add_voice_log(self, file_path, transcription=None, tone=None, 
                     detected_emotion=None, language="hinglish"):
        """Add voice metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO voice_metadata 
            (file_path, transcription, tone, detected_emotion, language, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_path, transcription, tone, detected_emotion, language,
              datetime.now().isoformat()))
        
        voice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return voice_id
    
    def get_recent_interactions(self, limit=10, days=7):
        """Get recent interactions for context injection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interactions 
            WHERE datetime(timestamp) >= datetime('now', '-{} days')
            ORDER BY timestamp DESC LIMIT ?
        '''.format(days), (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_by_emotion(self, emotion, limit=5):
        """Find similar emotional states"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interactions 
            WHERE emotion = ? OR mood = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (emotion, emotion, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_bit_worthy_collection(self):
        """Get all bit-worthy content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interactions 
            WHERE bit_worthy = 1
            ORDER BY timestamp DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def update_pattern_frequency(self, pattern_text, pattern_type="humor"):
        """Track recurring patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute('''
            SELECT id, frequency FROM memory_patterns 
            WHERE pattern_text = ? AND pattern_type = ?
        ''', (pattern_text, pattern_type))
        
        result = cursor.fetchone()
        
        if result:
            # Update frequency
            pattern_id, frequency = result
            cursor.execute('''
                UPDATE memory_patterns 
                SET frequency = ?, last_seen = ?
                WHERE id = ?
            ''', (frequency + 1, datetime.now().isoformat(), pattern_id))
        else:
            # Create new pattern
            cursor.execute('''
                INSERT INTO memory_patterns 
                (pattern_type, pattern_text, frequency, first_seen, last_seen)
                VALUES (?, ?, 1, ?, ?)
            ''', (pattern_type, pattern_text, datetime.now().isoformat(),
                  datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

# Initialize database when module is imported
if __name__ == "__main__":
    db = BhoolamindDB()
    
    # Add sample data for testing
    sample_interactions = [
        ("Yaar, maine aaj ek funny observation kiya - why do people say 'sleep tight'? Kya loose sleep hoti hai?", 
         "voice", "humor,wordplay", "amused", "high", 3, True),
        ("Feeling anxious about the standup show tomorrow", 
         "manual", "anxiety,performance", "nervous", "medium", 2, False),
        ("Gotu kola liya aaj, memory slightly better lag raha hai", 
         "manual", "health,memory", "hopeful", "medium", 2, False)
    ]
    
    for interaction in sample_interactions:
        db.add_interaction(*interaction)
    
    print("✅ Sample data added to BhoolamMind database")
