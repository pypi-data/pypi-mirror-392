# 🏗️ Arquitetura Avançada

Este documento detalha a arquitetura interna do Mangaba AI, explicando como os componentes se integram e como o sistema funciona sob o capô.

## 📋 Índice

1. [Visão Geral da Arquitetura](#-visão-geral-da-arquitetura)
2. [Componentes Principais](#-componentes-principais)
3. [Fluxo de Dados](#-fluxo-de-dados)
4. [Protocolos Internos](#-protocolos-internos)
5. [Gerenciamento de Estado](#-gerenciamento-de-estado)
6. [Integração com Provedores](#-integração-com-provedores)
7. [Escalabilidade](#-escalabilidade)
8. [Segurança](#-segurança)

---

## 🎯 Visão Geral da Arquitetura

### Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                      │
│              (CLI, Web, API, Integrations)             │
├─────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                    │
│                   (MangabaAgent)                       │
├─────────────────────────────────────────────────────────┤
│                   PROTOCOL LAYER                       │
│               (MCP + A2A Protocols)                    │
├─────────────────────────────────────────────────────────┤
│                  PROCESSING LAYER                      │
│           (NLP, Context Management, Routing)           │
├─────────────────────────────────────────────────────────┤
│                   PROVIDER LAYER                       │
│            (Google AI, OpenAI, Anthropic)             │
├─────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE                        │
│         (SQLite, Logging, Cache, Networking)          │
└─────────────────────────────────────────────────────────┘
```

### Princípios Arquiteturais

1. **🔧 Modularidade**: Componentes independentes e intercambiáveis
2. **⚡ Performance**: Otimizado para baixa latência e alta throughput
3. **🛡️ Resilência**: Tolerante a falhas com recuperação automática
4. **📈 Escalabilidade**: Suporte horizontal e vertical
5. **🔒 Segurança**: Segurança por design em todas as camadas
6. **🔄 Extensibilidade**: Fácil adição de novos recursos

---

## 🧩 Componentes Principais

### 1. MangabaAgent - Core Engine

```python
class MangabaAgent:
    """
    Núcleo do sistema que orquestra todas as operações.
    
    Responsabilidades:
    - Gerenciar ciclo de vida do agente
    - Coordenar protocolos (MCP + A2A)
    - Interface com provedores de IA
    - Processamento de requisições
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_id = self._generate_agent_id()
        
        # Inicializar componentes
        self.mcp_protocol = self._init_mcp()
        self.ai_provider = self._init_ai_provider()
        self.protocols = {}
        self.middleware_stack = []
        
        # Estado interno
        self._session_context = {}
        self._performance_metrics = PerformanceMetrics()
```

### 2. Protocolo MCP - Context Management

```
MCP Architecture:
┌─────────────────────────────────────────────────┐
│                MCP Protocol                     │
├─────────────────┬───────────────┬───────────────┤
│   Context       │   Session     │   Storage     │
│   Manager       │   Manager     │   Engine      │
├─────────────────┼───────────────┼───────────────┤
│ • Add Context   │ • Create      │ • SQLite      │
│ • Search        │ • Isolate     │ • Indexing    │
│ • Prioritize    │ • Cleanup     │ • Retrieval   │
│ • Compress      │ • Restore     │ • Backup      │
└─────────────────┴───────────────┴───────────────┘
```

#### Context Storage Schema

```sql
-- Estrutura interna do banco de contexto
CREATE TABLE contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    session_id TEXT,
    content TEXT NOT NULL,
    context_type TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    tags TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    embeddings BLOB -- Vector embeddings para busca semântica
);

CREATE INDEX idx_agent_session ON contexts(agent_id, session_id);
CREATE INDEX idx_priority ON contexts(priority DESC);
CREATE INDEX idx_type ON contexts(context_type);
```

### 3. Protocolo A2A - Inter-Agent Communication

```
A2A Network Topology:
     ┌─────────┐         ┌─────────┐
     │ Agent A │◄────────┤Discovery│
     └─────┬───┘         │Service  │
           │             └─────────┘
       Message                │
       Queue               ┌─────────┐
           │               │ Agent C │
           ▼               └─────────┘
     ┌─────────┐                │
     │ Agent B │◄───────────────┘
     └─────────┘
```

#### Message Flow

```python
class A2AMessage:
    """Estrutura de mensagem A2A"""
    def __init__(self):
        self.message_id = str(uuid.uuid4())
        self.sender_id = None
        self.receiver_id = None
        self.message_type = None  # REQUEST, RESPONSE, BROADCAST, NOTIFICATION
        self.content = {}
        self.timestamp = time.time()
        self.priority = 1
        self.ttl = 300  # Time to live em segundos
        self.correlation_id = None  # Para req/resp tracking
```

---

## 🔄 Fluxo de Dados

### 1. Request Processing Pipeline

```
User Input → Validation → Context Retrieval → AI Processing → Response Assembly → Output

┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ User Input  │───▶│ Input        │───▶│ Context     │
│             │    │ Validation   │    │ Retrieval   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Response    │◄───│ Response     │◄───│ AI Provider │
│ Output      │    │ Assembly     │    │ Processing  │
└─────────────┘    └──────────────┘    └─────────────┘
```

### 2. Detailed Request Flow

```python
async def process_request(self, request: UserRequest) -> Response:
    """Pipeline completo de processamento de requisição"""
    
    # 1. Validação de entrada
    validated_input = await self._validate_input(request.content)
    
    # 2. Aplicar middlewares (rate limiting, auth, etc.)
    for middleware in self.middleware_stack:
        validated_input = await middleware.process(validated_input)
    
    # 3. Recuperar contexto relevante
    relevant_context = await self.mcp_protocol.search_relevant_context(
        query=validated_input.text,
        session_id=request.session_id,
        max_results=10
    )
    
    # 4. Construir prompt enriquecido
    enriched_prompt = self._build_prompt(
        user_input=validated_input.text,
        context=relevant_context,
        agent_personality=self._get_personality()
    )
    
    # 5. Chamar provedor de IA
    ai_response = await self.ai_provider.generate(
        prompt=enriched_prompt,
        temperature=0.7,
        max_tokens=2000
    )
    
    # 6. Pós-processar resposta
    processed_response = self._post_process_response(ai_response)
    
    # 7. Armazenar interação no contexto
    await self.mcp_protocol.add_context(
        content=f"User: {validated_input.text}\nAssistant: {processed_response}",
        context_type="conversation",
        session_id=request.session_id
    )
    
    # 8. Construir resposta final
    return Response(
        content=processed_response,
        metadata={
            "request_id": request.id,
            "processing_time": time.time() - request.timestamp,
            "context_used": len(relevant_context)
        }
    )
```

---

## 🔧 Protocolos Internos

### Event-Driven Architecture

```python
class EventBus:
    """Sistema de eventos interno"""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_history = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Registra handler para tipo de evento"""
        self.subscribers[event_type].append(handler)
    
    def publish(self, event: Event):
        """Publica evento para todos os subscribers"""
        self.event_history.append(event)
        
        for handler in self.subscribers[event.type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

# Eventos do sistema
class Events:
    AGENT_CREATED = "agent.created"
    CONTEXT_ADDED = "context.added"
    MESSAGE_RECEIVED = "message.received"
    AI_REQUEST_STARTED = "ai.request.started"
    AI_REQUEST_COMPLETED = "ai.request.completed"
    ERROR_OCCURRED = "error.occurred"
```

### Plugin Architecture

```python
class PluginManager:
    """Gerenciador de plugins extensível"""
    
    def __init__(self):
        self.plugins = {}
        self.hooks = defaultdict(list)
    
    def register_plugin(self, plugin: Plugin):
        """Registra novo plugin"""
        self.plugins[plugin.name] = plugin
        
        # Registrar hooks do plugin
        for hook_name, handler in plugin.get_hooks().items():
            self.hooks[hook_name].append(handler)
    
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """Executa todos os handlers de um hook"""
        results = []
        for handler in self.hooks[hook_name]:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Plugin hook error: {e}")
        return results

# Interface de plugin
class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def get_hooks(self) -> Dict[str, Callable]:
        pass
    
    def initialize(self):
        pass
    
    def cleanup(self):
        pass
```

---

## 💾 Gerenciamento de Estado

### State Management Strategy

```python
class StateManager:
    """Gerenciador centralizado de estado"""
    
    def __init__(self):
        self.agent_states = {}
        self.global_state = {}
        self.state_observers = []
    
    def get_agent_state(self, agent_id: str) -> AgentState:
        """Obtém estado específico do agente"""
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = AgentState(agent_id)
        return self.agent_states[agent_id]
    
    def update_state(self, agent_id: str, updates: Dict):
        """Atualiza estado e notifica observers"""
        state = self.get_agent_state(agent_id)
        old_state = state.snapshot()
        
        state.update(updates)
        
        # Notificar observers
        for observer in self.state_observers:
            observer.state_changed(agent_id, old_state, state.snapshot())

class AgentState:
    """Estado individual do agente"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.created_at = time.time()
        self.last_activity = time.time()
        
        # Estado operacional
        self.status = "active"  # active, idle, busy, error
        self.current_session = None
        self.active_protocols = set()
        
        # Métricas
        self.total_requests = 0
        self.total_errors = 0
        self.average_response_time = 0.0
        
        # Configuração
        self.personality = {}
        self.capabilities = set()
```

### Session Management

```python
class SessionManager:
    """Gerenciador de sessões de usuário"""
    
    def __init__(self):
        self.active_sessions = {}
        self.session_store = SQLiteSessionStore()
    
    def create_session(self, user_id: str) -> Session:
        """Cria nova sessão para usuário"""
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=time.time()
        )
        
        self.active_sessions[session.session_id] = session
        self.session_store.save(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Recupera sessão ativa ou do storage"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Tentar carregar do storage
        session = self.session_store.load(session_id)
        if session and not session.is_expired():
            self.active_sessions[session_id] = session
            return session
        
        return None
```

---

## 🔌 Integração com Provedores

### Provider Abstraction Layer

```python
class AIProvider(ABC):
    """Interface abstrata para provedores de IA"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def analyze_text(self, text: str, instruction: str) -> str:
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_limits(self) -> Dict[str, Any]:
        pass

class GoogleAIProvider(AIProvider):
    """Implementação para Google Generative AI"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        await self.rate_limiter.acquire()
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 1000)
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Google AI error: {e}")
            raise AIProviderError(f"Generation failed: {e}")

class ProviderManager:
    """Gerenciador de múltiplos provedores"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.fallback_chain = []
    
    def register_provider(self, name: str, provider: AIProvider, is_default: bool = False):
        """Registra novo provedor"""
        self.providers[name] = provider
        
        if is_default or not self.default_provider:
            self.default_provider = name
    
    async def generate_with_fallback(self, prompt: str, **kwargs) -> str:
        """Gera texto com fallback automático"""
        providers_to_try = [self.default_provider] + self.fallback_chain
        
        for provider_name in providers_to_try:
            if provider_name in self.providers:
                try:
                    return await self.providers[provider_name].generate_text(prompt, **kwargs)
                except Exception as e:
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    continue
        
        raise AIProviderError("All providers failed")
```

---

## 📈 Escalabilidade

### Horizontal Scaling

```python
class AgentCluster:
    """Cluster de agentes para escalabilidade horizontal"""
    
    def __init__(self, cluster_config: ClusterConfig):
        self.config = cluster_config
        self.agents = {}
        self.load_balancer = LoadBalancer()
        self.service_discovery = ServiceDiscovery()
    
    def add_agent_node(self, node_config: NodeConfig):
        """Adiciona novo nó ao cluster"""
        agent = MangabaAgent(
            agent_name=f"{self.config.cluster_name}-{node_config.node_id}"
        )
        
        # Configurar para cluster
        agent.add_middleware(ClusterMiddleware(self.service_discovery))
        agent.add_protocol(A2AProtocol(
            agent_id=agent.agent_name,
            cluster_mode=True,
            discovery_service=self.service_discovery
        ))
        
        self.agents[node_config.node_id] = agent
        self.load_balancer.register_node(node_config.node_id, agent)
    
    async def process_distributed(self, request: Request) -> Response:
        """Processa requisição distribuída"""
        # Selecionar melhor nó
        selected_node = self.load_balancer.select_node(request)
        
        # Processar no nó selecionado
        agent = self.agents[selected_node]
        return await agent.process_request(request)

class LoadBalancer:
    """Load balancer para distribuição de carga"""
    
    def __init__(self, algorithm: str = "least_connections"):
        self.algorithm = algorithm
        self.nodes = {}
        self.metrics = MetricsCollector()
    
    def select_node(self, request: Request) -> str:
        """Seleciona melhor nó baseado no algoritmo"""
        if self.algorithm == "least_connections":
            return min(
                self.nodes.keys(),
                key=lambda n: self.nodes[n].active_connections
            )
        elif self.algorithm == "response_time":
            return min(
                self.nodes.keys(),
                key=lambda n: self.metrics.get_avg_response_time(n)
            )
        elif self.algorithm == "resource_usage":
            return min(
                self.nodes.keys(),
                key=lambda n: self.metrics.get_resource_usage(n)
            )
```

### Performance Optimization

```python
class PerformanceOptimizer:
    """Otimizador de performance automático"""
    
    def __init__(self, agent: MangabaAgent):
        self.agent = agent
        self.metrics = PerformanceMetrics()
        self.optimization_rules = []
    
    def add_optimization_rule(self, rule: OptimizationRule):
        """Adiciona regra de otimização"""
        self.optimization_rules.append(rule)
    
    async def optimize_continuously(self):
        """Loop de otimização contínua"""
        while True:
            current_metrics = self.metrics.get_current_snapshot()
            
            for rule in self.optimization_rules:
                if rule.should_apply(current_metrics):
                    await rule.apply_optimization(self.agent, current_metrics)
            
            await asyncio.sleep(60)  # Otimizar a cada minuto

class CacheOptimizationRule(OptimizationRule):
    """Regra para otimizar cache baseado em padrões de uso"""
    
    def should_apply(self, metrics: MetricsSnapshot) -> bool:
        return metrics.cache_hit_rate < 0.7
    
    async def apply_optimization(self, agent: MangabaAgent, metrics: MetricsSnapshot):
        # Aumentar TTL para itens frequentemente acessados
        frequently_accessed = metrics.get_frequently_accessed_items()
        
        for item_key in frequently_accessed:
            current_ttl = agent.cache.get_ttl(item_key)
            new_ttl = min(current_ttl * 1.5, 3600)  # Max 1 hora
            agent.cache.update_ttl(item_key, new_ttl)
```

---

## 🛡️ Segurança

### Security Architecture

```python
class SecurityManager:
    """Gerenciador central de segurança"""
    
    def __init__(self):
        self.auth_provider = AuthenticationProvider()
        self.authorization = AuthorizationEngine()
        self.input_validator = InputValidator()
        self.audit_logger = AuditLogger()
    
    async def secure_request(self, request: Request) -> SecureRequest:
        """Aplica todas as validações de segurança"""
        
        # 1. Autenticação
        user = await self.auth_provider.authenticate(request.auth_token)
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # 2. Autorização
        if not await self.authorization.is_authorized(user, request.action):
            raise AuthorizationError("Insufficient permissions")
        
        # 3. Validação de entrada
        sanitized_input = self.input_validator.validate_and_sanitize(request.content)
        
        # 4. Audit log
        self.audit_logger.log_request(user, request, sanitized_input)
        
        return SecureRequest(
            user=user,
            content=sanitized_input,
            original_request=request
        )

class InputValidator:
    """Validador de entrada para prevenir ataques"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # XSS
            r'(\||\;|\&|\$|\>|\<|\`|\!)',  # Command injection
            r'(union|select|insert|delete|update|drop|exec|script)',  # SQL injection
        ]
    
    def validate_and_sanitize(self, content: str) -> str:
        """Valida e sanitiza entrada do usuário"""
        
        # Verificar padrões perigosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
        
        # Sanitizar HTML
        import html
        sanitized = html.escape(content)
        
        # Limitar tamanho
        if len(sanitized) > 10000:
            raise SecurityError("Input too large")
        
        return sanitized

class RateLimiter:
    """Rate limiter para prevenir abuso"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_history = defaultdict(list)
    
    async def check_rate_limit(self, user_id: str) -> bool:
        """Verifica se usuário está dentro do limite"""
        now = time.time()
        minute_ago = now - 60
        
        # Limpar histórico antigo
        self.request_history[user_id] = [
            timestamp for timestamp in self.request_history[user_id]
            if timestamp > minute_ago
        ]
        
        # Verificar limite
        if len(self.request_history[user_id]) >= self.requests_per_minute:
            return False
        
        # Registrar nova requisição
        self.request_history[user_id].append(now)
        return True
```

---

## 📊 Monitoramento e Observabilidade

### Metrics Collection

```python
class MetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.metrics = {}
        self.counters = defaultdict(int)
        self.gauges = {}
        self.histograms = defaultdict(list)
    
    def increment_counter(self, metric_name: str, value: int = 1, tags: Dict = None):
        """Incrementa contador"""
        key = self._build_key(metric_name, tags)
        self.counters[key] += value
    
    def set_gauge(self, metric_name: str, value: float, tags: Dict = None):
        """Define valor de gauge"""
        key = self._build_key(metric_name, tags)
        self.gauges[key] = value
    
    def record_histogram(self, metric_name: str, value: float, tags: Dict = None):
        """Registra valor em histograma"""
        key = self._build_key(metric_name, tags)
        self.histograms[key].append(value)
        
        # Manter apenas últimos 1000 valores
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def get_metrics_summary(self) -> Dict:
        """Retorna resumo de todas as métricas"""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                key: {
                    "count": len(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0,
                    "p95": self._percentile(values, 0.95) if values else 0
                }
                for key, values in self.histograms.items()
            }
        }

# Métricas do agente instrumentadas
class InstrumentedMangabaAgent(MangabaAgent):
    """Agente com instrumentação completa"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = MetricsCollector()
    
    async def chat(self, message: str, use_context: bool = True) -> str:
        start_time = time.time()
        
        try:
            self.metrics.increment_counter("chat.requests", tags={"agent": self.agent_name})
            
            result = await super().chat(message, use_context)
            
            self.metrics.increment_counter("chat.success", tags={"agent": self.agent_name})
            return result
            
        except Exception as e:
            self.metrics.increment_counter("chat.errors", tags={"agent": self.agent_name})
            raise
            
        finally:
            duration = time.time() - start_time
            self.metrics.record_histogram("chat.duration", duration, tags={"agent": self.agent_name})
```

---

> 🏗️ **Arquitetura Evolutiva**: O Mangaba AI foi projetado para evoluir continuamente, mantendo compatibilidade backwards enquanto incorpora novas tecnologias e padrões.

> 🔧 **Extensibilidade**: Cada componente pode ser estendido ou substituído sem afetar outros, permitindo customizações profundas quando necessário.