"""
TalkLabs plugins for LiveKit Agents

High-quality Portuguese text-to-speech and speech-to-text for LiveKit applications.
"""

from .stt import TalkLabsSTT, TalkLabsSpeechStream
from .tts import TalkLabsTTS, TalkLabsStream
from .version import __version__

__all__ = [
    "TalkLabsSTT",
    "TalkLabsSpeechStream",
    "TalkLabsTTS",
    "TalkLabsStream",
    "__version__",
]

# Namespace package declaration for LiveKit plugins
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
