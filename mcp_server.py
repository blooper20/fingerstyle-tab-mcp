# 1. Suppress library logs via environment variables
import os
import sys
import logging
import contextlib

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import gettext
from mcp.server.fastmcp import FastMCP

# Setup logging to STDERR
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import core logic
try:
    from src.transcriber import transcribe_audio
    from src.tab_generator import create_tab
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)

# Internationalization Setup
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
translate = gettext.translation('messages', localedir, fallback=True)
_ = translate.gettext

# Create MCP Server
mcp = FastMCP("Fingerstyle Tab Generator")

print("------------------------------------------------", file=sys.stderr, flush=True)
print("🚀 FINGERSTYLE MCP SERVER IS NOW ONLINE AND READY", file=sys.stderr, flush=True)
print("------------------------------------------------", file=sys.stderr, flush=True)

# Result cache to avoid re-processing identical files
_TAB_CACHE = {}

@mcp.tool()
def analyze_audio_to_tab(file_path: str, duration_seconds: float = None, start_seconds: float = 0.0) -> str:
    """
    Analyzes an audio file and converts it to guitar tablature.
    
    Args:
        file_path: The absolute path to the file OR just the filename (it will search in the local 'resource/' folder).
        duration_seconds: (Optional) Limit analysis to N seconds (default: None - process all).
        start_seconds: (Optional) Start analysis from N seconds (default: 0.0).
    
    Returns:
        Generated ASCII guitar tablature or a CRITICAL error message.
    """
    cache_key = f"{file_path}_{start_seconds}_{duration_seconds}"
    if cache_key in _TAB_CACHE:
        logger.info(f"Returning cached result for: {file_path}")
        return _TAB_CACHE[cache_key]

    print(f"DEBUG: Tool called for: {file_path} (Start: {start_seconds}s, Duration: {duration_seconds}s)", file=sys.stderr, flush=True)

    project_root = os.path.dirname(os.path.abspath(__file__))
    resource_dir = os.path.join(project_root, 'resource')
    
    full_path = os.path.abspath(os.path.expanduser(file_path))
    
    # 1. Improved Fuzzy Matching
    if not os.path.exists(full_path):
        print(f"DEBUG: Path {full_path} not found. Fuzzy matching in {resource_dir}", file=sys.stderr, flush=True)
        filename = os.path.basename(full_path)
        
        if os.path.exists(resource_dir):
            import re
            def normalize(s):
                # Remove extension and keep only alphanumeric
                name_only = os.path.splitext(s)[0]
                return re.sub(r'[^a-zA-Z0-9]', '', name_only).lower()
            
            target_norm = normalize(filename)
            available_files = os.listdir(resource_dir)
            
            for f in available_files:
                if f.startswith('.'): continue
                f_norm = normalize(f)
                if f_norm == target_norm or target_norm in f_norm or f_norm in target_norm:
                    found_path = os.path.join(resource_dir, f)
                    if os.path.isfile(found_path):
                        print(f"DEBUG: SUCCESSful fuzzy match: {f}", file=sys.stderr, flush=True)
                        full_path = found_path
                        break

    # 2. Final check with explicit failure message
    if not os.path.exists(full_path):
        files = os.listdir(resource_dir) if os.path.exists(resource_dir) else []
        err_msg = (
            "CRITICAL ERROR: TAB GENERATION FAILED. NO FILE FOUND.\n"
            f"Expected: {full_path}\n"
            f"Available in resource/: {', '.join(files)}\n"
            "INSTRUCTION TO AI: Do NOT hallucinate a tab. Tell the user the file is missing in the 로컬 'resource' folder."
        )
        return err_msg
    
    try:
        print(f"DEBUG: Processing {full_path}...", file=sys.stderr, flush=True)
        # Wrap everything in redirect_stdout to keep MCP-STDOUT clean
        with contextlib.redirect_stdout(sys.stderr):
            # Step 1: Transcribe audio to note data
            notes, detected_bpm = transcribe_audio(full_path, duration=duration_seconds, start_offset=start_seconds)
            
            # Step 2: Convert notes to tablature
            tab = create_tab(notes, bpm=detected_bpm)
        
        print(f"DEBUG: Processing complete!", file=sys.stderr, flush=True)
        result = _("Analysis Successful (Start: {}s, Duration: {}s) - Path: {}:\n\n{}").format(start_seconds, duration_seconds, full_path, tab)
        _TAB_CACHE[cache_key] = result
        return result
    except Exception as e:
        logger.error(_("Error during analysis: {}").format(str(e)))
        return _("Error occurred during processing (Check server logs for details): {}").format(str(e))

@mcp.tool()
def list_available_audio_files() -> str:
    """
    Lists all audio files available in the local 'resource' directory.
    Use this to see which songs are ready for analysis.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    resource_dir = os.path.join(project_root, 'resource')
    
    if os.path.exists(resource_dir):
        files = [f for f in os.listdir(resource_dir) if not f.startswith('.')]
        if files:
            return _("Available files in 'resource/':\n- {}").format("\n- ".join(files))
        return _("The 'resource/' folder is empty.")
    return _("The 'resource/' folder does not exist.")

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

@mcp.resource("guitar://tuning/standard")
def get_standard_tuning() -> str:
    """Returns standard guitar tuning information."""
    return _("Standard Tuning: E2, A2, D3, G3, B3, E4 (82.41Hz - 329.63Hz)")

if __name__ == "__main__":
    mcp.run()
