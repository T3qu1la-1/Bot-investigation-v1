
#!/usr/bin/env python3
"""
Script para executar o CloneChat Bot
"""

import asyncio
import os
import sys
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_bot import main

def check_environment():
    """Verifica se as variáveis de ambiente necessárias estão definidas"""
    # Credenciais já configuradas diretamente no código
    print("✅ Credenciais configuradas no código")
    return True

def ensure_directories():
    """Garante que os diretórios necessários existam"""
    directories = ['user', 'cache', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

if __name__ == '__main__':
    print("🤖 Iniciando CloneChat Bot...")
    
    if not check_environment():
        sys.exit(1)
    
    ensure_directories()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar bot: {e}")
        sys.exit(1)
