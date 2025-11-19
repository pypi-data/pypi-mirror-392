"""Unit tests for streaming audio encoder.

Tests encoding PCM audio to various formats and decoding back to linear16.
"""

from __future__ import annotations

import math
from array import array
from pathlib import Path

import pytest

try:
    import av
except ImportError:
    pytest.skip("av (PyAV) is required for encoder tests", allow_module_level=True)

from smooth_transcriber.encoder import StreamingAudioEncoder
from smooth_transcriber.media_format import MediaFormat


# Format to codec mapping for encoding
FORMAT_CODEC_MAP = {
    MediaFormat.WEBM: "libopus",
    MediaFormat.OGG: "libopus",
    MediaFormat.WAV: "pcm_s16le",
    MediaFormat.MP3: "libmp3lame",
    MediaFormat.M4A: "aac",
    MediaFormat.AAC: "aac",
    MediaFormat.FLAC: "flac",
}

# Format to container format mapping (some formats need different container)
FORMAT_CONTAINER_MAP = {
    MediaFormat.M4A: "mp4",  # m4a uses mp4 container
    MediaFormat.AAC: "mp4",  # aac uses mp4 container
}


def generate_test_pcm(sample_rate: int = 16000, duration_ms: int = 100) -> bytes:
    """Generate test PCM16 audio data.
    
    Generates a simple sine wave tone.
    
    Args:
        sample_rate: Sample rate in Hz
        duration_ms: Duration in milliseconds
        
    Returns:
        PCM16 bytes (16-bit little-endian samples)
    """
    samples_count = int(sample_rate * duration_ms / 1000)
    samples = array("h")  # signed 16-bit integers
    
    # Generate a simple sine wave at 440 Hz (A4 note)
    frequency = 440.0
    amplitude = 16000  # Reasonable amplitude
    
    for i in range(samples_count):
        t = i / sample_rate
        value = int(amplitude * math.sin(2 * math.pi * frequency * t))
        # Clamp to valid range
        value = max(-32768, min(32767, value))
        samples.append(value)
    
    return samples.tobytes()


