# 📝 Glossário de Termos - Mangaba AI

Este glossário define todos os termos técnicos e conceitos utilizados no projeto Mangaba AI. Os termos estão organizados alfabeticamente para facilitar a consulta.

## 📋 Navegação Rápida

**Por Categoria:**
- [🤖 Agentes e IA](#-agentes-e-ia)
- [🌐 Protocolos](#-protocolos)
- [🔧 Técnicos](#-técnicos)
- [🏢 Negócios](#-negócios)

**Por Letra:**
[A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [G](#g) | [H](#h) | [I](#i) | [J](#j) | [K](#k) | [L](#l) | [M](#m) | [N](#n) | [O](#o) | [P](#p) | [Q](#q) | [R](#r) | [S](#s) | [T](#t) | [U](#u) | [V](#v) | [W](#w) | [X](#x) | [Y](#y) | [Z](#z)

---

## A

### **Agent-to-Agent (A2A)**
**Definição**: Protocolo de comunicação que permite que múltiplos agentes de IA se comuniquem diretamente entre si, compartilhando informações e coordenando tarefas.

**Exemplo de uso**: Um agente especializado em análise financeira pode solicitar a um agente redator que crie um relatório baseado em seus dados de análise.

**Veja também**: [Protocolo A2A](#protocolo-a2a), [Broadcast](#broadcast)

### **Agente**
**Definição**: Uma instância do sistema Mangaba AI capaz de processar linguagem natural, analisar textos, traduzir idiomas e se comunicar com outros agentes.

**Características**:
- 🧠 Processamento de linguagem natural
- 🔄 Comunicação A2A
- 💾 Gerenciamento de contexto MCP
- 🎯 Especialização em domínios específicos

**Exemplo**:
```python
agente = MangabaAgent(
    api_key="sua_chave",
    agent_id="agente_financeiro",
    enable_mcp=True
)
```

### **API Key**
**Definição**: Chave de autenticação fornecida pelo Google Cloud que permite acesso aos serviços do Google Generative AI (Gemini).

**Como obter**: Através do [Google AI Studio](https://makersuite.google.com/app/apikey)

**Segurança**: Sempre armazene em variáveis de ambiente, nunca diretamente no código.

### **Análise de Texto**
**Definição**: Capacidade do agente de examinar, interpretar e extrair insights de textos usando instruções específicas.

**Exemplo**:
```python
resultado = agente.analyze_text(
    text="Relatório financeiro trimestral...",
    instruction="Identifique tendências e riscos principais"
)
```

### **Assíncrono (Async)**
**Definição**: Execução não-bloqueante de operações, permitindo que múltiplas tarefas sejam processadas simultaneamente.

**Uso no Mangaba**: Comunicação A2A, processamento de múltiplas requisições, operações de I/O.

---

## B

### **Broadcast**
**Definição**: Envio de uma mensagem de um agente para múltiplos agentes simultaneamente através do protocolo A2A.

**Exemplo**:
```python
resultados = agente.broadcast_message(
    message="Reunião às 15h hoje",
    tags=["meeting", "urgent"]
)
```

**Diferença do send**: Send é 1:1, broadcast é 1:N (um para muitos).

### **Builder Pattern**
**Definição**: Padrão de design usado para construir objetos complexos passo a passo, comum na configuração de agentes.

**Exemplo**:
```python
agente = (AgentBuilder()
          .with_mcp(True)
          .with_model("gemini-pro")
          .with_cache(True)
          .build())
```

---

## C

### **Cache**
**Definição**: Sistema de armazenamento temporário que guarda respostas já processadas para evitar chamadas desnecessárias à API.

**Benefícios**:
- ⚡ Reduz tempo de resposta
- 💰 Diminui custos da API
- 🔄 Melhora eficiência geral

**Implementação**:
```python
cache = ResponseCache(duration=3600)  # 1 hora
agente = CachedMangabaAgent(cache=cache)
```

### **Context Type**
**Definição**: Classificação dos tipos de contexto no protocolo MCP.

**Tipos disponíveis**:
- `USER`: Informações sobre o usuário
- `TASK`: Dados de tarefas específicas
- `SYSTEM`: Configurações e estado do sistema
- `CONVERSATION`: Histórico de conversas

### **Context Priority**
**Definição**: Nível de importância atribuído a um contexto MCP.

**Níveis**:
- `HIGH`: Alta prioridade, sempre mantido
- `MEDIUM`: Prioridade média, mantido conforme espaço
- `LOW`: Baixa prioridade, primeiro a ser removido

### **Contexto**
**Definição**: Informações armazenadas pelo protocolo MCP que influenciam as respostas do agente, incluindo histórico de conversas, preferências do usuário e dados de tarefas.

**Exemplo de uso**: Se um usuário mencionou que trabalha em marketing, futuras perguntas considerarão essa informação.

---

## D

### **Deploy**
**Definição**: Processo de colocar o sistema Mangaba AI em produção, incluindo configuração de ambiente, instalação de dependências e validação de funcionamento.

**Scripts disponíveis**:
- `quick_setup.py`: Deploy automatizado
- `validate_env.py`: Validação pós-deploy
- `health_check.py`: Monitoramento contínuo

### **Docstring**
**Definição**: Documentação embutida no código Python que descreve função, parâmetros, retorno e exemplos de uso.

**Padrão do projeto**:
```python
def processar_texto(texto: str, instrucao: str) -> str:
    """
    Processa texto usando o agente Mangaba.
    
    Args:
        texto (str): Texto a ser processado
        instrucao (str): Instrução para processamento
        
    Returns:
        str: Texto processado
    """
```

---

## E

### **Environment Variables**
**Definição**: Variáveis do sistema operacional usadas para configurar o Mangaba AI sem expor informações sensíveis no código.

**Principais variáveis**:
```bash
GOOGLE_API_KEY=sua_chave_google
MODEL_NAME=gemini-pro
LOG_LEVEL=INFO
AGENT_ID_PREFIX=prod_
```

### **Error Handling**
**Definição**: Tratamento de erros específico do Mangaba AI, incluindo exceções customizadas para diferentes tipos de falha.

**Exceções principais**:
- `ErroMangabaAPI`: Erro geral da API
- `ErroConfiguracaoAgente`: Configuração inválida
- `ErroProtocoloA2A`: Falha na comunicação A2A
- `ErroContextoMCP`: Problema no gerenciamento de contexto

---

## F

### **Factory Pattern**
**Definição**: Padrão de design para criar agentes especializados de forma padronizada.

**Exemplo**:
```python
class AgentFactory:
    @staticmethod
    def criar_agente_medico():
        return MangabaAgent(
            agent_id="medico_especialista",
            model="gemini-pro"
        )
```

### **Framework**
**Definição**: O Mangaba AI como um todo - conjunto de ferramentas, protocolos e bibliotecas para desenvolvimento de sistemas de agentes de IA.

---

## G

### **Gemini**
**Definição**: Modelo de inteligência artificial da Google usado como base pelos agentes Mangaba AI.

**Modelos disponíveis**:
- `gemini-pro`: Texto e raciocínio geral
- `gemini-pro-vision`: Texto e imagens
- `gemini-ultra`: Versão mais avançada (quando disponível)

### **Google Generative AI**
**Definição**: Plataforma de IA generativa da Google que fornece os modelos Gemini através de APIs REST.

**Documentação oficial**: [ai.google.dev](https://ai.google.dev)

---

## H

### **Handler**
**Definição**: Função especializada que processa tipos específicos de mensagens no protocolo A2A.

**Exemplo**:
```python
@agente.a2a_protocol.register_handler("analisar_documento")
def handle_analise(message):
    documento = message.content.get("texto")
    return agente.analyze_text(documento, "análise completa")
```

### **Health Check**
**Definição**: Verificação automática do status e funcionamento dos agentes e protocolos.

**Endpoint típico**: `GET /health`
**Resposta**: Status (healthy/unhealthy/degraded) e métricas

---

## I

### **Integration Tests**
**Definição**: Testes que verificam a interação entre diferentes componentes do sistema, como comunicação A2A entre agentes.

**Exemplo**: Teste que verifica se dois agentes conseguem trocar mensagens com sucesso.

### **Instruction**
**Definição**: Comando ou diretriz fornecida ao agente durante análise de texto, especificando que tipo de processamento deve ser realizado.

**Exemplos**:
- "Analise o sentimento do texto"
- "Extraia os pontos principais"
- "Traduza para linguagem técnica"

---

## J

### **JSON**
**Definição**: Formato de dados usado na comunicação entre agentes e armazenamento de contextos MCP.

**Exemplo de mensagem A2A**:
```json
{
  "sender_id": "agente1",
  "target_id": "agente2", 
  "action": "analyze",
  "params": {"text": "texto para análise"}
}
```

---

## L

### **Load Balancing**
**Definição**: Distribuição de carga entre múltiplos agentes para otimizar performance e evitar sobrecarga.

**Estratégias**:
- Round-robin: Distribuição sequencial
- Least-load: Agente com menor carga
- Capability-based: Baseado em especialização

### **Logging**
**Definição**: Sistema de registro de eventos e atividades dos agentes para monitoramento e debug.

**Níveis**:
- `DEBUG`: Informações detalhadas
- `INFO`: Eventos normais
- `WARNING`: Situações de atenção
- `ERROR`: Erros que impedem funcionamento

---

## M

### **Mangaba AI**
**Definição**: Framework brasileiro open-source para criação de agentes de IA com protocolos A2A e MCP, otimizado para português brasileiro.

**Origem do nome**: Mangaba é uma fruta nativa do Brasil, simbolizando a origem nacional do projeto.

### **MangabaAgent**
**Definição**: Classe principal que representa um agente no sistema, combinando capacidades de IA, comunicação A2A e gerenciamento de contexto MCP.

**Principais métodos**:
- `chat()`: Conversa geral
- `analyze_text()`: Análise específica
- `translate()`: Tradução
- `send_agent_request()`: Comunicação A2A

### **MCP (Model Context Protocol)**
**Definição**: Protocolo proprietário do Mangaba AI para gerenciamento inteligente de contexto, permitindo que agentes "lembrem" de informações relevantes.

**Funcionalidades**:
- 💾 Armazenamento de contexto
- 🔍 Busca por relevância
- 🏷️ Organização por tags
- ⏰ Limpeza automática

### **Metrics**
**Definição**: Métricas de performance e uso coletadas automaticamente pelo sistema.

**Métricas principais**:
- Tempo de resposta
- Número de requisições
- Uso de memória
- Taxa de erro

### **Model Context Protocol** → Veja [MCP](#mcp-model-context-protocol)

---

## P

### **Performance**
**Definição**: Medida da eficiência e velocidade do sistema Mangaba AI.

**Fatores que influenciam**:
- Tamanho do contexto MCP
- Complexidade das instruções
- Número de agentes conectados
- Cache de respostas

### **Prompt**
**Definição**: Texto enviado ao modelo de IA (Gemini) contendo a pergunta do usuário, contexto relevante e instruções específicas.

**Estrutura típica**:
```
[CONTEXTO MCP]
[INSTRUÇÃO ESPECÍFICA]
[PERGUNTA DO USUÁRIO]
```

### **Protocolo**
**Definição**: Conjunto de regras e formatos para comunicação entre componentes do sistema.

**Protocolos do Mangaba**:
- **A2A**: Comunicação entre agentes
- **MCP**: Gerenciamento de contexto

### **Protocolo A2A**
**Definição**: Sistema de comunicação que permite que agentes se conectem e troquem mensagens diretamente, formando redes distribuídas de IA.

**Características**:
- 🔄 Comunicação bidirecional
- 📡 Suporte a broadcast
- 🎯 Handlers especializados
- 🌐 Conexões de rede

### **Pull Request (PR)**
**Definição**: Proposta de mudança no código do projeto, submetida por contribuidores para revisão e possível incorporação.

**Processo típico**:
1. Fork do repositório
2. Implementação da mudança
3. Criação do PR
4. Code review
5. Merge (se aprovado)

---

## Q

### **Query**
**Definição**: Consulta ou pergunta feita ao agente, seja através de chat direto ou busca de contexto MCP.

### **Queue**
**Definição**: Fila de mensagens ou tarefas aguardando processamento, especialmente relevante em cenários de alta carga.

---

## R

### **Rate Limiting**
**Definição**: Controle da frequência de requisições para evitar exceder limites da API Google e otimizar custos.

**Implementação típica**:
```python
@rate_limit(calls_per_minute=30)
def funcao_limitada():
    return agente.chat("pergunta")
```

### **Response**
**Definição**: Resposta gerada pelo agente após processar uma requisição, seja de chat, análise ou tradução.

### **RPM (Requests Per Minute)**
**Definição**: Métrica que mede quantas requisições por minuto são feitas à API Google.

**Limites típicos**:
- Gratuito: 15 RPM
- Pago: Configurável (padrão 60 RPM)

---

## S

### **Session**
**Definição**: Sessão MCP que agrupa contextos relacionados, permitindo isolamento de diferentes conversas ou usuários.

**Operações**:
- Criar nova sessão
- Adicionar contextos à sessão
- Buscar contextos na sessão
- Limpar/deletar sessão

### **Setup**
**Definição**: Processo de configuração inicial do ambiente Mangaba AI.

**Scripts disponíveis**:
- `quick_setup.py`: Configuração automática
- `setup_env.py`: Configuração manual
- `validate_env.py`: Validação da configuração

---

## T

### **Tag**
**Definição**: Rótulo usado para categorizar e buscar contextos MCP.

**Exemplos de tags**:
- `usuario`, `perfil`
- `financeiro`, `marketing`
- `tarefa`, `analise`
- `traducao`, `documento`

### **Target Language**
**Definição**: Idioma de destino especificado em operações de tradução.

**Exemplo**:
```python
traducao = agente.translate(
    text="Hello world",
    target_language="português brasileiro"
)
```

### **Thread-Safe**
**Definição**: Característica de código que pode ser executado simultaneamente por múltiplas threads sem causar problemas.

**Relevante para**: Comunicação A2A, operações MCP, cache compartilhado.

### **Timeout**
**Definição**: Tempo limite para operações, após o qual são consideradas falhadas.

**Aplicações**:
- Requisições à API Google
- Comunicação A2A
- Operações de cache

### **Type Hints**
**Definição**: Anotações de tipo em Python que indicam os tipos esperados para parâmetros e retornos.

**Exemplo**:
```python
def processar(texto: str, opcoes: Dict[str, Any]) -> Optional[str]:
    pass
```

---

## U

### **Unit Tests**
**Definição**: Testes que verificam o funcionamento de componentes individuais do sistema.

**Exemplo**: Teste que verifica se a função `chat()` retorna uma string não-vazia.

### **User Context**
**Definição**: Tipo específico de contexto MCP que armazena informações sobre o usuário.

**Exemplos**:
- Nome e cargo
- Empresa e setor
- Preferências de resposta
- Histórico de interações

---

## V

### **Validation**
**Definição**: Verificação de que configurações, parâmetros e estados estão corretos.

**Tipos de validação**:
- Configuração de ambiente
- Parâmetros de entrada
- Formato de mensagens A2A
- Integridade de contextos MCP

### **Verbose**
**Definição**: Modo de operação que fornece informações detalhadas sobre o que está acontecendo.

**Uso**: Debug, troubleshooting, monitoramento de desenvolvimento.

---

## W

### **WebSocket**
**Definição**: Protocolo de comunicação bidirecional usado em implementações avançadas de A2A para conexões persistentes.

### **Wrapper**
**Definição**: Função ou classe que encapsula outra para adicionar funcionalidades extras.

**Exemplo**: `CachedMangabaAgent` é um wrapper que adiciona cache ao `MangabaAgent`.

---

## 🤖 Agentes e IA

### **Termos Relacionados a Agentes**
- [Agente](#agente)
- [MangabaAgent](#mangabaagent)
- [Handler](#handler)
- [Especialização](#agente)

### **Termos de IA e ML**
- [Gemini](#gemini)
- [Google Generative AI](#google-generative-ai)
- [Prompt](#prompt)
- [Instruction](#instruction)

---

## 🌐 Protocolos

### **A2A - Agent-to-Agent**
- [Agent-to-Agent (A2A)](#agent-to-agent-a2a)
- [Protocolo A2A](#protocolo-a2a)
- [Broadcast](#broadcast)
- [Handler](#handler)

### **MCP - Model Context Protocol**
- [MCP (Model Context Protocol)](#mcp-model-context-protocol)
- [Contexto](#contexto)
- [Context Type](#context-type)
- [Context Priority](#context-priority)
- [Session](#session)
- [Tag](#tag)

---

## 🔧 Técnicos

### **Desenvolvimento**
- [Framework](#framework)
- [API Key](#api-key)
- [Environment Variables](#environment-variables)
- [Type Hints](#type-hints)
- [Docstring](#docstring)

### **Arquitetura**
- [Factory Pattern](#factory-pattern)
- [Builder Pattern](#builder-pattern)
- [Thread-Safe](#thread-safe)
- [Wrapper](#wrapper)

### **Performance**
- [Cache](#cache)
- [Rate Limiting](#rate-limiting)
- [Load Balancing](#load-balancing)
- [Assíncrono (Async)](#assíncrono-async)

### **Qualidade**
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Validation](#validation)
- [Error Handling](#error-handling)

---

## 🏢 Negócios

### **Custos e Limites**
- [RPM (Requests Per Minute)](#rpm-requests-per-minute)
- [Rate Limiting](#rate-limiting)

### **Operações**
- [Deploy](#deploy)
- [Health Check](#health-check)
- [Logging](#logging)
- [Metrics](#metrics)

---

## 📞 Ainda Tem Dúvidas?

### **Não encontrou um termo?**
- 🔍 Use Ctrl+F para buscar na página
- 💬 Abra uma [discussion no GitHub](https://github.com/Mangaba-ai/mangaba_ai/discussions)
- 📚 Consulte a [documentação completa](WIKI.md)

### **Quer contribuir com o glossário?**
- ➕ Sugira novos termos via [Pull Request](CONTRIBUICAO.md)
- ✏️ Corrija definições existentes
- 📖 Adicione exemplos mais claros

---

> 💡 **Dica**: Use este glossário como referência rápida durante o desenvolvimento!

> 🔗 **Links úteis**: [Wiki](WIKI.md) | [FAQ](FAQ.md) | [Melhores Práticas](MELHORES_PRATICAS.md) | [Como Contribuir](CONTRIBUICAO.md)

---

*Última atualização: Dezembro 2024 | Versão: 1.0 | Total de termos: 80+*