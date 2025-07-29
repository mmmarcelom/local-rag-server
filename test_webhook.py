#!/usr/bin/env python3
"""
Script para testar o webhook do WTS
"""

import json
from src.models.schemas import WtsWebhookData

# JSON recebido do webhook
webhook_data = {
    "responseKeys": [],
    "sessionId": "de72497e-21b5-46b1-830b-1d98d081816a",
    "session": {
        "id": "de72497e-21b5-46b1-830b-1d98d081816a",
        "createdAt": "2025-07-29T17:49:19.452982Z",
        "departmentId": "657716fb-9539-4e37-b261-b9e828229069",
        "userId": "00000000-0000-0000-0000-000000000000",
        "number": "2025072900001",
        "utm": None
    },
    "channel": {
        "id": "f85f93f1-c58a-4f88-a5d2-d4551ab9f07d",
        "key": "5582999939356",
        "platform": "WhatsApp",
        "displayName": "Instância 432129"
    },
    "contact": {
        "id": "bd492008-782e-4ea1-a4bc-2e0de5ca74ff",
        "name": "Marcelo",
        "first-name": "Marcelo",
        "phonenumber": "+55|82999464789",
        "display-phonenumber": "(82) 99946-4789",
        "email": "marcelo.mesquita@techstrategy.com.br",
        "instagram": None,
        "tags": None,
        "annotation": "",
        "metadata": {},
        "rg": "123456 SSP/SP",
        "cep": "12345123",
        "pa-s": "Brasil",
        "bairro": "Serraria",
        "cidade": "Maceio",
        "cpf-62": "12345678900",
        "estado": "AL",
        "profiss-o": "Empresário",
        "complemento": "Apto 101",
        "endere-o-53": "Rua exemplar, 55",
        "estado-civil": "Casado"
    },
    "questions": {},
    "menus": {},
    "templates": {},
    "metadata": {},
    "lastContactMessage": "Me fale sobre a hubnordeste",
    "lastMessage": {
        "id": "3350e716-fa4a-419c-a9c9-d1714c683136",
        "createdAt": "2025-07-29T17:49:50.281Z",
        "type": "TEXT",
        "text": "Me fale sobre a hubnordeste",
        "fileId": None,
        "file": None
    },
    "lastMessagesAggregated": {
        "text": "Me fale sobre a hubnordeste",
        "files": []
    }
}

def test_webhook():
    try:
        # Tentar criar o objeto WtsWebhookData
        webhook = WtsWebhookData(**webhook_data)
        print("✅ Webhook válido!")
        print(f"📱 Plataforma: {webhook.channel.platform}")
        print(f"👤 Contato: {webhook.contact.name}")
        print(f"📞 Telefone: {webhook.contact.phonenumber}")
        print(f"💬 Mensagem: {webhook.lastContactMessage}")
        return True
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

if __name__ == "__main__":
    test_webhook() 