from services.rag_system import RAGSystem
from services.supabase_manager import SupabaseManager
from services.wts_api import WtsAPIService
from fastapi import BackgroundTasks

supabase_manager = SupabaseManager()
rag_system = RAGSystem()
external_api = WtsAPIService()

async def process_message_background(message, conversation_id):
    """Processa mensagem em background"""
    try:
        # 3. Buscar histórico
        history = await supabase_manager.get_conversation_history(conversation_id)
        print('history: \n', '\n'.join([msg['message'] for msg in history]))

        # 4. Recuperar contexto
        context = await rag_system.retrieve_context(message.message, history)
        print('context:', context)

        # 5. Gerar resposta
        resposta = await rag_system.generate_response(message.message, context, history)
        print('resposta:', resposta)

        # 6. Salvar resposta
        await supabase_manager.save_message(conversation_id, message.phone_number, resposta, "outgoing")

        # 7. Enviar resposta via API externa
        await external_api.send_message(message.phone_number, resposta)
        
        print(f"Resposta enviada para {message.phone_number}")
        
    except Exception as e:
        print(f"Erro no processamento em background: {e}")

async def receive_message(message, background_tasks: BackgroundTasks):
    print('mensagem recebida', message.json())

    phone_number = message.phone_number
    user_name = message.user_name
    message_id = message.message_id

    # 1. Buscar ou criar conversa
    conversation_id = await supabase_manager.get_or_create_conversation(phone_number, user_name)

    # 2. Salvar mensagem recebida
    await supabase_manager.save_message(conversation_id, phone_number, message.message, "incoming", message_id)

    # 3. Adicionar processamento em background
    background_tasks.add_task(process_message_background, message, conversation_id)

    return {"status": "success", "message": "Mensagem adicionada para processamento em background"}

async def get_conversation(phone_number: str):
    """Recupera histórico de conversa por número de telefone"""
    try:
        # Buscar conversa
        result = supabase_manager.supabase.table("conversations").select("*").eq("phone_number", phone_number).order("created_at", desc=True).limit(1).execute()
        
        if not result.data:
            return {"conversation": None, "messages": []}
        
        conversation = result.data[0]
        messages = await supabase_manager.get_conversation_history(conversation["id"], limit=50)
        
        return {
            "conversation": conversation,
            "messages": messages
        }
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))