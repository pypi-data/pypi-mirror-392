# 🤝 Diretrizes de Contribuição - Mangaba AI

Obrigado por seu interesse em contribuir com o **Mangaba AI**! Este documento fornece todas as informações necessárias para contribuir de forma efetiva e colaborativa com o projeto.

## 📋 Índice

1. [🎯 Como Contribuir](#-como-contribuir)
2. [🚀 Configuração do Ambiente de Desenvolvimento](#-configuração-do-ambiente-de-desenvolvimento)
3. [📝 Padrões de Código](#-padrões-de-código)
4. [🧪 Testes e Qualidade](#-testes-e-qualidade)
5. [📚 Documentação](#-documentação)
6. [🔄 Processo de Pull Request](#-processo-de-pull-request)
7. [🐛 Reportando Issues](#-reportando-issues)
8. [💡 Sugestões de Melhorias](#-sugestões-de-melhorias)
9. [🏆 Reconhecimento de Contribuidores](#-reconhecimento-de-contribuidores)

---

## 🎯 Como Contribuir

### 🌟 **Tipos de Contribuição Bem-Vindas**

#### **1. 🐛 Correção de Bugs**
- Identificação e correção de problemas existentes
- Melhoria na estabilidade do sistema
- Otimização de performance

#### **2. ✨ Novas Funcionalidades**
- Implementação de recursos solicitados pela comunidade
- Melhorias nos protocolos A2A e MCP
- Integração com novas APIs e serviços

#### **3. 📚 Documentação**
- Melhoria da documentação existente
- Criação de tutoriais e exemplos
- Tradução para outros idiomas

#### **4. 🧪 Testes**
- Adição de novos casos de teste
- Melhoria da cobertura de testes
- Testes de performance e stress

#### **5. 🎨 UX/UI**
- Melhorias na experiência do usuário
- Interface para ferramentas de desenvolvimento
- Dashboards e monitoramento

### 🎯 **Áreas de Prioridade**

| Prioridade | Área | Descrição |
|-----------|------|-----------|
| 🔥 **Alta** | Protocolos | Melhorias nos protocolos A2A e MCP |
| 🔥 **Alta** | Performance | Otimizações e cache |
| 🚀 **Média** | Exemplos | Novos casos de uso e examples |
| 🚀 **Média** | Documentação | Expansão da wiki e tutoriais |
| 💡 **Baixa** | Ferramentas | Utilitários de desenvolvimento |

---

## 🚀 Configuração do Ambiente de Desenvolvimento

### **1. Fork e Clone do Repositório**

```bash
# 1. Faça fork do repositório no GitHub
# 2. Clone seu fork localmente
git clone https://github.com/SEU_USUARIO/mangaba_ai.git
cd mangaba_ai

# 3. Adicione o repositório original como upstream
git remote add upstream https://github.com/Mangaba-ai/mangaba_ai.git

# 4. Verifique os remotes
git remote -v
```

### **2. Configuração do Ambiente Python**

**Opção A: Com UV (Recomendado - Muito mais rápido)**

```bash
# Instalar UV (se ainda não tiver)
pip install uv

# Sincronizar ambiente (cria .venv e instala todas as dependências)
# Windows
.\uv sync

# Linux/Mac
uv sync

# Ativar ambiente virtual
# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

**Opção B: Com pip (Tradicional)**

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-test.txt
```

**Configurar pre-commit hooks (opcional mas recomendado):**

```bash
# Com UV
uv pip install pre-commit
pre-commit install

# Com pip
pip install pre-commit
pre-commit install
```

### **3. Configuração das Variáveis de Ambiente**

```bash
# Copiar template de configuração
cp .env.example .env

# Editar .env com suas configurações
# GOOGLE_API_KEY=sua_chave_aqui
# MODEL_NAME=gemini-pro
# LOG_LEVEL=DEBUG
```

### **4. Validação da Configuração**

```bash
# Executar script de validação
python scripts/validate_env.py

# Executar testes básicos
python -m pytest tests/test_basic.py -v

# Testar exemplo básico
python examples/basic_example.py
```

---

## 📝 Padrões de Código

### **🐍 Estilo Python (PEP 8)**

#### **1. Formatação**
```python
# ✅ BOM: Imports organizados
import os
import sys
from typing import Optional, List, Dict

from mangaba_agent import MangabaAgent
from protocols.mcp import MCPContext

# ✅ BOM: Docstrings em português
def processar_texto(texto: str, instrucao: str) -> str:
    """
    Processa texto usando o agente Mangaba.
    
    Args:
        texto (str): Texto a ser processado
        instrucao (str): Instrução para processamento
        
    Returns:
        str: Texto processado
        
    Raises:
        ValueError: Se o texto estiver vazio
    """
    if not texto.strip():
        raise ValueError("Texto não pode estar vazio")
    
    return f"Processado: {texto}"

# ✅ BOM: Type hints sempre que possível
class ProcessadorTexto:
    def __init__(self, agente: MangabaAgent) -> None:
        self.agente = agente
        self._cache: Dict[str, str] = {}
    
    def processar(self, texto: str) -> Optional[str]:
        """Processa texto com cache"""
        if texto in self._cache:
            return self._cache[texto]
        
        resultado = self.agente.analyze_text(texto, "análise geral")
        self._cache[texto] = resultado
        return resultado
```

#### **2. Convenções de Nomenclatura**
```python
# ✅ BOM: Nomes descritivos em português
class GerenciadorAgentes:
    def __init__(self):
        self.agentes_ativos: List[MangabaAgent] = []
        self.contador_requisicoes: int = 0
        
    def adicionar_agente(self, agente: MangabaAgent) -> None:
        """Adiciona um novo agente ao gerenciador"""
        self.agentes_ativos.append(agente)
    
    def obter_agente_disponivel(self) -> Optional[MangabaAgent]:
        """Retorna o agente com menor carga de trabalho"""
        if not self.agentes_ativos:
            return None
        
        # Encontrar agente menos ocupado
        agente_livre = min(
            self.agentes_ativos,
            key=lambda a: a.carga_atual
        )
        return agente_livre

# ❌ EVITAR: Nomes genéricos ou em inglês
class AgentManager:  # Use português
    def __init__(self):
        self.agents = []  # Use nomes descritivos
        self.counter = 0  # Use português
```

#### **3. Tratamento de Erros**
```python
# ✅ BOM: Exceções específicas e informativas
class ErroMangabaAPI(Exception):
    """Exceção base para erros da API Mangaba"""
    pass

class ErroConfiguracaoAgente(ErroMangabaAPI):
    """Erro na configuração do agente"""
    pass

class ErroProtocoloA2A(ErroMangabaAPI):
    """Erro na comunicação A2A"""
    pass

def criar_agente_seguro(config: Dict) -> MangabaAgent:
    """
    Cria agente com tratamento robusto de erros.
    
    Args:
        config: Dicionário de configuração
        
    Returns:
        MangabaAgent instanciado
        
    Raises:
        ErroConfiguracaoAgente: Se configuração inválida
    """
    try:
        api_key = config.get('api_key')
        if not api_key:
            raise ErroConfiguracaoAgente(
                "API key é obrigatória. "
                "Configure GOOGLE_API_KEY no .env"
            )
        
        agent_id = config.get('agent_id', 'agente_default')
        
        agente = MangabaAgent(
            api_key=api_key,
            agent_id=agent_id,
            enable_mcp=config.get('enable_mcp', True)
        )
        
        return agente
        
    except Exception as e:
        raise ErroConfiguracaoAgente(
            f"Falha ao criar agente: {str(e)}"
        ) from e
```

### **📁 Estrutura de Arquivos**

#### **1. Organização de Módulos**
```
mangaba_ai/
├── mangaba_agent.py          # Agente principal
├── config.py                 # Configurações
├── protocols/                # Protocolos
│   ├── __init__.py
│   ├── a2a_protocol.py      # Protocolo A2A
│   └── mcp_protocol.py      # Protocolo MCP
├── utils/                    # Utilitários
│   ├── __init__.py
│   ├── logger.py            # Sistema de logs
│   └── validators.py        # Validadores
├── examples/                 # Exemplos
│   ├── basic_example.py
│   └── advanced_example.py
├── tests/                    # Testes
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_protocols.py
│   └── integration/
└── docs/                     # Documentação
    ├── WIKI.md
    ├── FAQ.md
    └── ...
```

#### **2. Convenções para Novos Arquivos**
```python
"""
Nome do arquivo: exemplo_novo_modulo.py

Descrição: Breve descrição do que o módulo faz

Author: Seu Nome <email@exemplo.com>
Created: YYYY-MM-DD
Last Modified: YYYY-MM-DD
"""

import logging
from typing import Optional, Dict, List

# Configuração do logger específico do módulo
logger = logging.getLogger(__name__)

# Constantes do módulo
VERSAO_MODULO = "1.0.0"
MAX_TENTATIVAS = 3

# Classes e funções principais...
```

---

## 🧪 Testes e Qualidade

### **🎯 Estrutura de Testes**

#### **1. Testes Unitários**
```python
# tests/test_mangaba_agent.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from mangaba_agent import MangabaAgent
from protocols.mcp import MCPContext

class TestMangabaAgent(unittest.TestCase):
    """Testes unitários para MangabaAgent"""
    
    def setUp(self):
        """Configuração executada antes de cada teste"""
        self.api_key = "test_api_key"
        self.agent_id = "test_agent"
        
        # Mock do modelo para evitar chamadas reais à API
        self.mock_model = Mock()
        self.mock_response = Mock()
        self.mock_response.text = "Resposta de teste"
        self.mock_model.generate_content.return_value = self.mock_response
        
    @patch('mangaba_agent.genai.GenerativeModel')
    def test_inicializacao_agente(self, mock_genai):
        """Testa inicialização básica do agente"""
        mock_genai.return_value = self.mock_model
        
        agente = MangabaAgent(
            api_key=self.api_key,
            agent_id=self.agent_id,
            enable_mcp=True
        )
        
        # Verificações
        self.assertEqual(agente.agent_id, self.agent_id)
        self.assertTrue(agente.mcp_enabled)
        self.assertIsNotNone(agente.logger)
        mock_genai.assert_called_once()
    
    @patch('mangaba_agent.genai.GenerativeModel')
    def test_chat_basico(self, mock_genai):
        """Testa funcionalidade básica de chat"""
        mock_genai.return_value = self.mock_model
        
        agente = MangabaAgent(api_key=self.api_key)
        resultado = agente.chat("Olá, como você está?")
        
        # Verificações
        self.assertEqual(resultado, "Resposta de teste")
        self.mock_model.generate_content.assert_called_once()
        
        # Verificar se o prompt foi construído corretamente
        args, kwargs = self.mock_model.generate_content.call_args
        prompt_usado = args[0]
        self.assertIn("Olá, como você está?", prompt_usado)
    
    @patch('mangaba_agent.genai.GenerativeModel')
    def test_analise_texto(self, mock_genai):
        """Testa análise de texto"""
        mock_genai.return_value = self.mock_model
        self.mock_response.text = "Análise: O texto é positivo"
        
        agente = MangabaAgent(api_key=self.api_key)
        resultado = agente.analyze_text(
            "Texto de exemplo", 
            "Analise o sentimento"
        )
        
        self.assertIn("Análise", resultado)
        self.assertIn("positivo", resultado)
    
    def test_validacao_parametros(self):
        """Testa validação de parâmetros de entrada"""
        with self.assertRaises(ValueError):
            MangabaAgent(api_key="")  # API key vazia
        
        with self.assertRaises(ValueError):
            MangabaAgent(api_key=None)  # API key None
    
    def tearDown(self):
        """Limpeza executada após cada teste"""
        # Limpar arquivos temporários se necessário
        pass
```

#### **2. Testes de Integração**
```python
# tests/integration/test_a2a_integration.py
import unittest
import threading
import time
from mangaba_agent import MangabaAgent

class TestIntegracaoA2A(unittest.TestCase):
    """Testes de integração para protocolo A2A"""
    
    def setUp(self):
        """Configurar agentes para teste de integração"""
        self.agente1 = MangabaAgent(
            api_key=os.getenv('GOOGLE_API_KEY', 'test_key'),
            agent_id="agente_teste_1"
        )
        self.agente2 = MangabaAgent(
            api_key=os.getenv('GOOGLE_API_KEY', 'test_key'),
            agent_id="agente_teste_2"
        )
        
        # Configurar protocolos A2A em portas diferentes
        self.agente1.setup_a2a_protocol(port=8080)
        self.agente2.setup_a2a_protocol(port=8081)
        
        # Aguardar inicialização
        time.sleep(1)
    
    def test_comunicacao_entre_agentes(self):
        """Testa comunicação básica entre dois agentes"""
        # Conectar agente1 ao agente2
        sucesso_conexao = self.agente1.a2a_protocol.connect_to_agent(
            "localhost", 8081
        )
        self.assertTrue(sucesso_conexao)
        
        # Enviar mensagem do agente1 para agente2
        resposta = self.agente1.send_agent_request(
            target_agent_id="agente_teste_2",
            action="chat",
            params={"message": "Mensagem de teste A2A"}
        )
        
        # Verificar resposta
        self.assertIsNotNone(resposta)
        self.assertTrue(resposta.get('success', False))
        self.assertIn('result', resposta)
    
    def test_broadcast_multiplos_agentes(self):
        """Testa broadcast para múltiplos agentes"""
        # Configurar terceiro agente
        agente3 = MangabaAgent(
            api_key=os.getenv('GOOGLE_API_KEY', 'test_key'),
            agent_id="agente_teste_3"
        )
        agente3.setup_a2a_protocol(port=8082)
        
        # Conectar agentes
        self.agente1.a2a_protocol.connect_to_agent("localhost", 8081)
        self.agente1.a2a_protocol.connect_to_agent("localhost", 8082)
        
        # Fazer broadcast
        resultados = self.agente1.broadcast_message(
            message="Mensagem broadcast de teste",
            tags=["teste", "broadcast"]
        )
        
        # Verificar que múltiplos agentes receberam
        self.assertGreater(len(resultados), 1)
        
        # Limpar
        agente3.a2a_protocol.stop()
    
    def tearDown(self):
        """Limpeza após testes"""
        self.agente1.a2a_protocol.stop()
        self.agente2.a2a_protocol.stop()
```

#### **3. Testes de Performance**
```python
# tests/test_performance.py
import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from mangaba_agent import MangabaAgent

class TestPerformance(unittest.TestCase):
    """Testes de performance e carga"""
    
    def setUp(self):
        self.agente = MangabaAgent(
            api_key=os.getenv('GOOGLE_API_KEY', 'test_key')
        )
    
    def test_tempo_resposta_chat(self):
        """Testa tempo de resposta para chat simples"""
        inicio = time.time()
        
        resposta = self.agente.chat("Teste de performance")
        
        fim = time.time()
        tempo_resposta = fim - inicio
        
        # Deve responder em menos de 30 segundos
        self.assertLess(tempo_resposta, 30.0)
        self.assertIsNotNone(resposta)
        self.assertGreater(len(resposta), 0)
    
    def test_multiplas_requisicoes_simultaneas(self):
        """Testa múltiplas requisições simultâneas"""
        def fazer_requisicao(numero):
            return self.agente.chat(f"Requisição número {numero}")
        
        num_requisicoes = 5
        
        inicio = time.time()
        
        # Executar requisições em paralelo
        with ThreadPoolExecutor(max_workers=num_requisicoes) as executor:
            futures = [
                executor.submit(fazer_requisicao, i) 
                for i in range(num_requisicoes)
            ]
            resultados = [future.result() for future in futures]
        
        fim = time.time()
        tempo_total = fim - inicio
        
        # Verificar que todas retornaram resultado
        self.assertEqual(len(resultados), num_requisicoes)
        for resultado in resultados:
            self.assertIsNotNone(resultado)
            self.assertIsInstance(resultado, str)
        
        # Tempo total deve ser razoável
        self.assertLess(tempo_total, 60.0)
    
    def test_uso_memoria_contexto_mcp(self):
        """Testa uso de memória com muitos contextos MCP"""
        import psutil
        import os
        
        processo = psutil.Process(os.getpid())
        memoria_inicial = processo.memory_info().rss / 1024 / 1024  # MB
        
        # Adicionar muitos contextos
        for i in range(1000):
            self.agente.chat(f"Contexto número {i}")
        
        memoria_final = processo.memory_info().rss / 1024 / 1024  # MB
        incremento_memoria = memoria_final - memoria_inicial
        
        # Incremento de memória deve ser razoável (menos de 100MB)
        self.assertLess(incremento_memoria, 100)
```

### **📊 Cobertura de Testes**

#### **Executar Testes com Cobertura**
```bash
# Instalar coverage
pip install coverage

# Executar testes com cobertura
coverage run -m pytest tests/

# Gerar relatório
coverage report -m

# Gerar relatório HTML
coverage html
```

#### **Meta de Cobertura**
- **Mínimo**: 80% de cobertura de código
- **Ideal**: 90%+ para código crítico
- **Obrigatório**: 100% para funções de segurança

---

## 📚 Documentação

### **📝 Padrões de Documentação**

#### **1. Docstrings em Português**
```python
def processar_contexto_mcp(contexto: MCPContext, sessao_id: str) -> bool:
    """
    Processa e armazena um contexto MCP na sessão especificada.
    
    Esta função valida o contexto, aplica filtros de segurança
    e o armazena no sistema MCP para uso futuro pelo agente.
    
    Args:
        contexto (MCPContext): Contexto a ser processado
        sessao_id (str): Identificador único da sessão
        
    Returns:
        bool: True se processado com sucesso, False caso contrário
        
    Raises:
        ValueError: Se o contexto for inválido
        SessionError: Se a sessão não existir
        
    Example:
        >>> contexto = MCPContext.create(
        ...     context_type=ContextType.USER,
        ...     content="Informação do usuário"
        ... )
        >>> sucesso = processar_contexto_mcp(contexto, "sessao123")
        >>> print(sucesso)
        True
        
    Note:
        Esta função é thread-safe e pode ser chamada concorrentemente.
        
    See Also:
        - MCPContext.create(): Para criar novos contextos
        - obter_contextos_sessao(): Para recuperar contextos
    """
```

#### **2. Documentação de API**
```python
# docs/api/agents.md

# API - Agentes

## MangabaAgent

### Métodos Principais

#### `chat(message: str, use_context: bool = True) -> str`

**Descrição**: Inicia uma conversa com o agente usando o modelo de IA.

**Parâmetros**:
- `message` (str): Mensagem do usuário
- `use_context` (bool, opcional): Se deve usar contexto MCP. Padrão: True

**Retorna**: 
- `str`: Resposta gerada pelo agente

**Exemplo**:
```python
agente = MangabaAgent(api_key="sua_chave")
resposta = agente.chat("Explique quantum computing")
print(resposta)
```

**Exceções**:
- `ValueError`: Se message estiver vazio
- `APIError`: Se houver erro na API do Gemini
```

#### **3. Tutoriais e Guias**
```markdown
# Tutorial: Criando seu Primeiro Agente Especializado

## Objetivo
Neste tutorial, você aprenderá a criar um agente especializado 
para análise financeira usando o Mangaba AI.

## Pré-requisitos
- Python 3.8+
- Conta Google Cloud com API key
- Conhecimento básico de Python

## Passo 1: Configuração Inicial

Primeiro, vamos configurar o ambiente...

```python
# código exemplo aqui
```

## Passo 2: Criando o Agente

Agora vamos criar nosso agente especializado...

## Resultado Esperado
Ao final, você terá um agente capaz de...
```

---

## 🔄 Processo de Pull Request

### **📋 Checklist para PR**

#### **Antes de Submeter**
- [ ] ✅ Código segue padrões estabelecidos
- [ ] 🧪 Todos os testes passam
- [ ] 📚 Documentação atualizada
- [ ] 🔍 Code review interno realizado
- [ ] 📊 Cobertura de testes mantida/melhorada
- [ ] 🚀 Testado em ambiente local

#### **Informações no PR**

**Template de Pull Request**:
```markdown
## 📋 Descrição

Breve descrição das mudanças implementadas.

## 🎯 Tipo de Mudança

- [ ] 🐛 Bug fix
- [ ] ✨ Nova funcionalidade
- [ ] 💥 Breaking change
- [ ] 📚 Documentação
- [ ] 🧪 Testes
- [ ] 🔧 Refatoração

## 🧪 Como Foi Testado

Descreva os testes realizados:
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes manuais
- [ ] Testes de performance

## 📸 Screenshots (se aplicável)

Adicione screenshots se houver mudanças visuais.

## ✅ Checklist

- [ ] Meu código segue os padrões do projeto
- [ ] Realizei self-review do código
- [ ] Comentei código complexo
- [ ] Atualizei documentação
- [ ] Adicionei testes que provam que a correção/funcionalidade funciona
- [ ] Novos e existentes testes passam localmente

## 📝 Notas Adicionais

Qualquer informação adicional relevante.
```

### **🔍 Processo de Review**

#### **1. Review Automático**
- ✅ Testes automatizados devem passar
- ✅ Linters devem passar sem erros
- ✅ Cobertura de testes mantida
- ✅ Build deve ser bem-sucedido

#### **2. Review Manual**
- 👀 Revisão de código por pelo menos 1 maintainer
- 🧪 Verificação de funcionalidade
- 📚 Validação da documentação
- 🔐 Verificação de segurança

#### **3. Aprovação e Merge**
- ✅ Pelo menos 1 aprovação de maintainer
- ✅ Todos os checks automáticos passando
- ✅ Conflitos resolvidos
- ✅ Branch atualizada com master

---

## 🐛 Reportando Issues

### **📝 Template de Issue**

```markdown
## 🐛 Descrição do Bug

Descrição clara e concisa do problema.

## 🔄 Para Reproduzir

Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '....'
3. Role até '....'
4. Veja o erro

## ✅ Comportamento Esperado

Descrição clara do que você esperava que acontecesse.

## 🖼️ Screenshots

Se aplicável, adicione screenshots para ajudar a explicar o problema.

## 🖥️ Ambiente

**Desktop/Servidor:**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.9.7]
- Versão Mangaba AI: [e.g. 1.2.3]

## 📄 Logs

Adicione logs relevantes aqui:

```
[cole os logs aqui]
```

## 🔧 Informações Adicionais

Qualquer outra informação sobre o problema.
```

### **🏷️ Labels para Issues**

| Label | Descrição | Cor |
|-------|-----------|-----|
| `bug` | Algo não está funcionando | 🔴 Vermelho |
| `enhancement` | Nova funcionalidade ou solicitação | 🟢 Verde |
| `documentation` | Melhorias ou adições à documentação | 🔵 Azul |
| `good first issue` | Bom para novos contribuidores | 🟡 Amarelo |
| `help wanted` | Ajuda extra é solicitada | 🟣 Roxo |
| `question` | Informações adicionais são solicitadas | 🔵 Azul claro |
| `wontfix` | Isso não será trabalhado | ⚫ Preto |
| `priority: high` | Alta prioridade | 🔴 Vermelho escuro |
| `priority: medium` | Prioridade média | 🟠 Laranja |
| `priority: low` | Baixa prioridade | 🟡 Amarelo |

---

## 💡 Sugestões de Melhorias

### **🌟 Ideias para Contribuição**

#### **1. Funcionalidades Solicitadas**

**📊 Dashboard de Monitoramento**
- Interface web para monitorar agentes
- Métricas em tempo real
- Visualização de contextos MCP

**🔌 Integrações**
- Conectores para bancos de dados
- APIs de terceiros (Slack, Discord, etc.)
- Plugins para IDEs

**🧠 Melhorias de IA**
- Suporte a modelos locais (Ollama, etc.)
- Fine-tuning específico por domínio
- Pipelines de processamento de dados

#### **2. Exemplos e Casos de Uso**

**Setores Específicos**:
- 🏥 Healthcare: Análise de prontuários
- ⚖️ Legal: Análise de contratos
- 📈 Finance: Análise de mercado
- 🎓 Education: Assistente educacional

**Casos Técnicos**:
- Processamento de PDFs
- Análise de imagens
- Integração com APIs REST
- Processamento em lote

#### **3. Ferramentas de Desenvolvimento**

**CLI Tools**:
- Gerador de agentes especializados
- Ferramenta de debug para A2A
- Utilitário de backup/restore de contextos

**VS Code Extensions**:
- Syntax highlighting para configs
- Snippets para código comum
- Integração com debugging

---

## 🏆 Reconhecimento de Contribuidores

### **🌟 Tipos de Contribuição Reconhecidas**

#### **🏅 Badges de Contribuição**

| Badge | Critério | Descrição |
|-------|----------|-----------|
| 🥇 **Core Contributor** | 10+ PRs aceitos | Contribuidor principal |
| 🥈 **Active Contributor** | 5+ PRs aceitos | Contribuidor ativo |
| 🥉 **First Contributor** | 1° PR aceito | Primeira contribuição |
| 📚 **Documentation Master** | 5+ docs PRs | Especialista em documentação |
| 🐛 **Bug Hunter** | 5+ bugs reportados | Caçador de bugs |
| 🧪 **Test Champion** | Melhorias significativas em testes | Campeão de testes |
| 💡 **Feature Creator** | Nova funcionalidade implementada | Criador de funcionalidades |

#### **📊 Hall of Fame**

**Top Contributors (Última Atualização: Dezembro 2024)**

| Posição | Contribuidor | Contribuições | Área Principal |
|---------|--------------|---------------|----------------|
| 🥇 1º | - | - | - |
| 🥈 2º | - | - | - |
| 🥉 3º | - | - | - |

### **🎉 Formas de Reconhecimento**

#### **1. No Código**
- Créditos em docstrings de funcionalidades
- Menção em CHANGELOG.md
- Listagem em CONTRIBUTORS.md

#### **2. Na Documentação**
- Menção especial em tutoriais criados
- Créditos em exemplos desenvolvidos
- Destaque na wiki

#### **3. Na Comunidade**
- Menção em redes sociais
- Convite para apresentações
- Participação em decisões técnicas

---

## 📞 Contato e Suporte

### **💬 Canais de Comunicação**

#### **Para Contribuidores**
- 🐙 **GitHub Issues**: Para bugs e sugestões
- 📧 **Email**: Para questões privadas
- 💬 **Discussions**: Para perguntas da comunidade

#### **Para Maintainers**
- 📋 **Project Board**: Acompanhamento de tarefas
- 🎯 **Milestones**: Planejamento de releases
- 📊 **Wiki**: Documentação interna

### **⏰ Tempos de Resposta**

| Tipo | Tempo Esperado | Prioridade |
|------|----------------|------------|
| 🐛 Bug Crítico | 24h | Alta |
| 🆕 Nova Funcionalidade | 1 semana | Média |
| 📚 Documentação | 3 dias | Média |
| ❓ Questões Gerais | 1 semana | Baixa |

---

## 📜 Código de Conduta

### **🤝 Nossos Compromissos**

Nós, como membros, contribuidores e líderes, nos comprometemos a fazer da participação em nossa comunidade uma experiência livre de assédio para todos, independentemente de idade, tamanho corporal, deficiência visível ou invisível, etnia, características sexuais, identidade e expressão de gênero, nível de experiência, educação, status socioeconômico, nacionalidade, aparência pessoal, raça, religião ou identidade e orientação sexual.

### **✅ Comportamentos Esperados**

- 🤝 Demonstrar empatia e bondade com outras pessoas
- 🎯 Ser respeitoso com opiniões, pontos de vista e experiências diferentes
- 📝 Dar e aceitar feedback construtivo graciosamente
- 🔄 Aceitar responsabilidade e pedir desculpas aos afetados por nossos erros
- 🌟 Focar no que é melhor não apenas para nós como indivíduos, mas para a comunidade como um todo

### **❌ Comportamentos Inaceitáveis**

- 💬 Uso de linguagem ou imagens sexualizadas e atenção ou avanços sexuais de qualquer tipo
- 👎 Trolling, comentários insultuosos ou depreciativos e ataques pessoais ou políticos
- 📧 Assédio público ou privado
- 🔒 Publicar informações privadas de outras pessoas sem permissão explícita
- 🚫 Outras condutas que poderiam razoavelmente ser consideradas inadequadas em um ambiente profissional

---

## 🚀 Primeiros Passos para Novos Contribuidores

### **🎯 Guia Rápido de Início**

#### **1. Issues "Good First Issue"**
Procure por issues marcadas com `good first issue` - são perfeitas para começar!

#### **2. Documentação**
Contribuições em documentação são sempre bem-vindas e uma ótima forma de conhecer o projeto.

#### **3. Exemplos**
Criar novos exemplos de uso é uma excelente maneira de contribuir.

#### **4. Testes**
Adicionar testes sempre ajuda a melhorar a qualidade do projeto.

### **🆘 Precisa de Ajuda?**

- 📖 Consulte nossa [Wiki](WIKI.md)
- ❓ Leia o [FAQ](FAQ.md)
- 💬 Abra uma Discussion no GitHub
- 📧 Entre em contato com os maintainers

---

> 🙏 **Obrigado por contribuir com o Mangaba AI!** 
> 
> Sua participação é fundamental para tornar este projeto ainda melhor para toda a comunidade brasileira de desenvolvedores.

---

*Última atualização: Dezembro 2024 | Versão: 1.0*