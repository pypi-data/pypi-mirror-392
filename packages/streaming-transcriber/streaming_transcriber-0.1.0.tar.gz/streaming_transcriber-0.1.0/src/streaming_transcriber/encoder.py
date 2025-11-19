"""Streaming audio encoder and decoder using PyAV.

This module provides:
- Streaming audio encoder that accepts PCM audio chunks and encodes them into various formats
- Audio decoder that decodes various audio formats into PCM16
- Stream utilities for chunked PCM audio processing using async iterators
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
from pathlib import Path
from typing import AsyncIterator, Optional

try:
    import av
except ImportError as err:
    raise ImportError(
        "av (PyAV) is required for audio encoding/decoding. "
        "Install it with: pip install av"
    ) from err

logger = logging.getLogger(__name__)

_BYTES_PER_SAMPLE = 2


class StreamingAudioEncoder:
    """Streaming audio encoder that accepts PCM chunks and encodes them."""

    def __init__(
        self,
        *,
        format: str = "webm",
        codec: str = "libopus",
        sample_rate: int = 16000,
        channels: int = 1,
        sample_format: str = "s16",
        bitrate: Optional[int] = None,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if channels <= 0:
            raise ValueError("channels must be positive")

        self.format = format
        self.codec = codec
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_format = sample_format
        self.bitrate = bitrate

        self._output_buffer = io.BytesIO()
        self._container: Optional[av.Container] = None
        self._stream: Optional[av.AudioStream] = None
        self._is_open = False
        self._buffer_pos = 0

    def __enter__(self) -> StreamingAudioEncoder:
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> None:
        """Open the encoder for streaming."""
        if self._is_open:
            raise RuntimeError("Encoder is already open")

        try:
            self._output_buffer = io.BytesIO()
            self._container = av.open(
                self._output_buffer,
                mode="w",
                format=self.format,
            )
            self._stream = self._container.add_stream(self.codec, rate=self.sample_rate)
            # Set layout based on channel count
            if self.channels == 1:
                self._stream.layout = "mono"
            elif self.channels == 2:
                self._stream.layout = "stereo"
            else:
                # For other channel counts, create a layout name
                layout_name = f"{self.channels}ch"
                try:
                    self._stream.layout = layout_name
                except Exception:
                    # Fallback: try to set channels directly if supported
                    pass
            
            if self.bitrate is not None:
                # Set bitrate using codec options
                self._stream.options = {"bitrate": str(self.bitrate)}

            self._is_open = True
            self._buffer_pos = 0
        except Exception as err:
            raise RuntimeError(f"Failed to open encoder: {err}") from err

    def close(self) -> None:
        """Close the encoder and finalize output."""
        if not self._is_open:
            return

        try:
            if self._container and self._stream:
                # Flush remaining frames
                for packet in self._stream.encode():
                    self._container.mux(packet)
                self._container.close()
            self._is_open = False
        except Exception as err:
            logger.error("Error closing encoder: %s", err)
            raise

    def encode_chunk(self, chunk: bytes) -> bytes:
        """Encode a PCM audio chunk and return encoded data."""
        if not self._is_open:
            raise RuntimeError("Encoder is not open. Call open() first.")

        if not chunk:
            return b""

        try:
            # Calculate number of samples (2 bytes per sample for s16 format)
            samples_count = len(chunk) // (2 * self.channels)
            
            # Create AudioFrame directly from bytes
            frame = av.AudioFrame(
                format=self.sample_format,
                layout="mono" if self.channels == 1 else "stereo",
                samples=samples_count,
            )
            frame.sample_rate = self.sample_rate
            # Update frame data from bytes
            frame.planes[0].update(chunk)

            # Encode and mux
            for packet in self._stream.encode(frame):
                self._container.mux(packet)

            # Read new data from buffer
            new_pos = self._output_buffer.tell()
            if new_pos > self._buffer_pos:
                self._output_buffer.seek(self._buffer_pos)
                data = self._output_buffer.read(new_pos - self._buffer_pos)
                self._buffer_pos = new_pos
                return data

            return b""
        except Exception as err:
            raise RuntimeError(f"Failed to encode chunk: {err}") from err

    def get_encoded_data(self) -> bytes:
        """Get all encoded data accumulated so far."""
        pos = self._output_buffer.tell()
        self._output_buffer.seek(0)
        data = self._output_buffer.read()
        self._output_buffer.seek(pos)
        return data

    def reset(self) -> None:
        """Reset the encoder and clear the output buffer."""
        self.close()
        self._output_buffer = io.BytesIO()
        self._container = None
        self._stream = None
        self._buffer_pos = 0


async def encode_stream(
    chunks: AsyncIterator[bytes],
    encoder: StreamingAudioEncoder,
    *,
    flush: bool = True,
) -> AsyncIterator[bytes]:
    """Encode a stream of PCM chunks asynchronously."""
    encoder.open()
    try:
        async for chunk in chunks:
            encoded = encoder.encode_chunk(chunk)
            if encoded:
                yield encoded
        if flush:
            # Flush remaining frames before getting final data
            if encoder._stream:
                for packet in encoder._stream.encode():
                    encoder._container.mux(packet)
            remaining = encoder.get_encoded_data()
            if remaining:
                yield remaining
    finally:
        encoder.close()


def _get_file_format(audio_path: str) -> str:
    """Detect audio file format from file extension."""
    ext = Path(audio_path).suffix.lower()
    return ext.lstrip(".")


def _decode_audio_with_av(audio_path: str, sample_rate_hz: int) -> bytes:
    """Decode audio file into 16-bit mono PCM at ``sample_rate_hz`` using PyAV."""
    try:
        container = av.open(audio_path, mode="r")
        try:
            stream = container.streams.audio[0]
            
            # Always use resampler to ensure correct format (s16, mono, target rate)
            resampler = av.AudioResampler(
                format="s16",
                layout="mono",
                rate=sample_rate_hz
            )
            
            pcm_data = bytearray()
            
            for frame in container.decode(stream):
                # Resample and convert to target format
                resampled_frames = resampler.resample(frame)
                # resample may return a list or a single frame
                if isinstance(resampled_frames, list):
                    frames_to_process = resampled_frames
                else:
                    frames_to_process = [resampled_frames]
                
                for resampled_frame in frames_to_process:
                    # Extract PCM data from frame
                    # frame.planes[0] is a memoryview, convert to bytes
                    plane_data = resampled_frame.planes[0]
                    pcm_data.extend(bytes(plane_data))
            
            return bytes(pcm_data)
        finally:
            container.close()
    except Exception as err:
        raise RuntimeError(f"Failed to decode audio file '{audio_path}': {err}") from err


async def _decode_audio_stream_with_av(
    audio_stream: AsyncIterator[bytes],
    sample_rate_hz: int,
) -> bytes:
    """Decode audio stream into 16-bit mono PCM at ``sample_rate_hz`` using PyAV.
    
    Args:
        audio_stream: Async iterator of audio data chunks.
        sample_rate_hz: Target sample rate.
        
    Returns:
        Decoded PCM16 bytes.
    """
    # Collect all stream data into a BytesIO buffer
    buffer = io.BytesIO()
    
    async for chunk in audio_stream:
        buffer.write(chunk)
    
    buffer.seek(0)
    
    try:
        container = av.open(buffer, mode="r")
        try:
            stream = container.streams.audio[0]
            
            # Always use resampler to ensure correct format (s16, mono, target rate)
            resampler = av.AudioResampler(
                format="s16",
                layout="mono",
                rate=sample_rate_hz
            )
            
            pcm_data = bytearray()
            
            for frame in container.decode(stream):
                # Resample and convert to target format
                resampled_frames = resampler.resample(frame)
                # resample may return a list or a single frame
                if isinstance(resampled_frames, list):
                    frames_to_process = resampled_frames
                else:
                    frames_to_process = [resampled_frames]
                
                for resampled_frame in frames_to_process:
                    # Extract PCM data from frame
                    # frame.planes[0] is a memoryview, convert to bytes
                    plane_data = resampled_frame.planes[0]
                    pcm_data.extend(bytes(plane_data))
            
            return bytes(pcm_data)
        finally:
            container.close()
    except Exception as err:
        raise RuntimeError(f"Failed to decode audio stream: {err}") from err


def _decode_audio_to_pcm16(audio_path: str, sample_rate_hz: int) -> bytes:
    """Decode ``audio_path`` into 16-bit mono PCM at ``sample_rate_hz``.
    
    Uses PyAV for all formats (including WAV).
    """
    try:
        return _decode_audio_with_av(audio_path, sample_rate_hz)
    except Exception as av_err:
        raise RuntimeError(f"Failed to decode audio file '{audio_path}': {av_err}") from av_err


async def file_to_stream(file_path: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
    """Read a file and yield chunks as an async stream.
    
    Helper function to convert a file path to an async stream of bytes.
    Useful when you need to decode audio from a file using `decode_audio_to_pcm16_stream`.
    
    Args:
        file_path: Path to the file to read.
        chunk_size: Size of chunks to read.
        
    Yields:
        Chunks of file data.
        
    Raises:
        FileNotFoundError: When the file does not exist.
        
    Example:
        ```python
        file_stream = file_to_stream("audio.webm")
        pcm_stream = decode_audio_to_pcm16_stream(
            audio_stream=file_stream,
            sample_rate_hz=16000
        )
        ```
    """
    def read_file() -> bytes:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        with open(file_path, "rb") as f:
            return f.read()
    
    file_data = await asyncio.to_thread(read_file)
    
    for start in range(0, len(file_data), chunk_size):
        chunk = file_data[start : start + chunk_size]
        if chunk:
            yield chunk


async def decode_audio_to_pcm16_stream(
    audio_stream: AsyncIterator[bytes],
    sample_rate_hz: int,
    chunk_size: int = 8192,
) -> AsyncIterator[bytes]:
    """Decode audio stream and yield PCM16 chunks as an async iterator.
    
    Args:
        audio_stream: Async iterator of audio data chunks (supports WAV, webm, and other formats).
        sample_rate_hz: Target sample rate.
        chunk_size: Size of chunks to yield (bytes).
        
    Yields:
        Chunks of PCM audio data encoded as 16-bit little-endian mono samples.
        
    Raises:
        RuntimeError: When audio decoding fails.
        
    Example:
        ```python
        # From file
        async def file_stream():
            with open("audio.webm", "rb") as f:
                while chunk := f.read(8192):
                    yield chunk
        
        async for pcm_chunk in decode_audio_to_pcm16_stream(
            file_stream(),
            sample_rate_hz=16000
        ):
            # Process PCM chunk
            pass
        ```
    """
    try:
        pcm_bytes = await _decode_audio_stream_with_av(audio_stream, sample_rate_hz)
    except Exception as err:
        raise RuntimeError(f"Failed to decode audio stream: {err}") from err
    
    if not pcm_bytes:
        return
    
    for start in range(0, len(pcm_bytes), chunk_size):
        chunk = pcm_bytes[start : start + chunk_size]
        if chunk:
            yield chunk


async def stream_pcm_chunks(
    chunks: AsyncIterator[bytes],
    chunk_size: int,
    chunk_delay: float = 0.0,
) -> AsyncIterator[bytes]:
    """Yield PCM audio chunks from an async iterator, re-chunking to specified size.

    Args:
        chunks: Async iterator of PCM audio data (16-bit little-endian mono samples).
        chunk_size: Number of bytes to emit per iteration.
        chunk_delay: Optional delay (seconds) between chunks.

    Yields:
        Chunks of PCM audio data encoded as 16-bit little-endian mono samples.

    Raises:
        ValueError: When ``chunk_size`` is not positive or not a multiple of 2,
            or ``chunk_delay`` is negative.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_size % _BYTES_PER_SAMPLE != 0:
        raise ValueError("chunk_size must be a multiple of 2 for 16-bit PCM data")
    if chunk_delay < 0:
        raise ValueError("chunk_delay must be greater than or equal to zero")

    buffer = bytearray()
    chunk_index = 0

    async for chunk in chunks:
        if not chunk:
            continue
        
        buffer.extend(chunk)
        
        # Yield chunks of the specified size
        while len(buffer) >= chunk_size:
            output_chunk = bytes(buffer[:chunk_size])
            buffer = buffer[chunk_size:]
            chunk_index += 1
            logger.debug("Yielding chunk %d (%d bytes)", chunk_index, len(output_chunk))
            yield output_chunk
            if chunk_delay > 0:
                await asyncio.sleep(chunk_delay)
    
    # Yield any remaining data
    if buffer:
        chunk_index += 1
        logger.debug("Yielding final chunk %d (%d bytes)", chunk_index, len(buffer))
        yield bytes(buffer)
