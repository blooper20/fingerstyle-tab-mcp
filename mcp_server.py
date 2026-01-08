import os
import gettext
import logging
from mcp.server.fastmcp import FastMCP
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Internationalization Setup
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('messages', localedir, fallback=True)
_ = translate.gettext

# Create MCP Server
mcp = FastMCP("Fingerstyle Tab Generator")

@mcp.tool()
def analyze_audio_to_tab(file_path: str) -> str:
    """
    Analyzes an audio file (.mp3, .wav, .flac) and converts it to guitar tablature.
    
    Args:
        file_path: Absolute path to the audio file.
    
    Returns:
        Generated ASCII guitar tablature.
    """
    if not os.path.exists(file_path):
        return _("Error: File not found: {}").format(file_path)
    
    try:
        logger.info(_("Starting analysis for file: {}").format(file_path))
        
        # Step 1: Transcribe audio to note data
        notes, detected_bpm = transcribe_audio(file_path)
        
        # Step 2: Convert notes to tablature
        tab = create_tab(notes, bpm=detected_bpm)
        
        logger.info(_("Successfully generated tab for: {}").format(file_path))
        return _("Analysis Successful - Path: {}:\n\n{}").format(file_path, tab)
    except Exception as e:
        logger.error(_("Error during analysis: {}").format(str(e)))
        return _("Error occurred during processing: {}").format(str(e))

@mcp.tool()
def tweak_tab_fingering(note_pitch: int, preferred_string: int) -> str:
    """
    Suggests a preferred string for a specific note pitch.
    
    Args:
        note_pitch: MIDI pitch of the note (0-127).
        preferred_string: Target guitar string number (1: High E to 6: Low E).
    
    Returns:
        Feedback on the adjustment request.
    """
    string_names = ["Low E", "A", "D", "G", "B", "High E"]
    if 1 <= preferred_string <= 6:
        msg = _("Updated configuration to play pitch {} on string {} ({}) (Logic integration pending).").format(
            note_pitch, preferred_string, string_names[6-preferred_string]
        )
        return msg
    else:
        return _("Invalid string number. Please enter a value between 1 and 6.")

@mcp.resource("guitar/tuning/standard")
def get_standard_tuning() -> str:
    """Returns standard guitar tuning information."""
    return _("Standard Tuning: E2, A2, D3, G3, B3, E4 (82.41Hz - 329.63Hz)")

if __name__ == "__main__":
    mcp.run()
