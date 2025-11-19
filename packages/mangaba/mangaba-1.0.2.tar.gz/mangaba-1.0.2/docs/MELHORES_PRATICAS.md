# ⭐ Melhores Práticas - Mangaba AI

Este guia apresenta as melhores práticas para criação, configuração e uso de agentes de IA com o Mangaba AI. Siga estas diretrizes para obter máxima eficiência, segurança e maintainability em seus projetos.

## 📋 Índice

1. [🏗️ Arquitetura de Agentes](#️-arquitetura-de-agentes)
2. [🔐 Segurança e Configuração](#-segurança-e-configuração)
3. [🧠 Gerenciamento de Contexto (MCP)](#-gerenciamento-de-contexto-mcp)
4. [🔗 Comunicação A2A](#-comunicação-a2a)
5. [⚡ Performance e Otimização](#-performance-e-otimização)
6. [🧪 Testes e Validação](#-testes-e-validação)
7. [📊 Monitoramento e Logs](#-monitoramento-e-logs)
8. [🔄 Manutenção e Deploy](#-manutenção-e-deploy)

---

## 🏗️ Arquitetura de Agentes

### ✅ **Práticas Recomendadas**

#### 1. **Inicialização Adequada**
```python
# ✅ BOM: Inicialização com configuração explícita
from mangaba_agent import MangabaAgent
import os

agent = MangabaAgent(
    api_key=os.getenv('GOOGLE_API_KEY'),
    model='gemini-pro',
    agent_id='meu_agente_01',
    enable_mcp=True
)
```

```python
# ❌ EVITAR: Inicialização sem configuração
agent = MangabaAgent()  # Sem parâmetros explícitos
```

#### 2. **Nomeação de Agentes**
```python
# ✅ BOM: Nomes descritivos e únicos
agent_analista = MangabaAgent(agent_id="analista_financeiro_v1")
agent_redator = MangabaAgent(agent_id="redator_marketing_pt_br")

# ❌ EVITAR: Nomes genéricos
agent1 = MangabaAgent(agent_id="agent1")
agent2 = MangabaAgent(agent_id="teste")
```

#### 3. **Separação de Responsabilidades**
```python
# ✅ BOM: Um agente, uma responsabilidade
class AnalistaFinanceiro(MangabaAgent):
    def analisar_relatorio(self, dados):
        return self.analyze_text(dados, "Faça análise financeira detalhada")
    
    def gerar_insights(self, analise):
        return self.chat(f"Gere insights baseados em: {analise}")

# ❌ EVITAR: Agente fazendo tudo
class AgenteTudoEmUm(MangabaAgent):
    def fazer_tudo(self, dados):
        # Análise + redação + tradução + marketing em um método
        pass
```

### 🎯 **Padrões de Design**

#### **1. Factory Pattern para Agentes Especializados**
```python
class AgentFactory:
    @staticmethod
    def criar_agente_medico():
        return MangabaAgent(
            agent_id="medico_especialista",
            model="gemini-pro"
        )
    
    @staticmethod
    def criar_agente_juridico():
        return MangabaAgent(
            agent_id="advogado_consultor",
            model="gemini-pro"
        )
```

#### **2. Builder Pattern para Configuração Complexa**
```python
class AgentBuilder:
    def __init__(self):
        self.config = {}
    
    def with_mcp(self, enabled=True):
        self.config['enable_mcp'] = enabled
        return self
    
    def with_model(self, model):
        self.config['model'] = model
        return self
    
    def build(self):
        return MangabaAgent(**self.config)

# Uso
agent = (AgentBuilder()
         .with_mcp(True)
         .with_model("gemini-pro")
         .build())
```

---

## 🔐 Segurança e Configuração

### ✅ **Gestão de API Keys**

#### 1. **Variáveis de Ambiente**
```python
# ✅ BOM: Sempre use variáveis de ambiente
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    raise ValueError("GOOGLE_API_KEY não configurada!")
```

#### 2. **Arquivo .env Seguro**
```bash
# .env
GOOGLE_API_KEY=sua_chave_aqui
MODEL_NAME=gemini-pro
AGENT_ID_PREFIX=prod_
LOG_LEVEL=INFO
```

```python
# .env.example (para repositório)
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-pro
AGENT_ID_PREFIX=dev_
LOG_LEVEL=DEBUG
```

#### 3. **Validação de Configuração**
```python
class ConfigValidator:
    @staticmethod
    def validate_environment():
        required_vars = ['GOOGLE_API_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise EnvironmentError(f"Variáveis obrigatórias ausentes: {missing}")
        
        return True

# Use antes de criar agentes
ConfigValidator.validate_environment()
```

### 🛡️ **Práticas de Segurança**

#### 1. **Sanitização de Entrada**
```python
def sanitize_input(text: str) -> str:
    """Remove caracteres perigosos do input do usuário"""
    import re
    # Remove scripts e tags HTML
    text = re.sub(r'<[^>]*>', '', text)
    # Limita tamanho
    if len(text) > 10000:
        text = text[:10000] + "..."
    return text.strip()

# Uso
user_input = sanitize_input(request_data)
response = agent.chat(user_input)
```

#### 2. **Rate Limiting**
```python
from time import time, sleep
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            if left_to_wait > 0:
                sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time()
            return ret
        return wrapper
    return decorator

# Uso
@rate_limit(calls_per_minute=30)
def fazer_requisicao(agent, message):
    return agent.chat(message)
```

---

## 🧠 Gerenciamento de Contexto (MCP)

### ✅ **Estratégias de Contexto**

#### 1. **Contexto Estruturado**
```python
# ✅ BOM: Contexto bem estruturado
from protocols.mcp import MCPContext, ContextType, ContextPriority

# Contexto de usuário
user_context = MCPContext.create(
    context_type=ContextType.USER,
    content={
        "nome": "João Silva",
        "empresa": "TechCorp",
        "setor": "Financeiro",
        "preferencias": ["relatórios_detalhados", "graficos"]
    },
    priority=ContextPriority.HIGH,
    tags=["usuario", "perfil", "preferencias"]
)

# Contexto de tarefa
task_context = MCPContext.create(
    context_type=ContextType.TASK,
    content={
        "tipo": "analise_financeira",
        "periodo": "Q3_2024",
        "metricas": ["receita", "lucro", "margem"]
    },
    priority=ContextPriority.MEDIUM,
    tags=["tarefa", "financeiro", "q3"]
)
```

#### 2. **Limpeza de Contexto**
```python
class ContextManager:
    def __init__(self, agent):
        self.agent = agent
        self.session_contexts = {}
    
    def limpar_contexto_antigo(self, session_id, max_age_hours=24):
        """Remove contextos muito antigos"""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        contexts = self.agent.mcp.get_contexts(session_id)
        
        for context in contexts:
            if context.timestamp < cutoff:
                self.agent.mcp.remove_context(context.id, session_id)
    
    def resumir_contexto_longo(self, session_id, max_contexts=50):
        """Resumir quando há muitos contextos"""
        contexts = self.agent.mcp.get_contexts(session_id)
        
        if len(contexts) > max_contexts:
            # Manter contextos de alta prioridade
            high_priority = [c for c in contexts 
                           if c.priority == ContextPriority.HIGH]
            
            # Resumir contextos de baixa prioridade
            low_priority = [c for c in contexts 
                          if c.priority == ContextPriority.LOW]
            
            if len(low_priority) > 10:
                summary = self.agent.chat(
                    f"Resuma estes contextos: {low_priority[:10]}"
                )
                # Substituir contextos individuais por resumo
                # ... implementação do resumo
```

#### 3. **Busca Inteligente de Contexto**
```python
def buscar_contexto_relevante(agent, query, session_id):
    """Busca contexto mais relevante para a query"""
    
    # Buscar por tags relacionadas
    tags_relevantes = extrair_tags_da_query(query)
    contextos_por_tag = []
    
    for tag in tags_relevantes:
        contexts = agent.mcp.find_contexts_by_tag(tag, session_id)
        contextos_por_tag.extend(contexts)
    
    # Ordenar por prioridade e relevância
    contextos_ordenados = sorted(
        contextos_por_tag,
        key=lambda c: (c.priority.value, calcular_relevancia(c, query)),
        reverse=True
    )
    
    return contextos_ordenados[:5]  # Top 5 mais relevantes

def extrair_tags_da_query(query):
    """Extrai tags relevantes da query do usuário"""
    # Implementação simplificada
    keywords = {
        'financeiro': ['dinheiro', 'receita', 'lucro', 'financeiro'],
        'usuario': ['meu', 'minha', 'perfil', 'preferencia'],
        'analise': ['analise', 'relatorio', 'dados', 'grafico']
    }
    
    tags = []
    query_lower = query.lower()
    
    for tag, words in keywords.items():
        if any(word in query_lower for word in words):
            tags.append(tag)
    
    return tags
```

---

## 🔗 Comunicação A2A

### ✅ **Padrões de Comunicação**

#### 1. **Handlers Específicos**
```python
class AgentePrincipal(MangabaAgent):
    def setup_custom_handlers(self):
        """Configure handlers personalizados"""
        
        # Handler para análise de documentos
        @self.a2a_protocol.register_handler("analyze_document")
        def handle_doc_analysis(message):
            doc_content = message.content.get("document")
            doc_type = message.content.get("type", "text")
            
            if doc_type == "financial":
                return self.analyze_financial_document(doc_content)
            elif doc_type == "legal":
                return self.analyze_legal_document(doc_content)
            else:
                return self.analyze_text(doc_content, "Análise geral")
        
        # Handler para tradução especializada
        @self.a2a_protocol.register_handler("specialized_translation")
        def handle_translation(message):
            text = message.content.get("text")
            domain = message.content.get("domain", "general")
            target_lang = message.content.get("target_language", "português")
            
            # Contexto específico por domínio
            context = self.get_domain_context(domain)
            enhanced_prompt = f"Contexto: {context}\n\nTraduza para {target_lang}: {text}"
            
            return self.translate(enhanced_prompt, target_lang)
```

#### 2. **Retry e Error Handling**
```python
import asyncio
from typing import Optional

class ReliableA2ACommunication:
    def __init__(self, agent):
        self.agent = agent
        self.max_retries = 3
        self.timeout = 30
    
    async def send_with_retry(self, target_agent: str, action: str, 
                            params: dict, retries: int = None) -> Optional[dict]:
        """Envia mensagem com retry automático"""
        if retries is None:
            retries = self.max_retries
        
        for attempt in range(retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.agent.send_agent_request(target_agent, action, params),
                    timeout=self.timeout
                )
                
                if response and response.get('success'):
                    return response
                
            except asyncio.TimeoutError:
                if attempt < retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Timeout após {retries} tentativas")
            
            except Exception as e:
                if attempt < retries:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise e
        
        return None
```

#### 3. **Load Balancing entre Agentes**
```python
class AgentLoadBalancer:
    def __init__(self):
        self.agents = {}
        self.agent_stats = {}
    
    def register_agent(self, agent_id: str, capabilities: list):
        """Registra um agente com suas capacidades"""
        self.agents[agent_id] = {
            'capabilities': capabilities,
            'load': 0,
            'last_used': datetime.now()
        }
        self.agent_stats[agent_id] = {
            'requests': 0,
            'errors': 0,
            'avg_response_time': 0
        }
    
    def get_best_agent(self, capability: str) -> str:
        """Seleciona o melhor agente para uma capacidade"""
        suitable_agents = [
            agent_id for agent_id, info in self.agents.items()
            if capability in info['capabilities']
        ]
        
        if not suitable_agents:
            raise ValueError(f"Nenhum agente disponível para: {capability}")
        
        # Seleciona agente com menor carga
        best_agent = min(suitable_agents, 
                        key=lambda a: self.agents[a]['load'])
        
        return best_agent
    
    def update_agent_load(self, agent_id: str, increment: int = 1):
        """Atualiza a carga de um agente"""
        if agent_id in self.agents:
            self.agents[agent_id]['load'] += increment
            self.agents[agent_id]['last_used'] = datetime.now()
```

---

## ⚡ Performance e Otimização

### ✅ **Otimização de Prompts**

#### 1. **Templates de Prompt**
```python
class PromptTemplates:
    """Templates otimizados para diferentes tipos de tarefa"""
    
    ANALISE_FINANCEIRA = """
    Você é um analista financeiro especializado.
    
    DADOS: {dados}
    
    ANÁLISE SOLICITADA:
    - Tendências principais
    - Riscos identificados  
    - Oportunidades
    - Recomendações específicas
    
    FORMATO DE RESPOSTA:
    1. Resumo Executivo (2-3 linhas)
    2. Análise Detalhada
    3. Recomendações Acionáveis
    
    Responda em português brasileiro, seja objetivo e baseie-se apenas nos dados fornecidos.
    """
    
    TRADUCAO_TECNICA = """
    Traduza o texto técnico a seguir para {idioma_destino}.
    
    CONTEXTO: {contexto_tecnico}
    TEXTO: {texto_original}
    
    DIRETRIZES:
    - Mantenha termos técnicos apropriados
    - Preserve formatação e estrutura
    - Use terminologia consistente
    
    TRADUÇÃO:
    """

# Uso
def analisar_com_template(agent, dados_financeiros):
    prompt = PromptTemplates.ANALISE_FINANCEIRA.format(dados=dados_financeiros)
    return agent.chat(prompt)
```

#### 2. **Cache de Respostas**
```python
import hashlib
from functools import lru_cache
import pickle
import os

class ResponseCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Gera chave única para o cache"""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Recupera resposta do cache"""
        key = self._get_cache_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    # Verifica se não expirou (24h)
                    if time.time() - cached_data['timestamp'] < 86400:
                        return cached_data['response']
            except:
                pass
        return None
    
    def set(self, prompt: str, model: str, response: str):
        """Armazena resposta no cache"""
        key = self._get_cache_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        data = {
            'response': response,
            'timestamp': time.time()
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)

# Integração com agente
class CachedMangabaAgent(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = ResponseCache()
    
    def chat(self, message: str, use_context: bool = True) -> str:
        # Verificar cache primeiro
        cached = self.cache.get(message, self.model_name)
        if cached:
            return cached
        
        # Se não existe, processar normalmente
        response = super().chat(message, use_context)
        
        # Armazenar no cache
        self.cache.set(message, self.model_name, response)
        return response
```

#### 3. **Processamento Assíncrono**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

class AsyncAgentManager:
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.agents = {}
    
    def add_agent(self, agent_id: str, agent: MangabaAgent):
        """Adiciona um agente ao pool"""
        self.agents[agent_id] = agent
    
    async def process_batch(self, requests: List[Dict]) -> List[Dict]:
        """Processa múltiplas requisições em paralelo"""
        tasks = []
        
        for request in requests:
            task = asyncio.create_task(
                self._process_single_request(request)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def _process_single_request(self, request: Dict) -> Dict:
        """Processa uma única requisição"""
        agent_id = request.get('agent_id')
        action = request.get('action')
        params = request.get('params', {})
        
        if agent_id not in self.agents:
            return {'error': f'Agente {agent_id} não encontrado'}
        
        agent = self.agents[agent_id]
        
        try:
            # Executa em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            
            if action == 'chat':
                result = await loop.run_in_executor(
                    self.executor, 
                    agent.chat, 
                    params.get('message', '')
                )
            elif action == 'analyze':
                result = await loop.run_in_executor(
                    self.executor,
                    agent.analyze_text,
                    params.get('text', ''),
                    params.get('instruction', '')
                )
            else:
                result = f"Ação '{action}' não suportada"
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Uso
async def exemplo_batch_processing():
    manager = AsyncAgentManager(max_workers=3)
    
    # Adicionar agentes
    agent1 = MangabaAgent(agent_id="analista")
    agent2 = MangabaAgent(agent_id="redator")
    
    manager.add_agent("analista", agent1)
    manager.add_agent("redator", agent2)
    
    # Processar em lote
    requests = [
        {'agent_id': 'analista', 'action': 'analyze', 'params': {'text': 'dados1'}},
        {'agent_id': 'redator', 'action': 'chat', 'params': {'message': 'escreva resumo'}},
        {'agent_id': 'analista', 'action': 'analyze', 'params': {'text': 'dados2'}},
    ]
    
    results = await manager.process_batch(requests)
    return results
```

---

## 🧪 Testes e Validação

### ✅ **Testes Unitários**

#### 1. **Testes para Agentes**
```python
import unittest
from unittest.mock import Mock, patch
from mangaba_agent import MangabaAgent

class TestMangabaAgent(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.agent = MangabaAgent(
            api_key="test_key",
            agent_id="test_agent",
            enable_mcp=True
        )
    
    @patch('mangaba_agent.genai.GenerativeModel')
    def test_chat_basic(self, mock_model):
        """Testa chat básico"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.text = "Resposta de teste"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Teste
        result = self.agent.chat("Olá")
        
        # Verificações
        self.assertEqual(result, "Resposta de teste")
        mock_model.return_value.generate_content.assert_called_once()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertTrue(self.agent.mcp_enabled)
        self.assertIsNotNone(self.agent.logger)
    
    @patch('mangaba_agent.genai.GenerativeModel')
    def test_analyze_text(self, mock_model):
        """Testa análise de texto"""
        mock_response = Mock()
        mock_response.text = "Análise: texto positivo"
        mock_model.return_value.generate_content.return_value = mock_response
        
        result = self.agent.analyze_text("texto teste", "analise sentimento")
        
        self.assertIn("Análise", result)
        self.assertIn("positivo", result)
```

#### 2. **Testes de Integração**
```python
class TestA2AIntegration(unittest.TestCase):
    def setUp(self):
        """Configurar dois agentes para teste A2A"""
        self.agent1 = MangabaAgent(agent_id="agent1")
        self.agent2 = MangabaAgent(agent_id="agent2")
        
        # Configurar protocolos A2A
        self.agent1.setup_a2a_protocol(port=8080)
        self.agent2.setup_a2a_protocol(port=8081)
    
    def test_agent_communication(self):
        """Testa comunicação entre agentes"""
        # Conectar agentes
        self.agent1.a2a_protocol.connect_to_agent("localhost", 8081)
        
        # Enviar mensagem
        response = self.agent1.send_agent_request(
            "agent2", 
            "chat", 
            {"message": "teste"}
        )
        
        # Verificar resposta
        self.assertIsNotNone(response)
        self.assertTrue(response.get('success', False))
    
    def tearDown(self):
        """Limpar após testes"""
        self.agent1.a2a_protocol.stop()
        self.agent2.a2a_protocol.stop()
```

#### 3. **Testes de Performance**
```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestPerformance(unittest.TestCase):
    def test_response_time(self):
        """Testa tempo de resposta"""
        agent = MangabaAgent(api_key="test_key")
        
        start_time = time.time()
        result = agent.chat("teste rápido")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Deve responder em menos de 10 segundos
        self.assertLess(response_time, 10.0)
        self.assertIsNotNone(result)
    
    def test_concurrent_requests(self):
        """Testa múltiplas requisições simultâneas"""
        agent = MangabaAgent(api_key="test_key")
        
        def make_request(i):
            return agent.chat(f"Mensagem {i}")
        
        # Executar 5 requisições simultâneas
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        # Todos devem retornar resultados
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
```

---

## 📊 Monitoramento e Logs

### ✅ **Sistema de Logs Estruturado**

#### 1. **Configuração Avançada de Logs**
```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, agent_id: str, log_level: str = "INFO"):
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"mangaba.{agent_id}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Formatter para logs estruturados
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo
        file_handler = logging.FileHandler(f"logs/{agent_id}.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_interaction(self, action: str, input_data: Any, 
                       output_data: Any, metadata: Dict = None):
        """Log estruturado de interações"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "input": str(input_data)[:500],  # Limitar tamanho
            "output": str(output_data)[:500],
            "metadata": metadata or {}
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_performance(self, action: str, duration: float, 
                       success: bool, error: str = None):
        """Log de métricas de performance"""
        perf_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "type": "performance",
            "action": action,
            "duration_seconds": duration,
            "success": success,
            "error": error
        }
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, json.dumps(perf_entry, ensure_ascii=False))

# Integração com MangabaAgent
class MonitoredMangabaAgent(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structured_logger = StructuredLogger(self.agent_id)
    
    def chat(self, message: str, use_context: bool = True) -> str:
        start_time = time.time()
        success = False
        error = None
        result = None
        
        try:
            result = super().chat(message, use_context)
            success = True
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            self.structured_logger.log_performance(
                "chat", duration, success, error
            )
            
            if success:
                self.structured_logger.log_interaction(
                    "chat", message, result, 
                    {"use_context": use_context}
                )
```

#### 2. **Métricas de Sistema**
```python
import psutil
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    active_agents: int
    total_requests: int
    avg_response_time: float

class MetricsCollector:
    def __init__(self):
        self.request_times: Deque[float] = deque(maxlen=1000)
        self.request_counts = defaultdict(int)
        self.active_agents = set()
        self.running = True
        
        # Thread para coleta contínua
        self.metrics_thread = threading.Thread(target=self._collect_metrics)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
    
    def record_request(self, agent_id: str, duration: float):
        """Registra uma requisição"""
        self.request_times.append(duration)
        self.request_counts[agent_id] += 1
        self.active_agents.add(agent_id)
    
    def get_current_metrics(self) -> SystemMetrics:
        """Retorna métricas atuais"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        avg_response = (sum(self.request_times) / len(self.request_times) 
                       if self.request_times else 0)
        
        return SystemMetrics(
            cpu_usage=cpu,
            memory_usage=memory,
            active_agents=len(self.active_agents),
            total_requests=sum(self.request_counts.values()),
            avg_response_time=avg_response
        )
    
    def _collect_metrics(self):
        """Coleta métricas em background"""
        while self.running:
            metrics = self.get_current_metrics()
            
            # Log métricas a cada minuto
            logging.info(f"System Metrics: {metrics}")
            time.sleep(60)
    
    def stop(self):
        """Para a coleta de métricas"""
        self.running = False

# Instância global
metrics_collector = MetricsCollector()
```

---

## 🔄 Manutenção e Deploy

### ✅ **Estratégias de Deploy**

#### 1. **Configuração por Ambiente**
```python
# config/environments.py
class BaseConfig:
    """Configuração base"""
    LOG_LEVEL = "INFO"
    MAX_CONTEXT_SIZE = 1000
    ENABLE_CACHE = True

class DevelopmentConfig(BaseConfig):
    """Configuração para desenvolvimento"""
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHE = False
    DEBUG_MODE = True
    
class ProductionConfig(BaseConfig):
    """Configuração para produção"""
    LOG_LEVEL = "WARNING"
    MAX_RETRIES = 5
    ENABLE_MONITORING = True
    CACHE_TTL = 3600

class TestingConfig(BaseConfig):
    """Configuração para testes"""
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHE = False
    TESTING = True

# Seleção de ambiente
import os

def get_config():
    env = os.getenv('MANGABA_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig)()
```

#### 2. **Health Checks**
```python
from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

class HealthChecker:
    def __init__(self, agents: Dict[str, MangabaAgent]):
        self.agents = agents
        self.last_check = {}
    
    def check_agent_health(self, agent_id: str) -> Dict:
        """Verifica saúde de um agente específico"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"status": "not_found", "message": f"Agente {agent_id} não encontrado"}
        
        try:
            # Teste simples de resposta
            start_time = time.time()
            response = agent.chat("health check")
            response_time = time.time() - start_time
            
            # Verificar se a resposta é válida
            if response and len(response) > 0:
                status = "healthy"
                if response_time > 10:  # Muito lento
                    status = "slow"
            else:
                status = "unhealthy"
            
            self.last_check[agent_id] = datetime.now()
            
            return {
                "status": status,
                "response_time": response_time,
                "last_check": self.last_check[agent_id].isoformat(),
                "message": "Health check concluído"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def check_all_agents(self) -> Dict:
        """Verifica saúde de todos os agentes"""
        results = {}
        overall_status = "healthy"
        
        for agent_id in self.agents:
            results[agent_id] = self.check_agent_health(agent_id)
            
            if results[agent_id]["status"] in ["unhealthy", "error"]:
                overall_status = "unhealthy"
            elif results[agent_id]["status"] == "slow" and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "agents": results,
            "timestamp": datetime.now().isoformat()
        }

# Endpoints de health check
health_checker = HealthChecker({})

@app.route('/health')
def health_check():
    """Endpoint principal de saúde"""
    return jsonify(health_checker.check_all_agents())

@app.route('/health/<agent_id>')
def agent_health(agent_id):
    """Health check de agente específico"""
    return jsonify(health_checker.check_agent_health(agent_id))

@app.route('/metrics')
def metrics_endpoint():
    """Endpoint de métricas"""
    return jsonify(metrics_collector.get_current_metrics().__dict__)
```

#### 3. **Scripts de Deploy Automático**
```bash
#!/bin/bash
# deploy.sh

set -e  # Sair se qualquer comando falhar

echo "🚀 Iniciando deploy do Mangaba AI..."

# 1. Verificar ambiente
echo "📋 Verificando ambiente..."
python scripts/validate_env.py || {
    echo "❌ Falha na validação do ambiente"
    exit 1
}

# 2. Executar testes
echo "🧪 Executando testes..."
python -m pytest tests/ -v || {
    echo "❌ Testes falharam"
    exit 1
}

# 3. Backup de configuração atual
echo "💾 Fazendo backup..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 4. Atualizar dependências
echo "📦 Atualizando dependências..."
pip install -r requirements.txt

# 5. Aplicar migrações (se houver)
echo "🔄 Aplicando atualizações..."
python scripts/migrate_configs.py

# 6. Reiniciar serviços
echo "♻️ Reiniciando serviços..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart mangaba-ai
else
    # Desenvolvimento - apenas notificar
    echo "⚠️ Reinicie manualmente os agentes em execução"
fi

# 7. Verificar saúde após deploy
echo "🏥 Verificando saúde do sistema..."
sleep 10  # Aguardar inicialização

curl -f http://localhost:5000/health || {
    echo "❌ Health check falhou após deploy"
    exit 1
}

echo "✅ Deploy concluído com sucesso!"
echo "📊 Métricas disponíveis em: http://localhost:5000/metrics"
echo "🏥 Health check em: http://localhost:5000/health"
```

---

## 📚 Resumo das Melhores Práticas

### 🎯 **Pontos-Chave para Lembrar**

#### **🏗️ Arquitetura**
- Use Factory/Builder patterns para agentes complexos
- Separe responsabilidades claramente
- Implemente handlers específicos para A2A

#### **🔐 Segurança**
- Sempre use variáveis de ambiente para API keys
- Implemente rate limiting e sanitização
- Valide configurações antes de usar

#### **🧠 Contexto MCP**
- Estruture contextos com tags e prioridades
- Implemente limpeza automática de contextos antigos
- Use busca inteligente para melhor relevância

#### **⚡ Performance**
- Use templates de prompt otimizados
- Implemente cache para respostas repetidas
- Processe requisições em paralelo quando possível

#### **🧪 Qualidade**
- Escreva testes unitários e de integração
- Monitore métricas de performance
- Implemente health checks robustos

#### **🔄 Operações**
- Configure ambientes separados
- Use scripts de deploy automatizados
- Monitore logs estruturados

---

> ⚡ **Dica Final**: Comece simples e evolua gradualmente. Implemente estas práticas conforme sua aplicação cresce em complexidade.

> 📚 **Próximos Passos**: Consulte o [FAQ](FAQ.md) para dúvidas comuns ou o [Glossário](GLOSSARIO.md) para termos técnicos.

---

*Última atualização: Dezembro 2024 | Versão: 1.0*