"""Event models for streaming transcription.

This module defines the data structures used to represent transcription events
in a streaming transcription system. Events can be either interim (preliminary)
or final results, and include metadata such as confidence scores and stability
metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

EventType = Literal["interim", "final"]
"""Type alias for transcription event types.

Possible values:
    - "interim": A preliminary transcription result that may change
    - "final": A confirmed transcription result that will not be updated
"""


@dataclass(frozen=True)
class TranscriptionEvent:
    """Representation of a streaming transcription update.
    
    This class encapsulates a single transcription event from a streaming
    transcription system. Events can be either interim (preliminary) or final
    results, and may include additional metadata such as confidence scores
    and stability metrics.
    
    Attributes:
        type: The event type, either "interim" or "final"
        transcript: The transcribed text content
        is_final: Boolean flag indicating if this is a final result
        confidence: Optional confidence score (0.0 to 1.0) for the transcription
        stability: Optional stability metric indicating how stable the result is
        result_index: Optional index indicating the position of this result
            in a sequence of results
    """

    type: EventType
    """The event type: "interim" for preliminary results, "final" for confirmed results."""
    
    transcript: str
    """The transcribed text content."""
    
    is_final: bool
    """Whether this is a final, confirmed transcription result."""
    
    confidence: Optional[float] = None
    """Confidence score for the transcription, typically between 0.0 and 1.0."""
    
    stability: Optional[float] = None
    """Stability metric indicating how stable the transcription result is."""
    
    result_index: Optional[int] = None
    """Index indicating the position of this result in a sequence of results."""

    def is_empty(self) -> bool:
        """Check if the transcript contains no visible characters.
        
        Returns:
            True if the transcript is empty or contains only whitespace,
            False otherwise.
        """
        return not self.transcript.strip()

