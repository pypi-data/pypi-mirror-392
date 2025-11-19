#!/usr/bin/env python3
"""
Script de verificação rápida - Testa se o ambiente está ok
Não requer GOOGLE_API_KEY configurada
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"  ✅ {text}")

def print_error(text):
    print(f"  ❌ {text}")

def print_warning(text):
    print(f"  ⚠️  {text}")

def print_info(text):
    print(f"  ℹ️  {text}")

def main():
    print_header("MANGABA AI - VERIFICAÇÃO RÁPIDA DE SETUP")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 1. Verificar estrutura
    print("\n📁 Verificando estrutura do projeto...")
    
    required_files = {
        "mangaba_agent.py": "Agente principal",
        "config.py": "Configuração",
        ".env": "Variáveis de ambiente",
        "pyproject.toml": "Configuração do projeto",
        "README.md": "Documentação",
    }
    
    required_dirs = {
        "protocols": "Protocolos A2A e MCP",
        "scripts": "Scripts utilitários",
        "examples": "Exemplos de uso",
        "docs": "Documentação completa",
    }
    
    files_ok = True
    for file, desc in required_files.items():
        if (project_root / file).exists():
            print_success(f"{file:<25} - {desc}")
        else:
            print_error(f"{file:<25} - NÃO ENCONTRADO")
            files_ok = False
    
    dirs_ok = True
    for dir_name, desc in required_dirs.items():
        if (project_root / dir_name).exists():
            print_success(f"{dir_name}/<30          - {desc}")
        else:
            print_error(f"{dir_name}/<30          - NÃO ENCONTRADO")
            dirs_ok = False
    
    # 2. Verificar Python
    print("\n🐍 Verificando Python...")
    print_success(f"Versão: {sys.version.split()[0]}")
    
    # 3. Verificar dependências
    print("\n📦 Verificando dependências instaladas...")
    
    deps = {
        "google.generativeai": "Google Gemini API",
        "dotenv": "Carregador de variáveis",
        "loguru": "Sistema de logging",
        "pydantic": "Validação de dados",
        "requests": "Cliente HTTP",
    }
    
    deps_ok = True
    for package, desc in deps.items():
        try:
            __import__(package)
            print_success(f"{package:<25} - {desc}")
        except ImportError:
            print_error(f"{package:<25} - NÃO INSTALADO")
            deps_ok = False
    
    # 4. Verificar .env
    print("\n🔐 Verificando configuração...")
    
    env_file = project_root / ".env"
    env_ok = True
    
    if env_file.exists():
        print_success(f".env encontrado")
        
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        model = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        log_level = os.getenv("LOG_LEVEL", "INFO")
        
        if api_key:
            print_success(f"GOOGLE_API_KEY: Configurada (primeiros 10 chars: {api_key[:10]}...)")
        else:
            print_warning(f"GOOGLE_API_KEY: ⏳ Vazia (configure antes de usar)")
            env_ok = False
        
        print_info(f"MODEL_NAME: {model}")
        print_info(f"LOG_LEVEL: {log_level}")
    else:
        print_error(".env não encontrado")
        env_ok = False
    
    # 5. Verificar imports
    print("\n📚 Verificando imports...")
    
    imports_ok = True
    
    try:
        import google.generativeai as genai
        print_success("google.generativeai importado")
    except Exception as e:
        print_error(f"google.generativeai: {e}")
        imports_ok = False
    
    try:
        from dotenv import load_dotenv
        print_success("dotenv importado")
    except Exception as e:
        print_error(f"dotenv: {e}")
        imports_ok = False
    
    try:
        from loguru import logger
        print_success("loguru importado")
    except Exception as e:
        print_error(f"loguru: {e}")
        imports_ok = False
    
    try:
        from pydantic import BaseModel
        print_success("pydantic importado")
    except Exception as e:
        print_error(f"pydantic: {e}")
        imports_ok = False
    
    # Resumo
    print_header("RESUMO DE STATUS")
    
    all_critical_ok = files_ok and dirs_ok and deps_ok and imports_ok
    api_key_configured = os.getenv("GOOGLE_API_KEY", "").strip() != ""
    
    print(f"\n  📁 Estrutura do projeto:  {'✅ OK' if files_ok and dirs_ok else '❌ PROBLEMAS'}")
    print(f"  📦 Dependências:         {'✅ OK' if deps_ok else '❌ PROBLEMAS'}")
    print(f"  📚 Imports Python:       {'✅ OK' if imports_ok else '❌ PROBLEMAS'}")
    print(f"  🔐 Configuração .env:    {'✅ OK' if env_ok else '⚠️  FALTA CONFIG'}")
    print(f"  🔑 API Key:              {'✅ CONFIGURADA' if api_key_configured else '⏳ FALTA ADICIONAR'}")
    
    print("\n" + "="*70)
    
    if all_critical_ok:
        if api_key_configured:
            print("  ✅ AMBIENTE COMPLETO - PRONTO PARA USAR!")
            print("\n  Próximos passos:")
            print("    1. python examples/basic_example.py")
            print("    2. Explore os outros exemplos em examples/")
            print("    3. Leia a documentação em docs/")
            return 0
        else:
            print("  ⚠️  AMBIENTE PRONTO, MAS FALTA CONFIGURAÇÃO")
            print("\n  O que fazer:")
            print("    1. Obtenha sua GOOGLE_API_KEY em:")
            print("       https://makersuite.google.com/app/apikey")
            print("    2. Adicione ao arquivo .env:")
            print("       GOOGLE_API_KEY=AIza...sua_chave...")
            print("    3. Depois execute:")
            print("       python examples/basic_example.py")
            return 0
    else:
        print("  ❌ PROBLEMAS ENCONTRADOS")
        print("\n  Resolva os erros acima antes de continuar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
