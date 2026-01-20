# 🧠 BhoolamMind v1.5

**AI Memory & Emotional Context Engine for Long-term Behavioral Consistency**

BhoolamMind v1.5 is a robust, persistent AI memory and emotional context engine designed to solve the fundamental memory limitation of AI agents (Copilot, ChatGPT, Claude, etc.). It enables daily logging, emotional analysis, humor pattern tracking, and dynamic memory injection for long-term behavioral consistency and learning.

---

## Proof (Smoke Test)

- `python run.py test` (writes to SQLite and exits)
- `pip install -r requirements-ml.txt` (enable ML extras)

BhoolamMind runs in two modes: a lightweight core mode (no heavy ML dependencies) and an optional ML-enhanced mode for emotion analysis, embeddings, and voice processing.

## 🎯 Core Features

### 🎭 **Bit Tracker**
- Automatically identifies comedy-worthy moments from daily logs
- Tracks humor evolution patterns (wordplay → observational → tech humor)
- Tags content as "Bit-worthy", "BhoolaMoment", "StonerLogic"
- Analyzes comedy patterns and suggests bit development

### 😊 **Emotion Tagger** 
- Detects emotions using pre-trained transformers (BERT/RoBERTa)
- Supports Hindi, English, and Hinglish emotional expressions
- Maps to Bhoola-specific moods: khush, udaas, pareshan, mast, confuse
- Tracks emotional intensity (1-10 scale) and mood transitions

### 🎤 **Voice Transcriber**
- Whisper-based local transcription for multilingual audio
- Processes Hindi, Hinglish, English voice logs
- Audio quality analysis and emotional indicator extraction
- Batch processing for daily voice note collections

### 🧠 **Memory Injector**
- Vector-based semantic memory search using sentence transformers
- Emotional context matching for similar mood states
- ChromaDB integration for persistent memory storage
- Automatic context injection for relevant past experiences

### � **RAG Engine**
- LangChain-based Retrieval-Augmented Generation system
- Multi-LLM backend support (ChatGPT, Claude, local models)
- Contextual compression and memory ranking
- Dynamic prompt enhancement with relevant memories

### 📊 **Weekly Summarizer**
- Automated emotion trend analysis and mood journey tracking
- Humor pattern evolution and best bits compilation
- Memory loop detection and recurring theme identification
- Weekly narrative generation with insights and reflections

### 💻 **Streamlit Dashboard**
- Interactive web interface for memory exploration
- Real-time emotion and humor analytics
- Voice upload and transcription interface
- Memory search and pattern visualization

---

## 🏗️ System Architecture

```
bhoolamind_v1.5/
├── modules/
│   ├── database.py           # SQLite schema & operations
│   ├── bit_tracker.py        # Comedy pattern detection
│   ├── emotion_tagger.py     # Emotion/mood analysis
│   ├── voice_transcriber.py  # Audio transcription
│   ├── memory_injector.py    # Vector memory storage/retrieval
│   ├── rag_engine.py         # LangChain RAG system
│   └── summarizer.py         # Weekly summary generation
├── data/
│   ├── raw_voice/           # Audio files storage
│   ├── logs/                # Daily text logs
│   └── embeddings/          # Vector embeddings cache
├── memory/
│   ├── sqlite_db/           # SQLite database
│   └── chroma_vectors/      # ChromaDB vector store
├── frontend/
│   └── dashboard.py         # Streamlit web interface
├── tests/
│   └── test_modules.py      # Unit tests
├── requirements.txt         # Dependencies
├── README.md               # This file
├── run.py                  # Canonical CLI entrypoint
└── run_bhoolamind.py       # Main orchestrator module
│   ├── voice_transcriber.py  # Audio → text processing
│   ├── memory_injector.py    # Context retrieval & injection
│   └── summarizer.py         # Daily/weekly insights
├── data/
│   ├── raw_voice/           # Audio files storage
│   ├── logs/                # Daily transcription logs
│   └── embeddings/          # Vector embeddings cache
├── memory/
│   ├── sqlite_db/           # Structured data storage
│   └── chroma_vectors/      # Vector similarity search
├── frontend/
│   └── dashboard.py         # Streamlit/Gradio interface
├── tests/
│   └── test_modules.py      # Unit tests
├── requirements.txt         # Dependencies
├── README.md               # This file
├── run.py                  # Canonical CLI entrypoint
└── run_bhoolamind.py       # Main orchestrator module
```

---

## Quickstart

```bash
cd bhoolamind_v1.5
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Self-check
python run.py --help

# Run the CLI (interactive mode)
python run.py interactive

# Optional: Streamlit dashboard
streamlit run frontend/dashboard.py
```

## Optional ML Features
Core mode runs with `requirements.txt`. For advanced features (emotion detection, voice transcription, vector search), install:

```bash
pip install -r requirements-ml.txt
```

### CLI Commands

```bash
python run.py batch-voice
python run.py summary
python run.py sync
python run.py test
```

### Demo Output

`python run.py test` runs a single demo input and prints a concise summary:

```text
Demo input: Had a funny realization - why do they call it rush hour when nobody's moving?
Demo result:
  Stored: True
  Emotion: None
  Bit-worthy: True
  Interaction ID: 55
```

Demo output also captured in `assets/demo-output.txt`.

### Optional ML Features

If you want full ML features (transformers, whisper, vector search, dashboard), install:

```bash
pip install -r requirements-ml.txt
```

For local HF cache paths (recommended when using ML features):

```bash
source env.sh
```

### 3. Core Workflow

1. **Input**: Text or voice logs about daily thoughts/experiences
2. **Processing**: 
   - Emotion detection and mood mapping
   - Comedy pattern identification
   - Memory context injection
