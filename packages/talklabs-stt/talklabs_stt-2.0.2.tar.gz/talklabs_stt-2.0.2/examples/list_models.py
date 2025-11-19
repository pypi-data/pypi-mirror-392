#!/usr/bin/env python3
"""
Exemplo - Listar modelos disponíveis no servidor

IMPORTANTE: Este é um método informativo/debugging.
O SDK TalkLabs STT usa exclusivamente o modelo 'turbo'.
A lista abaixo mostra modelos disponíveis no servidor,
mas o SDK sempre utilizará 'turbo' independente desta lista.
"""
import os
from dotenv import load_dotenv
from talklabs_stt import STTClient

load_dotenv()
client = STTClient(api_key=os.getenv("TALKLABS_STT_API_KEY")) # type: ignore

print("📋 Modelos disponíveis no servidor:\n")
print("⚠️  NOTA: O SDK usa apenas 'turbo' - esta lista é informativa.\n")
models = client.list_models()
for model in models.get("models", []):
    model_name = model.get('name', 'N/A')
    marker = " ✅ (usado pelo SDK)" if model_name == "turbo" else ""
    print(f"  - {model_name}{marker}")
