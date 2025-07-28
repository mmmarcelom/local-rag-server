# Local RAG Server

Sistema de chatbot inteligente para WhatsApp com RAG (Retrieval-Augmented Generation) usando FastAPI, Supabase, Qdrant e Ollama.

## 🚀 Características

- **Chatbot WhatsApp**: Integração via WTS.chat API
- **RAG System**: Busca vetorial com Qdrant + embeddings
- **IA Local**: Ollama com modelos de linguagem
- **Banco de Dados**: Supabase (PostgreSQL)
- **Concorrência**: Background tasks + load balancing
- **Docker**: Containers isolados e escaláveis

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.11+
- 8GB+ RAM (recomendado)
- GPU (opcional, para aceleração)

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd local-rag-server
```

### 2. Configure as variáveis de ambiente
```bash
# Windows (CMD)
copy env.example .env

# Windows (PowerShell)
copy env.example .env

# Linux/Mac
cp env.example .env
```

### 3. Edite o arquivo .env
Configure as seguintes variáveis no arquivo `.env`:

```bash
# Configurações do WhatsApp API (WTS.chat) - OBRIGATÓRIO
WTS_API_TOKEN=your_wts_api_token_here

# Configurações do Supabase (OBRIGATÓRIO)
SUPABASE_PUBLIC_URL=your_supabase_url_here
ANON_KEY=your_supabase_anon_key_here

# As outras configurações já vêm com valores padrão para desenvolvimento
```

**⚠️ Importante**: Você precisa obter um token da API WTS.chat para que o WhatsApp funcione.

### 4. Escolha o modo de execução

#### **Modo Teste (1 Ollama - Recomendado para desenvolvimento)**
```bash
docker-compose --profile single-ollama up -d
```

#### **Modo Produção (3 Ollamas + Load Balancer)**
```bash
docker-compose --profile multi-ollama up -d
```

### 5. Verificar se tudo está funcionando
```bash
# Verificar status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f

# Acessar documentação da API
# http://localhost:8000/docs
```

## 🖥️ **Execução Local (sem Docker)**

### **1. Ativar ambiente virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### **2. Instalar dependências**
```bash
pip install -r requirements.txt
```

### **3. Executar servidor**
```bash
# Opção 1: Executar diretamente
python src/server.py

# Opção 2: Executar como módulo
python -m src.server
```

## 📁 Estrutura do Projeto

```
local-rag-server/
├── src/                    # Código fonte da aplicação
│   ├── controllers/        # Controladores da API
│   ├── models/            # Modelos e schemas
│   ├── services/          # Serviços (RAG, Supabase, etc.)
│   ├── routes.py          # Rotas da API
│   └── server.py          # Servidor FastAPI
├── docker-compose.yml     # Orquestração de containers
├── Dockerfile            # Container da aplicação
├── requirements.txt      # Dependências Python
└── README.md            # Documentação
```

## 🏗️ Arquitetura

### **Modo Teste:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Qdrant    │    │   Redis     │    │  Supabase   │
│  (Vetores)  │    │   (Cache)   │    │ (PostgreSQL)│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
              ┌─────────────┐    ┌─────────────┐
              │   Ollama    │    │   FastAPI   │
              │   (IA)      │    │  (Server)   │
              └─────────────┘    └─────────────┘
```

### **Modo Produção:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Ollama-1  │    │   Ollama-2  │    │   Ollama-3  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
              ┌─────────────┐    ┌─────────────┐
              │   Nginx     │    │   FastAPI   │
              │ (Load Bal.) │    │  (Server)   │
              └─────────────┘    └─────────────┘
```

## 📡 Endpoints da API

### **Receber Mensagem**
```http
POST /message
Content-Type: application/json

{
  "phone_number": "5511999999999",
  "message": "Olá, como posso ajudar?",
  "message_id": "msg_123",
  "user_name": "João Silva"
}
```

### **Buscar Conversa**
```http
GET /conversation/{phone_number}
```

### **Adicionar Conhecimento**
```http
POST /knowledge
Content-Type: application/json

{
  "documents": ["Texto do documento 1", "Texto do documento 2"],
  "source": "manual"
}
```

## 🎯 Comandos Úteis

### **Inicialização**
```bash
# Modo teste (1 Ollama)
docker-compose --profile single-ollama up -d

# Modo produção (3 Ollamas)
docker-compose --profile multi-ollama up -d

# Parar todos os serviços
docker-compose down

# Verificar status
docker-compose ps
```

### **Build**
```bash
# Build completo
docker-compose build --parallel

# Build individual
docker-compose build server-test

# Build limpo
docker-compose build --no-cache
```

### **Monitoramento**
```bash
# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f

# Ver logs de serviço específico
docker-compose logs -f server-test
docker-compose logs -f ollama

