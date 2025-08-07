# Script para Adicionar Conhecimento na Base RAG

Este script permite adicionar textos na base de conhecimento do sistema RAG local através da API.

## 📋 Pré-requisitos

1. **Servidor RAG rodando**: Certifique-se de que o servidor local está funcionando na porta 8000
2. **Dependências Python**: O script usa apenas bibliotecas padrão (`requests`, `json`, `typing`, `datetime`)

## 🚀 Como Usar

### Opção 1: Executar diretamente no terminal

```bash
python add_knowledge_script.py
```

### Opção 2: Usar no Jupyter Notebook

1. Abra o Jupyter Notebook
2. Execute o script:
   ```python
   %run add_knowledge_script.py
   ```
3. Use as funções disponíveis

### Opção 3: Importar e usar as funções

```python
# Importar o script
exec(open('add_knowledge_script.py').read())

# Usar as funções
add_knowledge(['Seu texto aqui'], 'fonte_personalizada')
```

## 🔧 Funções Disponíveis

### 1. `test_connection()`
Testa a conexão com o servidor RAG.

```python
test_connection()
```

### 2. `add_knowledge(documents, source)`
Adiciona documentos à base de conhecimento.

**Parâmetros:**
- `documents`: Lista de strings com os textos
- `source`: String identificando a fonte (padrão: "jupyter_notebook")

**Exemplo:**
```python
# Adicionar um texto
add_knowledge(['Python é uma linguagem de programação...'], 'exemplo_python')

# Adicionar múltiplos textos
textos = ['Texto 1', 'Texto 2', 'Texto 3']
add_knowledge(textos, 'múltiplos_textos')
```

### 3. `add_knowledge_from_file(file_path, source)`
Carrega texto de um arquivo e adiciona à base de conhecimento.

**Parâmetros:**
- `file_path`: Caminho para o arquivo
- `source`: Fonte dos documentos (padrão: "arquivo")

**Exemplo:**
```python
add_knowledge_from_file('documento.txt', 'documento_externo')
```

### 4. `split_long_text(text, max_length)`
Divide um texto longo em partes menores.

**Parâmetros:**
- `text`: Texto para dividir
- `max_length`: Tamanho máximo de cada parte (padrão: 1000)

**Exemplo:**
```python
texto_longo = "Texto muito longo..."
partes = split_long_text(texto_longo, max_length=500)
add_knowledge(partes, 'texto_dividido')
```

### 5. `check_services_status()`
Verifica o status de todos os serviços (Supabase, Qdrant, Ollama, etc.).

```python
check_services_status()
```

## 📝 Exemplos Práticos

### Exemplo 1: Adicionar conhecimento sobre Python

```python
texto_python = """
Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. 
Foi criada por Guido van Rossum e lançada em 1991. Python é conhecida por sua sintaxe 
simples e legível, que enfatiza a legibilidade do código.
"""

resultado = add_knowledge([texto_python], "documentacao_python")
print(f"Resultado: {resultado}")
```

### Exemplo 2: Adicionar múltiplos tópicos

```python
textos = [
    "FastAPI é um framework web moderno para Python.",
    "Machine Learning é um subcampo da inteligência artificial.",
    "Docker é uma plataforma para containers."
]

resultado = add_knowledge(textos, "conceitos_tech")
```

### Exemplo 3: Carregar de arquivo

```python
# Se você tem um arquivo de texto
resultado = add_knowledge_from_file("meu_documento.txt", "documento_manual")
```

### Exemplo 4: Dividir texto longo

```python
texto_longo = """
Este é um texto muito longo que precisa ser dividido em partes menores.
Cada parte será processada separadamente pelo sistema RAG.
Isso melhora a performance e a organização das informações.
"""

partes = split_long_text(texto_longo, max_length=200)
resultado = add_knowledge(partes, "texto_processado")
```

## 🔍 Verificação de Status

Antes de adicionar conhecimento, é recomendado verificar se todos os serviços estão funcionando:

```python
# Verificar conexão básica
test_connection()

# Verificar status detalhado de todos os serviços
check_services_status()
```

## ⚙️ Configuração

### Alterar URL do servidor

Se seu servidor não estiver rodando na porta 8000, edite a variável `BASE_URL` no script:

```python
BASE_URL = "http://localhost:8000"  # Altere conforme necessário
```

### Exemplos de URLs:
- `http://localhost:8000` (padrão)
- `http://127.0.0.1:8000`
- `http://seu-servidor:8000`

## 🐛 Solução de Problemas

### Erro de conexão
```
❌ Erro ao conectar: Connection refused
```
**Solução:** Verifique se o servidor RAG está rodando.

### Erro 404
```
❌ Erro: 404
```
**Solução:** Verifique se a URL está correta e se o endpoint `/knowledge` existe.

### Erro 500
```
❌ Erro: 500
```
**Solução:** Verifique os logs do servidor para mais detalhes sobre o erro.

### Arquivo não encontrado
```
❌ Arquivo não encontrado: documento.txt
```
**Solução:** Verifique se o caminho do arquivo está correto.

## 📊 Monitoramento

O script fornece feedback detalhado sobre:
- ✅ Status de conexão
- 📤 Documentos enviados
- 📋 Fonte dos documentos
- ✅ Documentos adicionados com sucesso
- ❌ Erros encontrados

## 🔄 Fluxo de Trabalho Recomendado

1. **Verificar conexão**: `test_connection()`
2. **Verificar serviços**: `check_services_status()`
3. **Preparar textos**: Organize os textos que deseja adicionar
4. **Adicionar conhecimento**: Use `add_knowledge()` ou `add_knowledge_from_file()`
5. **Verificar resultado**: Confirme se os documentos foram adicionados

## 📚 Estrutura da API

O script usa a rota `/knowledge` do servidor RAG:

```python
POST /knowledge
{
    "documents": ["texto1", "texto2", "texto3"],
    "source": "fonte_personalizada"
}
```

**Resposta de sucesso:**
```json
{
    "status": "success",
    "added": 3
}
```

## 🤝 Contribuição

Para melhorar este script:
1. Adicione novas funcionalidades
2. Melhore o tratamento de erros
3. Adicione validações
4. Documente novas funções

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o servidor está rodando
2. Confirme se a URL está correta
3. Verifique os logs do servidor
4. Teste a API diretamente com curl ou Postman 