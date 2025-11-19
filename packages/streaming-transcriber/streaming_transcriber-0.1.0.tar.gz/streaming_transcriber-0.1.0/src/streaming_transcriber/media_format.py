"""Media format enumeration for audio files.

Supports all HTML5 recording formats for MediaRecorder API.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional


class MediaFormat(Enum):
    """Audio format enumeration supporting all HTML5 recording formats.
    
    HTML5 MediaRecorder API supports these formats:
    - webm: Most common, uses Opus or Vorbis codec
    - ogg: Uses Opus or Vorbis codec
    - wav: PCM format, well-supported by browsers
    - mp3: Not natively supported for recording, but can be converted
    - m4a/aac: Supported by some browsers
    - flac: Supported by some browsers
    """
    
    WEBM = "webm"
    OGG = "ogg"
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    AAC = "aac"
    FLAC = "flac"
    
    @property
    def extension(self) -> str:
        """Get the file extension for this format (without the dot)."""
        return self.value
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type for this format."""
        mime_map = {
            MediaFormat.WEBM: "audio/webm",
            MediaFormat.OGG: "audio/ogg",
            MediaFormat.WAV: "audio/wav",
            MediaFormat.MP3: "audio/mpeg",
            MediaFormat.M4A: "audio/mp4",
            MediaFormat.AAC: "audio/aac",
            MediaFormat.FLAC: "audio/flac",
        }
        return mime_map.get(self, f"audio/{self.value}")
    
    @property
    def is_html5_supported(self) -> bool:
        """Check if this format is natively supported by HTML5 MediaRecorder API."""
        # Most browsers support webm and ogg natively for recording
        # wav is also commonly supported
        return self in (MediaFormat.WEBM, MediaFormat.OGG, MediaFormat.WAV)
    
    @classmethod
    def from_file_path(cls, file_path: str) -> Optional[MediaFormat]:
        """Detect media format from file path/extension.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            MediaFormat enum value if recognized, None otherwise
        """
        ext = Path(file_path).suffix.lower().lstrip(".")
        try:
            return cls(ext)
        except ValueError:
            return None
    
    @classmethod
    def from_extension(cls, extension: str) -> Optional[MediaFormat]:
        """Detect media format from file extension.
        
        Args:
            extension: File extension (with or without leading dot)
            
        Returns:
            MediaFormat enum value if recognized, None otherwise
        """
        ext = extension.lstrip(".").lower()
        try:
            return cls(ext)
        except ValueError:
            return None
    
    @classmethod
    def from_mime_type(cls, mime_type: str) -> Optional[MediaFormat]:
        """Detect media format from MIME type.
        
        Args:
            mime_type: MIME type string (e.g., "audio/webm")
            
        Returns:
            MediaFormat enum value if recognized, None otherwise
        """
        mime_to_format = {
            "audio/webm": cls.WEBM,
            "audio/ogg": cls.OGG,
            "audio/oga": cls.OGG,
            "audio/wav": cls.WAV,
            "audio/wave": cls.WAV,
            "audio/x-wav": cls.WAV,
            "audio/mpeg": cls.MP3,
            "audio/mp3": cls.MP3,
            "audio/mp4": cls.M4A,
            "audio/x-m4a": cls.M4A,
            "audio/aac": cls.AAC,
            "audio/flac": cls.FLAC,
            "audio/x-flac": cls.FLAC,
        }
        return mime_to_format.get(mime_type.lower())
    
    def __str__(self) -> str:
        """Return the format name."""
        return self.value
