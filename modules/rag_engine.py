"""
BhoolamMind v1.5 - RAG Engine Module
LangChain-based Retrieval-Augmented Generation system for memory injection.
Integrates with ChromaDB for vector search and supports multiple LLM backends.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

# LangChain imports
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    from langchain_community.llms import OpenAI
except ImportError:
    # Fallback for older LangChain versions
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    from langchain.llms import OpenAI

# Local imports
from .database import BhoolamindDB
from .memory_injector import MemoryInjector

@dataclass
class RAGConfig:
    """Configuration for RAG engine"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    max_context_length: int = 4000
    compression_enabled: bool = True

class BhoolaRAGEngine:
    def __init__(self, 
                 db_path: str = None,
                 vector_store_path: str = None,
                 config: RAGConfig = None):
        """
        Initialize the RAG engine with database and vector store connections.
        
        Args:
            db_path: Path to SQLite database
            vector_store_path: Path to ChromaDB vector store
            config: RAG configuration parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or RAGConfig()
        
        # Initialize database connection
        self.db = BhoolamindDB(db_path)
        
        # Initialize memory injector
        self.memory_injector = MemoryInjector(db_path, vector_store_path)
        
        # Set up vector store path
        if vector_store_path is None:
            vector_store_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'memory', 'chroma_vectors'
            )
        self.vector_store_path = vector_store_path
        
        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector store
        self.vector_store = self._initialize_vector_store()
        
        # Initialize retriever
        self.retriever = self._setup_retriever()
        
        self.logger.info("BhoolaRAGEngine initialized successfully")
    
    def _initialize_vector_store(self) -> Chroma:
        """Initialize or load existing ChromaDB vector store"""
        try:
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=self.embeddings,
                collection_name="bhoola_memories"
            )
            
            self.logger.info(f"Vector store initialized at: {self.vector_store_path}")
            return vector_store
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _setup_retriever(self):
        """Setup the retriever with optional compression"""
        base_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.config.top_k_results}
        )
        
        if self.config.compression_enabled:
            try:
                # Note: This requires OpenAI API key for compression
                # Falls back to base retriever if not available
                compressor = LLMChainExtractor.from_llm(OpenAI())
                compressed_retriever = ContextualCompressionRetriever(
                    base_compressor=compressor,
                    base_retriever=base_retriever
                )
                self.logger.info("Compression retriever enabled")
                return compressed_retriever
            except Exception as e:
                self.logger.warning(f"Compression unavailable, using base retriever: {e}")
                return base_retriever
        
        return base_retriever
    
    def add_interaction_to_vector_store(self, interaction_id: int, text: str, metadata: Dict[str, Any] = None):
        """Add an interaction to the vector store for future retrieval"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            documents = []
            for i, chunk in enumerate(chunks):
                # Prepare metadata
                chunk_metadata = {
                    "interaction_id": interaction_id,
                    "chunk_index": i,
                    "timestamp": datetime.now().isoformat(),
                    "source": "interaction"
                }
                if metadata:
                    chunk_metadata.update(metadata)
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                ))
            
            # Add to vector store
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            
            # Update embeddings table in database
            for i, doc in enumerate(documents):
                self.db.add_embedding_metadata(
                    content_id=interaction_id,
                    content_type="interaction",
                    embedding_id=f"{interaction_id}_{i}"
                )
            
            self.logger.info(f"Added interaction {interaction_id} to vector store ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add interaction to vector store: {e}")
            return False
    
    def retrieve_relevant_memories(self, 
                                 query: str, 
                                 emotion_context: str = None,
                                 time_range_days: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on query and context.
        
        Args:
            query: Search query
            emotion_context: Current emotional context for filtering
            time_range_days: Limit to memories from last N days
            
        Returns:
            List of relevant memory documents with scores
        """
        try:
            # Enhance query with emotion context
            enhanced_query = query
            if emotion_context:
                enhanced_query = f"{query} emotion:{emotion_context}"
            
            # Retrieve documents
            if self.config.compression_enabled and hasattr(self.retriever, 'get_relevant_documents'):
                docs = self.retriever.get_relevant_documents(enhanced_query)
            else:
                docs = self.vector_store.similarity_search_with_score(
                    enhanced_query, 
                    k=self.config.top_k_results
                )
            
            # Process and filter results
            relevant_memories = []
            for doc, score in docs if isinstance(docs[0], tuple) else [(doc, 0.0) for doc in docs]:
                # Filter by similarity threshold
                if score > self.config.similarity_threshold:
                    continue
                
                # Filter by time range if specified
                if time_range_days and 'timestamp' in doc.metadata:
                    doc_time = datetime.fromisoformat(doc.metadata['timestamp'])
                    if (datetime.now() - doc_time).days > time_range_days:
                        continue
                
                relevant_memories.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': score,
                    'interaction_id': doc.metadata.get('interaction_id'),
                    'timestamp': doc.metadata.get('timestamp')
                })
            
            # Sort by relevance score
            relevant_memories.sort(key=lambda x: x['similarity_score'])
            
            self.logger.info(f"Retrieved {len(relevant_memories)} relevant memories for query: {query}")
            return relevant_memories
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    def generate_context_prompt(self, 
                              query: str, 
                              emotion_context: str = None,
                              user_preferences: Dict[str, Any] = None) -> str:
        """
        Generate enhanced prompt with relevant memories and context.
        
        Args:
            query: User's current query/request
            emotion_context: Current emotional state
            user_preferences: User behavioral preferences
            
        Returns:
            Enhanced prompt with memory context
        """
        try:
            # Retrieve relevant memories
            memories = self.retrieve_relevant_memories(query, emotion_context, time_range_days=30)
            
            # Get recent patterns from memory injector
            humor_patterns = self.memory_injector.get_humor_patterns(limit=3)
            recent_emotions = self.memory_injector.get_recent_emotions(limit=5)
            
            # Build context sections
            context_sections = []
            
            # User preferences
            if user_preferences:
                prefs_text = "\n".join([f"- {key}: {value}" for key, value in user_preferences.items()])
                context_sections.append(f"USER PREFERENCES:\n{prefs_text}")
            
            # Recent emotional context
            if recent_emotions:
                emotions_text = ", ".join([f"{e['emotion']} ({e['intensity']})" for e in recent_emotions[:3]])
                context_sections.append(f"RECENT EMOTIONAL CONTEXT: {emotions_text}")
            
            # Humor patterns
            if humor_patterns:
                humor_text = "\n".join([f"- {p['pattern']}" for p in humor_patterns])
                context_sections.append(f"HUMOR STYLE PATTERNS:\n{humor_text}")
            
            # Relevant memories
            if memories:
                memory_texts = []
                for memory in memories[:3]:  # Top 3 most relevant
                    timestamp = memory.get('timestamp', 'Unknown time')
                    content = memory['content'][:200] + "..." if len(memory['content']) > 200 else memory['content']
                    memory_texts.append(f"[{timestamp}] {content}")
                
                memories_text = "\n".join(memory_texts)
                context_sections.append(f"RELEVANT PAST MEMORIES:\n{memories_text}")
            
            # Construct final prompt
            if context_sections:
                context_block = "\n\n".join(context_sections)
                enhanced_prompt = f"""CONTEXT FOR RESPONSE:
{context_block}

CURRENT REQUEST: {query}

Please respond considering the above context, maintaining consistency with past interactions and emotional patterns."""
            else:
                enhanced_prompt = query
            
            # Ensure prompt doesn't exceed max length
            if len(enhanced_prompt) > self.config.max_context_length:
                enhanced_prompt = enhanced_prompt[:self.config.max_context_length] + "..."
            
            self.logger.info(f"Generated context prompt with {len(context_sections)} context sections")
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to generate context prompt: {e}")
            return query
    
    def sync_database_to_vector_store(self, days_back: int = 7):
        """Sync recent database interactions to vector store"""
        try:
            # Get recent interactions
            recent_interactions = self.db.get_recent_interactions(limit=100)
            
            synced_count = 0
            for interaction in recent_interactions:
                # Check if already in vector store
                existing_embeddings = self.db.get_embeddings_for_content(
                    interaction['id'], 'interaction'
                )
                
                if not existing_embeddings:
                    # Add to vector store
                    metadata = {
                        'source': interaction['source'],
                        'emotion': interaction['emotion'],
                        'tags': interaction['tags'],
                        'session_id': interaction['session_id']
                    }
                    
                    success = self.add_interaction_to_vector_store(
                        interaction['id'],
                        interaction['text'],
                        metadata
                    )
                    
                    if success:
                        synced_count += 1
            
            self.logger.info(f"Synced {synced_count} interactions to vector store")
            return synced_count
            
        except Exception as e:
            self.logger.error(f"Failed to sync database to vector store: {e}")
            return 0
    
    def search_memories_by_emotion(self, emotion: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories filtered by specific emotion"""
        try:
            # Search vector store with emotion filter
            docs_with_scores = self.vector_store.similarity_search_with_score(
                f"emotion:{emotion}",
                k=limit,
                filter={"emotion": emotion}
            )
            
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': score
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search memories by emotion: {e}")
            return []
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            collection = self.vector_store._collection
            count = collection.count()
            
            # Get sample of metadata to analyze
            if count > 0:
                sample = collection.peek(limit=min(100, count))
                
                # Analyze metadata
                emotions = []
                sources = []
                for metadata in sample.get('metadatas', []):
                    if metadata and 'emotion' in metadata:
                        emotions.append(metadata['emotion'])
                    if metadata and 'source' in metadata:
                        sources.append(metadata['source'])
                
                from collections import Counter
                emotion_counts = Counter(emotions)
                source_counts = Counter(sources)
                
                return {
                    'total_documents': count,
                    'emotions_distribution': dict(emotion_counts),
                    'sources_distribution': dict(source_counts),
                    'vector_store_path': self.vector_store_path
                }
            else:
                return {
                    'total_documents': 0,
                    'emotions_distribution': {},
                    'sources_distribution': {},
                    'vector_store_path': self.vector_store_path
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get vector store stats: {e}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize RAG engine
    rag_engine = BhoolaRAGEngine()
    
    # Test adding interaction
    db = rag_engine.db
    interaction_id = db.add_interaction(
        text="Today I discovered that debugging is like being a detective in a crime movie where you're also the murderer. Very meta experience! 🕵️‍♂️",
        source="text",
        tags=["BhoolaMoment", "programming-humor", "meta"],
        emotion="amused",
        mood_intensity=8
    )
    
    # Add to vector store
    rag_engine.add_interaction_to_vector_store(
        interaction_id,
        "Today I discovered that debugging is like being a detective in a crime movie where you're also the murderer. Very meta experience! 🕵️‍♂️",
        {"emotion": "amused", "tags": ["BhoolaMoment"]}
    )
    
    # Test retrieval
    memories = rag_engine.retrieve_relevant_memories("debugging programming")
    print(f"Found {len(memories)} relevant memories")
    
    # Test context generation
    context_prompt = rag_engine.generate_context_prompt(
        "Help me write better code",
        emotion_context="focused"
    )
    print("Generated context prompt:")
    print(context_prompt)
    
    # Get stats
    stats = rag_engine.get_vector_store_stats()
    print("Vector store stats:", json.dumps(stats, indent=2))
