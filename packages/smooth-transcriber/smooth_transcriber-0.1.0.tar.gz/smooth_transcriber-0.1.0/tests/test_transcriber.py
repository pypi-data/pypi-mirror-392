"""Tests for streaming transcription with real audio files and Google credentials."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest

from smooth_transcriber import StreamingTranscriber, TranscriptionConfig, file_to_stream
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def credentials_path() -> str:
    """Return path to Google credentials file."""
    test_dir = Path(__file__).parent
    credentials = test_dir / "data" / "google.json"
    if not credentials.exists():
        pytest.skip(f"Google credentials not found at {credentials}")
    return str(credentials)


@pytest.fixture
def audio_file_path() -> Path:
    """Return path to test audio file."""
    test_dir = Path(__file__).parent
    audio_file = test_dir / "data" / "zh-CN_test.webm"
    if not audio_file.exists():
        pytest.skip(f"Test audio file not found at {audio_file}")
    return audio_file


@pytest.mark.asyncio
async def test_transcribe_webm_file(credentials_path: str, audio_file_path: Path) -> None:
    """Test transcription of a Chinese audio file in webm format."""
    config = TranscriptionConfig(
        language_code="zh-CN",
        sample_rate_hz=16_000,
        chunk_size=8_192,
        chunk_delay=0.1,
        enable_interim_results=True,
        enable_automatic_punctuation=True,
    )
    
    transcriber = StreamingTranscriber(credentials_path=credentials_path)
    
    # Create stream from webm file
    audio_stream = file_to_stream(str(audio_file_path))
    
    # Collect transcription events
    events = []
    final_transcripts = []
    
    logger.info(f"Starting transcription test with config: language={config.language_code}, sample_rate={config.sample_rate_hz}")
    
    async for event in transcriber.stream_from_audio(audio_stream, config):
        logger.info(f"[{event.type.upper()}] Transcript: {event.transcript}")
        if event.type == "final":
            logger.info(f"  Confidence: {event.confidence}, Is Final: {event.is_final}")
        else:
            logger.info(f"  Stability: {event.stability}, Is Final: {event.is_final}")
        
        events.append(event)
        if event.type == "final" and event.transcript:
            final_transcripts.append(event.transcript)
    
    # Verify that we received at least some events
    assert len(events) > 0, "Should receive at least one transcription event"
    
    # Verify that we received at least one final transcript
    assert len(final_transcripts) > 0, "Should receive at least one final transcription result"
    
    # Verify final transcripts are not empty
    logger.info(f"Total events received: {len(events)}, Final transcripts: {len(final_transcripts)}")
    for idx, transcript in enumerate(final_transcripts, 1):
        logger.info(f"Final transcript #{idx}: {transcript}")
        assert transcript.strip(), "Final transcripts should not be empty"
    
    # Verify event structure
    for event in events:
        assert event.type in ("interim", "final"), f"Event type should be 'interim' or 'final', got {event.type}"
        assert event.is_final == (event.type == "final"), "is_final should match event type"
        if event.type == "final":
            assert event.confidence is not None, "Final events should have confidence scores"
            assert 0.0 <= event.confidence <= 1.0, "Confidence should be between 0 and 1"
        else:
            assert event.stability is not None or event.stability is None, "Interim events may have stability"


@pytest.mark.asyncio
async def test_transcribe_webm_file_interim_disabled(credentials_path: str, audio_file_path: Path) -> None:
    """Test transcription with interim results disabled."""
    config = TranscriptionConfig(
        language_code="zh-CN",
        sample_rate_hz=16_000,
        chunk_size=8_192,
        chunk_delay=0.1,
        enable_interim_results=False,
        enable_automatic_punctuation=True,
    )
    
    transcriber = StreamingTranscriber(credentials_path=credentials_path)
    audio_stream = file_to_stream(str(audio_file_path))
    
    logger.info("Starting transcription test with interim results disabled")
    
    events = []
    async for event in transcriber.stream_from_audio(audio_stream, config):
        logger.info(f"[{event.type.upper()}] Transcript: {event.transcript}")
        if event.type == "final":
            logger.info(f"  Confidence: {event.confidence}")
        
        events.append(event)
        # All events should be final when interim results are disabled
        assert event.type == "final", "Should only receive final events when interim results are disabled"
    
    # Should still receive at least one final event
    logger.info(f"Total final events received: {len(events)}")
    assert len(events) > 0, "Should receive at least one final transcription event"


@pytest.mark.asyncio
async def test_transcribe_with_invalid_credentials(tmp_path: Path) -> None:
    """Test that transcription fails gracefully with invalid credentials."""
    invalid_credentials = tmp_path / "invalid.json"
    invalid_credentials.write_text('{"type": "service_account", "invalid": "credentials"}')
    
    config = TranscriptionConfig(language_code="zh-CN")
    transcriber = StreamingTranscriber(credentials_path=str(invalid_credentials))
    
    # Create a minimal audio stream
    async def empty_stream():
        yield b""
    
    with pytest.raises(RuntimeError, match="Failed to create Speech client|Streaming recognition failed"):
        async for _ in transcriber.stream_from_audio(empty_stream(), config):
            pass


@pytest.mark.asyncio
async def test_transcribe_webm_file_single_utterance(credentials_path: str, audio_file_path: Path) -> None:
    """Test transcription with single_utterance mode enabled."""
    config = TranscriptionConfig(
        language_code="zh-CN",
        sample_rate_hz=16_000,
        chunk_size=8_192,
        chunk_delay=0,
        single_utterance=True,
        enable_interim_results=True,
    )
    
    transcriber = StreamingTranscriber(credentials_path=credentials_path)
    audio_stream = file_to_stream(str(audio_file_path))
    
    logger.info("Starting transcription test with single_utterance mode enabled")
    
    events = []
    async for event in transcriber.stream_from_audio(audio_stream, config):
        logger.info(f"[{event.type.upper()}] Transcript: {event.transcript}")
        if event.type == "final":
            logger.info(f"  Confidence: {event.confidence}, Is Final: {event.is_final}")
        else:
            logger.info(f"  Stability: {event.stability}, Is Final: {event.is_final}")
        
        events.append(event)
    
    # In single_utterance mode, we should get at least one final result
    logger.info(f"Total events received: {len(events)}")
    assert len(events) > 0, "Should receive transcription events"
    final_events = [e for e in events if e.type == "final"]
    logger.info(f"Final events: {len(final_events)}")
    for idx, event in enumerate(final_events, 1):
        logger.info(f"Final transcript #{idx}: {event.transcript} (confidence: {event.confidence})")
    assert len(final_events) > 0, "Should receive at least one final result in single_utterance mode"

