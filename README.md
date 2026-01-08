# 🎸 Fingerstyle Tab MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An AI-powered MCP (Model Context Protocol) server that converts guitar audio recordings into high-quality fingerstyle tablature. This tool uses cutting-edge AI models to analyze your guitar playing and generate accurate, playable tabs automatically.

[한국어 문서](./README_KR.md)

## ✨ Features

- **🎵 AI Transcription**: High-precision note detection using Spotify's Basic Pitch deep learning model
- **🎯 Smart Fingering**: Chord-based mapping logic that prioritizes playable open-chord shapes (0-5 fret focus)
- **🎼 Chord Recognition**: Automatic chord detection with a comprehensive library of 40+ chord shapes (Major, Minor, 7th, sus4, etc.)
- **⏱️ Auto BPM Detection**: Tempo detection using Librosa for accurate measure-based formatting
- **🤖 MCP Integration**: Interact with the server directly via Claude Desktop to iterate on and refine your tabs
- **🌍 Internationalization**: Multi-language support (English, Korean, and more)
- **⚙️ Configurable**: YAML-based configuration for customizing transcription behavior
- **📊 Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Claude Desktop Integration](#-claude-desktop-integration)
- [Project Structure](#-project-structure)
- [Examples](#-examples)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/)
- **FFmpeg**: Required for audio processing
  - **macOS**: `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Installation

#### Option 1: Install from source (Recommended for development)

```bash
# Clone the repository
git clone https://github.com/yourusername/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

#### Option 2: Install as a package

```bash
pip install git+https://github.com/yourusername/fingerstyle-tab-mcp.git
```

## 📖 Usage

### Command Line Usage

Analyze a single audio file and generate tablature:

```bash
python test_workflow.py path/to/your/audio.mp3
```

**Example Output:**
```
--- 'sample.mp3' 분석 시작 ---
1. 오디오 분석 중 (BPM 감지 및 Basic Pitch 실행)...
   분석 완료: 142개의 음이 검출되었습니다. (감지된 BPM: 120.50)
2. 기타 타브로 변환 중 (코드 기반 운지 및 주법 분석)...

--- 생성된 타브 악보 ---
🎸 Fingerstyle Precision Analysis (BPM: 120.5)

  C               G               Am              F
e|----------------|----------------|----------------|----------------|
B|1---------1-----|0---------0-----|1---------1-----|1---------1-----|
G|0---------0-----|0---------0-----|2---------2-----|2---------2-----|
D|2---------2-----|0---------0-----|2---------2-----|3---------3-----|
A|3---------3-----|2---------2-----|0---------0-----|3---------3-----|
E|----------------|3---------3-----|----------------|1---------1-----|
```

### Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)
- OGG (`.ogg`)
- M4A (`.m4a`)
- AAC (`.aac`)

### Python API Usage

```python
from src.transcriber import transcribe_audio
from src.tab_generator import TabGenerator

# Step 1: Transcribe audio
notes, detected_bpm = transcribe_audio("path/to/audio.mp3")

# Step 2: Generate tablature
generator = TabGenerator(bpm=detected_bpm)
tab = generator.generate_ascii_tab(notes)

print(tab)
```

## ⚙️ Configuration

Create a `config.yaml` file in the project root to customize behavior:

```bash
cp config.yaml.example config.yaml
```

### Configuration Options

```yaml
# Audio Processing
audio:
  default_bpm: 120.0
  min_bpm: 40
  max_bpm: 200

# Tablature Generation
tablature:
  standard_tuning: ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
  bass_threshold: 50
  slots_per_measure: 16

# Logging
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
```

For all available options, see [config.yaml.example](config.yaml.example).

## 🤖 Claude Desktop Integration

This project implements the Model Context Protocol (MCP), allowing you to interact with it through Claude Desktop.

### Setup Instructions

1. **Install Claude Desktop**: Download from [claude.ai](https://claude.ai/download)

2. **Configure MCP Server**: Add to your Claude Desktop configuration:

**macOS/Linux**: `~/.config/claude/config.json`
```json
{
  "mcpServers": {
    "fingerstyle-tab": {
      "command": "python",
      "args": [
        "/absolute/path/to/fingerstyle-tab-mcp/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/fingerstyle-tab-mcp"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\config.json`
```json
{
  "mcpServers": {
    "fingerstyle-tab": {
      "command": "python",
      "args": [
        "C:\\absolute\\path\\to\\fingerstyle-tab-mcp\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\absolute\\path\\to\\fingerstyle-tab-mcp"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

### Using with Claude

Once configured, you can ask Claude:

> "Analyze this guitar recording and create a tab: /path/to/recording.mp3"

> "Convert my audio file at ~/Music/guitar_solo.wav into tablature"

Claude will use the MCP server to process your audio and return formatted tablature.

## 🛠 Project Structure

```
fingerstyle-tab-mcp/
├── src/
│   ├── transcriber.py       # Audio analysis and note extraction
│   ├── tab_generator.py     # Smart fingering and ASCII tab generation
│   └── config.py            # Configuration management
├── locales/                 # Internationalization files
├── resource/                # Example audio files
├── mcp_server.py            # FastMCP server implementation
├── test_workflow.py         # Command-line testing tool
├── requirements.txt         # Python dependencies
├── setup.py                 # Package installation script
├── config.yaml.example      # Example configuration
├── README.md                # This file
└── LICENSE                  # MIT License

```

### Key Components

- **`src/transcriber.py`**: Uses Basic Pitch and Librosa for audio analysis
  - BPM detection
  - Note extraction (pitch, timing, velocity)
  - Audio format validation

- **`src/tab_generator.py`**: Converts notes to playable tablature
  - Chord detection (40+ chord types)
  - Smart fingering algorithm
  - ASCII tab rendering

- **`mcp_server.py`**: MCP protocol implementation
  - `analyze_audio_to_tab`: Main transcription tool
  - `tweak_tab_fingering`: Adjust note positions
  - `get_standard_tuning`: Guitar tuning reference

## 📚 Examples

### Example 1: Basic Usage

```bash
python test_workflow.py examples/simple_melody.mp3
```

### Example 2: Custom Tuning

```python
from src.tab_generator import TabGenerator

# Drop D tuning
generator = TabGenerator(
    tuning=['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    bpm=140
)
```

### Example 3: Batch Processing

```python
import glob
from src.transcriber import transcribe_audio
from src.tab_generator import TabGenerator

for audio_file in glob.glob("songs/*.mp3"):
    notes, bpm = transcribe_audio(audio_file)
    generator = TabGenerator(bpm=bpm)
    tab = generator.generate_ascii_tab(notes)

    # Save to file
    output_file = audio_file.replace('.mp3', '.txt')
    with open(output_file, 'w') as f:
        f.write(tab)
```

## 🌍 Internationalization

This project supports multiple languages using `gettext`.

### Supported Languages

- English (en)
- Korean (ko)

### Adding a New Language

1. Create a new locale directory:
```bash
mkdir -p locales/[language_code]/LC_MESSAGES
```

2. Create translation file:
```bash
# Generate .pot template (if needed)
xgettext -o locales/messages.pot src/*.py

# Create .po file for your language
msginit -i locales/messages.pot -o locales/[language_code]/LC_MESSAGES/messages.po
```

3. Translate strings in the `.po` file

4. Compile translations:
```bash
msgfmt locales/[language_code]/LC_MESSAGES/messages.po -o locales/[language_code]/LC_MESSAGES/messages.mo
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp

# Install with dev dependencies
pip install -e ".[dev]"

# Run code formatting
black src/ test/
isort src/ test/

# Run linting
flake8 src/ test/
mypy src/
```

### Areas for Contribution

- 🎵 Improve chord detection accuracy
- 🎸 Add support for alternate tunings
- 🌍 Add translations for more languages
- 📊 Enhance tab visualization
- 🧪 Increase test coverage
- 📖 Improve documentation
- 🐛 Fix bugs and issues

## 🙏 Acknowledgments

This project uses the following open-source libraries:

- [Basic Pitch](https://github.com/spotify/basic-pitch) by Spotify - Audio transcription
- [Librosa](https://librosa.org/) - Audio analysis
- [Music21](https://web.mit.edu/music21/) - Music theory
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework

## 📜 License

This project is licensed under the [MIT License](./LICENSE).

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'basic_pitch'`
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: `FileNotFoundError: Audio file not found`
- **Solution**: Check the file path is correct and the file exists

**Issue**: BPM detection is inaccurate
- **Solution**: Manually specify BPM in config.yaml or use the `--bpm` flag

**Issue**: No notes detected
- **Solution**: Ensure audio quality is good and guitar is prominent in the mix

### Getting Help

- 📝 [Open an issue](https://github.com/yourusername/fingerstyle-tab-mcp/issues)
- 💬 [Start a discussion](https://github.com/yourusername/fingerstyle-tab-mcp/discussions)

## 🗺️ Roadmap

- [ ] MIDI export support
- [ ] PDF tablature export
- [ ] Real-time audio processing
- [ ] Web interface
- [ ] Mobile app integration
- [ ] Advanced fingering customization
- [ ] Multiple instrument support

---

Made with ❤️ by the open-source community
