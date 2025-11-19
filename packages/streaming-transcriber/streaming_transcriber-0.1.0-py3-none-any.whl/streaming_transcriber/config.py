"""Configuration objects for streaming transcription."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptionConfig:
    """User-facing configuration for streaming speech recognition."""

    language_code: str = "zh-CN"
    sample_rate_hz: int = 16_000
    chunk_size: int = 8_192
    chunk_delay: float = 0.0
    enable_interim_results: bool = True
    enable_automatic_punctuation: bool = True
    single_utterance: bool = False

    def validate(self) -> None:
        """Validate configuration values and raise ``ValueError`` when invalid."""

        if not self.language_code:
            raise ValueError("language_code must not be empty")
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_size % 2 != 0:
            raise ValueError("chunk_size must be a multiple of 2 for 16-bit PCM data")
        if self.chunk_delay < 0:
            raise ValueError("chunk_delay must be greater than or equal to zero")

