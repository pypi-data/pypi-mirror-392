from array import array
from builtins import anext
import wave

import pytest

from smooth_transcriber.encoder import decode_audio_to_pcm16_stream, stream_pcm_chunks, file_to_stream


@pytest.mark.asyncio
async def test_stream_pcm_chunks_from_wav(tmp_path) -> None:
    audio_path = tmp_path / "tone.wav"

    samples = array("h", [0, 1000, -1000, 2000, -2000, 0])
    with wave.open(str(audio_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16_000)
        wav_file.writeframes(samples.tobytes())

    # Create stream from file
    file_stream = file_to_stream(str(audio_path))
    
    # Decode audio stream to get PCM stream
    audio_stream = decode_audio_to_pcm16_stream(
        audio_stream=file_stream,
        sample_rate_hz=16_000,
        chunk_size=8192,
    )
    
    # Re-chunk the stream
    collected = []
    async for chunk in stream_pcm_chunks(
        chunks=audio_stream,
        chunk_size=4,
        chunk_delay=0.0,
    ):
        collected.append(chunk)

    assert collected
    combined = b"".join(collected)
    # PyAV may add padding or return more data, so we check at least the expected length
    assert len(combined) >= len(samples) * 2
    recovered = array("h")
    # Only check the first N samples worth of data (PyAV may add padding)
    recovered.frombytes(combined[:len(samples) * 2])
    assert recovered.tolist() == list(samples)


@pytest.mark.asyncio
async def test_stream_pcm_chunks_validation(tmp_path) -> None:
    audio_path = tmp_path / "missing.wav"

    # Test FileNotFoundError for file_to_stream
    # file_to_stream raises FileNotFoundError when creating the generator
    with pytest.raises(FileNotFoundError):
        file_stream = file_to_stream(str(audio_path))
        # Consume the stream to trigger the exception
        async for _ in file_stream:
            pass

    # Test ValueError for stream_pcm_chunks
    async def empty_chunks():
        yield b"test"
    
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        async for _ in stream_pcm_chunks(
            chunks=empty_chunks(),
            chunk_size=0,
            chunk_delay=0.0,
        ):
            pass

    with pytest.raises(ValueError, match="chunk_size must be a multiple of 2"):
        async for _ in stream_pcm_chunks(
            chunks=empty_chunks(),
            chunk_size=3,
            chunk_delay=0.0,
        ):
            pass

    with pytest.raises(ValueError, match="chunk_delay must be greater than or equal to zero"):
        async for _ in stream_pcm_chunks(
            chunks=empty_chunks(),
            chunk_size=4,
            chunk_delay=-0.1,
        ):
            pass
