from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set, Any
from datetime import timezone

@dataclass
class ProcessingTask:
    phone_number: str
    message: str
    message_id: str
    user_name: Optional[str]
    timestamp: datetime
    conversation_id: Optional[str] = None 

async def process_message_async(
    task: ProcessingTask,
    rag_system: Any,
    supabase_manager: Any,
    external_api: Any,
    processing_users: Set[str]
):
    """Processa mensagem de forma assíncrona"""
    phone_number = task.phone_number
    
    # Evitar processamento duplo do mesmo usuário
    if phone_number in processing_users:
        print(f"Usuário {phone_number} já está sendo processado")
        return
    
    processing_users.add(phone_number)
    
    try:
        print(f"Processando mensagem de {phone_number}: {task.message}")
        
        # 1. Obter ou criar conversa
        conversation_id = await supabase_manager.get_or_create_conversation(phone_number, task.user_name)
        
        # 2. Salvar mensagem recebida
        await supabase_manager.save_message(
            conversation_id=conversation_id,
            phone_number=phone_number,
            message=task.message,
            message_type="incoming",
            message_id=task.message_id
        )
        
        # 3. Recuperar histórico da conversa
        conversation_history = await supabase_manager.get_conversation_history(conversation_id)
        
        # 4. Recuperar contexto relevante do RAG e gerar resposta com IA
        context = await rag_system.retrieve_context(task.message, conversation_history)
        response = await rag_system.generate_response(task.message, context, conversation_history)
        
        # 5. Enviar resposta via API externa
        success = await external_api.send_message(phone_number=phone_number, message=response, metadata={"conversation_id": conversation_id})
        
        if success:
            # 6. Salvar resposta enviada
            await supabase_manager.save_message(
                conversation_id=conversation_id,
                phone_number=phone_number,
                message=response,
                message_type="outgoing"
            )
            
            # 7. Atualizar conversa
            await supabase_manager.update_conversation(
                conversation_id, 
                {"last_message_at": datetime.now(timezone.utc).isoformat()}
            )
            
            print(f"Resposta enviada e salva para {phone_number}")
        else:
            print(f"Falha ao enviar resposta para {phone_number}")
            
    except Exception as e:
        print(f"Erro no processamento da mensagem de {phone_number}: {e}")
    
    finally:
        # Remover usuário da lista de processamento
        processing_users.discard(phone_number) 