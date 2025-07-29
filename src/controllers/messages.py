import uuid
from datetime import datetime
from fastapi import BackgroundTasks
from models.schemas import WtsWebhookData, Message
from config import get_supabase_manager, get_rag_system, get_external_api

async def process_message(incoming_message: Message, conversation_id):
    """Processa mensagem em background"""
    print(f"🔄 Iniciando processamento em background para {incoming_message.sender}")
    
    # Obter instâncias
    supabase_manager = get_supabase_manager()
    rag_system = get_rag_system()
    external_api = get_external_api()

    log_prefix = incoming_message.sender
    
    # 1. Buscar histórico
    try:
        print(f"{log_prefix} - Recuperando histórico de conversa...", end="")
        history = await supabase_manager.get_conversation_history(conversation_id)
        print('OK')
    except Exception as e:
        print(f"Erro no processamento em background: {e}")
        return
    
    # 2. Recuperar contexto
    try:
        print(f"{log_prefix} - Recuperando contexto...", end="")
        context = await rag_system.retrieve_context(incoming_message.content, history)
        print("OK")
    except Exception as e:
        print(f"Erro ao recuperar contexto: {e}")
        return
    
    # 3. Gerar resposta
    try:
        print(f"{log_prefix} - Gerando resposta...", end="")
        generated_response = await rag_system.generate_response(incoming_message.content, context, history)
        print('OK')
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return

    # 5. Salvar resposta
    try:
        outgoing_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=incoming_message.conversation_id,
            platform="whatsapp",
            sender=incoming_message.receiver,  # O bot envia para quem recebeu
            receiver=incoming_message.sender,  # O bot responde para quem enviou
            content=generated_response,
            direction="outgoing",
            message_type="text"
            )
            
        print(f"{log_prefix} - Salvando resposta...", end="")
        await supabase_manager.save_message(outgoing_message)

        print("OK")
    except Exception as e:
        print(f"Erro ao salvar resposta: {e}")
        return

    # 6. Enviar resposta
    try:
        print(f"{log_prefix} - Enviando resposta...", end="")
        await external_api.send_message(outgoing_message)        
        print('OK')
        
    except Exception as e:
        print(f"Erro ao enviar resposta: {e}")
        return

async def receive_webhook(webhook_data: WtsWebhookData, background_tasks: BackgroundTasks):
    print("🚀 Iniciando processamento do webhook...")
    # Obter instâncias
    supabase_manager = get_supabase_manager()
    try:
        if webhook_data.channel.platform.lower() == "whatsapp":
            print(f"📱 Processando mensagem WhatsApp")
            print(f"👤 Sender: {webhook_data.contact.phonenumber}")
            print(f"📞 Receiver: {webhook_data.channel.key}")
            print(f"💬 Content: {webhook_data.lastContactMessage}")
            
            # Limpar o número de telefone
            contact_phone = webhook_data.contact.phonenumber.replace("+55|", "").replace("+55", "")
            
            incoming_message = Message(
                id=webhook_data.lastMessage.id,
                conversation_id="",  # Será definido depois
                platform="whatsapp",
                sender=contact_phone,
                receiver=webhook_data.channel.key,
                content=webhook_data.lastContactMessage,
                message_type="text",
                direction="incoming"
            )

            print(f"✅ Message criada com sucesso")
            conversation_id = await supabase_manager.get_or_create_conversation(contact_phone)
            
            # 2. Atualizar conversation_id na mensagem
            incoming_message.conversation_id = conversation_id
            
            # 3. Salvar mensagem recebida
            await supabase_manager.save_message(incoming_message)

    except Exception as e:
        print(f"❌ Erro ao buscar ou criar conversa: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": f"Erro ao buscar ou criar conversa: {str(e)}"}

    try:
        print("🔄 Adicionando tarefa em background...")
        background_tasks.add_task(process_message, incoming_message, conversation_id)
        print("✅ Tarefa adicionada com sucesso")
        return {"status": "success", "message": "Mensagem adicionada para processamento em background"}

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return {"status": "error", "message": f"Erro ao processar mensagem: {str(e)}"}