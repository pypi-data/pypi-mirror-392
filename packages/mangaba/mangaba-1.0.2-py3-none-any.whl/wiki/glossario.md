# 📝 Glossário de Termos

Este glossário define todos os termos técnicos, conceitos e siglas usados no projeto Mangaba AI, organizados alfabeticamente para facilitar a consulta.

## 📋 Índice Alfabético

[**A**](#a) | [**B**](#b) | [**C**](#c) | [**D**](#d) | [**E**](#e) | [**F**](#f) | [**G**](#g) | [**H**](#h) | [**I**](#i) | [**J**](#j) | [**K**](#k) | [**L**](#l) | [**M**](#m) | [**N**](#n) | [**O**](#o) | [**P**](#p) | [**Q**](#q) | [**R**](#r) | [**S**](#s) | [**T**](#t) | [**U**](#u) | [**V**](#v) | [**W**](#w) | [**X**](#x) | [**Y**](#y) | [**Z**](#z)

---

## A

### **A2A (Agent-to-Agent)**
Protocolo de comunicação que permite que múltiplos agentes de IA se comuniquem entre si de forma estruturada e eficiente.

**Exemplo**: Um agente tradutor enviando texto processado para um agente analisador.

**Veja também**: [Protocolo A2A](exemplos-protocolos.md#-protocolo-a2a), MCP

### **Agente (Agent)**
Uma instância do MangabaAgent que encapsula capacidades de IA, protocolos de comunicação e contexto. É a unidade básica de processamento do sistema.

**Exemplo**: 
```python
agente = MangabaAgent(agent_name="AssistenteVirtual")
```

**Veja também**: MangabaAgent, Instância

### **Agnóstico (Provider Agnostic)**
Característica do Mangaba AI que permite usar diferentes provedores de IA (Google, OpenAI, etc.) sem alterar o código principal.

**Exemplo**: Trocar de Google Gemini para OpenAI GPT apenas mudando configurações.

**Veja também**: Provedor de IA, API

### **API (Application Programming Interface)**
Interface que permite comunicação entre diferentes sistemas de software. No Mangaba AI, usada para acessar serviços de IA externa.

**Exemplo**: Google Generative AI API, OpenAI API

**Veja também**: API Key, Endpoint

### **API Key**
Chave de autenticação única que permite acesso a serviços de IA externa. Essencial para o funcionamento do sistema.

**Exemplo**: `GOOGLE_API_KEY=AIzaSyC...`

**Veja também**: Autenticação, Configuração

### **Async/Await**
Padrão de programação assíncrona que permite execução não-bloqueante de operações, melhorando performance em operações I/O.

**Exemplo**:
```python
async def processar_multiplos():
    resultado = await agent.chat_async("Olá")
```

**Veja também**: Concorrência, Performance

---

## B

### **Backoff Exponencial**
Estratégia de retry que aumenta progressivamente o tempo de espera entre tentativas (1s, 2s, 4s, 8s...).

**Exemplo**: Usado em falhas de API para evitar sobrecarga.

**Veja também**: Retry, Rate Limiting, Resilência

### **Broadcast**
Tipo de comunicação A2A onde uma mensagem é enviada simultaneamente para múltiplos agentes.

**Exemplo**:
```python
agente.broadcast_message("Sistema será reiniciado", ["Agent1", "Agent2"])
```

**Veja também**: A2A, Multicast, Comunicação

### **Builder Pattern**
Padrão de design usado para construir objetos complexos passo a passo, usado na criação avançada de agentes.

**Exemplo**: ConstrutorDeAgente no código de melhores práticas.

**Veja também**: Design Patterns, Factory Pattern

---

## C

### **Cache**
Sistema de armazenamento temporário que guarda resultados de operações para evitar reprocessamento.

**Exemplo**: Cache de traduções para evitar traduzir o mesmo texto múltiplas vezes.

**Veja também**: Performance, TTL, Hit/Miss

### **Chat**
Função principal do agente para conversação natural com usuários, mantendo contexto conversacional.

**Exemplo**:
```python
resposta = agente.chat("Como está o tempo?", use_context=True)
```

**Veja também**: Contexto, MCP, Conversação

### **Circuit Breaker**
Padrão de design que previne falhas em cascata ao "abrir" temporariamente conexões com serviços que estão falhando.

**Estados**: Fechado (normal), Aberto (bloqueando), Meio-Aberto (testando)

**Veja também**: Resilência, Timeout, A2A

### **Contexto (Context)**
Informação de fundo que o agente mantém sobre conversas anteriores, preferências do usuário, e estado da sessão.

**Tipos**: Sistema, Usuário, Sessão, Tarefa, Temporário

**Veja também**: MCP, Memória, Sessão

### **Context Type**
Categorização do contexto para organização e priorização (user_profile, chat_history, business_rule, etc.).

**Exemplo**:
```python
agent.mcp_protocol.add_context(
    content="Usuário prefere respostas concisas",
    context_type="user_preference"
)
```

**Veja também**: MCP, Contexto, Prioridade

---

## D

### **Deploy**
Processo de colocar o sistema em produção, tornando-o disponível para usuários finais.

**Métodos**: Docker, Kubernetes, Cloud, VM

**Veja também**: Produção, Docker, CI/CD

### **Docker**
Plataforma de containerização que empacota aplicações com suas dependências para execução consistente.

**Exemplo**: `docker build -t mangaba-ai .`

**Veja também**: Container, Deploy, Produção

---

## E

### **Endpoint**
URL específica de uma API que responde a requisições HTTP para uma funcionalidade específica.

**Exemplo**: `/api/chat`, `/api/analyze`

**Veja também**: API, REST, HTTP

### **Environment (Ambiente)**
Conjunto de configurações e recursos onde o sistema executa (desenvolvimento, teste, produção).

**Exemplo**: `.env.development`, `.env.production`

**Veja também**: Configuração, Variáveis de Ambiente

---

## F

### **Factory Pattern**
Padrão de design que cria objetos sem especificar sua classe exata, usado para criar diferentes tipos de agentes.

**Exemplo**: FabricaDeAgentes no código de melhores práticas.

**Veja também**: Builder Pattern, Design Patterns

### **Fallback**
Mecanismo de contingência que fornece funcionalidade alternativa quando o sistema principal falha.

**Exemplo**: Usar cache quando API está indisponível.

**Veja também**: Resilência, Circuit Breaker

---

## G

### **Gemini**
Modelo de IA generativa do Google usado como provedor padrão no Mangaba AI.

**Variantes**: gemini-pro, gemini-pro-vision

**Veja também**: Provedor de IA, Google AI, API

---

## H

### **Handler**
Função que processa tipos específicos de mensagens ou eventos no sistema A2A.

**Exemplo**:
```python
def handler_analise(message):
    return processar_analise(message.content)
```

**Veja também**: A2A, Evento, Callback

### **Health Check**
Verificação automática do estado do sistema para garantir que está funcionando corretamente.

**Exemplo**: Teste de conectividade com APIs, banco de dados, etc.

**Veja também**: Monitoramento, Status

---

## I

### **Instância (Instance)**
Uma ocorrência específica de um agente em execução, com sua própria memória e estado.

**Exemplo**: Múltiplas instâncias do mesmo tipo de agente para load balancing.

**Veja também**: Agente, Pool, Escalabilidade

---

## J

### **JSON (JavaScript Object Notation)**
Formato de dados usado para comunicação entre agentes e armazenamento de configurações.

**Exemplo**:
```json
{
  "action": "analyze",
  "params": {"text": "documento"}
}
```

**Veja também**: Serialização, A2A, API

---

## L

### **Load Balancer**
Sistema que distribui requisições entre múltiplos agentes para otimizar performance e disponibilidade.

**Algoritmos**: Round Robin, Least Connections, Weighted Random

**Veja também**: Escalabilidade, Performance, Pool

### **Logging**
Sistema de registro de eventos e erros para debugging e monitoramento.

**Níveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Veja também**: Debug, Monitoramento, Observabilidade

---

## M

### **MangabaAgent**
Classe principal do sistema que implementa um agente de IA com capacidades de chat, análise, tradução e comunicação.

**Exemplo**:
```python
agent = MangabaAgent(agent_name="MeuAssistente")
```

**Veja também**: Agente, Classe, Core

### **MCP (Model Context Protocol)**
Protocolo que gerencia o contexto e memória dos agentes, permitindo conversas contínuas e inteligentes.

**Funcionalidades**: Armazenamento, Busca, Priorização, Sessões

**Veja também**: Contexto, Memória, Protocolo

### **Métricas**
Medições quantitativas do desempenho do sistema (latência, throughput, taxa de erro, etc.).

**Exemplos**: Tempo de resposta, Requisições por minuto, Taxa de sucesso

**Veja também**: Monitoramento, Performance, KPI

### **Multicast**
Tipo de comunicação onde uma mensagem é enviada para um grupo específico de destinatários.

**Diferença do Broadcast**: Multicast é para grupo específico, Broadcast é para todos.

**Veja também**: Broadcast, A2A, Comunicação

---

## O

### **Observabilidade**
Capacidade de entender o estado interno do sistema através de logs, métricas e traces.

**Pilares**: Logs, Métricas, Distributed Tracing

**Veja também**: Monitoring, Debugging, Logs

---

## P

### **Pipeline**
Sequência de processamento onde a saída de um agente serve como entrada para o próximo.

**Exemplo**: Extrator → Limpador → Analisador → Relatório

**Veja também**: Workflow, A2A, Chain

### **Pool de Agentes**
Conjunto de agentes pré-criados disponíveis para processamento paralelo de requisições.

**Benefícios**: Melhor utilização de recursos, redução de latência

**Veja também**: Load Balancer, Performance, Escalabilidade

### **Prioridade (Priority)**
Valor numérico que determina a importância de um contexto no protocolo MCP.

**Escala**: Geralmente 1-10, onde 10 é máxima prioridade

**Veja também**: MCP, Contexto, Context Type

### **Protocolo**
Conjunto de regras que define como diferentes componentes do sistema se comunicam.

**Tipos no Mangaba**: A2A (comunicação), MCP (contexto)

**Veja também**: A2A, MCP, Comunicação

### **Provedor de IA (AI Provider)**
Serviço externo que fornece capacidades de inteligência artificial (Google, OpenAI, etc.).

**Exemplos**: Google Generative AI, OpenAI GPT, Anthropic Claude

**Veja também**: API, Agnóstico, Gemini

---

## Q

### **Query**
Consulta ou requisição feita ao sistema, geralmente para buscar informações ou executar ações.

**Tipos**: Busca de contexto, Requisição A2A, Chat

**Veja também**: Requisição, API, Busca

---

## R

### **Rate Limiting**
Técnica que limita o número de requisições que um usuário pode fazer em um período de tempo.

**Objetivo**: Prevenir abuso, controlar custos, garantir qualidade

**Veja também**: Throttling, Custos, API

### **Resilência**
Capacidade do sistema de continuar funcionando mesmo quando componentes falham.

**Técnicas**: Circuit Breaker, Retry, Fallback, Timeout

**Veja também**: Circuit Breaker, Timeout, Fallback

### **REST (Representational State Transfer)**
Estilo arquitetural para APIs web que usa métodos HTTP padrão.

**Métodos**: GET, POST, PUT, DELETE

**Veja também**: API, HTTP, Endpoint

### **Retry**
Mecanismo que tenta executar uma operação novamente após uma falha.

**Estratégias**: Linear, Exponential Backoff, Fixed Interval

**Veja também**: Backoff Exponencial, Resilência, Timeout

---

## S

### **Sessão (Session)**
Contexto isolado que mantém informações específicas de uma interação ou usuário.

**Exemplo**: Cada usuário tem sua própria sessão com contexto separado

**Veja também**: MCP, Contexto, Isolamento

### **SQLite**
Banco de dados leve usado pelo MCP para armazenar contexto persistente.

**Vantagens**: Sem servidor, arquivo único, ACID compliance

**Veja também**: MCP, Persistência, Banco de dados

---

## T

### **Tags**
Etiquetas que categorizam contexto para facilitar busca e organização.

**Exemplo**: ["usuario", "preferencia", "idioma"]

**Veja também**: MCP, Contexto, Metadados

### **Timeout**
Tempo limite para uma operação completar antes de ser considerada como falha.

**Exemplo**: Timeout de 30 segundos para chamadas de API

**Veja também**: Resilência, API, Circuit Breaker

### **TTL (Time To Live)**
Tempo que um item permanece válido no cache antes de expirar.

**Exemplo**: Cache de 1 hora (TTL=3600 segundos)

**Veja também**: Cache, Expiração, Performance

---

## U

### **Use Context**
Parâmetro que determina se o agente deve usar contexto anterior na operação.

**Exemplo**:
```python
# Com contexto
resposta = agent.chat("E sobre Python?", use_context=True)

# Sem contexto  
resposta = agent.chat("E sobre Python?", use_context=False)
```

**Veja também**: MCP, Contexto, Chat

---

## V

### **Variáveis de Ambiente**
Configurações do sistema definidas fora do código, geralmente no arquivo `.env`.

**Exemplos**: `GOOGLE_API_KEY`, `LOG_LEVEL`, `ENVIRONMENT`

**Veja também**: Configuração, Environment, Segurança

---

## W

### **WebSocket**
Protocolo de comunicação bidirecional em tempo real entre cliente e servidor.

**Uso**: Interfaces web interativas, notificações em tempo real

**Veja também**: Real-time, Comunicação, Socket.IO

### **Workflow**
Sequência de tarefas ou processos executados pelos agentes para atingir um objetivo.

**Exemplo**: Workflow de análise de documentos

**Veja também**: Pipeline, A2A, Automação

---

## 🔍 Termos por Categoria

### 📡 **Protocolos e Comunicação**
- A2A (Agent-to-Agent)
- MCP (Model Context Protocol)
- Broadcast
- Multicast
- Handler
- Endpoint
- WebSocket

### 🤖 **Agentes e IA**
- MangabaAgent
- Agente (Agent)
- Instância (Instance)
- Provedor de IA
- Gemini
- API Key
- Agnóstico

### 🧠 **Contexto e Memória**
- Contexto (Context)
- Context Type
- Sessão (Session)
- Prioridade (Priority)
- Tags
- Use Context
- TTL

### ⚡ **Performance e Escalabilidade**
- Cache
- Pool de Agentes
- Load Balancer
- Métricas
- Pipeline
- Async/Await
- Rate Limiting

### 🛡️ **Confiabilidade e Segurança**
- Circuit Breaker
- Resilência
- Retry
- Backoff Exponencial
- Timeout
- Fallback
- Health Check

### 🔧 **Desenvolvimento e Deploy**
- Docker
- Environment
- Deploy
- Variáveis de Ambiente
- Logging
- Debug
- REST

### 📊 **Dados e Formatos**
- JSON
- SQLite
- Query
- Serialização
- API
- HTTP

---

## 🆘 Não Encontrou um Termo?

Se você não encontrou um termo específico:

1. **🔍 Use Ctrl+F** para buscar na página
2. **📖 Consulte a [Documentação](README.md)** para contexto adicional  
3. **💡 Veja os [Exemplos](exemplos-protocolos.md)** para uso prático
4. **❓ Consulte o [FAQ](faq.md)** para dúvidas comuns
5. **🐛 Abra uma [Issue](https://github.com/Mangaba-ai/mangaba_ai/issues)** para sugerir novos termos

---

> 📚 **Dica de Estudo**: Use este glossário como referência enquanto lê a documentação técnica para melhor compreensão.

> 🔄 **Glossário Vivo**: Este documento é atualizado continuamente com novos termos e conceitos do projeto.