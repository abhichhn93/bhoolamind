"""
BhoolamMind v1.5 - Voice Transcriber
Whisper-based local transcription for Hindi, Hinglish, English audio logs
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
import logging

try:
    import whisper
    import torch
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available. Install with: pip install openai-whisper")

try:
    import librosa
    import numpy as np
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    logging.warning("Audio processing libs not available. Install: pip install librosa")

class VoiceTranscriber:
    def __init__(self, model_size: str = "base", data_dir: str = "data"):
        """
        Initialize Whisper transcription system
        model_size options: tiny, base, small, medium, large
        """
        self.model_size = model_size
        self.model = None
        self.data_dir = Path(data_dir)
        self.voice_dir = self.data_dir / "raw_voice"
        self.logs_dir = self.data_dir / "logs"
        
        # Create directories
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load Whisper model
        if WHISPER_AVAILABLE:
            try:
                print(f"🎤 Loading Whisper model: {model_size}")
                self.model = whisper.load_model(model_size)
                print(f"✅ Whisper model loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load Whisper model: {e}")
                self.model = None
        
        # Language detection patterns
        self.language_patterns = {
            "hindi": ["है", "का", "की", "में", "को", "से", "पर", "और", "या"],
            "hinglish": ["yaar", "matlab", "basically", "obviously", "hai", "ka", "ki"],
            "english": ["the", "and", "is", "are", "was", "were", "have", "has"]
        }
        
        # Audio quality thresholds
        self.quality_thresholds = {
            "duration_min": 0.5,  # Minimum 0.5 seconds
            "duration_max": 300,  # Maximum 5 minutes
            "sample_rate_min": 8000,  # Minimum sample rate
            "silence_ratio_max": 0.8  # Maximum silence ratio
        }
    
    def transcribe_audio(self, audio_path: str, language: str = "auto") -> Dict:
        """
        Transcribe audio file to text with metadata
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            return {"error": f"Audio file not found: {audio_path}"}
        
        transcription_result = {
            "file_path": str(audio_path),
            "transcription": "",
            "language": language,
            "confidence": 0.0,
            "duration": 0.0,
            "quality_score": 0.0,
            "segments": [],
            "detected_emotions": [],
            "timestamp": datetime.now().isoformat(),
            "model_used": self.model_size
        }
        
        try:
            # Analyze audio quality first
            quality_analysis = self._analyze_audio_quality(audio_path)
            transcription_result.update(quality_analysis)
            
            if transcription_result["quality_score"] < 0.3:
                transcription_result["warning"] = "Low audio quality detected"
            
            # Transcribe using Whisper
            if self.model:
                print(f"🎤 Transcribing: {audio_path.name}")
                
                # Whisper transcription
                result = self.model.transcribe(
                    str(audio_path),
                    language=None if language == "auto" else language,
                    task="transcribe"
                )
                
                transcription_result["transcription"] = result["text"].strip()
                transcription_result["language"] = result.get("language", "unknown")
                transcription_result["segments"] = result.get("segments", [])
                
                # Calculate confidence from segments
                if transcription_result["segments"]:
                    avg_confidence = np.mean([
                        segment.get("avg_logprob", -1.0) 
                        for segment in transcription_result["segments"]
                    ])
                    # Convert log probability to confidence score
                    transcription_result["confidence"] = max(0.0, min(1.0, (avg_confidence + 1.0)))
                
                # Detect language mix (Hinglish detection)
                detected_lang = self._detect_language_mix(transcription_result["transcription"])
                transcription_result["detected_language_mix"] = detected_lang
                
                # Extract emotional indicators from transcript
                transcription_result["emotional_indicators"] = self._extract_emotional_indicators(
                    transcription_result["transcription"]
                )
                
                print(f"✅ Transcription complete: {len(transcription_result['transcription'])} chars")
                
            else:
                transcription_result["error"] = "Whisper model not available"
                
        except Exception as e:
            transcription_result["error"] = f"Transcription failed: {str(e)}"
            logging.error(f"Transcription error: {e}")
        
        # Save transcription log
        self._save_transcription_log(transcription_result)
        
        return transcription_result
    
    def _analyze_audio_quality(self, audio_path: Path) -> Dict:
        """Analyze audio file quality"""
        quality_info = {
            "duration": 0.0,
            "sample_rate": 0,
            "quality_score": 0.0,
            "quality_issues": []
        }
        
        if not AUDIO_PROCESSING_AVAILABLE:
            quality_info["quality_score"] = 0.5  # Default moderate quality
            return quality_info
        
        try:
            # Load audio with librosa
            y, sr = librosa.load(audio_path)
            quality_info["duration"] = len(y) / sr
            quality_info["sample_rate"] = sr
            
            # Check duration
            if quality_info["duration"] < self.quality_thresholds["duration_min"]:
                quality_info["quality_issues"].append("too_short")
            elif quality_info["duration"] > self.quality_thresholds["duration_max"]:
                quality_info["quality_issues"].append("too_long")
            
            # Check sample rate
            if sr < self.quality_thresholds["sample_rate_min"]:
                quality_info["quality_issues"].append("low_sample_rate")
            
            # Calculate silence ratio
            silence_threshold = 0.01
            silence_frames = np.sum(np.abs(y) < silence_threshold)
            silence_ratio = silence_frames / len(y)
            
            if silence_ratio > self.quality_thresholds["silence_ratio_max"]:
                quality_info["quality_issues"].append("too_much_silence")
            
            # Calculate overall quality score
            quality_score = 1.0
            quality_score -= len(quality_info["quality_issues"]) * 0.2
            quality_score -= silence_ratio * 0.3
            
            if sr >= 16000:
                quality_score += 0.1
            
            quality_info["quality_score"] = max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logging.warning(f"Audio quality analysis failed: {e}")
            quality_info["quality_score"] = 0.5
        
        return quality_info
    
    def _detect_language_mix(self, text: str) -> Dict:
        """Detect language mixing in transcription"""
        text_lower = text.lower()
        
        language_scores = {}
        for lang, patterns in self.language_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                language_scores[lang] = score
        
        total_words = len(text.split())
        language_percentages = {
            lang: (score / total_words) * 100 
            for lang, score in language_scores.items()
        }
        
        # Determine primary language and mixing
        if not language_scores:
            return {"primary": "unknown", "mixing": False, "percentages": {}}
        
        primary_lang = max(language_scores.items(), key=lambda x: x[1])[0]
        is_mixed = len(language_scores) > 1
        
        return {
            "primary": primary_lang,
            "mixing": is_mixed,
            "percentages": language_percentages,
            "languages_detected": list(language_scores.keys())
        }
    
    def _extract_emotional_indicators(self, text: str) -> List[Dict]:
        """Extract emotional cues from transcription"""
        emotional_patterns = {
            "laughter": ["haha", "hehe", "lol", "laugh", "हंसी"],
            "excitement": ["wow", "amazing", "fantastic", "brilliant", "वाह"],
            "frustration": ["ugh", "damn", "shit", "frustrated", "परेशान"],
            "confusion": ["huh", "what", "confused", "समझ", "confuse"],
            "sadness": ["sad", "upset", "crying", "उदास", "दुखी"],
            "surprise": ["oh", "whoa", "shocked", "surprised", "अरे"]
        }
        
        indicators = []
        text_lower = text.lower()
        
        for emotion, patterns in emotional_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    # Find position in text
                    start_pos = text_lower.find(pattern)
                    indicators.append({
                        "emotion": emotion,
                        "pattern": pattern,
                        "position": start_pos,
                        "context": text[max(0, start_pos-20):start_pos+20]
                    })
        
        return indicators
    
    def _save_transcription_log(self, transcription_data: Dict):
        """Save transcription results to log file"""
        log_file = self.logs_dir / f"transcriptions_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Add new transcription
        logs.append(transcription_data)
        
        # Save updated logs
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save transcription log: {e}")
    
    def batch_transcribe_directory(self, directory: str = None) -> List[Dict]:
        """Transcribe all audio files in a directory"""
        if directory is None:
            directory = self.voice_dir
        
        directory = Path(directory)
        audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(directory.glob(f"*{ext}"))
        
        if not audio_files:
            print(f"No audio files found in {directory}")
            return []
        
        print(f"🎤 Found {len(audio_files)} audio files to transcribe")
        
        results = []
        for audio_file in audio_files:
            print(f"Processing: {audio_file.name}")
            result = self.transcribe_audio(audio_file)
            results.append(result)
            
            # Brief pause between files
            import time
            time.sleep(0.5)
        
        print(f"✅ Batch transcription complete: {len(results)} files processed")
        return results
    
    def get_recent_transcriptions(self, days: int = 7) -> List[Dict]:
        """Get recent transcription logs"""
        recent_logs = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_file = self.logs_dir / f"transcriptions_{date.strftime('%Y%m%d')}.json"
            
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        daily_logs = json.load(f)
                        recent_logs.extend(daily_logs)
                except Exception as e:
                    logging.warning(f"Failed to read log file {log_file}: {e}")
        
        # Sort by timestamp
        recent_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return recent_logs

