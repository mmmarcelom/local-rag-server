from fastapi import BackgroundTasks
from models.schemas import IncomingMessage
from config import get_supabase_manager, get_rag_system, get_external_api

async def process_message(message: IncomingMessage, conversation_id):
    """Processa mensagem em background"""
    # Obter instâncias
    supabase_manager = get_supabase_manager()
    rag_system = get_rag_system()
    external_api = get_external_api()
    
    # 1. Buscar histórico
    try:
        print(f"{message.phone_number} - Recuperando histórico de conversa...", end="")
        history = await supabase_manager.get_conversation_history(conversation_id)
        print('OK')
    except Exception as e:
        print(f"Erro no processamento em background: {e}")
        return
    
    # 2. Recuperar contexto
    try:
        print(f"{message.phone_number} - Recuperando contexto...", end="")
        context = await rag_system.retrieve_context(message.message, history)
        print("OK")
    except Exception as e:
        print(f"Erro ao recuperar contexto: {e}")
        return
    
    # 3. Gerar resposta
    try:
        print(f"{message.phone_number} - Gerando resposta...", end="")
        resposta = await rag_system.generate_response(message.message, context, history)
        print('OK')
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return

    # 5. Salvar resposta
    try:
        print(f"{message.phone_number} - Salvando resposta...", end="")
        await supabase_manager.save_message(conversation_id, message.phone_number, resposta, "outgoing")
        print("OK")
    except Exception as e:
        print(f"Erro ao salvar resposta: {e}")
        return

    # 6. Enviar resposta
    try:
        print(f"{message.phone_number} - Enviando resposta...", end="")
        await external_api.send_message(message.phone_number, resposta)        
        print('OK')
        
    except Exception as e:
        print(f"Erro ao enviar resposta: {e}")
        return

async def receive_message(messageData: IncomingMessage, background_tasks: BackgroundTasks):
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