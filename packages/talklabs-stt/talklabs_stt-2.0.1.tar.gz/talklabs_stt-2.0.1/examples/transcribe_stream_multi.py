#!/usr/bin/env python3
"""
Exemplo - Múltiplas Transcrições com Conexão Persistente

Este exemplo demonstra:
- transcribe_stream() reutiliza conexão WebSocket automaticamente
- Primeira chamada: abre conexão (nova)
- Chamadas seguintes: reutilizam a mesma conexão (mais rápido)
- close() fecha a conexão quando terminar

Ideal para: processar múltiplos áudios em sequência
"""
import os
import asyncio
import time
from dotenv import load_dotenv
from talklabs_stt import STTClient

load_dotenv()

API_KEY = os.getenv("TALKLABS_STT_API_KEY")
AUDIO_FILE = "/home/TALKLABS/STT/teste_base_bookplay.wav"

async def main():
    # async with garante que close() seja chamado automaticamente
    async with STTClient(api_key=API_KEY) as client:  # type: ignore
        print("🔗 CONEXÃO PERSISTENTE AUTOMÁTICA")
        print("="*60)
        print("transcribe_stream mantém a conexão aberta automaticamente!")
        print("="*60)

        # Callback
        transcription_count = 0

        def on_transcript(data):
            nonlocal transcription_count
            transcript = data["channel"]["alternatives"][0]["transcript"]
            is_final = data["is_final"]

            if is_final:
                transcription_count += 1
                print(f"✅ [{transcription_count}]: {transcript}")

        num_transcriptions = 3
        start_time = time.time()

        for i in range(num_transcriptions):
            print(f"\n🎤 Transcrição {i+1}/{num_transcriptions}")
            print("-" * 60)

            iteration_start = time.time()

            # Primeira chamada: abre conexão
            # Chamadas seguintes: reutilizam automaticamente
            # Modelo 'turbo', punctuate e smart_format são sempre aplicados
            await client.transcribe_stream(
                AUDIO_FILE,
                language="pt",
                interim_results=False,
                on_transcript=on_transcript
            )

            iteration_time = time.time() - iteration_start
            print(f"⏱️  Tempo: {iteration_time:.2f}s")

        total_time = time.time() - start_time

        # RESULTADOS
        print("\n" + "="*60)
        print("📈 RESULTADOS:")
        print("="*60)
        print(f"Total de transcrições: {num_transcriptions}")
        print(f"Segmentos transcritos: {transcription_count}")
        print(f"Tempo total: {total_time:.2f}s")
        print(f"Média por transcrição: {total_time/num_transcriptions:.2f}s")
        print("="*60)
    # Conexão fechada automaticamente aqui

if __name__ == "__main__":
    asyncio.run(main())
