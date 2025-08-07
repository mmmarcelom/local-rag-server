# Scripts para Limpar Dados do Qdrant

Este documento explica como usar os scripts para limpar dados da base de conhecimento do Qdrant.

## 🗑️ Problema Resolvido

O erro `Unsupported points selector type: <class 'dict'>` ocorria porque a sintaxe `{"all": True}` não é suportada pelo Qdrant. Os scripts foram corrigidos para usar métodos alternativos.

## 📁 Arquivos Disponíveis

### 1. `clear_qdrant_fixed.py`
Script standalone com funções corrigidas para limpar o Qdrant.

### 2. `clear_qdrant_script.py`
Script completo com múltiplas opções de limpeza.

### 3. Rota API `/knowledge` (DELETE)
Endpoint da API para limpar dados via HTTP.

## 🚀 Como Usar

### Opção 1: Script Corrigido (Recomendado)

```python
# No Jupyter notebook
%run clear_qdrant_fixed.py

# Ou importar as funções
from clear_qdrant_fixed import clear_qdrant_simple
clear_qdrant_simple()
```

### Opção 2: Via API

```python
import requests

# Limpar via API
response = requests.delete("http://localhost:8000/knowledge")
if response.status_code == 200:
    print("✅ Base limpa com sucesso!")
```

### Opção 3: Script Completo

```bash
python clear_qdrant_script.py
```

## 🔧 Funções Disponíveis

### `clear_qdrant_simple()`
**Recomendado** - Versão simplificada que deleta e recria a coleção.

```python
from clear_qdrant_fixed import clear_qdrant_simple

# Limpar com configurações padrão
clear_qdrant_simple()

# Limpar com configurações personalizadas
clear_qdrant_simple(
    host="localhost",
    port=6333,
    collection_name="knowledge_base"
)
```

### `clear_qdrant()`
Versão avançada com múltiplos métodos de limpeza.

```python
from clear_qdrant_fixed import clear_qdrant

# Tentar limpeza com diferentes métodos
clear_qdrant()
```

## 📊 O que Cada Função Faz

### `clear_qdrant_simple()`
1. **Conecta** ao Qdrant
2. **Verifica** se a coleção existe
3. **Deleta** a coleção existente
4. **Recria** a coleção vazia
5. **Confirma** sucesso

### `clear_qdrant()`
1. **Conecta** ao Qdrant
2. **Verifica** informações da coleção
3. **Tenta** deletar pontos com `PointIdsList(points=[])`
4. **Se falhar**, deleta e recria a coleção
5. **Confirma** sucesso

## ⚙️ Configurações

### Host e Porta
- **Padrão**: `localhost:6333`
- **Docker**: `qdrant:6333` (se rodando em container)

### Nome da Coleção
- **Padrão**: `knowledge_base`
- **Configurável**: via parâmetro `collection_name`

## 🔍 Verificação

Após limpar, você pode verificar se funcionou:

```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
collection_info = client.get_collection("knowledge_base")
print(f"Pontos na coleção: {collection_info.points_count}")
# Deve retornar: Pontos na coleção: 0
```

## 🐛 Solução de Problemas

### Erro: "Biblioteca qdrant-client não encontrada"
```bash
pip install qdrant-client
```

### Erro: "Connection refused"
- Verifique se o Qdrant está rodando
- Confirme host e porta corretos

### Erro: "Collection not found"
- A coleção será criada automaticamente
- Não é um problema

## 📝 Exemplo Completo

```python
# Importar função
from clear_qdrant_fixed import clear_qdrant_simple

# Limpar Qdrant
print("🗑️ Iniciando limpeza do Qdrant...")
success = clear_qdrant_simple()

if success:
    print("✅ Qdrant limpo com sucesso!")
    
    # Verificar resultado
    from qdrant_client import QdrantClient
    client = QdrantClient(host="localhost", port=6333)
    collection_info = client.get_collection("knowledge_base")
    print(f"📊 Pontos na coleção: {collection_info.points_count}")
else:
    print("❌ Falha ao limpar Qdrant")
```

## 🔄 Fluxo de Trabalho Recomendado

1. **Verificar** se o Qdrant está rodando
2. **Executar** `clear_qdrant_simple()`
3. **Confirmar** que a coleção está vazia
4. **Adicionar** novos dados se necessário

## ⚠️ Avisos Importantes

- **Irreversível**: A limpeza não pode ser desfeita
- **Todos os dados**: Remove TODOS os documentos da base
- **Backup**: Faça backup se necessário antes de limpar

## 🎯 Casos de Uso

### Desenvolvimento
```python
# Limpar para testes
clear_qdrant_simple()
```

### Produção
```python
# Limpar com confirmação
if confirm_clear():
    clear_qdrant_simple()
```

### Debug
```python
# Verificar status antes de limpar
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)
collection_info = client.get_collection("knowledge_base")
print(f"Pontos antes: {collection_info.points_count}")
``` 