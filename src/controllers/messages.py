from datetime import datetime
from fastapi import BackgroundTasks
from models.schemas import WtsWebhookData, Message
from config import get_supabase_manager, get_rag_system, get_external_api

async def process_message(incoming_message: Message, conversation_id):
    """Processa mensagem em background"""
    # Obter instâncias
    supabase_manager = get_supabase_manager()
    rag_system = get_rag_system()
    external_api = get_external_api()

    log_prefix = incoming_message.from_number
    
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
            conversation_id=incoming_message.conversation_id,
            plataform="whatsapp",
            sender=incoming_message.to_number,
            receiver=incoming_message.from_number,
            content=generated_response,
            direction="outgoing"
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
    # Obter instâncias
    supabase_manager = get_supabase_manager()
    try:
        if webhook_data.channel.platform == "whatsapp":
            incoming_message = Message(
                id=webhook_data.lastMessage.id,
                sender=webhook_data.contact.phonenumber,
                receiver=webhook_data.channel.number,
                content=webhook_data.lastContactMessage,
            )

            conversation_id = await supabase_manager.get_or_create_conversation(incoming_message.sender)
            
            # 2. Salvar mensagem recebida
            await supabase_manager.save_message(incoming_message)

    except Exception as e:
        print(f"Erro ao buscar ou criar conversa: {e}")
        return {"status": "error", "message": f"Erro ao buscar ou criar conversa: {str(e)}"}

    try:
        background_tasks.add_task(process_message, incoming_message, conversation_id)
        return {"status": "success", "message": "Mensagem adicionada para processamento em background"}

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return {"status": "error", "message": f"Erro ao processar mensagem: {str(e)}"}