3. **Storage**: SQLite + vector embeddings for retrieval
4. **Output**: Enhanced responses with relevant historical context

---

## 💡 Usage Examples

### Text Processing
```python
from run_bhoolamind import BhoolamMind

# Initialize system
bmind = BhoolamMind()

# Process daily thoughts
result = bmind.process_text_input(
    "Yaar, I'm feeling anxious about tomorrow's performance but also excited"
)

# Get relevant memories and emotional context
print(result["emotion_analysis"])    # Current mood analysis
print(result["memory_context"])      # Similar past experiences
print(result["bit_analysis"])        # Comedy potential assessment
```

### Voice Processing
```python
# Process voice note
result = bmind.process_voice_input("data/raw_voice/daily_log_20250717.wav")

# Automatic transcription + full analysis pipeline
print(result["voice_metadata"]["transcription"])
print(result["emotion_analysis"]["bhoola_mood"])
```

### Memory Retrieval
```python
# Find similar emotional states
memories = bmind.memory_injector.find_emotional_memories("anxious", limit=5)

# Find topically related content  
similar = bmind.memory_injector.find_similar_memories(
    "comedy performance preparation", limit=3
)
```

---

## 📋 Database Schema

### Interactions Table
- `text`: Raw input content
- `emotion`: Detected emotional state
- `tags`: Comma-separated categories
- `bit_worthy`: Boolean for comedy potential
- `intensity`: Emotional intensity (1-3)

### Voice Metadata Table
- `file_path`: Audio file location
- `transcription`: Whisper output
- `detected_emotion`: Voice-based mood
- `quality_score`: Audio quality assessment

### Memory Patterns Table
- `pattern_type`: humor, observation, confusion
- `frequency`: Occurrence tracking
- `evolution_notes`: Pattern development

---

## 🔧 Configuration

### Model Settings
```python
# Emotion detection model
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

# Voice transcription model
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

# Embedding model for memory
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
```

### Similarity Thresholds
```python
SIMILARITY_THRESHOLDS = {
    "emotional": 0.6,   # Emotional similarity
    "topical": 0.7,     # Topic similarity  
    "temporal": 0.5     # Time-based relevance
}
```

---

## 🎭 Bhoola-Specific Features

### Humor Categories
- **Wordplay**: Puns, language mixing, sound similarities
- **Observations**: Daily life insights, behavioral patterns
- **Stoner Logic**: Philosophical tangents, deep thoughts
- **Bhoola Moments**: Memory lapses, confusion, forgetfulness
- **Hinglish Gold**: Natural code-switching expressions

### Emotional Mapping
- **khush** ↔ joy, happiness, contentment
- **udaas** ↔ sadness, melancholy, blues
- **pareshan** ↔ anxiety, stress, worry
- **mast** ↔ high, elevated, philosophical
- **confuse** ↔ bewildered, uncertain, lost

### Memory Integration
- **Claude Pro Memory**: Optional API integration for extended context
- **Cross-AI Access**: Shareable context for ChatGPT, Gemini interactions
- **Behavioral Consistency**: Long-term personality trait tracking

---

## 🔮 Future Enhancements

### Phase 2 Features
- **Face Emotion Tracker**: OpenCV + DeepFace for webcam journaling
- **Gotu Reminder Bot**: Telegram bot for daily check-ins
- **GitHub Auto-commits**: Emoji-tagged progress tracking
- **Public Portfolio**: GitHub Pages showcase with Bhoola illustrations

### Advanced Capabilities
- **Dream Journal Integration**: Sleep pattern ↔ creativity correlation
- **Performance Analytics**: Stage confidence vs. practice patterns
- **Audience Response Mapping**: Crowd reaction pattern learning
- **Multi-model Ensemble**: Combined emotion detection approaches

---

## 🐛 Troubleshooting

### Common Issues

**"Transformers not available"**
```bash
pip install transformers torch
```

**"Whisper model not found"**
```bash
pip install openai-whisper
```

**"ChromaDB connection failed"**
```bash
pip install chromadb
# Check memory/chroma_vectors/ directory permissions
```

**"Low audio quality detected"**
- Ensure sample rate ≥ 8kHz
- Keep recordings 0.5-300 seconds
- Minimize background noise

---

## 📊 System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 2GB storage

### Recommended  
- Python 3.10+
- 8GB RAM
- GPU for faster transformers
- SSD for vector database performance

---

## 🤝 Contributing

BhoolamMind is built specifically for Bhoola's use case but can be adapted for other emotional AI memory applications. Key extension points:

1. **Custom Emotion Models**: Train domain-specific classifiers
2. **Language Modules**: Add support for other code-switching patterns
3. **Memory Strategies**: Implement alternative retrieval algorithms
4. **Interface Plugins**: Create custom dashboards or integrations

---

## 📄 License

Built for personal use during Bhoola's 15-month sabbatical. Open for educational reference and adaptation with attribution.

---

## 🎤 About Bhoola

**Abhishek "Bhoola" Chauhan** is a stand-up comedian on a 15-month sabbatical, working on memory improvement and comedy skill development. BhoolamMind is his personal AI assistant for tracking emotional patterns, humor evolution, and maintaining consistent behavioral context across long-term conversations with various AI platforms.

**Core Challenge**: Severe memory issues requiring systematic conversation logging and context preservation across AI interactions.

**Mission**: Build comedy career while training personal AI systems to understand and maintain behavioral consistency.

---

*"Yaar, if I'm going to forget everything anyway, at least let the AI remember for me!"* - Bhoola

🧠 **BhoolamMind v1.5** - Because every thought matters, even the forgotten ones.