# Teste de carga
python monitor_load.py

# Verificar uso de recursos
docker stats
```

### **Manutenção**
```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Limpar Docker
docker system prune -a

# Limpar imagens não utilizadas
docker image prune -a

# Verificar espaço em disco
docker system df
```

## 🔧 Configuração

### **Variáveis de Ambiente (.env)**
```bash
# Supabase (OBRIGATÓRIO)
SUPABASE_PUBLIC_URL=your_supabase_url
ANON_KEY=your_supabase_key

# WhatsApp API (OBRIGATÓRIO)
WTS_API_TOKEN=your_wts_token

# Ollama
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=ollama  # ou nginx para produção
OLLAMA_PORT=11434   # ou 80 para produção

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### **Portas Utilizadas**
- **8000**: FastAPI Server
- **6333**: Qdrant (Vetores)
- **6379**: Redis (Cache)
- **54322**: Supabase (PostgreSQL)
- **11434-11436**: Ollama Instances
- **11437**: Nginx Load Balancer

## 🧪 Testes

### **Teste de Saúde**
```bash
# Verificar se todos os serviços estão rodando
curl http://localhost:8000/docs
curl http://localhost:6333/collections
curl http://localhost:11434/api/tags

# Verificar status dos containers
docker-compose ps

# Verificar logs de inicialização
docker-compose logs --tail=50

# Teste completo de todos os serviços (script local)
python test_all_services.py

# Teste via API (retorna JSON detalhado)
curl http://localhost:8000/test-services
```

### **Teste de Carga**
```bash
# Executar teste de performance
python monitor_load.py
```

### **Teste Assíncrono de Serviços**
```bash
# Teste completo com análise detalhada
python test_all_services.py

# Teste via API (JSON response)
curl http://localhost:8000/test-services

# Teste de health check básico
curl http://localhost:8000/health
```

**Exemplo de resposta do teste assíncrono:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "overall_status": "healthy",
  "services": {
    "supabase": {
      "status": "success",
      "message": "Serviço funcionando",
      "success": true
    },
    "qdrant": {
      "status": "success", 
      "message": "Serviço funcionando",
      "success": true
    },
    "ollama": {
      "status": "success",
      "message": "Serviço funcionando", 
      "success": true
    },
    "wts_api": {
      "status": "success",
      "message": "Serviço funcionando",
      "success": true
    }
  },
  "summary": {
    "total_services": 4,
    "successful_services": 4,
    "failed_services": 0
  }
}
```

## 📊 Performance

### **Modo Teste:**
- **Build Time**: ~5 minutos
- **RAM**: ~4GB
- **Concorrência**: Baixa

### **Modo Produção:**
- **Build Time**: ~15 minutos
- **RAM**: ~8GB
- **Concorrência**: Alta (3x Ollamas)

## 🐛 Troubleshooting

### **Build Lento**
```bash
# Windows (CMD)
set DOCKER_BUILDKIT=1
docker-compose build --parallel

# Linux/Mac
export DOCKER_BUILDKIT=1
docker-compose build --parallel
```

### **Erro de Conectividade**
```bash
# Verificar se todos os containers estão rodando
docker-compose ps

# Verificar logs
docker-compose logs -f

# Verificar logs de erro específicos
docker-compose logs server-test
```

### **Problemas de Memória**
```bash
# Usar modo teste (menos RAM)
docker-compose --profile single-ollama up -d

# Verificar uso de memória
docker stats
```

### **Reconstruir Containers**
```bash
# Reconstruir sem cache
docker-compose build --no-cache

# Reconstruir e iniciar
docker-compose build --no-cache && docker-compose --profile single-ollama up -d
```

## 📋 Checklist de Inicialização

- [ ] Docker instalado e funcionando
- [ ] Arquivo `.env` criado e configurado
- [ ] Token WTS.chat configurado no `.env`
- [ ] Configurações do Supabase configuradas no `.env`
- [ ] Containers iniciados com sucesso (`docker-compose ps`)
- [ ] API acessível em http://localhost:8000/docs
- [ ] Qdrant acessível em http://localhost:6333/collections
- [ ] Ollama acessível em http://localhost:11434/api/tags
- [ ] Logs sem erros críticos (`docker-compose logs`)

## ⚠️ Pré-requisitos Importantes

1. **Docker e Docker Compose** instalados e funcionando
2. **8GB+ RAM** (recomendado para modo produção)
3. **Token da API WTS.chat** para integração WhatsApp
4. **Conexão com internet** para download das imagens Docker

## 📝 Logs

### **Localização dos Logs**
- **Dados**: `./volumes/`
- **Logs Docker**: `docker-compose logs`
- **Logs Aplicação**: Console do container

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ para chatbots inteligentes** 