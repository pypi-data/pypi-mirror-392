# 🥭 Mangaba AI

[![PyPI version](https://img.shields.io/pypi/v/mangaba.svg)](https://pypi.org/project/mangaba/)
[![Python](https://img.shields.io/pypi/pyversions/mangaba.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/usuario/mangaba-ai/actions)

Repositório minimalista para criação de agentes de IA inteligentes e versáteis com protocolos **A2A** (Agent-to-Agent) e **MCP** (Model Context Protocol).

> 📚 **[WIKI AVANÇADA](wiki/README.md)** - Documentação completa em português brasileiro

> 📋 **[ÍNDICE COMPLETO](INDICE.md)** - Navegação rápida por todo o repositório

## ✨ Características Principais

- 🤖 **Agente de IA Versátil**: Suporte a qualquer provedor de IA
- 🔗 **Protocolo A2A**: Comunicação entre agentes
- 🧠 **Protocolo MCP**: Gerenciamento avançado de contexto
- 📝 **Funcionalidades Integradas**: Chat, análise, tradução e mais
- ⚡ **Configuração Simples**: Apenas 2 passos para começar

## 🚀 Instalação Rápida

Precisa apenas usar a biblioteca diretamente? Ela já está publicada no PyPI e pode ser instalada tanto com **pip** quanto com **UV**:

```bash
# pip tradicional
pip install mangaba

# usando UV (mesmo comando do pip, porém turbo)
uv pip install mangaba

# teste rápido após a instalação
python -c "from mangaba_ai import MangabaAgent; print(MangabaAgent)"
```

> ✅ Esses comandos funcionam em qualquer ambiente virtual ou no sistema.  
> ✅ `uv pip install mangaba` também aceita `--extra`/`--index` iguais ao pip.

Se quiser clonar o repositório para contribuir, rode os passos abaixo e escolha entre **UV** (ultra-rápido) ou **pip** (tradicional):

### ⚡ Opção A: Com UV (10-100x mais rápido!)

```bash
# Windows
.\uv sync
.\uv run python examples/basic_example.py

# Linux/Mac
uv sync
uv run python examples/basic_example.py
```

> 💡 **Novo em UV?** [Guia completo de comandos UV](COMANDOS_UV.md) • [Como usar UV](COMO_USAR_UV.md)

### 🐍 Opção B: Com pip (tradicional)

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar exemplo
python examples/basic_example.py
```

### 🤖 Opção C: Setup Automático

```bash
# Detecta automaticamente UV ou pip
python scripts/quick_setup.py
```

<details>
<summary>📋 <strong>Configuração do arquivo .env</strong></summary>

```bash
# Copiar template (ou criar manualmente)
cp .env.example .env  # Linux/Mac
copy .env.example .env  # Windows
```

Edite `.env` e adicione sua chave:
```env
GOOGLE_API_KEY=sua_chave_aqui
MODEL_NAME=gemini-2.5-flash
LOG_LEVEL=INFO
```

Obtenha sua chave em: https://makersuite.google.com/app/apikey

</details>

## 📦 UV vs pip - Qual usar?

| Característica | UV ⚡ | pip 🐍 |
|----------------|------|--------|
| **Velocidade** | 10-100x mais rápido | Padrão Python |
| **Instalação** | `pip install uv` | Já vem com Python |
| **Compatibilidade** | 100% compatível | Nativo |
| **Lock file** | ✅ `uv.lock` | ❌ Manual |
| **Uso** | `.\uv sync` | `pip install -r requirements.txt` |
| **Recomendado para** | Desenvolvimento ativo | CI/CD tradicional |

**💡 Dica:** Pode usar ambos! UV é retrocompatível com pip.

## ⚙️ Configuração

### 🔧 Comandos por Gerenciador

#### Com UV:
```bash
# Sincronizar dependências
.\uv sync                    # Windows
uv sync                      # Linux/Mac

# Instalar pacote novo
.\uv pip install nome-pacote

# Executar script
.\uv run python seu_script.py

# Ver pacotes instalados
.\uv pip list
```

#### Com pip:
```bash
# Ativar ambiente virtual primeiro
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Instalar pacote novo
pip install nome-pacote

# Executar script
python seu_script.py

# Ver pacotes instalados
pip list
```

### 🛠️ Configuração Manual do .env

1. **Copie o arquivo de exemplo:**
```bash
cp .env.example .env      # Linux/Mac
copy .env.example .env    # Windows
```

2. **Edite o arquivo .env:**
```env
# Obrigatório
GOOGLE_API_KEY=sua_chave_google_api_aqui

# Opcional (com valores padrão)
MODEL_NAME=gemini-2.5-flash
AGENT_NAME=MangabaAgent
LOG_LEVEL=INFO
```

3. **Obtenha sua Google API Key:**
   - Acesse: https://makersuite.google.com/app/apikey
   - Crie uma nova chave
   - Cole no arquivo .env

### 🔍 Validação do Ambiente

```bash
# Validação rápida
python check_setup.py

# Validação completa
python scripts/validate_env.py

# Com relatório detalhado
python scripts/validate_env.py --save-report
```

## 📖 Uso Super Simples

```python
from mangaba_ai import MangabaAgent

# Inicializar com protocolos A2A e MCP habilitados
agent = MangabaAgent()

# Chat com contexto automático
resposta = agent.chat("Olá! Como você pode me ajudar?")
print(resposta)
```

## 🎯 Exemplos Práticos

### Chat Básico com Contexto MCP
```python
from mangaba_ai import MangabaAgent

agent = MangabaAgent()

# O contexto é mantido automaticamente
print(agent.chat("Meu nome é João"))
print(agent.chat("Qual é o meu nome?"))  # Lembra do contexto anterior
```

### Análise de Texto
```python
agent = MangabaAgent()
text = "A inteligência artificial está transformando o mundo."
analysis = agent.analyze_text(text, "Faça uma análise detalhada")
print(analysis)
```

### Tradução
```python
agent = MangabaAgent()
translation = agent.translate("Hello, how are you?", "português")
print(translation)
```

### Resumo do Contexto
```python
agent = MangabaAgent()

# Após algumas interações...
summary = agent.get_context_summary()
print(summary)
```

## 🔗 Protocolo A2A (Agent-to-Agent)

O protocolo A2A permite comunicação entre múltiplos agentes:

### Comunicação entre Agentes
```python
# Criar dois agentes
agent1 = MangabaAgent()
agent2 = MangabaAgent()

# Enviar requisição de um agente para outro
result = agent1.send_agent_request(
    target_agent_id=agent2.agent_id,
    action="chat",
    params={"message": "Olá do Agent 1!"}
)
```

### Broadcast para Múltiplos Agentes
```python
agent = MangabaAgent()

# Enviar mensagem para todos os agentes conectados
result = agent.broadcast_message(
    message="Olá a todos!",
    tags=["general", "announcement"]
)
```

### Tipos de Mensagens A2A
- **REQUEST**: Requisições entre agentes
- **RESPONSE**: Respostas a requisições
- **BROADCAST**: Mensagens para múltiplos agentes
- **NOTIFICATION**: Notificações assíncronas
- **ERROR**: Mensagens de erro

## 🧠 Protocolo MCP (Model Context Protocol)

O protocolo MCP gerencia contexto avançado automaticamente:

### Tipos de Contexto
- **CONVERSATION**: Conversas e diálogos
- **TASK**: Tarefas e operações específicas
- **MEMORY**: Memórias de longo prazo
- **SYSTEM**: Informações do sistema

### Prioridades de Contexto
- **HIGH**: Contexto crítico (sempre preservado)
- **MEDIUM**: Contexto importante
- **LOW**: Contexto opcional

### Funcionalidades MCP
```python
agent = MangabaAgent()

# Chat com contexto automático
response = agent.chat("Mensagem", use_context=True)

# Chat sem contexto
response = agent.chat("Mensagem", use_context=False)

# Obter resumo do contexto atual
summary = agent.get_context_summary()
```

## 🛠️ Exemplo Avançado

```python
from mangaba_ai import MangabaAgent

def demo_completa():
    # Criar agente com protocolos habilitados
    agent = MangabaAgent()
    
    print(f"Agent ID: {agent.agent_id}")
    print(f"MCP Habilitado: {agent.mcp_enabled}")
    
    # Sequência de interações com contexto
    agent.chat("Olá, meu nome é Maria")
    agent.chat("Eu trabalho com programação")
    
    # Análise com contexto preservado
    analysis = agent.analyze_text(
        "Python é uma linguagem versátil",
        "Analise considerando meu perfil profissional"
    )
    
    # Tradução
    translation = agent.translate("Good morning", "português")
    
    # Resumo do contexto acumulado
    context = agent.get_context_summary()
    print("Contexto atual:", context)
    
    # Comunicação A2A
    agent.broadcast_message("Demonstração concluída!")

if __name__ == "__main__":
    demo_completa()
```

## 🎮 Exemplo Interativo

Execute o exemplo interativo:

```bash
python examples/basic_example.py
```

Comandos disponíveis:
- `/analyze <texto>` - Analisa texto
- `/translate <texto>` - Traduz texto
- `/context` - Mostra contexto atual
- `/broadcast <mensagem>` - Envia broadcast
- `/request <agent_id> <action>` - Requisição para outro agente
- `/help` - Ajuda

## 🧪 Demonstração dos Protocolos

Para ver uma demonstração completa dos protocolos A2A e MCP:

```bash
python examples/basic_example.py --demo
```

## 📋 Funcionalidades Principais

### MangabaAgent
- `chat(message, use_context=True)` - Chat com/sem contexto
- `analyze_text(text, instruction)` - Análise de texto
- `translate(text, target_language)` - Tradução
- `get_context_summary()` - Resumo do contexto
- `send_agent_request(agent_id, action, params)` - Requisição A2A
- `broadcast_message(message, tags)` - Broadcast A2A

### Protocolos Integrados
- **A2A Protocol**: Comunicação entre agentes
- **MCP Protocol**: Gerenciamento de contexto
- **Handlers Customizados**: Para requisições específicas
- **Sessões MCP**: Contexto isolado por sessão

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
API_KEY=sua_chave_api_aqui          # Obrigatório
MODEL=modelo_desejado               # Opcional
LOG_LEVEL=INFO                      # Opcional (DEBUG, INFO, WARNING, ERROR)
```

### Personalização
```python
# Agente com configurações customizadas
agent = MangabaAgent()

# Acessar protocolos diretamente
a2a = agent.a2a_protocol
mcp = agent.mcp

# ID único do agente
print(f"Agent ID: {agent.agent_id}")

# Sessão MCP atual
print(f"Session ID: {agent.current_session_id}")
```

agent = MangabaAgent()
resposta = agent.chat_with_context(
    context="Você é um tutor de programação",
    message="Como criar uma lista em Python?"
)
print(resposta)
```

### Análise de Texto
```python
from mangaba_ai import MangabaAgent

agent = MangabaAgent()
texto = "Este é um texto para analisar..."
analise = agent.analyze_text(texto, "Resuma os pontos principais")
print(analise)
```

## 🔧 Personalização

Para usar um modelo diferente, apenas mude no `.env`:
```
MODEL=modelo-avancado     # Modelo mais avançado
MODEL=modelo-multimodal   # Para diferentes tipos de entrada
```

## 🚀 Scripts Disponíveis

> 🔧 **Todos os scripts estão organizados na pasta [scripts/](scripts/)**

- [`validate_env.py`](scripts/validate_env.py) - Valida configuração do ambiente
- [`quick_setup.py`](scripts/quick_setup.py) - Configuração rápida automatizada
- [`example_env_usage.py`](scripts/example_env_usage.py) - Exemplo de uso das configurações
- [`exemplo_curso_basico.py`](scripts/exemplo_curso_basico.py) - Exemplos práticos do curso básico
- [`setup_env.py`](scripts/setup_env.py) - Configuração manual detalhada

## 📁 Estrutura do Projeto

```
mangaba_ai/
├── 📁 docs/                    # 📚 Documentação
│   ├── CURSO_BASICO.md         # Curso básico completo
│   ├── SETUP.md                # Guia de configuração
│   ├── PROTOCOLS.md            # Documentação dos protocolos
│   ├── CHANGELOG.md            # Histórico de mudanças
│   ├── SCRIPTS.md              # Documentação dos scripts
│   └── README.md               # Índice da documentação
├── 📁 scripts/                 # 🔧 Scripts de configuração
│   ├── validate_env.py         # Validação do ambiente
│   ├── quick_setup.py          # Setup rápido automatizado
│   ├── example_env_usage.py    # Exemplo de uso
│   ├── exemplo_curso_basico.py # Exemplos do curso
│   ├── setup_env.py            # Setup manual detalhado
│   └── README.md               # Documentação dos scripts
├── 📁 protocols/               # 🌐 Protocolos de comunicação
│   ├── mcp_protocol.py         # Model Context Protocol
│   └── a2a_protocol.py         # Agent-to-Agent Protocol
├── 📁 examples/                # 📖 Exemplos de uso
│   └── basic_example.py        # Exemplo básico completo
├── 📁 utils/                   # 🛠️ Utilitários
│   ├── __init__.py
│   └── logger.py               # Sistema de logs
├── mangaba_agent.py            # 🤖 Agente principal
├── config.py                   # ⚙️ Configurações do sistema
├── ESTRUTURA.md                # 📁 Organização do repositório
├── .env.example                # 🔐 Exemplo de configuração
├── requirements.txt            # 📦 Dependências Python
└── README.md                   # 📖 Este arquivo
```

> 📋 **Para detalhes completos da estrutura, consulte [ESTRUTURA.md](ESTRUTURA.md)**

## 🧪 Testar Rapidamente

### Com UV:
```bash
.\uv run python check_setup.py              # Validação rápida
.\uv run python examples/basic_example.py   # Exemplo básico
.\uv run python -m pytest tests/            # Executar testes
```

### Com pip (após ativar .venv):
```bash
python check_setup.py                       # Validação rápida
python examples/basic_example.py            # Exemplo básico
python scripts/quick_setup.py               # Setup automático
python -m pytest tests/                     # Executar testes
```

### Scripts Úteis:
```bash
python scripts/validate_env.py              # Validação completa
python scripts/example_env_usage.py         # Exemplo de uso
python scripts/exemplo_curso_basico.py      # Exemplos do curso
python test_correcoes.py                    # Testar correções
```

## 📚 Wiki Avançada e Documentação

### 🌟 **[📖 WIKI COMPLETA](docs/WIKI.md) - Portal Principal da Documentação**

A **Wiki Avançada** do Mangaba AI oferece documentação abrangente em português brasileiro para todos os níveis:

#### 🎓 **Para Iniciantes**
- [🚀 Visão Geral do Projeto](docs/WIKI.md#-visão-geral-do-projeto) - O que é e para que serve
- [🎓 Curso Básico Completo](docs/CURSO_BASICO.md) - Tutorial passo-a-passo  
- [⚙️ Instalação e Configuração](docs/SETUP.md) - Guia detalhado de setup
- [❓ FAQ - Perguntas Frequentes](docs/FAQ.md) - Dúvidas comuns e soluções

#### 👨‍💻 **Para Desenvolvedores**
- [🌐 Protocolos A2A e MCP](docs/PROTOCOLS.md) - Documentação técnica completa
- [⭐ Melhores Práticas](docs/MELHORES_PRATICAS.md) - Guia de boas práticas
- [🤝 Como Contribuir](docs/CONTRIBUICAO.md) - Diretrizes de contribuição
- [📝 Glossário de Termos](docs/GLOSSARIO.md) - Definições técnicas

#### 🛠️ **Recursos Técnicos**
- [🔧 Scripts e Automação](docs/SCRIPTS.md) - Documentação dos scripts
- [📊 Histórico de Mudanças](docs/CHANGELOG.md) - Changelog completo
- [📁 Estrutura do Projeto](ESTRUTURA.md) - Organização do repositório

> 🎯 **Comece pela [Wiki Principal](docs/WIKI.md)** - É seu portal de entrada para toda a documentação!

## 🤝 Contribuição

Agradecemos seu interesse em contribuir! Consulte nosso **[Guia Completo de Contribuição](docs/CONTRIBUICAO.md)** para informações detalhadas.

### 🚀 **Primeiros Passos**
1. 📚 Leia as [Diretrizes de Contribuição](docs/CONTRIBUICAO.md)
2. 🍴 Faça fork do projeto
3. 🔧 Configure o ambiente de desenvolvimento
4. ⭐ Siga as [Melhores Práticas](docs/MELHORES_PRATICAS.md)
5. 🧪 Execute os testes
6. 📤 Abra um Pull Request

### 💡 **Formas de Contribuir**
- 🐛 **Correção de bugs**
- ✨ **Novas funcionalidades**
- 📚 **Melhoria da documentação**
- 🧪 **Adição de testes**
- 🌐 **Tradução para outros idiomas**

> 📖 **Primeira contribuição?** Procure por issues marcadas com `good first issue`!

## 📄 Licença

MIT License

---

**Mangaba AI** - Agentes de IA simples e eficazes! 🤖✨
