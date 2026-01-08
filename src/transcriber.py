import numpy as np
import librosa
import gettext
import os
import logging
from typing import List, Dict, Tuple, Any
from pathlib import Path
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Internationalization Setup
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../locales')
translate = gettext.translation('messages', localedir, fallback=True)
_ = translate.gettext

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}

def validate_audio_file(audio_path: str) -> Path:
    """
    Validates that the audio file exists and is in a supported format.

    Args:
        audio_path: Path to the audio file

    Returns:
        Path object for the validated file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is not supported
    """
    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(_("Audio file not found: {}").format(audio_path))

    if not path.is_file():
        raise ValueError(_("Path is not a file: {}").format(audio_path))

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            _("Unsupported audio format: {}. Supported formats: {}").format(
                path.suffix, ', '.join(SUPPORTED_FORMATS)
            )
        )

    return path

def transcribe_audio(audio_path: str) -> Tuple[List[Dict[str, Any]], float]:
    """
    Analyzes an audio file using Basic Pitch and Librosa.

    Args:
        audio_path: Path to the audio file (.mp3, .wav, .flac, etc.)

    Returns:
        Tuple containing:
            - List of detected notes with start, end, pitch, and velocity
            - Detected BPM (tempo)

    Raises:
        FileNotFoundError: If the audio file doesn't exist
        ValueError: If the file format is not supported
        RuntimeError: If audio processing fails
    """
    try:
        # Validate input file
        validated_path = validate_audio_file(audio_path)
        logger.info(_("Processing audio file: {}").format(validated_path))

        # 1. Detect BPM using Librosa
        logger.info(_("Detecting tempo..."))
        try:
            y, sr = librosa.load(str(validated_path))
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            detected_bpm = float(tempo)
            logger.info(_("Detected BPM: {:.2f}").format(detected_bpm))
        except Exception as e:
            logger.error(_("Failed to detect BPM: {}").format(str(e)))
            # Use default BPM if detection fails
            detected_bpm = 120.0
            logger.warning(_("Using default BPM: {:.2f}").format(detected_bpm))

        # 2. Pitch Analysis using Basic Pitch
        logger.info(_("Analyzing pitch with Basic Pitch..."))
        try:
            model_output, midi_data, note_events = predict(str(validated_path))
        except Exception as e:
            raise RuntimeError(_("Failed to analyze pitch: {}").format(str(e))) from e

        # 3. Process note events
        notes = []
        for note in note_events:
            try:
                notes.append({
                    'start': float(note[0]),
                    'end': float(note[1]),
                    'pitch': int(note[2]),
                    'velocity': float(note[3])
                })
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(_("Skipping invalid note: {} - Error: {}").format(note, str(e)))
                continue

        # Sort notes by start time
        notes.sort(key=lambda x: x['start'])
        logger.info(_("Successfully extracted {} notes").format(len(notes)))

        return notes, detected_bpm

    except (FileNotFoundError, ValueError) as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(_("Unexpected error during transcription: {}").format(str(e)))
        raise RuntimeError(_("Audio transcription failed: {}").format(str(e))) from e
