# 🔗 Configuração do Webhook WTS

## 📋 Visão Geral

O sistema agora suporta webhooks do WTS.chat para receber mensagens automaticamente. Quando uma mensagem é recebida no WhatsApp, o WTS envia um POST request para nosso servidor com os dados da mensagem.

## 🚀 Configuração

### 1. Configurar Webhook no WTS

1. Acesse o painel do WTS.chat
2. Vá em **Configurações** > **Webhooks**
3. Adicione um novo webhook com:
   - **URL**: `http://seu-servidor:8000/webhook/wts`
   - **Eventos**: `MESSAGE_RECEIVED`
   - **Método**: `POST`

### 2. Verificar Configuração

O endpoint `/webhook/wts` está disponível em:
```
POST http://localhost:8000/webhook/wts
```

## 📊 Estrutura do Webhook

### Exemplo de Payload Recebido:

```json
{
    "eventType": "MESSAGE_RECEIVED",
    "date": "2025-07-27T23:46:00.1260435Z",
    "content": {
        "id": "facbd59c-5415-4c1c-a46c-26c4d4576863",
        "senderId": null,
        "createdAt": "2025-07-27T23:46:00.1040498Z",
        "updatedAt": "2025-07-27T23:46:00.1040498Z",
        "editedAt": null,
        "type": "TEXT",
        "active": true,
        "sessionId": "8917bc7b-ab53-4e1c-940d-1fbd309bdabd",
        "templateId": null,
        "userId": null,
        "timestamp": "2025-07-27T23:45:56Z",
        "text": "Então... me fale sobre pendrives",
        "direction": "FROM_HUB",
        "status": "DELIVERED",
        "origin": "GATEWAY",
        "readContactAt": null,
        "fileId": null,
        "refId": null,
        "waitingOptIn": false,
        "details": {
            "file": null,
            "location": null,
            "contact": null,
            "errors": null,
            "transcription": null
        }
    },
    "changeMetadata": null
}
```

### Campos Importantes:

| Campo | Descrição | Uso |
|-------|-----------|-----|
| `eventType` | Tipo do evento | Só processamos `"MESSAGE_RECEIVED"` |
| `content.type` | Tipo da mensagem | Só processamos `"TEXT"` |
| `content.direction` | Direção da mensagem | Só processamos `"FROM_HUB"` |
| `content.text` | Texto da mensagem | Usado para processamento RAG |
| `content.sessionId` | ID da sessão | Usado como `phone_number` |
| `content.id` | ID único da mensagem | Usado como `message_id` |
| `content.timestamp` | Timestamp da mensagem | Usado para logs |

## 🔄 Fluxo de Processamento

### 1. Recepção do Webhook
```
WTS → POST /webhook/wts → receive_wts_webhook()
```

### 2. Validação
- ✅ Verifica se `eventType == "MESSAGE_RECEIVED"`
- ✅ Verifica se `content.type == "TEXT"`
- ✅ Verifica se `content.direction == "FROM_HUB"`

### 3. Conversão
```python
webhook_data → convert_wts_webhook_to_incoming_message() → IncomingMessage
```

### 4. Processamento
- 🔍 Busca contexto no RAG
- 🤖 Gera resposta com Ollama
- 💾 Salva no Supabase
- 📤 Envia resposta via WTS API

## 🧪 Testando

### 1. Teste Local com curl:

```bash
curl -X POST http://localhost:8000/webhook/wts \
  -H "Content-Type: application/json" \
  -d @src/services/wts_sample.json
```

### 2. Verificar Logs:

```bash
# Ver logs do servidor
python src/server.py
```

### 3. Verificar Resposta:

```json
{
  "status": "success",
  "message": "Mensagem adicionada para processamento em background"
}
```

## ⚠️ Tratamento de Erros

### Eventos Ignorados:
- ❌ `eventType != "MESSAGE_RECEIVED"`
- ❌ `content.type != "TEXT"`
- ❌ `content.direction != "FROM_HUB"`

### Respostas de Erro:
```json
{
  "status": "ignored",
  "message": "Evento ignorado: MESSAGE_SENT"
}
```

## 🔧 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/webhook/wts` | POST | Recebe webhooks do WTS |
| `/message` | POST | Endpoint manual (formato antigo) |
| `/health` | GET | Health check do sistema |

## 📝 Notas Importantes

1. **Compatibilidade**: O sistema mantém compatibilidade com o endpoint `/message` antigo
2. **Background Processing**: Todas as mensagens são processadas em background
3. **Validação**: Apenas mensagens de texto recebidas são processadas
4. **Identificação**: Usa `sessionId` como identificador do usuário
5. **Logs**: Todas as operações são logadas para debug

## 🚀 Próximos Passos

1. Configure o webhook no WTS.chat
2. Teste com uma mensagem simples
3. Verifique os logs do servidor
4. Confirme que a resposta é enviada de volta 