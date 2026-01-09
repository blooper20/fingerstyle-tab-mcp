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

# Global model cache to avoid re-loading for every request
_MODEL_CACHE = None

def get_model():
    """Lazy load and cache the Basic Pitch model."""
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        try:
            from basic_pitch.inference import Model
            logger.info(_("Loading Basic Pitch model into memory..."))
            _MODEL_CACHE = Model(str(ICASSP_2022_MODEL_PATH))
            logger.info(_("Model loaded successfully."))
        except Exception as e:
            logger.error(_("Failed to load model: {}").format(str(e)))
            # Fallback to path string if direct load fails
            _MODEL_CACHE = ICASSP_2022_MODEL_PATH
    return _MODEL_CACHE

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

def _transcribe_chunk(audio_path: str, duration: float = None, start_offset: float = 0.0) -> List[Dict[str, Any]]:
    """Internal function for processing a single audio chunk."""
    temp_path = None
    try:
        validated_path = validate_audio_file(audio_path)
        target_path = str(validated_path)
        if duration or start_offset > 0:
            import tempfile
            import soundfile as sf
            y, sr = librosa.load(str(validated_path), offset=start_offset, duration=duration)
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            sf.write(temp_path, y, sr)
            target_path = temp_path

        model = get_model()
        model_output, midi_data, note_events = predict(target_path, model_or_model_path=model)

        notes = []
        for note in note_events:
            notes.append({
                'start': float(note[0]) + start_offset,
                'end': float(note[1]) + start_offset,
                'pitch': int(note[2]),
                'velocity': float(note[3])
            })
        return notes
    finally:
        if temp_path and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except: pass

def transcribe_audio(audio_path: str, duration: float = None, start_offset: float = 0.0) -> Tuple[List[Dict[str, Any]], float]:
    """
    Analyzes an audio file, using parallel processing for files longer than 45 seconds.
    """
    validated_path = validate_audio_file(audio_path)
    audio_path_str = str(validated_path)
    
    # 1. Detect BPM
    logger.info(_("Detecting tempo..."))
    y, sr = librosa.load(audio_path_str, offset=start_offset, duration=min(60, duration if duration else 60))
    tempo, __ = librosa.beat.beat_track(y=y, sr=sr)
    detected_bpm = float(tempo)
    logger.info(_("Detected BPM: {:.2f}").format(detected_bpm))

    # 2. Determine chunks
    total_duration = float(librosa.get_duration(path=audio_path_str))
    if duration:
        total_duration = min(total_duration, duration)
    
    # Parallelize only if significant length
    if total_duration < 45:
        notes = _transcribe_chunk(audio_path_str, duration=total_duration, start_offset=start_offset)
        return notes, detected_bpm

    chunk_size = 30.0
    overlap = 2.0
    chunks = []
    curr = start_offset
    end_time = start_offset + total_duration
    
    while curr < end_time:
        d = min(chunk_size + overlap, end_time - curr)
        chunks.append((curr, d))
        if curr + chunk_size >= end_time: break
        curr += chunk_size

    logger.info(_("Parallel Analysis: Splitting into {} chunks to finish in < 1 min").format(len(chunks)))
    
    from concurrent.futures import ThreadPoolExecutor
    all_notes = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(_transcribe_chunk, audio_path_str, d, s) for s, d in chunks]
        for i, future in enumerate(futures):
            try:
                all_notes.extend(future.result())
            except Exception as e:
                logger.error(_("Error in chunk {}: {}").format(i+1, str(e)))
                raise RuntimeError(_("Parallel processing failed in chunk {}: {}").format(i+1, str(e))) from e

    # 3. Deduplicate
    all_notes.sort(key=lambda x: (x['start'], x['pitch']))
    unique_notes = []
    if all_notes:
        unique_notes.append(all_notes[0])
        for i in range(1, len(all_notes)):
            curr_n = all_notes[i]
            prev_n = unique_notes[-1]
            if curr_n['pitch'] == prev_n['pitch'] and (curr_n['start'] - prev_n['start']) < 0.1:
                continue
            unique_notes.append(curr_n)

    return unique_notes, detected_bpm
