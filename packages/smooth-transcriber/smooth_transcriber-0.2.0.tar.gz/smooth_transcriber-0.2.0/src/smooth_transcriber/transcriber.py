"""High-level streaming transcription API."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from google.api_core import exceptions as core_exceptions
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import speech_v1p1beta1 as speech

from .config import TranscriptionConfig
from .events import TranscriptionEvent
from .encoder import decode_audio_to_pcm16_stream, stream_pcm_chunks

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _speech_client(credentials_path: Optional[str]) -> AsyncIterator[speech.SpeechAsyncClient]:
    """Context manager that yields a configured SpeechAsyncClient."""

    previous_credentials = None
    if credentials_path:
        previous_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        logger.debug("Using credentials from %s", credentials_path)

    try:
        client = speech.SpeechAsyncClient()
    except (DefaultCredentialsError, core_exceptions.GoogleAPICallError) as err:
        raise RuntimeError(f"Failed to create Speech client: {err}") from err

    try:
        yield client
    finally:
        await client.transport.close()
        if credentials_path is not None:
            if previous_credentials is None:
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
            else:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = previous_credentials


class StreamingTranscriber:
    """Stream audio data to Google Speech-to-Text and yield transcripts."""

    def __init__(self, *, credentials_path: Optional[str] = None, logger_: Optional[logging.Logger] = None) -> None:
        self._credentials_path = credentials_path
        self._logger = logger_ or logging.getLogger(self.__class__.__name__)

    async def stream(
        self,
        audio_chunks: AsyncIterator[bytes],
        config: TranscriptionConfig,
    ) -> AsyncIterator[TranscriptionEvent]:
        """Stream audio chunks to Google Speech and yield ``TranscriptionEvent`` objects.

        Args:
            audio_chunks: Async iterator of PCM audio chunks (16-bit little-endian mono samples).
            config: Transcription configuration.

        Yields:
            TranscriptionEvent objects as they are received.
        """
        config.validate()

        lang_display = config.language_code if config.language_code else "auto"
        self._logger.info(
            "Streaming audio (lang=%s, sample_rate=%d Hz)...",
            lang_display,
            config.sample_rate_hz,
        )

        async with _speech_client(self._credentials_path) as client:
            request_iter = self._request_generator(audio_chunks=audio_chunks, config=config)

            try:
                responses = await client.streaming_recognize(requests=request_iter)
            except core_exceptions.GoogleAPICallError as err:
                raise RuntimeError(f"Streaming recognition failed: {err}") from err

            async for response in responses:
                self._logger.debug("Received response with %d result(s)", len(response.results))
                for result in response.results:
                    event = self._result_to_event(result)
                    if event is None:
                        continue
                    if not config.enable_interim_results and event.type == "interim":
                        continue
                    self._logger.debug(
                        "[%s] %s", event.type.upper(), event.transcript.replace("\n", " ")
                    )
                    yield event

    async def stream_from_audio(
        self,
        audio_stream: AsyncIterator[bytes],
        config: TranscriptionConfig,
    ) -> AsyncIterator[TranscriptionEvent]:
        """从任意格式的音频流转录文本。

        自动检测音频格式并解码为 PCM16，无需手动调用 decode_audio_to_pcm16_stream。

        Args:
            audio_stream: 任意格式的音频数据流（webm、wav 等）
            config: 转录配置

        Yields:
            TranscriptionEvent 对象

        Example:
            ```python
            async def websocket_audio_stream():
                async for chunk_bytes in receive_audio_chunks():
                    yield chunk_bytes

            transcriber = StreamingTranscriber(credentials_path="google.json")
            async for event in transcriber.stream_from_audio(websocket_audio_stream(), config):
                if event.type == "final":
                    print("[FINAL]", event.transcript)
            ```
        """
        pcm_stream = decode_audio_to_pcm16_stream(
            audio_stream=audio_stream,
            sample_rate_hz=config.sample_rate_hz,
        )
        async for event in self.stream(pcm_stream, config):
            yield event

    async def _request_generator(
        self,
        *,
        audio_chunks: AsyncIterator[bytes],
        config: TranscriptionConfig,
    ) -> AsyncIterator[speech.StreamingRecognizeRequest]:
        """Yield StreamingRecognizeRequest objects for the speech client."""

        # 当 language_code 为 None 时，使用自动语言检测
        # Google Speech API 通过设置多个 alternative_language_codes 来实现自动检测
        if config.language_code is None:
            # 使用常见的多语言列表进行自动检测
            alternative_languages = [
                "zh-CN",  # 中文（简体）
                "zh-TW",  # 中文（繁体）
                "en-US",  # 英语（美国）
                "en-GB",  # 英语（英国）
                "ja-JP",  # 日语
                "ko-KR",  # 韩语
                "es-ES",  # 西班牙语
                "fr-FR",  # 法语
                "de-DE",  # 德语
                "ru-RU",  # 俄语
            ]
            # 使用第一个作为主要语言，其余作为备选
            recognition_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=config.sample_rate_hz,
                language_code=alternative_languages[0],
                alternative_language_codes=alternative_languages[1:],
                enable_automatic_punctuation=config.enable_automatic_punctuation,
            )
        else:
            recognition_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=config.sample_rate_hz,
                language_code=config.language_code,
                enable_automatic_punctuation=config.enable_automatic_punctuation,
            )
        streaming_config = speech.StreamingRecognitionConfig(
            config=recognition_config,
            interim_results=True,
            single_utterance=config.single_utterance,
        )

        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

        # Re-chunk the audio stream to the specified chunk size
        async for chunk in stream_pcm_chunks(
            chunks=audio_chunks,
            chunk_size=config.chunk_size,
            chunk_delay=config.chunk_delay,
        ):
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    def _result_to_event(
        self,
        result: speech.StreamingRecognitionResult,
    ) -> Optional[TranscriptionEvent]:
        """Convert a ``StreamingRecognitionResult`` into a ``TranscriptionEvent``."""

        if not result.alternatives:
            return None

        transcript = result.alternatives[0].transcript.strip()
        if not transcript:
            return None

        event_type = "final" if result.is_final else "interim"
        confidence = result.alternatives[0].confidence if result.is_final else None
        stability = None if result.is_final else result.stability or None

        return TranscriptionEvent(
            type=event_type,
            transcript=transcript,
            is_final=result.is_final,
            confidence=confidence,
            stability=stability,
            result_index=getattr(result, "result_index", None),
        )

