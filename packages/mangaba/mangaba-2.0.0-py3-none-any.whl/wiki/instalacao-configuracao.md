# ⚙️ Instalação e Configuração

Este guia completo irá te ajudar a configurar o ambiente Mangaba AI do zero até estar pronto para desenvolvimento.

## 📋 Pré-requisitos

### Sistema Operacional
- **Windows 10/11**, **Linux (Ubuntu 18.04+)**, ou **macOS 10.15+**
- **Python 3.8 ou superior** (recomendado Python 3.9+)

### Softwares Necessários
- **Git** (para clonagem do repositório)
- **pip** (gerenciador de pacotes Python)
- **Editor de código** (VS Code, PyCharm, etc.)

### Contas e APIs
- **[Google AI Studio](https://makersuite.google.com/app/apikey)** - Para obter sua API key gratuita
- **GitHub** (opcional) - Para contribuições e issues

## 🚀 Configuração Rápida (Recomendada)

### Opção 1: Setup Automático

```bash
# 1. Clone o repositório
git clone https://github.com/Mangaba-ai/mangaba_ai.git
cd mangaba_ai

# 2. Execute o setup automático
python scripts/quick_setup.py
```

O script automático irá:
- ✅ Verificar dependências do sistema
- ✅ Criar ambiente virtual
- ✅ Instalar todas as dependências
- ✅ Configurar arquivo .env
- ✅ Executar testes de validação

### Opção 2: Setup Manual Detalhado

Se preferir controle total sobre o processo:

#### 1. Clone e Navegue
```bash
git clone https://github.com/Mangaba-ai/mangaba_ai.git
cd mangaba_ai
```

#### 2. Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instale Dependências
```bash
# Dependências principais
pip install -r requirements.txt

# Dependências de desenvolvimento (opcional)
pip install -r requirements-test.txt
```

#### 4. Configure Variáveis de Ambiente
```bash
# Copie o template
cp .env.template .env

# Edite o arquivo .env com seu editor preferido
nano .env  # ou code .env, vim .env, etc.
```

## 🔧 Configuração Detalhada

### Variáveis de Ambiente Obrigatórias

Edite seu arquivo `.env` com as seguintes configurações:

```bash
# === CONFIGURAÇÕES OBRIGATÓRIAS ===

# API do Google Generative AI
GOOGLE_API_KEY=sua_api_key_aqui

# Nome do modelo (opcional - padrão: gemini-pro)
MODEL_NAME=gemini-pro

# Nome do agente (opcional - padrão: MangabaAgent)
AGENT_NAME=MeuAgente
```

### Variáveis de Ambiente Opcionais

```bash
# === PROTOCOLOS ===

# Habilitar protocolo MCP (padrão: true)
USE_MCP=true

# Habilitar protocolo A2A (padrão: true)
USE_A2A=true

# Porta para comunicação A2A (padrão: 8080)
A2A_PORT=8080

# === LOGGING E DEBUGGING ===

# Nível de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Diretório de logs (padrão: ./logs)
LOG_DIR=./logs

# Formato dos logs (json, text)
LOG_FORMAT=text

# === CONTEXTO MCP ===

# Máximo de contextos armazenados (padrão: 1000)
MAX_CONTEXTS=1000

# Diretório do banco de contexto (padrão: ./data)
MCP_DATA_DIR=./data

# Tamanho máximo do contexto por sessão (padrão: 10MB)
MAX_CONTEXT_SIZE=10485760

# === PERFORMANCE ===

# Timeout para requisições IA (segundos - padrão: 30)
AI_REQUEST_TIMEOUT=30

# Rate limiting (requisições por minuto - padrão: 60)
RATE_LIMIT_PER_MINUTE=60

# Cache TTL em segundos (padrão: 3600 = 1 hora)
CACHE_TTL=3600
```

## 🔑 Obtendo sua API Key do Google

### Passo a Passo

1. **Acesse o Google AI Studio**
   - Vá para [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

2. **Faça Login**
   - Use sua conta Google existente

3. **Crie uma Nova API Key**
   - Clique em "Create API Key"
   - Escolha seu projeto do Google Cloud (ou crie um novo)

4. **Copie sua Chave**
   - Copie a chave gerada (começará com `AIza...`)
   - **⚠️ Importante**: Mantenha sua chave segura e nunca a compartilhe

5. **Configure no .env**
   ```bash
   GOOGLE_API_KEY=AIzaSyC...sua_chave_completa_aqui
   ```

## ✅ Validação da Instalação

### Teste Básico
```bash
# Execute o validador de ambiente
python scripts/validate_env.py
```

Você deve ver uma saída similar a:
```
✅ Python 3.9.7 detectado
✅ Todas as dependências instaladas
✅ Arquivo .env configurado
✅ API Key do Google válida
✅ Conexão com IA estabelecida
🎉 Ambiente configurado com sucesso!
```

### Teste Funcional
```bash
# Execute um teste básico
python examples/basic_example.py
```

Se tudo estiver funcionando, você verá:
```
🤖 Iniciando Mangaba AI...
🧠 Contexto MCP inicializado
🔗 Protocolo A2A disponível
💬 Teste de chat: "Olá! Como posso ajudar?"
✅ Sistema funcionando perfeitamente!
```

## 🧪 Executando Testes

### Testes Unitários
```bash
# Execute todos os testes
python -m pytest

# Execute com cobertura
python -m pytest --cov=mangaba_agent

# Execute testes específicos
python -m pytest tests/test_basic.py -v
```

### Testes de Performance
```bash
# Benchmark de performance
python -m pytest tests/test_performance.py --benchmark-only
```

## 🐳 Configuração com Docker (Opcional)

### Build da Imagem
```bash
# Build local
docker build -t mangaba-ai .

# Ou use docker-compose
docker-compose build
```

### Execução
```bash
# Execute com docker-compose
docker-compose up -d

# Ou execute diretamente
docker run -d \
  --name mangaba-ai \
  -e GOOGLE_API_KEY=sua_api_key \
  -p 8080:8080 \
  mangaba-ai
```

## 📊 Configurações Avançadas

### Configuração para Desenvolvimento

```bash
# Instale hooks de pre-commit
pip install pre-commit
pre-commit install

# Configure ambiente de desenvolvimento
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Configuração para Produção

```bash
# Configurações otimizadas para produção
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=WARNING
export RATE_LIMIT_PER_MINUTE=120
export CACHE_TTL=7200
```

### Configuração Multi-Agente

```bash
# Configure múltiplos agentes
export A2A_ENABLED=true
export A2A_DISCOVERY_PORT=8081
export A2A_CLUSTER_NAME=meu-cluster

# Agente específico
export AGENT_ROLE=coordinator
export AGENT_SPECIALIZATION=data_analysis
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de API Key
```
❌ ValueError: GOOGLE_API_KEY não encontrada!
```
**Solução**: Verifique se sua API key está no arquivo `.env`

#### 2. Dependências em Conflito
```
❌ pip install falhou com conflito de versões
```
**Solução**: Use ambiente virtual limpo
```bash
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

#### 3. Porta em Uso
```
❌ OSError: [Errno 98] Address already in use
```
**Solução**: Mude a porta A2A no `.env`
```bash
A2A_PORT=8081
```

#### 4. Permissões de Arquivo
```
❌ PermissionError: [Errno 13] Permission denied
```
**Solução**: Verifique permissões do diretório
```bash
chmod 755 .
chmod 644 .env
```

### Logs de Debug

```bash
# Ative logs detalhados
export LOG_LEVEL=DEBUG

# Execute com logging verboso
python -c "
from mangaba_agent import MangabaAgent
agent = MangabaAgent()
print(agent.get_system_info())
"
```

## 🔄 Atualizações

### Atualizando o Projeto
```bash
# Atualize o código
git pull origin main

# Atualize dependências
pip install -r requirements.txt --upgrade

# Re-execute validação
python scripts/validate_env.py
```

### Migrações de Dados
```bash
# Execute scripts de migração quando necessário
python scripts/migrate_data.py
```

## 🆘 Suporte

### Se encontrar problemas:

1. **Consulte o [FAQ](faq.md)** para soluções rápidas
2. **Verifique os logs** em `./logs/mangaba.log`
3. **Execute o diagnóstico** com `python scripts/diagnostic.py`
4. **Abra uma [issue](https://github.com/Mangaba-ai/mangaba_ai/issues)** com detalhes

### Informações para Support

Quando reportar problemas, inclua:
```bash
# Execute este comando e copie a saída
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Arquitetura: {platform.machine()}')
"
```

---

> 🎯 **Próximos Passos**: Com o ambiente configurado, continue para [Primeiros Passos](primeiros-passos.md) para criar seu primeiro agente!

> ⚡ **Dica de Performance**: Para melhor performance, use Python 3.9+ e mantenha as dependências atualizadas.