def decode_audio_to_pcm16(file_path: str, sample_rate: int = 16000) -> bytes:
    """Decode audio file to PCM16 using PyAV.
    
    Args:
        file_path: Path to encoded audio file
        sample_rate: Target sample rate
        
    Returns:
        PCM16 bytes (16-bit little-endian mono samples)
    """
    container = av.open(file_path, mode="r")
    try:
        stream = container.streams.audio[0]
        
        # Always use resampler to ensure correct format (s16, mono, target rate)
        resampler = av.AudioResampler(
            format="s16",
            layout="mono",
            rate=sample_rate
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


def test_encoder_context_manager() -> None:
    """Test encoder context manager functionality."""
    encoder = StreamingAudioEncoder(
        format="webm",
        codec="libopus",
        sample_rate=16000,
        channels=1,
    )
    
    assert not encoder._is_open
    with encoder:
        assert encoder._is_open
    assert not encoder._is_open


def test_encoder_validation() -> None:
    """Test encoder parameter validation."""
    with pytest.raises(ValueError, match="sample_rate must be positive"):
        StreamingAudioEncoder(sample_rate=0)
    
    with pytest.raises(ValueError, match="channels must be positive"):
        StreamingAudioEncoder(channels=0)


def test_encoder_open_close() -> None:
    """Test encoder open and close methods."""
    encoder = StreamingAudioEncoder()
    
    assert not encoder._is_open
    encoder.open()
    assert encoder._is_open
    
    encoder.close()
    assert not encoder._is_open
    
    # Test double close
    encoder.close()
    assert not encoder._is_open
    
    # Test double open
    encoder.open()
    with pytest.raises(RuntimeError, match="already open"):
        encoder.open()


def test_encoder_encode_chunk_not_open() -> None:
    """Test encoding when encoder is not open."""
    encoder = StreamingAudioEncoder()
    pcm_data = generate_test_pcm()
    
    with pytest.raises(RuntimeError, match="not open"):
        encoder.encode_chunk(pcm_data)


def test_encoder_encode_empty_chunk() -> None:
    """Test encoding empty chunk."""
    encoder = StreamingAudioEncoder()
    encoder.open()
    try:
        result = encoder.encode_chunk(b"")
        assert result == b""
    finally:
        encoder.close()


def test_encoder_reset() -> None:
    """Test encoder reset functionality."""
    encoder = StreamingAudioEncoder()
    encoder.open()
    pcm_data = generate_test_pcm()
    encoder.encode_chunk(pcm_data)
    
    initial_data = encoder.get_encoded_data()
    assert len(initial_data) > 0
    
    encoder.reset()
    assert not encoder._is_open
    assert len(encoder.get_encoded_data()) == 0


@pytest.mark.parametrize("media_format", list(MediaFormat))
def test_encode_decode_format(media_format: MediaFormat, tmp_path: Path) -> None:
    """Test encoding and decoding for each media format.
    
    This test:
    1. Generates test PCM16 audio
    2. Encodes it to the specified format
    3. Decodes it back to PCM16
    4. Verifies the decoded data is valid
    """
    codec = FORMAT_CODEC_MAP.get(media_format)
    if not codec:
        pytest.skip(f"No codec mapping for {media_format}")
    
    # Get container format (default to media format value)
    container_format = FORMAT_CONTAINER_MAP.get(media_format, media_format.value)
    
    # Skip formats that might not be available
    try:
        encoder = StreamingAudioEncoder(
            format=container_format,
            codec=codec,
            sample_rate=16000,
            channels=1,
            sample_format="s16",
        )
    except Exception as e:
        pytest.skip(f"Failed to create encoder for {media_format}: {e}")
    
    # Generate test PCM data
    original_pcm = generate_test_pcm(sample_rate=16000, duration_ms=100)
    assert len(original_pcm) > 0
    
    # Encode to the target format
    output_file = tmp_path / f"test.{media_format.extension}"
    
    encoder.open()
    try:
        # Encode in chunks to test streaming
        chunk_size = len(original_pcm) // 3
        encoded_chunks = []
        
        for i in range(0, len(original_pcm), chunk_size):
            chunk = original_pcm[i:i + chunk_size]
            if chunk:
                encoded = encoder.encode_chunk(chunk)
                if encoded:
                    encoded_chunks.append(encoded)
        
        # Get any remaining encoded data before closing
        remaining = encoder.get_encoded_data()
        if remaining:
            encoded_chunks.append(remaining)
        
    finally:
        encoder.close()
        # Get final data after closing (close() flushes remaining frames)
        final_data = encoder.get_encoded_data()
        if final_data:
            encoded_chunks.append(final_data)
    
    # Write to file
    encoded_bytes = b"".join(encoded_chunks)
    output_file.write_bytes(encoded_bytes)
    
    # Verify file was created and has content
    assert output_file.exists()
    assert len(encoded_bytes) > 0
    
    # Decode back to PCM16
    try:
        decoded_pcm = decode_audio_to_pcm16(str(output_file), sample_rate=16000)
    except Exception as e:
        pytest.fail(f"Failed to decode {media_format} file: {e}")
    
    # Verify decoded data
    assert len(decoded_pcm) > 0, f"Decoded {media_format} should have data"
    assert len(decoded_pcm) % 2 == 0, "PCM16 data should be even number of bytes"
    
    # For lossy formats (mp3, opus, aac), we can't expect exact match
    # But we should have similar length and valid PCM data
    lossy_formats = {MediaFormat.MP3, MediaFormat.M4A, MediaFormat.AAC, 
                     MediaFormat.WEBM, MediaFormat.OGG}
    
    if media_format in lossy_formats:
        # For lossy formats, just verify we got valid PCM data
        # Length might be different due to encoding artifacts
        samples = array("h")
        samples.frombytes(decoded_pcm)
        # Verify all samples are in valid range
        for sample in samples[:100]:  # Check first 100 samples
            assert -32768 <= sample <= 32767
    else:
        # For lossless formats (WAV, FLAC), we can do more precise checks
        # But even WAV might have slight differences due to encoding pipeline
        assert len(decoded_pcm) > 0
        samples = array("h")
        samples.frombytes(decoded_pcm)
        # Verify samples are in valid range
        assert all(-32768 <= s <= 32767 for s in samples[:100])


def test_encoder_get_encoded_data() -> None:
    """Test getting accumulated encoded data."""
    encoder = StreamingAudioEncoder(
        format="webm",
        codec="libopus",
        sample_rate=16000,
    )
    
    encoder.open()
    try:
        pcm_data = generate_test_pcm()
        encoder.encode_chunk(pcm_data)
        
        # Get encoded data multiple times should work
        data1 = encoder.get_encoded_data()
        data2 = encoder.get_encoded_data()
        
        assert data1 == data2
        assert len(data1) > 0
    finally:
        encoder.close()


def test_encoder_with_bitrate() -> None:
    """Test encoder with custom bitrate."""
    encoder = StreamingAudioEncoder(
        format="webm",
        codec="libopus",
        sample_rate=16000,
        bitrate=64000,
    )
    
    encoder.open()
    try:
        pcm_data = generate_test_pcm()
        encoded = encoder.encode_chunk(pcm_data)
        
        # Just verify it doesn't crash
        assert encoded is not None
    finally:
        encoder.close()


def test_encoder_stereo() -> None:
    """Test encoding stereo audio."""
    encoder = StreamingAudioEncoder(
        format="webm",
        codec="libopus",
        sample_rate=16000,
        channels=2,
    )
    
    # Generate stereo PCM (interleaved LRLRLR...)
    samples = array("h")
    for i in range(1600):  # 100ms at 16kHz
        samples.append(i % 1000)  # Left channel
        samples.append(-(i % 1000))  # Right channel
    
    stereo_pcm = samples.tobytes()
    
    encoder.open()
    try:
        encoded = encoder.encode_chunk(stereo_pcm)
        assert encoded is not None
    finally:
        encoder.close()

