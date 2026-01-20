"""
BhoolamMind v1.5 - Memory Injector
Pulls relevant past logs based on emotional and topical similarity using vector search
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("Sentence transformers not available. Install: pip install sentence-transformers")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install: pip install chromadb")

class MemoryInjector:
    def __init__(self, db_path: str = "memory/sqlite_db/bhoolamind.db", 
                 vector_db_path: str = "memory/chroma_vectors"):
        """
        Initialize memory injection system with both SQL and vector databases
        """
        self.db_path = Path(db_path)
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Sentence transformer model loaded")
            except Exception as e:
                print(f"❌ Failed to load embedding model: {e}")
        
        # Initialize ChromaDB
        self.chroma_client = None
        self.memory_collection = None
        if CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(path=str(self.vector_db_path))
                self.memory_collection = self.chroma_client.get_or_create_collection(
                    name="bhoola_memories",
                    metadata={"description": "Bhoola's emotional and topical memories"}
                )
                print(f"✅ ChromaDB initialized at {self.vector_db_path}")
            except Exception as e:
                print(f"❌ Failed to initialize ChromaDB: {e}")
        
        # Memory similarity thresholds
        self.similarity_thresholds = {
            "emotional": 0.6,  # Emotional similarity threshold
            "topical": 0.7,    # Topic similarity threshold
            "temporal": 0.5    # Time-based relevance threshold
        }
    
    def add_memory(self, text: str, emotion: str = None, tags: str = None, 
                   interaction_id: int = None) -> bool:
        """
        Add new memory to vector database with embeddings
        """
        if not self.embedding_model or not self.memory_collection:
            logging.warning("Vector search not available - memory not embedded")
            return False
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(text).tolist()
            
            # Prepare metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "emotion": emotion or "neutral",
                "tags": tags or "",
                "interaction_id": interaction_id or 0,
                "text_length": len(text)
            }
            
            # Add to ChromaDB
            doc_id = f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{interaction_id}"
            
            self.memory_collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            print(f"💾 Memory added to vector DB: {doc_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add memory: {e}")
            return False
    
    def find_similar_memories(self, query_text: str, emotion: str = None, 
                            limit: int = 5, days_back: int = 30) -> List[Dict]:
        """
        Find memories similar to query text based on semantic similarity
        """
        if not self.embedding_model or not self.memory_collection:
            return self._fallback_memory_search(query_text, emotion, limit, days_back)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # Search in ChromaDB
            results = self.memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # Get more results to filter
                include=["documents", "metadatas", "distances"]
            )
            
            # Process and filter results
            similar_memories = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                # Check temporal relevance
                memory_date = datetime.fromisoformat(metadata['timestamp'])
                if memory_date < cutoff_date:
                    continue
                
                # Calculate similarity score (ChromaDB returns distance, we want similarity)
                similarity = 1.0 - distance
                
                # Apply emotion filter if specified
                if emotion and metadata.get('emotion') != emotion:
                    similarity *= 0.7  # Reduce similarity for different emotions
                
                # Only include if above threshold
                if similarity >= self.similarity_thresholds['topical']:
                    similar_memories.append({
                        "text": doc,
                        "emotion": metadata.get('emotion'),
                        "tags": metadata.get('tags'),
                        "timestamp": metadata.get('timestamp'),
                        "similarity": similarity,
                        "interaction_id": metadata.get('interaction_id'),
                        "relevance_type": "semantic"
                    })
            
            # Sort by similarity and limit results
            similar_memories.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_memories[:limit]
            
        except Exception as e:
            logging.error(f"Vector search failed: {e}")
            return self._fallback_memory_search(query_text, emotion, limit, days_back)
    
    def find_emotional_memories(self, emotion: str, limit: int = 5, 
                              days_back: int = 30) -> List[Dict]:
        """
        Find memories with similar emotional states
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query for similar emotions within time range
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            cursor.execute('''
                SELECT text, emotion, mood, tags, timestamp, intensity, bit_worthy
                FROM interactions 
                WHERE (emotion = ? OR mood = ?) 
                AND timestamp >= ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (emotion, emotion, cutoff_date, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            emotional_memories = []
            for row in results:
                emotional_memories.append({
                    "text": row[0],
                    "emotion": row[1],
                    "mood": row[2],
                    "tags": row[3],
                    "timestamp": row[4],
                    "intensity": row[5],
                    "bit_worthy": bool(row[6]),
                    "relevance_type": "emotional"
                })
            
            return emotional_memories
            
        except Exception as e:
            logging.error(f"Emotional memory search failed: {e}")
            return []
    
    def _fallback_memory_search(self, query_text: str, emotion: str = None, 
                               limit: int = 5, days_back: int = 30) -> List[Dict]:
        """
        Fallback keyword-based memory search when vector search unavailable
        """
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple keyword matching
            query_words = query_text.lower().split()
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            # Build search query
            like_conditions = " OR ".join([f"LOWER(text) LIKE ?" for _ in query_words])
            like_params = [f"%{word}%" for word in query_words]
            
            base_query = f'''
                SELECT text, emotion, mood, tags, timestamp, intensity, bit_worthy
                FROM interactions 
                WHERE ({like_conditions}) AND timestamp >= ?
            '''
            
            if emotion:
                base_query += " AND (emotion = ? OR mood = ?)"
                like_params.extend([cutoff_date, emotion, emotion])
            else:
                like_params.append(cutoff_date)
            
            base_query += " ORDER BY timestamp DESC LIMIT ?"
            like_params.append(limit)
            
            cursor.execute(base_query, like_params)
            results = cursor.fetchall()
            conn.close()
            
            # Convert to standard format
            fallback_memories = []
            for row in results:
                # Calculate simple relevance score based on keyword matches
                text_lower = row[0].lower()
                matches = sum(1 for word in query_words if word in text_lower)
                relevance = matches / len(query_words) if query_words else 0
                
                fallback_memories.append({
                    "text": row[0],
                    "emotion": row[1],
                    "mood": row[2],
                    "tags": row[3],
                    "timestamp": row[4],
                    "intensity": row[5],
                    "bit_worthy": bool(row[6]),
                    "similarity": relevance,
                    "relevance_type": "keyword"
                })
            
            return fallback_memories
            
        except Exception as e:
            logging.error(f"Fallback memory search failed: {e}")
            return []
    
    def inject_context_memories(self, current_text: str, current_emotion: str = None,
                              max_memories: int = 3) -> Dict:
        """
        Main function to inject relevant memories as context
        Returns formatted context for AI responses
        """
        context = {
            "current_input": current_text,
            "current_emotion": current_emotion,
            "relevant_memories": [],
            "memory_summary": "",
            "injection_timestamp": datetime.now().isoformat()
        }
        
        # Find similar topical memories
        topical_memories = self.find_similar_memories(
            current_text, limit=max_memories, days_back=30
        )
        
        # Find similar emotional memories if emotion is specified
        emotional_memories = []
        if current_emotion:
            emotional_memories = self.find_emotional_memories(
                current_emotion, limit=max_memories//2, days_back=14
            )
        
        # Combine and rank memories
        all_memories = topical_memories + emotional_memories
        
        # Remove duplicates and rank by relevance
        seen_texts = set()
        unique_memories = []
        for memory in all_memories:
            if memory["text"] not in seen_texts:
                seen_texts.add(memory["text"])
                unique_memories.append(memory)
        
        # Sort by similarity/relevance and limit
        unique_memories.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        context["relevant_memories"] = unique_memories[:max_memories]
        
        # Generate memory summary
        if context["relevant_memories"]:
            memory_texts = [mem["text"][:100] for mem in context["relevant_memories"]]
            context["memory_summary"] = self._generate_memory_summary(
                context["relevant_memories"]
            )
        
        return context
    
    def _generate_memory_summary(self, memories: List[Dict]) -> str:
        """
        Generate a concise summary of relevant memories for context injection
        """
        if not memories:
            return "No relevant memories found."
        
        summary_parts = []
        
        # Group by type
        emotional_memories = [m for m in memories if m.get("relevance_type") == "emotional"]
        semantic_memories = [m for m in memories if m.get("relevance_type") == "semantic"]
        
        if emotional_memories:
            emotions = [m.get("emotion", "unknown") for m in emotional_memories]
            summary_parts.append(f"Similar emotional states: {', '.join(set(emotions))}")
        
        if semantic_memories:
            summary_parts.append(f"Found {len(semantic_memories)} topically related memories")
        
        # Add bit-worthy note
        bit_worthy_count = sum(1 for m in memories if m.get("bit_worthy"))
        if bit_worthy_count > 0:
            summary_parts.append(f"{bit_worthy_count} comedy-worthy moments")
        
        return " | ".join(summary_parts)
    
    def sync_sql_to_vector_db(self, days_back: int = 7) -> int:
        """
        Sync recent SQL interactions to vector database
        """
        if not self.embedding_model or not self.memory_collection:
            print("❌ Vector database not available for sync")
            return 0
        
        if not self.db_path.exists():
            print("❌ SQL database not found")
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent interactions not yet in vector DB
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            cursor.execute('''
                SELECT id, text, emotion, tags, timestamp
                FROM interactions 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff_date,))
            
            results = cursor.fetchall()
            conn.close()
            
            synced_count = 0
            for row in results:
                interaction_id, text, emotion, tags, timestamp = row
                
                # Check if already in vector DB
                doc_id = f"memory_{timestamp}_{interaction_id}"
                
                try:
                    # Try to get existing document
                    existing = self.memory_collection.get(ids=[doc_id])
                    if existing and existing['ids']:
                        continue  # Already exists
                except:
                    pass  # Document doesn't exist, proceed to add
                
                # Add to vector DB
                if self.add_memory(text, emotion, tags, interaction_id):
                    synced_count += 1
            
            print(f"✅ Synced {synced_count} memories to vector database")
            return synced_count
            
        except Exception as e:
            logging.error(f"Memory sync failed: {e}")
            return 0

