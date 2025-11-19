#!/usr/bin/env python3
"""
Exemplo - WebSocket Streaming (Conexão Persistente Automática)

Este exemplo demonstra:
- transcribe_stream() mantém conexão WebSocket aberta automaticamente
- Primeira chamada abre a conexão
- Conexão permanece aberta para reutilização
- Use close() quando terminar (opcional, mas recomendado)
"""
import os
import asyncio
from dotenv import load_dotenv
from talklabs_stt import STTClient

load_dotenv()

API_KEY = os.getenv("TALKLABS_STT_API_KEY")
AUDIO_FILE = "/home/TALKLABS/STT/teste_base_bookplay.wav"

async def main():
    # async with garante que close() seja chamado automaticamente
    async with STTClient(api_key=API_KEY) as client:  # type: ignore
        print(f"🎤 Streaming: {AUDIO_FILE}\n")

        def on_transcript(data):
            transcript = data["channel"]["alternatives"][0]["transcript"]
            is_final = data["is_final"]

            if is_final:
                print(f"✅ FINAL: {transcript}")
            else:
                print(f"⏳ Interim: {transcript}")

        # Primeira chamada: abre conexão WebSocket
        # Modelo 'turbo', punctuate e smart_format são sempre aplicados
        await client.transcribe_stream(
            AUDIO_FILE,
            language="pt",
            interim_results=True,
            on_transcript=on_transcript
        )

        print("\n🎉 Streaming finalizado!")
    # Conexão fechada automaticamente aqui

if __name__ == "__main__":
    asyncio.run(main())
