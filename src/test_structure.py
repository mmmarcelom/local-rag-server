#!/usr/bin/env python3

import sys
import os

print("=== Teste da Nova Estrutura ===")
print(f"PYTHONPATH: {sys.path}")
print(f"Diretório atual: {os.getcwd()}")

try:
    print("\n1. Testando importação de src...")
    import src
    print("✅ src importado com sucesso")
    
    print("2. Testando importação de src.models...")
    import src.models
    print("✅ src.models importado com sucesso")
    
    print("3. Testando importação de src.controllers...")
    import src.controllers
    print("✅ src.controllers importado com sucesso")
    
    print("4. Testando importação de src.services...")
    import src.services
    print("✅ src.services importado com sucesso")
    
    print("5. Testando importação de src.routes...")
    import src.routes
    print("✅ src.routes importado com sucesso")
    
    print("6. Testando importação de schemas...")
    from src.models.schemas import IncomingMessage, OutgoingMessage
    print("✅ schemas importado com sucesso")
    
    print("\n🎉 Nova estrutura funcionando perfeitamente!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc() 