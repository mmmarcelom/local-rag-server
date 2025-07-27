from fastapi import BackgroundTasks
from models.schemas import IncomingMessage, OutgoingMessage, WtsWebhookMessage, convert_wts_webhook_to_incoming_message
from config import get_supabase_manager, get_rag_system, get_external_api

async def process_message(message: IncomingMessage, conversation_id):
    """Processa mensagem em background"""
    # Obter instâncias
    supabase_manager = get_supabase_manager()
    rag_system = get_rag_system()
    external_api = get_external_api()
    
    # 1. Buscar histórico
    try:
        print("Recuperando histórico de conversa...", end="")
        history = await supabase_manager.get_conversation_history(conversation_id)
        print('OK')
    except Exception as e:
        print(f"Erro no processamento em background: {e}")
        return
    
    # 2. Recuperar contexto
    try:
        print("Recuperando contexto...", end="")
        context = await rag_system.retrieve_context(message.message, history)
        print("OK")
    except Exception as e:
        print(f"Erro ao recuperar contexto: {e}")
        return
    
    # 3. Gerar resposta
    try:
        print('Gerando resposta...', end="")
        resposta = await rag_system.generate_response(message.message, context, history)
        print('OK')
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return

    # 5. Salvar resposta
    try:
        print("Salvando resposta...", end="")
        await supabase_manager.save_message(conversation_id, message.phone_number, resposta, "outgoing")
        print("OK")
    except Exception as e:
        print(f"Erro ao salvar resposta: {e}")
        return

    # 6. Enviar resposta
    try:
        print(f"Enviando resposta...", end="")
        await external_api.send_message(message.phone_number, resposta)        
        print('OK')
        
    except Exception as e:
        print(f"Erro ao enviar resposta: {e}")
        return

async def receive_message(messageData: IncomingMessage, background_tasks: BackgroundTasks):
    print('mensagem recebida')

    # Obter instâncias
    supabase_manager = get_supabase_manager()

    try:
        # 1. Buscar ou criar conversa
        conversation_id = await supabase_manager.get_or_create_conversation(
            messageData.phone_number, 
            messageData.user_name
        )

        # 2. Salvar mensagem recebida
        await supabase_manager.save_message(
            conversation_id, 
            messageData.phone_number, 
            messageData.message, 
            "incoming", 
            messageData.message_id
        )

        # 3. Adicionar processamento em background
        background_tasks.add_task(process_message, messageData, conversation_id)
        return {"status": "success", "message": "Mensagem adicionada para processamento em background"}

    except ConnectionError as e:
        # Processar mensagem sem salvar no Supabase
        print(f"Erro de conexão com Supabase: {e}")
        background_tasks.add_task(process_message, messageData, "temp_conversation")
        return {"status": "warning", "message": "Mensagem processada sem persistência no Supabase"}
        
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return {"status": "error", "message": f"Erro ao processar mensagem: {str(e)}"}

async def receive_wts_webhook(webhook_data: WtsWebhookMessage, background_tasks: BackgroundTasks):
    """Recebe webhook do WTS e processa a mensagem"""
    print('Webhook do WTS recebido')
    
    # Verificar se é uma mensagem recebida
    if webhook_data.eventType != "MESSAGE_RECEIVED":
        return {"status": "ignored", "message": f"Evento ignorado: {webhook_data.eventType}"}
    
    # Verificar se é uma mensagem de texto
    if webhook_data.content.type != "TEXT":
        return {"status": "ignored", "message": f"Tipo de mensagem ignorado: {webhook_data.content.type}"}
    
    # Verificar se é uma mensagem recebida (não enviada)
    if webhook_data.content.direction != "FROM_HUB":
        return {"status": "ignored", "message": f"Direção ignorada: {webhook_data.content.direction}"}
    
    # Converter webhook para formato interno
    try:
        message_data = convert_wts_webhook_to_incoming_message(webhook_data)
        print(f"Mensagem convertida: {message_data.phone_number} - {message_data.message}")
    except Exception as e:
        print(f"Erro ao converter webhook: {e}")
        return {"status": "error", "message": f"Erro ao converter webhook: {str(e)}"}
    
    # Processar mensagem usando a função existente
    return await receive_message(message_data, background_tasks)