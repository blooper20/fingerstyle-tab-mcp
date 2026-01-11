# 🎸 Fingerstyle Tab MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io)

An AI-powered MCP (Model Context Protocol) server that converts guitar audio recordings into high-quality fingerstyle tablature. This tool uses cutting-edge AI models to analyze your guitar playing and generate accurate, playable tabs automatically.

[한국어 문서](./README_KR.md) | [English](./README.md)

## ✨ Features

- **🎵 AI-Powered Transcription**: High-precision note detection using Spotify's Basic Pitch deep learning model
- **⚡ Parallel Processing**: Process long audio files (45+ seconds) efficiently using multi-threaded chunk processing
- **🎯 Smart Fingering**: Chord-based mapping logic that prioritizes playable open-chord shapes (0-5 fret focus)
- **🎼 Advanced Chord Recognition**: Automatic chord detection with 40+ chord shapes (Major, Minor, 7th, sus4, dim, aug, etc.)
- **⏱️ Auto BPM Detection**: Intelligent tempo detection using Librosa for accurate measure-based formatting
- **💾 Smart Caching**: Result caching to avoid re-processing identical files
- **🔍 Fuzzy File Matching**: Intelligent file discovery in the resource directory
- **🤖 MCP Integration**: Seamless integration with Claude Desktop for interactive tab refinement
- **🌍 Internationalization**: Full multi-language support (English, Korean)
- **⚙️ Highly Configurable**: YAML-based configuration for customizing all aspects of transcription
- **📊 Comprehensive Logging**: Detailed logging with proper stderr redirection for debugging

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Claude Desktop Integration (Recommended)](#claude-desktop-integration-recommended)
  - [Command Line Usage](#command-line-usage)
  - [Python API Usage](#python-api-usage)
- [Features in Detail](#-features-in-detail)
- [Configuration](#-configuration)
- [MCP Tools Reference](#-mcp-tools-reference)
- [Project Structure](#-project-structure)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
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

```bash
# Clone the repository
git clone https://github.com/blooper20/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📖 Usage

### Claude Desktop Integration (Recommended)

This is the most powerful way to use the Fingerstyle Tab MCP Server. You can interact with Claude to generate, refine, and customize your guitar tabs.

#### 1. Setup Instructions

**Step 1: Install Claude Desktop**
Download from [claude.ai/download](https://claude.ai/download)

**Step 2: Configure MCP Server**

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "fingerstyle-mcp": {
      "command": "/absolute/path/to/fingerstyle-tab-mcp/venv/bin/python3",
      "args": ["/absolute/path/to/fingerstyle-tab-mcp/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/fingerstyle-tab-mcp"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "fingerstyle-mcp": {
      "command": "C:\\absolute\\path\\to\\fingerstyle-tab-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\absolute\\path\\to\\fingerstyle-tab-mcp\\mcp_server.py"],
      "env": {
        "PYTHONPATH": "C:\\absolute\\path\\to\\fingerstyle-tab-mcp"
      }
    }
  }
}
```

**Step 3: Restart Claude Desktop**

Close Claude Desktop completely (Cmd+Q on macOS) and reopen it.

**Step 4: Verify Installation**

Check the logs to ensure the server started successfully:

```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp-server-fingerstyle-mcp.log

# Look for this message:
# 🚀 FINGERSTYLE MCP SERVER IS NOW ONLINE AND READY
```

#### 2. Using with Claude

Once configured, you can interact with Claude using natural language:

**Example Conversations:**

> **You**: "What audio files are available?"
>
> **Claude**: *Uses `list_available_audio_files` tool*
>
> Available files in 'resource/':
> - Adelle-- someone like you-null.mp3
> - Falling Slowly - Once [legendado](MP3_70K)_1.mp3

---

> **You**: "Analyze 'someone like you' and create a guitar tab"
>
> **Claude**: *Uses `analyze_audio_to_tab` with fuzzy matching*
>
> 🎸 Fingerstyle Precision Analysis (BPM: 123.05)
>
> Dm              G               C               F
> e|----------------|----------------|----------------|----------------|
> B|3---3-------3---|0---0-------0---|1---1-------1---|1---1-------1---|
> G|2---2-------2---|0---0-------0---|0---0-------0---|2---2-------2---|
> D|0---0-------0---|0---0-------0---|2---2-------2---|3---3-------3---|
> A|----------------|2---2-------2---|3---3-------3---|3---3-------3---|
> E|----------------|3---3-------3---|----------------|1---1-------1---|

---

> **You**: "Analyze just the first 30 seconds starting from 10 seconds in"
>
> **Claude**: *Uses `analyze_audio_to_tab` with `start_seconds=10.0, duration_seconds=30.0`*
>
> Analysis Successful (Start: 10.0s, Duration: 30.0s)...

#### 3. Available MCP Tools

The server exposes the following tools to Claude:

| Tool | Description |
|------|-------------|
| `analyze_audio_to_tab` | Main tool to convert audio files to tablature |
| `list_available_audio_files` | List all audio files in the resource/ directory |
| `tweak_tab_fingering` | Adjust fingering preferences for specific pitches |
| `get_standard_tuning` | Get standard guitar tuning reference |

See [MCP Tools Reference](#-mcp-tools-reference) for detailed documentation.

### Command Line Usage

For quick testing or batch processing:

```bash
# Basic usage
python test_workflow.py path/to/your/audio.mp3

# Using files in the resource/ directory
python test_workflow.py "someone like you"  # Fuzzy matching works!
```

**Example Output:**
```
--- 'Adelle-- someone like you-null.mp3' 분석 시작 ---
1. 오디오 분석 중 (BPM 감지 및 Basic Pitch 실행)...
   Detecting tempo...
   Detected BPM: 123.05
   Parallel Analysis: Splitting into 11 chunks to finish in < 1 min
   분석 완료: 2554개의 음이 검출되었습니다. (감지된 BPM: 123.05)
2. 기타 타브로 변환 중 (코드 기반 운지 및 주법 분석)...

--- 생성된 타브 악보 ---
🎸 Fingerstyle Precision Analysis (BPM: 123.05)

  Dm              G               C               F
e|----------------|----------------|----------------|----------------|
B|3---3---3---3---|0---0---0---0---|1---1---1---1---|1---1---1---1---|
G|2---2---2---2---|0---0---0---0---|0---0---0---0---|2---2---2---2---|
D|0---0---0---0---|0---0---0---0---|2---2---2---2---|3---3---3---3---|
A|----------------|2---2---2---2---|3---3---3---3---|3---3---3---3---|
E|----------------|3---3---3---3---|----------------|1---1---1---1---|
```

### Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)
- OGG (`.ogg`)
- M4A (`.m4a`)
- AAC (`.aac`)

### Python API Usage

For integration into your own projects:

```python
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# Step 1: Transcribe audio (with optional parameters)
notes, detected_bpm = transcribe_audio(
    "path/to/audio.mp3",
    duration=30.0,        # Optional: analyze only first 30 seconds
    start_offset=10.0     # Optional: start from 10 seconds
)

# Step 2: Generate tablature
tab = create_tab(notes, bpm=detected_bpm)

print(tab)
```

#### Advanced API Usage

```python
from src.tab_generator import TabGenerator

# Custom configuration
generator = TabGenerator(
    tuning=['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],  # Drop D tuning
    bpm=140,
    slots_per_measure=16
)

# Generate tab with custom settings
tab = generator.generate_ascii_tab(notes)
```

## 🔥 Features in Detail

### 1. Parallel Processing

For audio files longer than 45 seconds, the server automatically:
- Splits the file into 30-second chunks with 2-second overlap
- Processes chunks in parallel using multiple worker threads
- Merges results and deduplicates overlapping notes
- **Result**: Significantly reduced processing time for long files

```python
# Automatic parallel processing for long files
notes, bpm = transcribe_audio("long_song.mp3")  # Auto-parallelized if > 45s
```

### 2. Smart Caching

Results are cached to avoid re-processing:

```python
# First call: processes audio
analyze_audio_to_tab("song.mp3")  # Takes ~30s

# Second call: returns cached result
analyze_audio_to_tab("song.mp3")  # Instant!

# Different parameters: new processing
analyze_audio_to_tab("song.mp3", duration_seconds=30)  # Takes ~5s
```

### 3. Fuzzy File Matching

No need for exact filenames:

```python
# All of these work:
analyze_audio_to_tab("someone like you")
analyze_audio_to_tab("someonelikeyou.mp3")
analyze_audio_to_tab("Adelle-- someone like you-null.mp3")
```

The server normalizes filenames and finds the best match in the `resource/` directory.

### 4. Intelligent Chord Detection

Recognizes 40+ chord types:
- **Major**: C, G, F, D, A, E, etc.
- **Minor**: Am, Dm, Em, etc.
- **7th Chords**: C7, G7, Cmaj7, Dm7, etc.
- **Suspended**: Csus4, Gsus2, etc.
- **Extended**: Cadd9, C6, etc.
- **Altered**: Cdim, Caug, etc.

### 5. Smart Fingering Algorithm

The tab generator:
- Prioritizes open chord shapes (0-5 fret range)
- Minimizes hand position changes
- Groups notes into chord shapes where possible
- Places bass notes on appropriate strings

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
  parallel_threshold: 45.0  # Enable parallel processing for files > 45s
  chunk_size: 30.0          # Chunk size in seconds
  chunk_overlap: 2.0        # Overlap between chunks

# Tablature Generation
tablature:
  standard_tuning: ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
  bass_threshold: 50        # MIDI note threshold for bass detection
  slots_per_measure: 16     # Granularity of tab grid
  min_fret: 0
  max_fret: 12

# Logging
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

For all available options, see [config.yaml.example](config.yaml.example).

## 🛠 MCP Tools Reference

### `analyze_audio_to_tab`

Main tool for audio-to-tab conversion.

**Parameters:**
- `file_path` (string, required): Path to audio file or just the filename
  - Supports absolute paths: `/Users/you/Music/song.mp3`
  - Supports relative paths: `~/Music/song.mp3`
  - Supports filename only: `song.mp3` (searches in `resource/`)
  - Supports fuzzy matching: `someone like you` → finds `Adelle-- someone like you-null.mp3`
- `duration_seconds` (float, optional): Limit analysis to N seconds (default: process entire file)
- `start_seconds` (float, optional): Start analysis from N seconds (default: 0.0)

**Returns:**
- ASCII guitar tablature with chord annotations and BPM info

**Example:**
```python
# Full file
analyze_audio_to_tab("song.mp3")

# First 30 seconds
analyze_audio_to_tab("song.mp3", duration_seconds=30.0)

# 30 seconds starting from 1 minute mark
analyze_audio_to_tab("song.mp3", start_seconds=60.0, duration_seconds=30.0)
```

### `list_available_audio_files`

Lists all audio files in the `resource/` directory.

**Parameters:** None

**Returns:**
- List of available audio files

**Example:**
```
Available files in 'resource/':
- Adelle-- someone like you-null.mp3
- Falling Slowly - Once [legendado](MP3_70K)_1.mp3
```

### `tweak_tab_fingering`

Suggest preferred string for a specific MIDI pitch.

**Parameters:**
- `note_pitch` (int, required): MIDI pitch (0-127)
- `preferred_string` (int, required): Target string number (1=High E, 6=Low E)

**Returns:**
- Confirmation message

### `get_standard_tuning`

Get standard guitar tuning reference information.

**Parameters:** None

**Returns:**
```
Standard Tuning: E2, A2, D3, G3, B3, E4 (82.41Hz - 329.63Hz)
```

## 🛠 Project Structure

```
fingerstyle-tab-mcp/
├── src/
│   ├── transcriber.py       # Audio analysis & parallel processing
│   │   ├── transcribe_audio()      # Main transcription function
│   │   ├── get_model()             # Model caching
│   │   └── _transcribe_chunk()     # Chunk processing
│   ├── tab_generator.py     # Smart fingering & ASCII tab generation
│   │   ├── TabGenerator            # Main generator class
│   │   ├── create_tab()            # High-level API
│   │   └── CHORD_LIBRARY           # 40+ chord templates
│   └── config.py            # Configuration management
├── locales/                 # Internationalization files
│   ├── en/LC_MESSAGES/      # English translations
│   └── ko/LC_MESSAGES/      # Korean translations
├── resource/                # Example audio files (place your files here)
├── mcp_server.py            # MCP server implementation
├── test_workflow.py         # Command-line testing tool
├── requirements.txt         # Python dependencies
├── setup.py                 # Package installation script
├── config.yaml.example      # Example configuration
├── README.md                # This file
├── README_KR.md             # Korean documentation
└── LICENSE                  # MIT License
```

### Key Components

- **[src/transcriber.py](src/transcriber.py)**: Audio analysis engine
  - Parallel processing for long files (45+ seconds)
  - Global model caching to avoid reloading
  - BPM detection using Librosa
  - Note extraction using Spotify's Basic Pitch
  - Chunk-level error handling

- **[src/tab_generator.py](src/tab_generator.py)**: Tab generation engine
  - 40+ chord type recognition
  - Smart fingering algorithm (open chord priority)
  - ASCII tab rendering with chord annotations
  - Measure-based formatting

- **[mcp_server.py](mcp_server.py)**: MCP protocol server
  - Smart file resolution with fuzzy matching
  - Result caching for performance
  - Comprehensive error handling
  - Clean stdout/stderr separation
  - Multi-language support

## 📚 Examples

### Example 1: Basic Usage

```bash
# Place your guitar recording in the resource/ directory
cp ~/Music/my_song.mp3 resource/

# Run analysis
python test_workflow.py "my_song"
```

### Example 2: Analyzing Specific Sections

```python
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# Analyze just the chorus (starts at 1:20, lasts 30 seconds)
notes, bpm = transcribe_audio(
    "resource/song.mp3",
    start_offset=80.0,      # 1:20 = 80 seconds
    duration=30.0
)

tab = create_tab(notes, bpm=bpm)
print(tab)
```

### Example 3: Custom Tuning

```python
from src.tab_generator import TabGenerator

# Drop D tuning (DADGBE)
generator = TabGenerator(
    tuning=['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    bpm=140
)

tab = generator.generate_ascii_tab(notes)
print(tab)
```

### Example 4: Batch Processing

```python
import glob
import os
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# Process all MP3 files in a directory
for audio_file in glob.glob("resource/*.mp3"):
    print(f"Processing {audio_file}...")

    try:
        # Transcribe
        notes, bpm = transcribe_audio(audio_file)

        # Generate tab
        tab = create_tab(notes, bpm=bpm)

        # Save to text file
        output_file = audio_file.replace('.mp3', '_tab.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tab)

        print(f"✓ Saved to {output_file}")
    except Exception as e:
        print(f"✗ Failed: {e}")
```

## 🌍 Internationalization

This project supports multiple languages using `gettext`.

### Supported Languages

- **English** (en) - Default
- **Korean** (ko) - 한국어 완전 지원

### Adding a New Language

1. **Extract translatable strings:**
```bash
xgettext -o locales/messages.pot src/*.py mcp_server.py
```

2. **Create translation for your language:**
```bash
# Replace 'ja' with your language code (e.g., 'es' for Spanish)
msginit -i locales/messages.pot -o locales/ja/LC_MESSAGES/messages.po -l ja
```

3. **Translate the strings** in the `.po` file

4. **Compile translations:**
```bash
msgfmt locales/ja/LC_MESSAGES/messages.po -o locales/ja/LC_MESSAGES/messages.mo
```

5. **Set language environment variable:**
```bash
export LANG=ja_JP.UTF-8  # For Japanese
python test_workflow.py "song.mp3"
```

## 🐛 Troubleshooting

### Common Issues

#### Issue: MCP server not showing up in Claude Desktop

**Solution:**
1. Check the configuration file path:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Verify the paths are absolute (not relative)
3. Restart Claude Desktop completely (Cmd+Q, not just close window)
4. Check logs: `tail -f ~/Library/Logs/Claude/mcp-server-fingerstyle-mcp.log`

#### Issue: Server starts but crashes immediately

**Solution:**
1. Check for the startup banner in logs:
   ```
   🚀 FINGERSTYLE MCP SERVER IS NOW ONLINE AND READY
   ```
2. If you see import errors, ensure all dependencies are installed:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Test the server manually:
   ```bash
   ./venv/bin/python3 -c "from src.transcriber import transcribe_audio"
   ```

#### Issue: `ModuleNotFoundError: No module named 'basic_pitch'`

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue: `FileNotFoundError: Audio file not found`

**Solution:**
- Ensure the file exists in the `resource/` directory
- Use the `list_available_audio_files` tool to see available files
- Try fuzzy matching with just part of the filename

#### Issue: Parallel processing fails with "chunk error"

**Solution:**
- This usually means one of the audio chunks couldn't be processed
- Check the error logs for the specific chunk that failed
- Try processing a shorter duration to isolate the issue
- Ensure the audio file is not corrupted

#### Issue: BPM detection is inaccurate

**Solution:**
- The first 60 seconds of audio are used for BPM detection
- Ensure the beginning of your file has a clear rhythm
- You can manually override BPM in the code:
  ```python
  notes, _ = transcribe_audio("song.mp3")
  tab = create_tab(notes, bpm=120)  # Force BPM to 120
  ```

#### Issue: No notes detected or very few notes

**Solution:**
- Ensure the guitar is prominent in the mix (not buried under other instruments)
- Try increasing the volume of the audio file
- Check that the audio quality is good (not heavily compressed)
- Solo guitar recordings work best

#### Issue: Tablature is unplayable or uses weird fingerings

**Solution:**
- The algorithm prioritizes open chord shapes (0-5 fret)
- Try using the `tweak_tab_fingering` tool to adjust specific notes
- Consider if the original recording uses a different tuning

### Getting Help

- 📝 **Report bugs**: [Open an issue](https://github.com/blooper20/fingerstyle-tab-mcp/issues)
- 💬 **Ask questions**: [Start a discussion](https://github.com/blooper20/fingerstyle-tab-mcp/discussions)
- 📖 **Check documentation**: See [Korean README](./README_KR.md) for 한국어 문서

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# In config.yaml
logging:
  level: DEBUG

# Or set environment variable
export LOG_LEVEL=DEBUG
python test_workflow.py "song.mp3"
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Development Setup

```bash
# Clone and setup
git clone https://github.com/blooper20/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

### Areas for Contribution

- 🎵 **Improve accuracy**: Better chord detection and fingering algorithms
- 🎸 **Add features**: Support for alternate tunings, capo positions, MIDI export
- 🌍 **Translations**: Add support for more languages
- 📊 **Visualization**: PDF export, better ASCII rendering
- 🧪 **Testing**: Add test coverage
- 📖 **Documentation**: Improve examples and tutorials
- 🐛 **Bug fixes**: Fix issues and edge cases
- ⚡ **Performance**: Optimize processing speed

### Commit Message Guidelines

We use conventional commits:

```
feat: add MIDI export functionality
fix: resolve chord detection for suspended chords
docs: update installation instructions
style: format code with black
refactor: simplify tab generation logic
test: add tests for parallel processing
chore: update dependencies
```

## 🙏 Acknowledgments

This project uses the following open-source libraries:

- [Basic Pitch](https://github.com/spotify/basic-pitch) by Spotify - Audio-to-MIDI transcription
- [Librosa](https://librosa.org/) - Audio analysis and BPM detection
- [Music21](https://web.mit.edu/music21/) - Music theory and chord detection
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [NumPy](https://numpy.org/) - Numerical computing
- [SoundFile](https://github.com/bastibe/python-soundfile) - Audio I/O

Special thanks to the open-source community for making this project possible.

## 📜 License

This project is licensed under the [MIT License](./LICENSE).

You are free to use, modify, and distribute this software for any purpose, including commercial use.

## 🗺️ Roadmap

### Short-term
- [ ] MIDI file export
- [ ] Support for alternative tunings (Drop D, DADGAD, etc.)
- [ ] Capo position detection
- [ ] Improved fingering customization

### Medium-term
- [ ] PDF tablature export with music notation
- [ ] Guitar Pro format export
- [ ] Web-based demo interface

### Long-term
- [ ] Support for multiple instruments (bass, ukulele)
- [ ] Machine learning for custom fingering preferences
- [ ] Real-time audio processing

---

**Made with ❤️ for the open-source community**

**Star this repo** ⭐ if you find it useful!
