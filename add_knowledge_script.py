#!/usr/bin/env python3
"""
Script para Adicionar Conhecimento na Base RAG
==============================================

Este script permite adicionar textos na base de conhecimento do sistema RAG local.
Pode ser executado diretamente ou importado no Jupyter notebook.

Uso:
    python add_knowledge_script.py
    # ou no Jupyter:
    %run add_knowledge_script.py
"""

import requests
import json
from typing import List
from datetime import datetime

# Configuração da API
BASE_URL = "http://localhost:8000"  # Ajuste conforme necessário

def test_connection():
    """Testa a conexão com o servidor"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor está funcionando!")
            print(f"Status: {response.json()['status']}")
            return True
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def add_knowledge(documents: List[str], source: str = "jupyter_notebook"):
    """
    Adiciona documentos à base de conhecimento
    
    Args:
        documents: Lista de textos para adicionar
        source: Fonte dos documentos (padrão: jupyter_notebook)
    """
    try:
        url = f"{BASE_URL}/knowledge"
        
        # A API espera documents como lista diretamente no corpo
        # e source como query parameter
        params = {"source": source}
        
        print(f"📤 Enviando {len(documents)} documento(s) para a base de conhecimento...")
        print(f"📋 Fonte: {source}")
        
        response = requests.post(url, json=documents, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! {result['added']} documento(s) adicionado(s)")
            return result
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao adicionar conhecimento: {e}")
        return None

def add_knowledge_from_file(file_path: str, source: str = "arquivo"):
    """
    Carrega texto de um arquivo e adiciona à base de conhecimento
    
    Args:
        file_path: Caminho para o arquivo
        source: Fonte dos documentos
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"📁 Carregando arquivo: {file_path}")
        print(f"📏 Tamanho: {len(content)} caracteres")
        
        return add_knowledge([content], source)
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return None

def split_long_text(text: str, max_length: int = 1000):
    """
    Divide um texto longo em partes menores
    
    Args:
        text: Texto para dividir
        max_length: Tamanho máximo de cada parte
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Dividir por parágrafos primeiro
    paragraphs = text.split("\n\n")
    
    for paragraph in paragraphs:
        if len(current_part) + len(paragraph) <= max_length:
            current_part += paragraph + "\n\n"
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = paragraph + "\n\n"
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def check_services_status():
    """Verifica o status de todos os serviços"""
    try:
        response = requests.get(f"{BASE_URL}/test-services")
        if response.status_code == 200:
            data = response.json()
            
            print(f"🔍 Status Geral: {data['overall_status']}")
            print(f"📊 Resumo: {data['summary']}")
            print("\n📋 Status dos Serviços:")
            
            for service, status in data['services'].items():
                emoji = "✅" if status['success'] else "❌"
                print(f"{emoji} {service}: {status['status']} - {status['message']}")
            
            return data
        else:
            print(f"❌ Erro ao verificar serviços: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao verificar serviços: {e}")
        return None

def exemplo_uso():
    """Exemplo de uso das funções"""
    print("🚀 Iniciando exemplo de uso...\n")
    
    # Teste de conexão
    print("1. Testando conexão com o servidor:")
    if not test_connection():
        print("❌ Não foi possível conectar ao servidor. Verifique se está rodando.")
        return
    
    print("\n2. Verificando status dos serviços:")
    check_services_status()
    
    print("\n3. Adicionando exemplo de conhecimento:")
    
    # Exemplo: Adicionar um texto sobre Python
    texto_python = """
    Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. 
    Foi criada por Guido van Rossum e lançada em 1991. Python é conhecida por sua sintaxe 
    simples e legível, que enfatiza a legibilidade do código. É amplamente utilizada em 
    desenvolvimento web, ciência de dados, inteligência artificial, automação e muito mais.
    """
    
    resultado = add_knowledge([texto_python], "exemplo_python")
    print(f"\n📊 Resultado: {resultado}")
    
    print("\n4. Exemplo com múltiplos textos:")
    
    # Exemplo: Adicionar múltiplos textos sobre diferentes tópicos
    textos = [
        """
        FastAPI é um framework web moderno e rápido para Python, baseado em type hints padrão do Python. 
        É usado para construir APIs com Python 3.6+ e oferece alta performance, rivalizando com NodeJS e Go.
        """,
        
        """
        Machine Learning é um subcampo da inteligência artificial que se concentra no desenvolvimento 
        de algoritmos e modelos estatísticos que permitem aos computadores melhorar automaticamente 
        através da experiência.
        """,
        
        """
        Docker é uma plataforma para desenvolver, enviar e executar aplicações em containers. 
        Os containers são unidades padronizadas de software que empacotam código e todas as suas 
        dependências para que a aplicação execute rapidamente e de forma confiável.
        """
    ]
    
    resultado = add_knowledge(textos, "exemplos_multiplos")
    print(f"\n📊 Resultado: {resultado}")
    
    print("\n5. Exemplo com divisão de texto longo:")
    
    # Exemplo de uso com texto longo
    texto_longo = """
    Este é um texto muito longo que será dividido em partes menores para ser adicionado à base de conhecimento. 
    Cada parte será processada separadamente pelo sistema RAG, permitindo uma melhor organização e recuperação 
    das informações quando necessário.

    A divisão de textos longos é uma prática comum em sistemas de recuperação de informação, pois permite 
    que o sistema encontre informações específicas dentro de documentos extensos de forma mais eficiente.

    Além disso, textos menores são mais fáceis de processar e indexar, melhorando a performance geral 
    do sistema de busca e recuperação de conhecimento.
    """
    
    partes = split_long_text(texto_longo, max_length=200)
    print(f"📝 Texto dividido em {len(partes)} parte(s):")
    for i, parte in enumerate(partes, 1):
        print(f"\n--- Parte {i} ---")
        print(parte[:100] + "..." if len(parte) > 100 else parte)
    
    # Adicionar as partes à base de conhecimento
    resultado = add_knowledge(partes, "texto_dividido")
    print(f"\n📊 Resultado: {resultado}")
    
    print("\n✅ Exemplo concluído!")

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT PARA ADICIONAR CONHECIMENTO NA BASE RAG")
    print("=" * 60)
    print()
    
    # Executar exemplo
    exemplo_uso()
    
    print("\n" + "=" * 60)
    print("INSTRUÇÕES DE USO:")
    print("=" * 60)
    print()
    print("Para usar este script no Jupyter notebook:")
    print("1. Execute: %run add_knowledge_script.py")
    print("2. Use as funções disponíveis:")
    print("   - add_knowledge(documents, source)")
    print("   - add_knowledge_from_file(file_path, source)")
    print("   - split_long_text(text, max_length)")
    print("   - check_services_status()")
    print("   - test_connection()")
    print()
    print("Exemplos:")
    print("add_knowledge(['Seu texto aqui'], 'fonte_personalizada')")
    print("add_knowledge_from_file('documento.txt', 'documento_externo')")
    print("check_services_status()") 