# Test the voice transcriber
if __name__ == "__main__":
    transcriber = VoiceTranscriber(model_size="base")
    
    print("🎤 BhoolamMind Voice Transcriber Test")
    print(f"Model available: {'✅' if transcriber.model else '❌'}")
    print(f"Audio processing: {'✅' if AUDIO_PROCESSING_AVAILABLE else '❌'}")
    
    # Test language detection
    test_texts = [
        "Hello this is a test in English",
        "Yaar maine aaj ek funny thing observe kiya hai",
        "मैं आज बहुत खुश हूं और comedy show के लिए excited हूं",
        "Basically main confused hun, matlab kya kar raha hun life mein"
    ]
    
    print("\n🌐 Language Detection Test:")
    for text in test_texts:
        lang_result = transcriber._detect_language_mix(text)
        print(f"Text: {text[:50]}...")
        print(f"Primary: {lang_result['primary']}, Mixed: {lang_result['mixing']}")
        print(f"Languages: {lang_result['languages_detected']}")
        print("-" * 50)
    
    # Test emotional indicator extraction
    print("\n😊 Emotional Indicator Test:")
    emotional_text = "Haha that was amazing yaar! But I'm also confused about what happened. Wow!"
    indicators = transcriber._extract_emotional_indicators(emotional_text)
    print(f"Text: {emotional_text}")
    for indicator in indicators:
        print(f"  {indicator['emotion']}: '{indicator['pattern']}' at position {indicator['position']}")
    
    # Check for audio files in voice directory
    audio_files = list(transcriber.voice_dir.glob("*.wav")) + list(transcriber.voice_dir.glob("*.mp3"))
    if audio_files:
        print(f"\n📁 Found {len(audio_files)} audio files in voice directory")
        print("Run batch_transcribe_directory() to process them")
    else:
        print(f"\n📁 No audio files found in {transcriber.voice_dir}")
        print("Add some .wav or .mp3 files to test transcription")