# Test the memory injector
if __name__ == "__main__":
    injector = MemoryInjector()
    
    print("🧠 BhoolamMind Memory Injector Test")
    print(f"Embeddings available: {'✅' if EMBEDDINGS_AVAILABLE else '❌'}")
    print(f"ChromaDB available: {'✅' if CHROMADB_AVAILABLE else '❌'}")
    print(f"Embedding model loaded: {'✅' if injector.embedding_model else '❌'}")
    
    # Test memory injection
    test_queries = [
        ("I'm feeling anxious about tomorrow's performance", "anxious"),
        ("Had a funny observation about life today", "amused"),
        ("Bhool gaya main kya kar raha tha", "confused"),
        ("Super excited about the new project", "excited")
    ]
    
    print("\n🔍 Memory Context Injection Test:")
    
    for query, emotion in test_queries:
        print(f"\nQuery: {query}")
        print(f"Emotion: {emotion}")
        
        context = injector.inject_context_memories(query, emotion, max_memories=3)
        
        print(f"Relevant memories found: {len(context['relevant_memories'])}")
        print(f"Summary: {context['memory_summary']}")
        
        for i, memory in enumerate(context['relevant_memories'], 1):
            print(f"  {i}. [{memory.get('relevance_type', 'unknown')}] "
                  f"{memory['text'][:60]}... "
                  f"(similarity: {memory.get('similarity', 0):.2f})")
        
        print("-" * 60)
    
    # Test sync functionality
    print(f"\n🔄 Testing memory sync...")
    synced = injector.sync_sql_to_vector_db(days_back=30)
    print(f"Synced {synced} memories from SQL to vector database")
