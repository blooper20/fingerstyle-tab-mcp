"""
HTTP-based MCP Server for PlayMCP deployment
Supports Server-Sent Events (SSE) for streaming responses
"""

import os
import sys
import logging
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import tempfile
import uvicorn

# Suppress library warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core logic
try:
    from src.transcriber import transcribe_audio
    from src.tab_generator import create_tab
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)

# FastAPI app
app = FastAPI(
    title="Fingerstyle Tab MCP Server",
    description="AI-powered guitar tablature generator",
    version="1.0.0"
)

# CORS middleware for PlayMCP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PlayMCP requires open CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class AnalyzeRequest(BaseModel):
    duration_seconds: Optional[float] = None
    start_seconds: Optional[float] = 0.0

# In-memory cache
_TAB_CACHE = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Fingerstyle Tab MCP Server",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    duration_seconds: Optional[float] = None,
    start_seconds: float = 0.0
):
    """
    Analyze uploaded audio file and generate guitar tablature

    Args:
        file: Audio file (MP3, WAV, FLAC, etc.)
        duration_seconds: Optional duration limit in seconds
        start_seconds: Start offset in seconds

    Returns:
        JSON response with generated tablature and BPM
    """
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create cache key
    cache_key = f"{file.filename}_{start_seconds}_{duration_seconds}"
    if cache_key in _TAB_CACHE:
        logger.info(f"Returning cached result for: {file.filename}")
        return JSONResponse(content=_TAB_CACHE[cache_key])

    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        fd, temp_path = tempfile.mkstemp(suffix=file_ext)
        os.close(fd)

        # Write uploaded content
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Processing {file.filename} (size: {len(content)} bytes)")

        # Analyze audio
        notes, detected_bpm = transcribe_audio(
            temp_path,
            duration=duration_seconds,
            start_offset=start_seconds
        )

        # Generate tablature
        tab = create_tab(notes, bpm=detected_bpm)

        # Prepare response
        result = {
            "status": "success",
            "filename": file.filename,
            "bpm": float(detected_bpm),
            "notes_detected": len(notes),
            "start_seconds": start_seconds,
            "duration_seconds": duration_seconds,
            "tablature": tab
        }

        # Cache result
        _TAB_CACHE[cache_key] = result

        logger.info(f"Successfully generated tab for {file.filename}")
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

@app.get("/api/tuning/standard")
async def get_standard_tuning():
    """Get standard guitar tuning information"""
    return {
        "tuning": ["E2", "A2", "D3", "G3", "B3", "E4"],
        "frequencies_hz": [82.41, 110.00, 146.83, 196.00, 246.94, 329.63],
        "description": "Standard guitar tuning"
    }

@app.get("/api/info")
async def get_server_info():
    """Get MCP server information"""
    return {
        "name": "Fingerstyle Tab Generator",
        "version": "1.0.0",
        "description": "AI-powered guitar tablature generator using Spotify's Basic Pitch",
        "features": [
            "AI-powered audio transcription",
            "Parallel processing for long files",
            "40+ chord type recognition",
            "Automatic BPM detection",
            "Smart fingering algorithm"
        ],
        "supported_formats": ["mp3", "wav", "flac", "ogg", "m4a", "aac"],
        "endpoints": [
            {"path": "/api/analyze", "method": "POST", "description": "Analyze audio and generate tab"},
            {"path": "/api/tuning/standard", "method": "GET", "description": "Get standard tuning"},
            {"path": "/api/info", "method": "GET", "description": "Get server information"}
        ]
    }

# MCP Protocol endpoints for PlayMCP
@app.get("/mcp/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "analyze_audio_to_tab",
                "description": "Convert audio files to guitar tablature",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "format": "binary",
                            "description": "Audio file to analyze"
                        },
                        "duration_seconds": {
                            "type": "number",
                            "description": "Optional duration limit in seconds"
                        },
                        "start_seconds": {
                            "type": "number",
                            "description": "Start offset in seconds",
                            "default": 0.0
                        }
                    },
                    "required": ["file"]
                }
            },
            {
                "name": "get_standard_tuning",
                "description": "Get standard guitar tuning information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }

@app.get("/mcp/resources")
async def list_resources():
    """List available MCP resources"""
    return {
        "resources": [
            {
                "uri": "guitar://tuning/standard",
                "name": "Standard Guitar Tuning",
                "description": "Standard guitar tuning reference (E A D G B E)"
            }
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
