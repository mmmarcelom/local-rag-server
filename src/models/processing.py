import uuid
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
        from models.schemas import Message
        incoming_message = Message(
            id=task.message_id,
            conversation_id=conversation_id,
            platform="whatsapp",
            sender=phone_number,
            receiver="bot",
            content=task.message,
            direction="incoming",
            message_type="text"
        )
        await supabase_manager.save_message(incoming_message)
        
        # 3. Recuperar histórico da conversa
        conversation_history = await supabase_manager.get_conversation_history(conversation_id)
        
        # 4. Recuperar contexto relevante do RAG e gerar resposta com IA
        context = await rag_system.retrieve_context(task.message, conversation_history)
        response = await rag_system.generate_response(task.message, context, conversation_history)
        
        # 5. Enviar resposta via API externa
        from models.schemas import Message
        response_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            platform="whatsapp",
            sender="bot",
            receiver=phone_number,
            content=response,
            direction="outgoing",
            message_type="text",
            metadata={"conversation_id": conversation_id}
        )
        success = await external_api.send_message(response_message)
        
        if success:
            # 6. Salvar resposta enviada
            outgoing_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                platform="whatsapp",
                sender="bot",
                receiver=phone_number,
                content=response,
                direction="outgoing",
                message_type="text"
            )
            await supabase_manager.save_message(outgoing_message)
            
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