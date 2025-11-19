# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-11-13

### ⚠️ BREAKING CHANGE

**Modelo de transcrição bloqueado para 'turbo'**

O SDK agora usa exclusivamente o modelo 'turbo' para todas as transcrições.
Esta é uma mudança de comportamento significativa que pode afetar código existente.

### Alterado
- 🔒 **Modelo fixado em 'turbo'**: O SDK agora usa apenas o modelo 'turbo' para todas as transcrições
- 📝 **Parâmetro \`model\` ignorado**: Passar \`model="qualquer_coisa"\` nos métodos ou em \`TranscriptionOptions\` será silenciosamente ignorado
- ⚡ **Chunks aumentados**: Tamanho padrão de chunks aumentado de 4800 bytes (~150ms) para 800000 bytes (~25s) para melhor performance
- 🔄 **Reconexão aprimorada**: Melhor detecção de conexões WebSocket fechadas pelo servidor

### Adicionado
- 📋 Nota em \`list_models()\` indicando que é apenas informativo
- 🛡️ Override forçado para 'turbo' em \`http_client.py\` e \`websocket_stream.py\`
- 📚 Documentação atualizada refletindo modelo único

### Guia de Migração

#### Antes (v1.x.x)
\`\`\`python
from talklabs_stt import STTClient, TranscriptionOptions

client = STTClient(api_key="tlk_live_xxxxx")

# Modelo era respeitado
result = client.transcribe_file("audio.wav", model="large-v3")  # Usava large-v3

# Options com modelo específico
options = TranscriptionOptions(
    model="medium",
    language="pt"
)
result = client.transcribe_file("audio.wav", options=options)  # Usava medium
\`\`\`

#### Depois (v2.0.0)
\`\`\`python
from talklabs_stt import STTClient, TranscriptionOptions

client = STTClient(api_key="tlk_live_xxxxx")

# Modelo é ignorado - sempre usa 'turbo'
result = client.transcribe_file("audio.wav", model="large-v3")  # Usa turbo
result = client.transcribe_file("audio.wav")  # Também usa turbo

# Options - modelo é ignorado
options = TranscriptionOptions(
    language="pt",  # ✅ Recomendado: não especificar model
    punctuate=True
)
result = client.transcribe_file("audio.wav", options=options)  # Usa turbo

# Forma recomendada (sem especificar model)
result = client.transcribe_file(
    "audio.wav",
    language="pt",
    punctuate=True
)
\`\`\`

### Ação Requerida

1. **Remova parâmetro \`model\`** de suas chamadas (opcional, mas recomendado para clareza)
2. **Teste suas transcrições** - o modelo 'turbo' pode ter resultados ligeiramente diferentes
3. **Atualize documentação** do seu projeto se menciona seleção de modelos

### Por que esta mudança?

- ✅ **Simplicidade**: Um modelo único elimina complexidade
- ✅ **Consistência**: Garante mesma qualidade para todos os usuários
- ✅ **Performance**: Modelo 'turbo' otimizado para velocidade e precisão
- ✅ **Manutenção**: Reduz superfície de testes e possíveis bugs

---

## [1.0.4] - 2025-11-12

### Adicionado
- 🔄 Reconexão automática de WebSocket quando conexão é fechada pelo servidor
- 🔍 Melhor detecção de estado de conexão WebSocket

### Corrigido
- 🐛 Erro ao tentar reutilizar conexão WebSocket fechada
- ⚡ Chunks padrão ainda em 4800 bytes nesta versão

---

## [2.0.0] - 2025-11-10

### Adicionado
- 📝 Documentação melhorada
- ✅ Testes adicionais

### Corrigido
- 🐛 Pequenos bugs de validação

---

## [1.0.0] - 2025-11-01

### Adicionado
- 🎉 Release inicial do TalkLabs STT SDK
- ✅ REST API para transcrição completa
- ✅ WebSocket Streaming para tempo real
- ✅ Compatibilidade com Deepgram
- ✅ Suporte a múltiplos modelos (large-v3, medium, small, turbo)
- ✅ Type hints completos
- ✅ Documentação completa

---

## Tipos de Mudanças

- \`Adicionado\` para novas funcionalidades
- \`Alterado\` para mudanças em funcionalidades existentes
- \`Depreciado\` para funcionalidades que serão removidas
- \`Removido\` para funcionalidades removidas
- \`Corrigido\` para correção de bugs
- \`Segurança\` para vulnerabilidades corrigidas
