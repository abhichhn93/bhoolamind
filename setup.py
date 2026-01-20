#!/usr/bin/env python3
"""
BhoolamMind v1.5 - Setup and Installation Script
Quick setup for all dependencies and initial configuration
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not compatible. Need Python 3.8+")
        return False

def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing BhoolamMind dependencies...")
    
    # Core dependencies that are most likely to work
    core_deps = [
        "torch",
        "transformers", 
        "sentence-transformers",
        "sqlite3",  # Built-in
        "pandas",
        "numpy",
        "tqdm",
        "requests",
        "pydantic",
        "python-dotenv"
    ]
    
    # Optional dependencies (may require additional setup)
    optional_deps = [
        "chromadb",
        "langchain",
        "langchain-community", 
        "openai-whisper",
        "streamlit",
        "plotly",
        "gradio",
        "pytest"
    ]
    
    # Install core dependencies first
    print("Installing core dependencies...")
    for dep in core_deps:
        if dep != "sqlite3":  # Skip built-in modules
            success = run_command(f"pip install {dep}", f"Installing {dep}")
            if not success:
                print(f"⚠️  Failed to install {dep}, continuing...")
    
    # Install optional dependencies
    print("\nInstalling optional dependencies...")
    for dep in optional_deps:
        success = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            print(f"⚠️  Failed to install {dep}, some features may not work")
    
    print("✅ Dependency installation completed")

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directory structure...")
    
    directories = [
        "data/raw_voice",
        "data/logs", 
        "data/embeddings",
        "memory/sqlite_db",
        "memory/chroma_vectors"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")

def test_imports():
    """Test if key modules can be imported"""
    print("🧪 Testing module imports...")
    
    test_imports = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pandas", "Pandas"),
        ("sqlite3", "SQLite3"),
        ("json", "JSON"),
        ("datetime", "DateTime")
    ]
    
    failed_imports = []
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
        except ImportError:
            print(f"❌ {name} import failed")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n⚠️  Some imports failed: {', '.join(failed_imports)}")
        print("Some features may not work until these are installed")
    else:
        print("🎉 All core imports successful!")
    
    return len(failed_imports) == 0

def create_sample_config():
    """Create a sample configuration file"""
    print("⚙️ Creating sample configuration...")
    
    config = {
        "database": {
            "path": "memory/sqlite_db/bhoolamind.db"
        },
        "voice": {
            "audio_directory": "data/raw_voice",
            "supported_formats": ["wav", "mp3", "m4a", "webm"]
        },
        "emotion": {
            "model": "cardiffnlp/twitter-roberta-base-emotion",
            "threshold": 0.5,
            "hinglish_support": True
        },
        "humor": {
            "confidence_threshold": 0.6,
            "bhoola_patterns": True
        },
        "memory": {
            "vector_store_path": "memory/chroma_vectors",
            "embedding_model": "all-MiniLM-L6-v2",
            "max_context_length": 4000
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("✅ Configuration file created: config.json")

def run_basic_test():
    """Run a basic functionality test"""
    print("🧪 Running basic functionality test...")
    
    try:
        # Test database creation
        sys.path.append("modules")
        from modules.database import BhoolamMindDB
        
        db = BhoolamMindDB()
        interaction_id = db.add_interaction(
            text="BhoolamMind setup test - everything working! 🎉",
            source="test",
            tags=["setup", "test"],
            emotion="excited",
            mood_intensity=9
        )
        
        print(f"✅ Database test passed (interaction ID: {interaction_id})")
        
        # Test bit tracker
        from modules.bit_tracker import BitTracker
        bit_tracker = BitTracker()
        result = bit_tracker.analyze_text("This is a test joke: Why did the AI cross the road? To get to the other dataset!")
        print(f"✅ Bit tracker test passed (bit-worthy: {result['is_bit_worthy']})")
        
        print("🎉 Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🧠 BhoolamMind v1.5 Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("Please upgrade Python to 3.8+ and try again")
        return False
    
    # Setup directories
    setup_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Test imports
    imports_ok = test_imports()
    
    # Create config
    create_sample_config()
    
    # Run basic test if imports are ok
    if imports_ok:
        test_ok = run_basic_test()
        if test_ok:
            print("\n🎉 BhoolamMind v1.5 setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: python run_bhoolamind.py")
            print("2. Or start dashboard: streamlit run frontend/dashboard.py")
            print("3. Or run tests: python tests/test_modules.py")
            return True
    
    print("\n⚠️  Setup completed with some issues")
    print("Some features may not work until missing dependencies are resolved")
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BhoolamMind v1.5 Setup")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--test-only", action="store_true", help="Only run tests")
    
    args = parser.parse_args()
    
    if args.test_only:
        print("🧪 Running tests only...")
        test_imports()
        run_basic_test()
    elif args.skip_deps:
        print("⏭️  Skipping dependency installation...")
        setup_directories()
        create_sample_config()
        test_imports()
    else:
        main()
