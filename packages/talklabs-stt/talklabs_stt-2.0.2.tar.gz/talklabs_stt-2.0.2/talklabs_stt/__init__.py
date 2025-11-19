"""
TalkLabs STT SDK - Speech-to-Text API Client

Transcrição de áudio via API TalkLabs, compatível com Deepgram.
O SDK usa automaticamente o modelo 'turbo' para todas as transcrições.

Usage:
    from talklabs_stt import STTClient, TranscriptionOptions

    # Cliente básico
    client = STTClient(api_key="tlk_live_xxxxx")

    # REST API (usa modelo 'turbo' automaticamente)
    result = client.transcribe_file("audio.wav")
    print(result["results"]["channels"][0]["alternatives"][0]["transcript"])

    # WebSocket Streaming (usa modelo 'turbo' automaticamente)
    async def main():
        await client.transcribe_stream(
            "audio.wav",
            on_transcript=lambda data: print(data)
        )

    asyncio.run(main())

Author: Francisco Lima <franciscorllima@gmail.com>
License: MIT
Repository: https://github.com/talklabs/talklabs-stt
"""

__version__ = "2.0.2"
__author__ = "Francisco Lima"
__email__ = "franciscorllima@gmail.com"
__license__ = "MIT"

from .client import STTClient
from .models import TranscriptionOptions

__all__ = ["STTClient", "TranscriptionOptions"]
