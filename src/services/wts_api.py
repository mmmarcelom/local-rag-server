import httpx
import logging

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
    
    async def send_message(self, phone_number: str, message: str, metadata: dict = None) -> bool:
        try:
            payload = { "body": {"text": message}, "to": phone_number }

            if metadata:
                payload["metadata"] = metadata

            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.api_url}/chat/v1/message/send"
                response = await client.post(url, json=payload, headers=self.headers)
            if response.status_code == 200:
                logger.info(f"Mensagem enviada para {phone_number}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False