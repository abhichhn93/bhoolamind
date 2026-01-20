"""
BhoolamMind v1.5 - Frontend Dashboard
Streamlit-based web interface for interacting with the memory and emotional context engine.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))

try:
    from modules.database import BhoolamMindDB
    from modules.emotion_tagger import EmotionTagger
    from modules.bit_tracker import BitTracker
    from modules.voice_transcriber import VoiceTranscriber
    from modules.memory_injector import MemoryInjector
    from modules.summarizer import WeeklySummarizer
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="BhoolamMind v1.5",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .emotion-tag {
        background-color: #e1f5fe;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    .bit-worthy {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class BhoolamindDashboard:
    def __init__(self):
        """Initialize the dashboard with all components"""
        try:
            self.db = BhoolamMindDB()
            self.emotion_tagger = EmotionTagger()
            self.bit_tracker = BitTracker()
            self.memory_injector = MemoryInjector()
            self.summarizer = WeeklySummarizer()
            self.voice_transcriber = VoiceTranscriber()
        except Exception as e:
            st.error(f"Failed to initialize components: {e}")
            st.stop()
    
    def sidebar_navigation(self):
        """Create sidebar navigation"""
        st.sidebar.markdown("# 🧠 BhoolamMind v1.5")
        st.sidebar.markdown("*AI Memory & Emotional Context Engine*")
        
        page = st.sidebar.selectbox(
            "Navigate to:",
            ["🏠 Dashboard", "📝 Log Entry", "📊 Analytics", "🎭 Emotion Trends", 
             "😄 Humor Tracker", "🔍 Memory Search", "📋 Weekly Summary", "⚙️ Settings"]
        )
        
        st.sidebar.markdown("---")
        
        # Quick stats in sidebar
        stats = self.db.get_stats()
        st.sidebar.markdown("### Quick Stats")
        st.sidebar.metric("Total Interactions", stats.get('total_interactions', 0))
        st.sidebar.metric("Voice Files", stats.get('total_voice_files', 0))
        
        if stats.get('top_emotions'):
            st.sidebar.markdown("**Top Emotions:**")
            for emotion, count in list(stats['top_emotions'].items())[:3]:
                st.sidebar.markdown(f"• {emotion.title()}: {count}")
        
        return page
    
    def dashboard_page(self):
        """Main dashboard overview"""
        st.markdown('<h1 class="main-header">🧠 BhoolamMind Dashboard</h1>', unsafe_allow_html=True)
        
        # Get recent stats
        recent_interactions = self.db.get_recent_interactions(limit=10)
        stats = self.db.get_stats()
        
        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Entries", 
                stats.get('total_interactions', 0),
                help="Total interactions logged"
            )
        
        with col2:
            st.metric(
                "This Week", 
                len([i for i in recent_interactions if 
                    (datetime.now() - datetime.fromisoformat(i['timestamp'])).days <= 7]),
                help="Entries in the last 7 days"
            )
        
        with col3:
            if stats.get('top_emotions'):
                top_emotion = list(stats['top_emotions'].keys())[0]
                st.metric("Top Emotion", top_emotion.title())
            else:
                st.metric("Top Emotion", "None")
        
        with col4:
            voice_count = stats.get('total_voice_files', 0)
            st.metric("Voice Files", voice_count)
        
        # Recent activity
        st.markdown("## 📝 Recent Activity")
        
        if recent_interactions:
            for interaction in recent_interactions[:5]:
                with st.expander(f"{interaction['source'].title()} - {interaction['timestamp'][:16]}"):
                    st.write(interaction['text'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if interaction['emotion']:
                            st.markdown(f"<span class='emotion-tag'>😊 {interaction['emotion']}</span>", 
                                      unsafe_allow_html=True)
                    with col2:
                        if interaction['mood_intensity']:
                            st.markdown(f"**Intensity:** {interaction['mood_intensity']}/10")
                    with col3:
                        if interaction['tags']:
                            tags = json.loads(interaction['tags']) if isinstance(interaction['tags'], str) else interaction['tags']
                            for tag in tags[:3]:
                                st.markdown(f"<span class='emotion-tag'>🏷️ {tag}</span>", 
                                          unsafe_allow_html=True)
        else:
            st.info("No recent interactions found. Start logging to see activity here!")
        
        # Quick charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Emotion Distribution")
            if stats.get('top_emotions'):
                emotions_df = pd.DataFrame(
                    list(stats['top_emotions'].items()),
                    columns=['Emotion', 'Count']
                )
                fig = px.pie(emotions_df, values='Count', names='Emotion', 
                           title="Recent Emotions")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No emotion data available yet")
        
        with col2:
            st.markdown("### 📈 Activity by Source")
            if stats.get('interactions_by_source'):
                sources_df = pd.DataFrame(
                    list(stats['interactions_by_source'].items()),
                    columns=['Source', 'Count']
                )
                fig = px.bar(sources_df, x='Source', y='Count', 
                           title="Interactions by Source")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No source data available yet")
    
    def log_entry_page(self):
        """Page for creating new log entries"""
        st.markdown("# 📝 New Log Entry")
        
        # Input method selection
        input_method = st.radio("Input Method:", ["Text", "Voice Upload"])
        
        if input_method == "Text":
            self.text_input_form()
        else:
            self.voice_input_form()
    
    def text_input_form(self):
        """Form for text input"""
        with st.form("text_entry_form"):
            st.markdown("### ✍️ Text Entry")
            
            text_input = st.text_area(
                "What's on your mind?",
                height=150,
                placeholder="Share your thoughts, ideas, or any Bhoola moments..."
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                emotion = st.selectbox(
                    "Current Emotion",
                    ["", "happy", "sad", "anxious", "excited", "calm", "frustrated", 
                     "inspired", "tired", "focused", "confused", "amused", "grateful"]
                )
            
            with col2:
                mood_intensity = st.slider("Mood Intensity", 1, 10, 5)
            
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="BhoolaMoment, funny, work, personal..."
            )
            
            submitted = st.form_submit_button("💾 Save Entry")
            
            if submitted and text_input.strip():
                # Process tags
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                
                # Analyze emotion if not provided
                if not emotion:
                    emotion_analysis = self.emotion_tagger.analyze_emotion(text_input)
                    emotion = emotion_analysis.get('primary_emotion', 'neutral')
                    if not mood_intensity or mood_intensity == 5:
                        mood_intensity = emotion_analysis.get('intensity', 5)
                
                # Check for humor/bits
                bit_analysis = self.bit_tracker.analyze_text(text_input)
                if bit_analysis['is_bit_worthy']:
                    tags.append('Bit-worthy')
                    tags.append(bit_analysis['bit_type'])
                
                # Save to database
                interaction_id = self.db.add_interaction(
                    text=text_input,
                    source="text",
                    tags=tags,
                    emotion=emotion,
                    mood_intensity=mood_intensity
                )
                
                st.success(f"✅ Entry saved! (ID: {interaction_id})")
                
                # Show analysis results
                if bit_analysis['is_bit_worthy']:
                    st.markdown(f"<div class='bit-worthy'>🎭 <strong>Bit-worthy moment detected!</strong><br>Type: {bit_analysis['bit_type']}<br>Confidence: {bit_analysis['confidence']:.2f}</div>", 
                              unsafe_allow_html=True)
                
                # Auto-tag suggestions
                if emotion != 'neutral':
                    st.info(f"💡 Auto-detected emotion: {emotion} (intensity: {mood_intensity})")
    
    def voice_input_form(self):
        """Form for voice input"""
        st.markdown("### 🎤 Voice Entry")
        
        uploaded_file = st.file_uploader(
            "Upload audio file",
            type=['wav', 'mp3', 'm4a', 'webm'],
            help="Upload an audio file to transcribe and analyze"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with st.spinner("Processing audio..."):
                # Save file
                temp_path = f"temp_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{uploaded_file.name.split('.')[-1]}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                try:
                    # Transcribe
                    transcription_result = self.voice_transcriber.transcribe_audio(temp_path)
                    
                    if transcription_result['success']:
                        st.success("✅ Audio transcribed successfully!")
                        
                        transcription = transcription_result['transcription']
                        language = transcription_result.get('language', 'unknown')
                        
                        # Show transcription
                        st.markdown("**Transcription:**")
                        st.write(transcription)
                        
                        # Additional processing form
                        with st.form("voice_processing_form"):
                            st.markdown("### Review and Save")
                            
                            # Editable transcription
                            edited_text = st.text_area(
                                "Edit transcription if needed:",
                                value=transcription,
                                height=100
                            )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                emotion = st.selectbox(
                                    "Emotion (auto-detected)",
                                    ["", "happy", "sad", "anxious", "excited", "calm", 
                                     "frustrated", "inspired", "tired", "focused", "confused", "amused"]
                                )
                            
                            with col2:
                                mood_intensity = st.slider("Mood Intensity", 1, 10, 5)
                            
                            save_voice = st.form_submit_button("💾 Save Voice Entry")
                            
                            if save_voice:
                                # Analyze emotion
                                if not emotion:
                                    emotion_analysis = self.emotion_tagger.analyze_emotion(edited_text)
                                    emotion = emotion_analysis.get('primary_emotion', 'neutral')
                                    mood_intensity = emotion_analysis.get('intensity', mood_intensity)
                                
                                # Save voice metadata
                                voice_id = self.db.add_voice_metadata(
                                    file_path=temp_path,
                                    transcription=edited_text,
                                    detected_emotion=emotion,
                                    language=language,
                                    duration_seconds=transcription_result.get('duration', 0)
                                )
                                
                                # Save as interaction
                                interaction_id = self.db.add_interaction(
                                    text=edited_text,
                                    source="voice",
                                    tags=["voice", language],
                                    emotion=emotion,
                                    mood_intensity=mood_intensity
                                )
                                
                                st.success(f"✅ Voice entry saved! (Voice ID: {voice_id}, Interaction ID: {interaction_id})")
                    
                    else:
                        st.error(f"❌ Transcription failed: {transcription_result.get('error', 'Unknown error')}")
                
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    def analytics_page(self):
        """Analytics and insights page"""
        st.markdown("# 📊 Analytics & Insights")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range:",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
        )
        
        # Get data based on time range
        if time_range == "Last 7 days":
            interactions = self.db.get_recent_interactions(limit=1000)
            cutoff = datetime.now() - timedelta(days=7)
        elif time_range == "Last 30 days":
            interactions = self.db.get_recent_interactions(limit=1000)
            cutoff = datetime.now() - timedelta(days=30)
        elif time_range == "Last 90 days":
            interactions = self.db.get_recent_interactions(limit=1000)
            cutoff = datetime.now() - timedelta(days=90)
        else:
            interactions = self.db.get_recent_interactions(limit=10000)
            cutoff = datetime.min
        
        # Filter by time range
        filtered_interactions = [
            i for i in interactions 
            if datetime.fromisoformat(i['timestamp']) >= cutoff
        ]
        
        if not filtered_interactions:
            st.warning("No data available for the selected time range.")
            return
        
        # Create analytics
        df = pd.DataFrame(filtered_interactions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        # Activity patterns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 Daily Activity")
            daily_counts = df.groupby('date').size().reset_index(name='count')
            fig = px.line(daily_counts, x='date', y='count', title="Daily Interaction Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🕐 Hourly Patterns")
            hourly_counts = df.groupby('hour').size().reset_index(name='count')
            fig = px.bar(hourly_counts, x='hour', y='count', title="Activity by Hour")
            st.plotly_chart(fig, use_container_width=True)
        
        # Emotion and mood analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎭 Emotion Timeline")
            emotion_df = df[df['emotion'].notna()].copy()
            if not emotion_df.empty:
                emotion_counts = emotion_df.groupby(['date', 'emotion']).size().reset_index(name='count')
                fig = px.line(emotion_counts, x='date', y='count', color='emotion', 
                            title="Emotion Trends Over Time")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No emotion data available")
        
        with col2:
            st.markdown("### 📊 Mood Intensity")
            mood_df = df[df['mood_intensity'].notna()].copy()
            if not mood_df.empty:
                fig = px.histogram(mood_df, x='mood_intensity', nbins=10, 
                                 title="Mood Intensity Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No mood intensity data available")
    
    def memory_search_page(self):
        """Memory search and retrieval page"""
        st.markdown("# 🔍 Memory Search")
        
        search_query = st.text_input(
            "Search your memories:",
            placeholder="Enter keywords, emotions, or topics..."
        )
        
        if search_query:
            # Search interactions
            results = self.db.search_interactions(search_query)
            
            st.markdown(f"### Found {len(results)} results")
            
            for result in results:
                with st.expander(f"{result['source'].title()} - {result['timestamp'][:16]}"):
                    st.write(result['text'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if result['emotion']:
                            st.markdown(f"**Emotion:** {result['emotion']}")
                    with col2:
                        if result['mood_intensity']:
                            st.markdown(f"**Intensity:** {result['mood_intensity']}/10")
                    with col3:
                        if result['tags']:
                            tags = json.loads(result['tags']) if isinstance(result['tags'], str) else result['tags']
                            st.markdown(f"**Tags:** {', '.join(tags[:3])}")
        
        # Memory patterns
        st.markdown("### 🧠 Memory Patterns")
        
        patterns = self.db.get_memory_patterns(min_frequency=2)
        
        if patterns:
            for pattern in patterns[:10]:
                with st.expander(f"{pattern['pattern_type'].title()} - {pattern['frequency']} occurrences"):
                    st.json(pattern['pattern_data'])
                    st.markdown(f"**Last seen:** {pattern['last_seen']}")
        else:
            st.info("No memory patterns found yet. Keep logging to build patterns!")
    
    def weekly_summary_page(self):
        """Weekly summary and insights"""
        st.markdown("# 📋 Weekly Summary")
        
        # Date selector for week
        target_date = st.date_input(
            "Select a date in the week you want to summarize:",
            value=datetime.now().date()
        )
        
        if st.button("📊 Generate Weekly Summary"):
            with st.spinner("Generating weekly summary..."):
                summary = self.summarizer.generate_weekly_summary(
                    datetime.combine(target_date, datetime.min.time())
                )
            
            # Display summary
            st.markdown("## Summary")
            st.markdown(summary['summary_text'])
            
            # Display detailed analytics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Statistics")
                st.json(summary['stats'])
            
            with col2:
                st.markdown("### 😄 Humor Analysis")
                humor = summary['humor_analysis']
                st.metric("Funny Moments", humor['total_funny_moments'])
                if humor['best_bits']:
                    st.markdown("**Top Bits:**")
                    for i, bit in enumerate(humor['best_bits'][:3], 1):
                        st.markdown(f"{i}. {bit['text'][:100]}...")
            
            # Mood trends
            st.markdown("### 🎭 Mood Trends")
            mood = summary['mood_analysis']
            if mood['daily_moods']:
                mood_df = pd.DataFrame.from_dict(mood['daily_moods'], orient='index')
                mood_df = mood_df.reset_index().rename(columns={'index': 'day'})
                
                if 'average_intensity' in mood_df.columns:
                    fig = px.bar(mood_df, x='day', y='average_intensity', 
                               title="Daily Mood Intensity")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Summary history
        st.markdown("### 📚 Previous Summaries")
        history = self.summarizer.get_summary_history(weeks_back=4)
        
        for summary in history:
            week_start = datetime.fromisoformat(summary['week_start']).strftime('%B %d')
            week_end = datetime.fromisoformat(summary['week_end']).strftime('%B %d, %Y')
            
            with st.expander(f"Week of {week_start} - {week_end}"):
                st.markdown(summary['summary_text'])
    
    def settings_page(self):
        """Settings and configuration page"""
        st.markdown("# ⚙️ Settings")
        
        st.markdown("### 🗃️ Database Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 View Database Stats"):
                stats = self.db.get_stats()
                st.json(stats)
        
        with col2:
            if st.button("🔄 Sync Memory Store"):
                # This would sync database to vector store
                st.info("Memory sync functionality would go here")
        
        st.markdown("### 🎯 Emotion Detection Settings")
        
        emotion_threshold = st.slider(
            "Emotion Detection Threshold",
            0.0, 1.0, 0.5,
            help="Minimum confidence for emotion detection"
        )
        
        st.markdown("### 🎭 Humor Detection Settings")
        
        humor_threshold = st.slider(
            "Humor Detection Threshold", 
            0.0, 1.0, 0.6,
            help="Minimum confidence for bit-worthy detection"
        )
        
        st.markdown("### 📁 Data Export")
        
        if st.button("📥 Export All Data"):
            # This would export data to JSON/CSV
            st.info("Data export functionality would go here")

def main():
    """Main application function"""
    dashboard = BhoolamindDashboard()
    
    # Sidebar navigation
    page = dashboard.sidebar_navigation()
    
    # Route to appropriate page
    if page == "🏠 Dashboard":
        dashboard.dashboard_page()
    elif page == "📝 Log Entry":
        dashboard.log_entry_page()
    elif page == "📊 Analytics":
        dashboard.analytics_page()
    elif page == "🔍 Memory Search":
        dashboard.memory_search_page()
    elif page == "📋 Weekly Summary":
        dashboard.weekly_summary_page()
    elif page == "⚙️ Settings":
        dashboard.settings_page()
    else:
        st.error("Page not implemented yet!")

if __name__ == "__main__":
    main()
