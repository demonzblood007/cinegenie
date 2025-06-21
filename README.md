# 🎬 Multi-Agent Movie Continuation System

An AI-powered system that researches trending movies, analyzes fan sentiment, and generates viral continuation content in the form of reels/shorts.

## 🏗️ System Architecture

### Core Components
- **Trend Mining Agent**: Analyzes movie popularity and fan sentiment
- **Movie Understanding Agent**: Extracts movie plot, characters, and themes
- **Script Generator Agent**: Creates continuation scripts based on fan desires
- **Voice & Audio Agent**: Generates character voices and background music
- **Video Generator Agent**: Creates final reels with visuals and audio
- **Upload Agent**: Distributes content across platforms

### Tech Stack
- **Agents**: LangGraph + FastAPI
- **LLMs**: GPT-4 Turbo, Claude 3, Command R+, Mistral
- **Embeddings**: Instructor-XL + Qdrant
- **Voice**: ElevenLabs, Bark, RVC
- **Music**: Boomy, Suno, YouTube Free
- **Video**: FFmpeg, MoviePy, CapCut API
- **Infrastructure**: Docker, Render, Supabase, AWS EC2

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the system
python main.py
```

## 📁 Project Structure

```
├── agents/                 # Individual agent modules
│   ├── trend_miner/       # Trend and sentiment analysis
│   ├── movie_analyzer/    # Movie understanding and extraction
│   ├── script_generator/  # Fan-fulfillment script creation
│   ├── voice_agent/       # Audio and voice generation
│   ├── video_generator/   # Reel/short creation
│   └── uploader/          # Content distribution
├── core/                  # Core utilities and shared components
├── data/                  # Data storage and caching
├── config/                # Configuration files
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## 🔄 Workflow

1. **Trend Analysis** → Identify trending movies and fan sentiment
2. **Movie Understanding** → Extract plot, characters, and themes
3. **Script Generation** → Create continuation scripts based on fan desires
4. **Audio Generation** → Generate voices and background music
5. **Video Creation** → Combine visuals, audio, and text into reels
6. **Content Distribution** → Upload to platforms with viral optimization

## 📊 Features

- **Automated Trend Detection**: Identifies trending movies automatically
- **Sentiment Analysis**: Analyzes thousands of reviews for fan desires
- **Character Voice Cloning**: Recreates original cast voices
- **Cinematic Quality**: Hollywood-grade video production
- **Viral Optimization**: Platform-specific optimization for maximum reach
- **Scalable Architecture**: Handles multiple movies simultaneously

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details. 