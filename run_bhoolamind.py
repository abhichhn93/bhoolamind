"""
BhoolamMind v1.5 - Main Runner
Central orchestrator for the AI memory and emotional context engine

Run this file to start the BhoolamMind system
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

# Import BhoolamMind modules
try:
    from modules.database import BhoolamindDB
    from modules.bit_tracker import BitTracker
    from modules.emotion_tagger import EmotionTagger
    from modules.voice_transcriber import VoiceTranscriber
    from modules.memory_injector import MemoryInjector
    print("✅ All BhoolamMind modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

class BhoolamMind:
    """
    Main BhoolamMind system controller
    Orchestrates all modules for complete emotional AI memory experience
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize BhoolamMind with all components"""
        print("🧠 Initializing BhoolamMind v1.5...")
        
        self.data_dir = Path(data_dir)
        self.session_log = []
        
        # Initialize core components
        try:
            self.db = BhoolamindDB()
            self.bit_tracker = BitTracker()
            self.emotion_tagger = EmotionTagger()
            self.voice_transcriber = VoiceTranscriber()
            self.memory_injector = MemoryInjector()
            
            print("✅ BhoolamMind fully initialized!")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise
        
        # System capabilities
        self.capabilities = {
            "database": True,
            "bit_tracking": True,
            "emotion_detection": hasattr(self.emotion_tagger, 'emotion_pipeline') and 
                                self.emotion_tagger.emotion_pipeline is not None,
            "voice_transcription": hasattr(self.voice_transcriber, 'model') and 
                                  self.voice_transcriber.model is not None,
            "memory_injection": hasattr(self.memory_injector, 'embedding_model') and 
                               self.memory_injector.embedding_model is not None,
            "vector_search": hasattr(self.memory_injector, 'chroma_client') and 
                            self.memory_injector.chroma_client is not None
        }
        
        self._print_system_status()
    
    def _print_system_status(self):
        """Print current system capabilities"""
        print("\n🎯 BhoolamMind System Status:")
        for capability, available in self.capabilities.items():
            status = "✅" if available else "⚠️"
            print(f"  {status} {capability.replace('_', ' ').title()}")
        
        missing_deps = []
        if not self.capabilities["emotion_detection"]:
            missing_deps.append("transformers, torch")
        if not self.capabilities["voice_transcription"]:
            missing_deps.append("openai-whisper")
        if not self.capabilities["memory_injection"]:
            missing_deps.append("sentence-transformers")
        if not self.capabilities["vector_search"]:
            missing_deps.append("chromadb")
        
        if missing_deps:
            print(f"\n⚠️  Install missing dependencies: pip install {' '.join(missing_deps)}")
        print()
    
    def process_text_input(self, text: str, source: str = "manual") -> Dict:
        """
        Process text input through complete BhoolamMind pipeline
        Returns comprehensive analysis and stores in memory
        """
        print(f"🔄 Processing text input: {text[:50]}...")
        
        result = {
            "input_text": text,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "processing_steps": [],
            "final_analysis": {}
        }
        
        try:
            # Step 1: Emotion Analysis
            if self.capabilities["emotion_detection"]:
                emotion_analysis = self.emotion_tagger.detect_emotions(text)
                result["emotion_analysis"] = emotion_analysis
                result["processing_steps"].append("emotion_detection")
                print(f"  😊 Emotion: {emotion_analysis['primary_emotion']} "
                      f"({emotion_analysis['bhoola_mood']})")
            
            # Step 2: Bit Tracking
            if self.capabilities["bit_tracking"]:
                bit_analysis = self.bit_tracker.analyze_text(text, source)
                result["bit_analysis"] = bit_analysis
                result["processing_steps"].append("bit_tracking")
                if bit_analysis["bit_worthy"]:
                    print(f"  🎭 BIT WORTHY! Categories: {', '.join(bit_analysis['humor_categories'])}")
            
            # Step 3: Memory Context Injection
            if self.capabilities["memory_injection"]:
                current_emotion = result.get("emotion_analysis", {}).get("bhoola_mood")
                memory_context = self.memory_injector.inject_context_memories(
                    text, current_emotion, max_memories=3
                )
                result["memory_context"] = memory_context
                result["processing_steps"].append("memory_injection")
                
                if memory_context["relevant_memories"]:
                    print(f"  🧠 Found {len(memory_context['relevant_memories'])} relevant memories")
            
            # Step 4: Store in Database
            emotion = result.get("emotion_analysis", {}).get("bhoola_mood")
            tags = result.get("bit_analysis", {}).get("tags", "")
            intensity = result.get("emotion_analysis", {}).get("intensity", 1)
            bit_worthy = result.get("bit_analysis", {}).get("bit_worthy", False)
            
            interaction_id = self.db.add_interaction(
                text=text,
                source=source,
                tags=tags,
                emotion=emotion,
                intensity=intensity,
                bit_worthy=bit_worthy
            )
            
            result["interaction_id"] = interaction_id
            result["processing_steps"].append("database_storage")
            
            # Step 5: Add to Vector Memory (if available)
            if self.capabilities["memory_injection"]:
                self.memory_injector.add_memory(text, emotion, tags, interaction_id)
                result["processing_steps"].append("vector_storage")
            
            # Compile final analysis
            result["final_analysis"] = {
                "stored": True,
                "emotion": emotion,
                "bit_worthy": bit_worthy,
                "interaction_id": interaction_id,
                "processing_complete": True
            }
            
            print(f"  ✅ Processing complete - stored as interaction #{interaction_id}")
            
        except Exception as e:
            result["error"] = str(e)
            result["final_analysis"]["processing_complete"] = False
            print(f"  ❌ Processing failed: {e}")
        
        # Add to session log
        self.session_log.append(result)
        
        return result
    
    def process_voice_input(self, audio_file_path: str) -> Dict:
        """
        Process voice input through transcription and full pipeline
        """
        print(f"🎤 Processing voice input: {audio_file_path}")
        
        if not self.capabilities["voice_transcription"]:
            return {"error": "Voice transcription not available"}
        
        # Transcribe audio
        transcription_result = self.voice_transcriber.transcribe_audio(audio_file_path)
        
        if "error" in transcription_result:
            return transcription_result
        
        transcribed_text = transcription_result.get("transcription", "")
        
        if not transcribed_text:
            return {"error": "No transcription generated"}
        
        print(f"  📝 Transcribed: {transcribed_text[:50]}...")
        
        # Process transcribed text through pipeline
        text_result = self.process_text_input(transcribed_text, source="voice")
        
        # Combine results
        combined_result = {
            **text_result,
            "voice_metadata": transcription_result,
            "audio_file": audio_file_path
        }
        
        return combined_result
    
    def get_daily_summary(self, date: str = None) -> Dict:
        """
        Generate daily summary of interactions, emotions, and bits
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's interactions
        recent_interactions = self.db.get_recent_interactions(limit=100, days=1)
        
        if not recent_interactions:
            return {"date": date, "summary": "No interactions found for today"}
        
        # Analyze patterns
        emotions = [i[4] for i in recent_interactions if i[4]]  # emotion column
        bit_worthy_count = sum(1 for i in recent_interactions if i[6])  # bit_worthy column
        total_interactions = len(recent_interactions)
        
        # Most common emotion
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
        
        # Get bit collection
        bit_collection = self.db.get_bit_worthy_collection()
        todays_bits = [bit for bit in bit_collection 
                      if bit[7].startswith(date)]  # timestamp column
        
        summary = {
            "date": date,
            "total_interactions": total_interactions,
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": emotion_counts,
            "bit_worthy_count": bit_worthy_count,
            "todays_bits": [bit[1] for bit in todays_bits],  # text column
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    def interactive_session(self):
        """
        Start interactive BhoolamMind session
        """
        print("\n🧠 BhoolamMind Interactive Session Started")
        print("Type 'quit' to exit, 'summary' for daily summary, 'voice <file>' for voice input")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n💭 Bhoola: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 BhoolamMind session ended")
                    break
                
                elif user_input.lower() == 'summary':
                    summary = self.get_daily_summary()
                    print(f"\n📊 Daily Summary for {summary['date']}:")
                    print(f"  Total interactions: {summary['total_interactions']}")
                    print(f"  Dominant emotion: {summary['dominant_emotion']}")
                    print(f"  Bit-worthy moments: {summary['bit_worthy_count']}")
                    
                    if summary['todays_bits']:
                        print("  Today's bits:")
                        for i, bit in enumerate(summary['todays_bits'][:3], 1):
                            print(f"    {i}. {bit[:60]}...")
                
                elif user_input.lower().startswith('voice '):
                    audio_file = user_input[6:].strip()
                    if os.path.exists(audio_file):
                        result = self.process_voice_input(audio_file)
                        if "error" not in result:
                            print(f"✅ Voice processed successfully")
                        else:
                            print(f"❌ Voice processing failed: {result['error']}")
                    else:
                        print(f"❌ Audio file not found: {audio_file}")
                
                elif user_input:
                    result = self.process_text_input(user_input)
                    
                    # Show relevant memories if found
                    if result.get("memory_context", {}).get("relevant_memories"):
                        print("\n🧠 Relevant memories:")
                        for i, memory in enumerate(result["memory_context"]["relevant_memories"][:2], 1):
                            print(f"  {i}. {memory['text'][:50]}...")
                
                else:
                    print("Please enter some text or a command")
                    
            except EOFError:
                print("\n👋 BhoolamMind session ended (no stdin)")
                break
            except KeyboardInterrupt:
                print("\n👋 BhoolamMind session ended")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def batch_process_voice_directory(self):
        """
        Process all audio files in the voice directory
        """
        if not self.capabilities["voice_transcription"]:
            print("❌ Voice transcription not available")
            return
        
        print("🎤 Processing all voice files...")
        results = self.voice_transcriber.batch_transcribe_directory()
        
        processed_count = 0
        for result in results:
            if "transcription" in result and result["transcription"]:
                # Process through full pipeline
                self.process_text_input(result["transcription"], source="voice")
                processed_count += 1
        
        print(f"✅ Batch processing complete: {processed_count} files processed")

def main():
    """Main entry point for BhoolamMind"""
    print("🧠 BhoolamMind v1.5 - AI Memory & Emotional Context Engine")
    print("=" * 60)

    parser = argparse.ArgumentParser(
        description="BhoolamMind v1.5 CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="interactive",
        choices=["interactive", "batch-voice", "summary", "sync", "test"],
        help="Command to run",
    )
    args = parser.parse_args()

    # Initialize system
    try:
        bhoolamind = BhoolamMind()
    except Exception as e:
        print(f"❌ Failed to initialize BhoolamMind: {e}")
        return

    if args.command == "interactive":
        bhoolamind.interactive_session()

    elif args.command == "batch-voice":
        bhoolamind.batch_process_voice_directory()

    elif args.command == "summary":
        summary = bhoolamind.get_daily_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    elif args.command == "sync":
        synced = bhoolamind.memory_injector.sync_sql_to_vector_db()
        print(f"✅ Synced {synced} memories to vector database")

    elif args.command == "test":
        # Run a single-sample demo and print a concise summary
        test_input = "Had a funny realization - why do they call it rush hour when nobody's moving?"
        print(f"\nDemo input: {test_input}")
        result = bhoolamind.process_text_input(test_input)
        final = result.get("final_analysis", {})
        print("\nDemo result:")
        print(f"  Stored: {final.get('stored')}")
        print(f"  Emotion: {final.get('emotion')}")
        print(f"  Bit-worthy: {final.get('bit_worthy')}")
        print(f"  Interaction ID: {final.get('interaction_id')}")

if __name__ == "__main__":
    main()
