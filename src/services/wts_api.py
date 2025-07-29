import httpx
import logging
from models.schemas import Message

logger = logging.getLogger(__name__)

class WtsAPIService:
    def __init__(self, token: str = None):
        self.api_url = 'https://api.wts.chat'
        self.api_token = token
        
        if not self.api_token:
            logger.error("WTS_API_TOKEN não encontrado nas variáveis de ambiente!")
            raise ValueError("WTS_API_TOKEN é obrigatório. Configure a variável de ambiente WTS_API_TOKEN.")
        
        self.headers = {
            "accept": "application/json",
            "content-type": "application/*+json",
            "Authorization": f"Bearer {self.api_token}"
        }
    
    async def test_connection(self) -> bool:
        """Testa a conexão com a API WTS"""
        try:
            logger.info("📱 Testando conexão com WTS API...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Testar se a API está respondendo
                url = f"{self.api_url}/core/v1/agent"
                response = await client.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    logger.error(f"❌ Erro ao testar WTS API: {response.status_code} - {response.text}")
                    return False

                agents = response.json()
                if len(agents) == 0:
                    logger.warning("⚠️ Nenhum agente encontrado na WTS API")
                    return False
                
                logger.info(f"✅ WTS API conectada! Agentes encontrados: {len(agents)}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com WTS API: {e}")
            return False
    
    async def send_message(self, message: Message) -> bool:
        try:
            logger.info(f"📤 Enviando mensagem via WTS API...")
            logger.info(f"📞 Para (original): {message.receiver}")
            logger.info(f"📞 De (original): {message.sender}")
            logger.info(f"💬 Conteúdo: {message.content}")
            
            # Formatar números de telefone para o formato esperado pela WTS API
            to_number = message.receiver
            from_number = message.sender
            
            # Se o número não tem o formato +55, adicionar
            if not to_number.startswith("+55"):
                to_number = f"+55{to_number}"
            if not from_number.startswith("+55"):
                from_number = f"+55{from_number}"
            
            payload = { 
                "body": {"text": message.content}, 
                "to": to_number,
                "from": from_number
            }
            
            logger.info(f"📞 Para (formatado): {to_number}")
            logger.info(f"📞 De (formatado): {from_number}")

            if message.metadata:
                payload["metadata"] = message.metadata

            logger.info(f"📦 Payload: {payload}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.api_url}/chat/v1/message/send"
                response = await client.post(url, json=payload, headers=self.headers)
                
            logger.info(f"📡 Response status: {response.status_code}")
            logger.info(f"📡 Response text: {response.text}")
                
            if response.status_code == 200:
                logger.info(f"✅ WTS: mensagem enviada com sucesso")
                return True
            else:
                logger.error(f"❌ WTS: erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ WTS: erro ao enviar mensagem: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return False