# ✨ Melhores Práticas para Criação de Agentes

Este guia apresenta as melhores práticas, padrões recomendados e técnicas avançadas para criar agentes eficientes, escaláveis e robustos com o Mangaba AI.

## 📋 Índice

1. [Princípios Fundamentais](#-princípios-fundamentais)
2. [Design de Agentes](#-design-de-agentes)
3. [Gerenciamento de Contexto](#-gerenciamento-de-contexto)
4. [Comunicação A2A](#-comunicação-a2a)
5. [Performance e Otimização](#-performance-e-otimização)
6. [Segurança e Confiabilidade](#-segurança-e-confiabilidade)
7. [Testes e Qualidade](#-testes-e-qualidade)
8. [Deploy e Produção](#-deploy-e-produção)

---

## 🎯 Princípios Fundamentais

### 1. Single Responsibility Principle (SRP)
Cada agente deve ter uma responsabilidade específica e bem definida.

```python
# ❌ Agente genérico demais
class AgenteGenerico:
    def fazer_tudo(self, tarefa):
        if "traducao" in tarefa:
            return self.traducir()
        elif "analise" in tarefa:
            return self.analisar()
        elif "vendas" in tarefa:
            return self.vender()
        # ... muito acoplado

# ✅ Agentes especializados
class AgenteTradutor(MangabaAgent):
    def __init__(self):
        super().__init__(agent_name="Tradutor")
        self.especializacao = "traducao"
        self.idiomas_suportados = ["pt", "en", "es", "fr"]
    
    def traduzir(self, texto, idioma_origem, idioma_destino):
        """Método especializado em tradução"""
        if idioma_destino not in self.idiomas_suportados:
            raise ValueError(f"Idioma {idioma_destino} não suportado")
        
        return self.translate(texto, idioma_destino)

class AgenteAnalista(MangabaAgent):
    def __init__(self):
        super().__init__(agent_name="Analista")
        self.especializacao = "analise_dados"
        self.tipos_analise = ["sentimento", "topicos", "estatistica"]
    
    def analisar_documento(self, documento, tipo_analise="sentimento"):
        """Método especializado em análise"""
        if tipo_analise not in self.tipos_analise:
            raise ValueError(f"Tipo {tipo_analise} não suportado")
        
        instrucao = f"Realizar análise de {tipo_analise}"
        return self.analyze_text(documento, instrucao)
```

### 2. Composition Over Inheritance
Prefira composição de funcionalidades ao invés de herança complexa.

```python
# ✅ Design baseado em composição
class CapacidadeAnalise:
    """Capacidade específica de análise"""
    def __init__(self, agente):
        self.agente = agente
    
    def analisar_sentimento(self, texto):
        return self.agente.analyze_text(texto, "Analisar sentimento")
    
    def extrair_entidades(self, texto):
        return self.agente.analyze_text(texto, "Extrair entidades nomeadas")

class CapacidadeTraducao:
    """Capacidade específica de tradução"""
    def __init__(self, agente):
        self.agente = agente
    
    def traduzir_automatico(self, texto):
        return self.agente.translate(texto, "auto-detect")

class AgenteComposto:
    """Agente que combina múltiplas capacidades"""
    def __init__(self, nome):
        self.agente_core = MangabaAgent(agent_name=nome)
        
        # Composição de capacidades
        self.analise = CapacidadeAnalise(self.agente_core)
        self.traducao = CapacidadeTraducao(self.agente_core)
    
    def processar_documento_multilingue(self, documento, idioma_destino):
        """Pipeline que usa múltiplas capacidades"""
        # 1. Analisar documento original
        analise = self.analise.analisar_sentimento(documento)
        
        # 2. Traduzir se necessário
        doc_traduzido = self.traducao.traduzir_automatico(documento)
        
        # 3. Analisar versão traduzida
        analise_traduzida = self.analise.analisar_sentimento(doc_traduzido)
        
        return {
            "analise_original": analise,
            "documento_traduzido": doc_traduzido,
            "analise_traduzida": analise_traduzida
        }
```

### 3. Fail Fast e Error Handling
Detecte e trate erros rapidamente, com logging adequado.

```python
from loguru import logger
from typing import Optional, Dict, Any

class AgenteRobusto(MangabaAgent):
    def __init__(self, nome: str, max_retries: int = 3):
        super().__init__(agent_name=nome)
        self.max_retries = max_retries
        
    def executar_com_retry(self, funcao, *args, **kwargs) -> Dict[str, Any]:
        """Executa função com retry automático"""
        for tentativa in range(self.max_retries):
            try:
                resultado = funcao(*args, **kwargs)
                logger.info(f"✅ Sucesso na tentativa {tentativa + 1}")
                return {"sucesso": True, "resultado": resultado}
                
            except Exception as e:
                logger.warning(f"⚠️ Falha na tentativa {tentativa + 1}: {e}")
                
                if tentativa == self.max_retries - 1:
                    logger.error(f"❌ Falha após {self.max_retries} tentativas")
                    return {
                        "sucesso": False, 
                        "erro": str(e),
                        "tentativas": self.max_retries
                    }
                
                # Backoff exponencial
                import time
                time.sleep(2 ** tentativa)
    
    def chat_seguro(self, mensagem: str, use_context: bool = True) -> Optional[str]:
        """Chat com tratamento de erro robusto"""
        if not mensagem or not mensagem.strip():
            logger.error("❌ Mensagem vazia fornecida")
            return None
        
        resultado = self.executar_com_retry(
            self.chat, mensagem, use_context=use_context
        )
        
        return resultado.get("resultado") if resultado["sucesso"] else None
```

---

## 🏗️ Design de Agentes

### Padrão Factory para Criação de Agentes

```python
from enum import Enum
from typing import Dict, Type

class TipoAgente(Enum):
    ANALISTA = "analista"
    TRADUTOR = "tradutor"
    ASSISTENTE = "assistente"
    COORDENADOR = "coordenador"

class FabricaDeAgentes:
    """Factory pattern para criação padronizada de agentes"""
    
    _configuracoes: Dict[TipoAgente, Dict] = {
        TipoAgente.ANALISTA: {
            "classe": AgenteAnalista,
            "config": {
                "max_context_size": 5000,
                "especializacao": "analise_dados",
                "protocolos": ["mcp"]
            }
        },
        TipoAgente.TRADUTOR: {
            "classe": AgenteTradutor,
            "config": {
                "max_context_size": 2000,
                "especializacao": "traducao",
                "protocolos": ["mcp"]
            }
        },
        TipoAgente.COORDENADOR: {
            "classe": AgenteCoordenador,
            "config": {
                "max_context_size": 10000,
                "especializacao": "coordenacao",
                "protocolos": ["mcp", "a2a"]
            }
        }
    }
    
    @classmethod
    def criar_agente(cls, tipo: TipoAgente, nome: str, **kwargs) -> MangabaAgent:
        """Cria agente do tipo especificado"""
        if tipo not in cls._configuracoes:
            raise ValueError(f"Tipo de agente {tipo} não suportado")
        
        config = cls._configuracoes[tipo]
        classe_agente = config["classe"]
        config_base = config["config"].copy()
        
        # Mesclar configurações personalizadas
        config_base.update(kwargs)
        
        # Criar e configurar agente
        agente = classe_agente(nome, **config_base)
        
        logger.info(f"✅ Agente {nome} ({tipo.value}) criado com sucesso")
        return agente

# Uso da Factory
agente_analista = FabricaDeAgentes.criar_agente(
    TipoAgente.ANALISTA, 
    "Analista-Principal",
    max_context_size=8000  # Override da configuração padrão
)
```

### Padrão Builder para Configuração Complexa

```python
class ConstrutorDeAgente:
    """Builder pattern para configuração flexível"""
    
    def __init__(self, nome: str):
        self.nome = nome
        self.config = {
            "protocolos": [],
            "capacidades": [],
            "handlers": {},
            "contexto_inicial": []
        }
    
    def com_protocolo_mcp(self, max_contextos: int = 1000) -> 'ConstrutorDeAgente':
        """Adiciona protocolo MCP"""
        self.config["protocolos"].append(("mcp", {"max_contextos": max_contextos}))
        return self
    
    def com_protocolo_a2a(self, porta: int) -> 'ConstrutorDeAgente':
        """Adiciona protocolo A2A"""
        self.config["protocolos"].append(("a2a", {"porta": porta}))
        return self
    
    def com_capacidade(self, capacidade: str, config: Dict = None) -> 'ConstrutorDeAgente':
        """Adiciona capacidade específica"""
        self.config["capacidades"].append((capacidade, config or {}))
        return self
    
    def com_handler_personalizado(self, evento: str, handler) -> 'ConstrutorDeAgente':
        """Adiciona handler personalizado"""
        self.config["handlers"][evento] = handler
        return self
    
    def com_contexto_inicial(self, contexto: str, tipo: str = "system") -> 'ConstrutorDeAgente':
        """Adiciona contexto inicial"""
        self.config["contexto_inicial"].append((contexto, tipo))
        return self
    
    def construir(self) -> MangabaAgent:
        """Constrói o agente com as configurações especificadas"""
        agente = MangabaAgent(agent_name=self.nome)
        
        # Configurar protocolos
        for protocolo, config in self.config["protocolos"]:
            if protocolo == "a2a":
                from protocols.a2a import A2AProtocol
                a2a = A2AProtocol(agent_id=self.nome, port=config["porta"])
                agente.add_protocol(a2a)
        
        # Adicionar contexto inicial
        for contexto, tipo in self.config["contexto_inicial"]:
            agente.mcp_protocol.add_context(
                content=contexto,
                context_type=tipo,
                priority=1
            )
        
        # Configurar handlers
        for evento, handler in self.config["handlers"].items():
            if hasattr(agente, "add_handler"):
                agente.add_handler(evento, handler)
        
        logger.info(f"🏗️ Agente {self.nome} construído com sucesso")
        return agente

# Uso do Builder
agente = (ConstrutorDeAgente("AgenteSuperAvancado")
          .com_protocolo_mcp(max_contextos=2000)
          .com_protocolo_a2a(porta=8080)
          .com_capacidade("analise_avancada", {"modelo": "gpt-4"})
          .com_contexto_inicial("Especialista em IA e Machine Learning", "profile")
          .com_handler_personalizado("erro", lambda e: logger.error(f"Erro: {e}"))
          .construir())
```

---

## 🧠 Gerenciamento de Contexto

### Estratégias de Contexto

```python
class GerenciadorDeContexto:
    """Gerenciador avançado de contexto MCP"""
    
    def __init__(self, agente: MangabaAgent):
        self.agente = agente
        self.estrategias = {
            "rolling_window": self._rolling_window,
            "priority_based": self._priority_based,
            "semantic_compression": self._semantic_compression
        }
    
    def _rolling_window(self, max_items: int = 50):
        """Mantém apenas os N contextos mais recentes"""
        contextos = self.agente.mcp_protocol.contexts
        if len(contextos) > max_items:
            # Remove contextos mais antigos
            for i in range(len(contextos) - max_items):
                contextos.pop(0)
    
    def _priority_based(self, min_priority: int = 3):
        """Remove contextos com prioridade baixa"""
        contextos = self.agente.mcp_protocol.contexts
        contextos_filtrados = [
            ctx for ctx in contextos 
            if ctx.priority >= min_priority
        ]
        self.agente.mcp_protocol.contexts = contextos_filtrados
    
    def _semantic_compression(self, similarity_threshold: float = 0.8):
        """Agrupa contextos semanticamente similares"""
        # Implementação simplificada
        contextos = self.agente.mcp_protocol.contexts
        grupos_similares = []
        
        for i, ctx1 in enumerate(contextos):
            for j, ctx2 in enumerate(contextos[i+1:], i+1):
                similaridade = self._calcular_similaridade(ctx1.content, ctx2.content)
                if similaridade > similarity_threshold:
                    grupos_similares.append([i, j])
        
        # Agrupa contextos similares
        for grupo in grupos_similares:
            self._agregar_contextos(grupo)
    
    def otimizar_contexto(self, estrategia: str = "rolling_window", **kwargs):
        """Aplica estratégia de otimização de contexto"""
        if estrategia in self.estrategias:
            self.estrategias[estrategia](**kwargs)
            logger.info(f"✅ Contexto otimizado usando {estrategia}")
        else:
            logger.warning(f"⚠️ Estratégia {estrategia} não encontrada")

# Uso prático
gerenciador = GerenciadorDeContexto(agente)

# Otimização automática a cada 100 interações
contador_interacoes = 0

def chat_com_otimizacao(mensagem):
    global contador_interacoes
    contador_interacoes += 1
    
    resposta = agente.chat(mensagem, use_context=True)
    
    # Otimização periódica
    if contador_interacoes % 100 == 0:
        gerenciador.otimizar_contexto("rolling_window", max_items=200)
    
    return resposta
```

### Contexto Hierárquico

```python
class ContextoHierarquico:
    """Sistema de contexto com hierarquia de prioridades"""
    
    PRIORIDADES = {
        "SISTEMA": 10,      # Configurações do sistema
        "USUARIO": 8,       # Informações do usuário
        "SESSAO": 6,        # Contexto da sessão atual
        "TAREFA": 4,        # Contexto da tarefa específica
        "TEMPORARIO": 2     # Informações temporárias
    }
    
    def __init__(self, agente: MangabaAgent):
        self.agente = agente
    
    def adicionar_contexto_sistema(self, conteudo: str):
        """Adiciona contexto de alta prioridade (sistema)"""
        self.agente.mcp_protocol.add_context(
            content=conteudo,
            context_type="sistema",
            priority=self.PRIORIDADES["SISTEMA"],
            tags=["sistema", "configuracao"]
        )
    
    def adicionar_contexto_usuario(self, conteudo: str, user_id: str):
        """Adiciona contexto do usuário"""
        self.agente.mcp_protocol.add_context(
            content=conteudo,
            context_type="usuario",
            priority=self.PRIORIDADES["USUARIO"],
            tags=["usuario", user_id]
        )
    
    def adicionar_contexto_sessao(self, conteudo: str, session_id: str):
        """Adiciona contexto da sessão"""
        self.agente.mcp_protocol.add_context(
            content=conteudo,
            context_type="sessao",
            priority=self.PRIORIDADES["SESSAO"],
            tags=["sessao", session_id]
        )
    
    def limpar_por_nivel(self, nivel_minimo: int):
        """Remove contextos abaixo do nível especificado"""
        contextos_filtrados = [
            ctx for ctx in self.agente.mcp_protocol.contexts
            if ctx.priority >= nivel_minimo
        ]
        self.agente.mcp_protocol.contexts = contextos_filtrados

# Exemplo de uso
contexto = ContextoHierarquico(agente)

# Configuração do sistema (alta prioridade)
contexto.adicionar_contexto_sistema(
    "Agente especializado em análise financeira. Sempre fornecer dados precisos."
)

# Informações do usuário (prioridade média-alta)
contexto.adicionar_contexto_usuario(
    "João Silva, analista financeiro sênior, especialista em ações brasileiras",
    user_id="user_123"
)

# Contexto da sessão (prioridade média)
contexto.adicionar_contexto_sessao(
    "Análise de portfolio de ações para Q1 2024",
    session_id="session_456"
)
```

---

## 🔗 Comunicação A2A

### Padrões de Comunicação

```python
class PadroesA2A:
    """Implementa padrões comuns de comunicação A2A"""
    
    @staticmethod
    def request_response(agente_origem, agente_destino, acao, params, timeout=30):
        """Padrão requisição-resposta simples"""
        try:
            resposta = agente_origem.send_agent_request(
                agente_destino, acao, params, timeout=timeout
            )
            return {"sucesso": True, "resposta": resposta}
        except TimeoutError:
            return {"sucesso": False, "erro": "Timeout na comunicação"}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    @staticmethod
    def pub_sub(agente_publicador, topico, mensagem, agentes_subscritos):
        """Padrão publish-subscribe"""
        resultados = {}
        
        for agente_id in agentes_subscritos:
            try:
                resultado = agente_publicador.send_agent_request(
                    agente_id, "notificacao_topico",
                    {"topico": topico, "mensagem": mensagem}
                )
                resultados[agente_id] = {"sucesso": True, "resultado": resultado}
            except Exception as e:
                resultados[agente_id] = {"sucesso": False, "erro": str(e)}
        
        return resultados
    
    @staticmethod
    def pipeline(agentes_pipeline, dados_iniciais):
        """Padrão pipeline - dados fluem sequencialmente"""
        dados_atuais = dados_iniciais
        historico = []
        
        for i, agente_info in enumerate(agentes_pipeline):
            agente_id = agente_info["id"]
            acao = agente_info["acao"]
            
            try:
                resultado = agentes_pipeline[0]["agente_origem"].send_agent_request(
                    agente_id, acao, {"dados": dados_atuais}
                )
                
                dados_atuais = resultado
                historico.append({
                    "etapa": i + 1,
                    "agente": agente_id,
                    "sucesso": True,
                    "resultado": resultado
                })
                
            except Exception as e:
                historico.append({
                    "etapa": i + 1,
                    "agente": agente_id,
                    "sucesso": False,
                    "erro": str(e)
                })
                break
        
        return {"resultado_final": dados_atuais, "historico": historico}

# Exemplo de uso do pipeline
pipeline_analise = [
    {"id": "Extrator", "acao": "extrair_dados"},
    {"id": "Limpador", "acao": "limpar_dados"},
    {"id": "Analisador", "acao": "analisar_dados"},
    {"id": "Relatorio", "acao": "gerar_relatorio"}
]

resultado = PadroesA2A.pipeline(
    pipeline_analise, 
    {"documento": "relatorio_vendas.pdf"}
)
```

### Circuit Breaker para A2A

```python
from enum import Enum
import time
from typing import Dict, Any

class EstadoCircuit(Enum):
    FECHADO = "fechado"      # Funcionando normalmente
    ABERTO = "aberto"        # Falhas detectadas, bloqueando requisições
    MEIO_ABERTO = "meio_aberto"  # Testando se o serviço voltou

class CircuitBreakerA2A:
    """Circuit breaker para comunicação A2A resiliente"""
    
    def __init__(self, 
                 limite_falhas: int = 5,
                 janela_tempo: int = 60,
                 timeout_abertura: int = 30):
        self.limite_falhas = limite_falhas
        self.janela_tempo = janela_tempo
        self.timeout_abertura = timeout_abertura
        
        self.circuitos: Dict[str, Dict] = {}
    
    def _obter_circuito(self, agente_id: str) -> Dict:
        """Obtém ou cria circuito para agente específico"""
        if agente_id not in self.circuitos:
            self.circuitos[agente_id] = {
                "estado": EstadoCircuit.FECHADO,
                "falhas": 0,
                "ultima_falha": 0,
                "proximo_teste": 0
            }
        return self.circuitos[agente_id]
    
    def _pode_executar(self, circuito: Dict) -> bool:
        """Verifica se requisição pode ser executada"""
        agora = time.time()
        
        if circuito["estado"] == EstadoCircuit.FECHADO:
            return True
        elif circuito["estado"] == EstadoCircuit.ABERTO:
            if agora >= circuito["proximo_teste"]:
                circuito["estado"] = EstadoCircuit.MEIO_ABERTO
                return True
            return False
        else:  # MEIO_ABERTO
            return True
    
    def executar_com_circuit_breaker(self, 
                                   agente_origem: MangabaAgent,
                                   agente_destino: str,
                                   acao: str,
                                   params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa requisição A2A com circuit breaker"""
        circuito = self._obter_circuito(agente_destino)
        
        if not self._pode_executar(circuito):
            return {
                "sucesso": False,
                "erro": f"Circuit breaker ABERTO para {agente_destino}",
                "estado_circuito": circuito["estado"].value
            }
        
        try:
            # Tentativa de execução
            resultado = agente_origem.send_agent_request(
                agente_destino, acao, params
            )
            
            # Sucesso - resetar circuito
            if circuito["estado"] == EstadoCircuit.MEIO_ABERTO:
                circuito["estado"] = EstadoCircuit.FECHADO
                circuito["falhas"] = 0
            
            return {"sucesso": True, "resultado": resultado}
            
        except Exception as e:
            # Falha - atualizar circuito
            agora = time.time()
            circuito["falhas"] += 1
            circuito["ultima_falha"] = agora
            
            if (circuito["falhas"] >= self.limite_falhas and 
                circuito["estado"] == EstadoCircuit.FECHADO):
                # Abrir circuito
                circuito["estado"] = EstadoCircuit.ABERTO
                circuito["proximo_teste"] = agora + self.timeout_abertura
                
            elif circuito["estado"] == EstadoCircuit.MEIO_ABERTO:
                # Voltar para aberto
                circuito["estado"] = EstadoCircuit.ABERTO
                circuito["proximo_teste"] = agora + self.timeout_abertura
            
            return {
                "sucesso": False,
                "erro": str(e),
                "estado_circuito": circuito["estado"].value
            }

# Uso do Circuit Breaker
cb = CircuitBreakerA2A(limite_falhas=3, timeout_abertura=60)

def comunicacao_resiliente(agente, destino, acao, params):
    resultado = cb.executar_com_circuit_breaker(
        agente, destino, acao, params
    )
    
    if not resultado["sucesso"]:
        logger.warning(f"⚠️ Falha na comunicação: {resultado['erro']}")
        
        # Implementar fallback
        return executar_fallback(acao, params)
    
    return resultado["resultado"]
```

---

## 🚀 Performance e Otimização

### Cache Inteligente

```python
import hashlib
import pickle
import time
from typing import Any, Optional

class CacheInteligente:
    """Sistema de cache com TTL e invalidação inteligente"""
    
    def __init__(self, ttl_default: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.ttl_default = ttl_default
    
    def _gerar_chave(self, funcao: str, args: tuple, kwargs: dict) -> str:
        """Gera chave única para cache"""
        dados = f"{funcao}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(dados.encode()).hexdigest()
    
    def _esta_valido(self, entrada: Dict) -> bool:
        """Verifica se entrada do cache ainda é válida"""
        return time.time() < entrada["expira_em"]
    
    def obter(self, chave: str) -> Optional[Any]:
        """Obtém valor do cache se válido"""
        if chave in self.cache and self._esta_valido(self.cache[chave]):
            self.cache[chave]["acessos"] += 1
            self.cache[chave]["ultimo_acesso"] = time.time()
            return self.cache[chave]["valor"]
        
        # Remove entrada expirada
        if chave in self.cache:
            del self.cache[chave]
        
        return None
    
    def armazenar(self, chave: str, valor: Any, ttl: Optional[int] = None) -> None:
        """Armazena valor no cache"""
        ttl = ttl or self.ttl_default
        agora = time.time()
        
        self.cache[chave] = {
            "valor": valor,
            "criado_em": agora,
            "ultimo_acesso": agora,
            "expira_em": agora + ttl,
            "acessos": 0
        }
    
    def invalidar_por_padrao(self, padrao: str) -> int:
        """Invalida entradas que correspondem ao padrão"""
        chaves_removidas = []
        
        for chave in self.cache:
            if padrao in chave:
                chaves_removidas.append(chave)
        
        for chave in chaves_removidas:
            del self.cache[chave]
        
        return len(chaves_removidas)
    
    def estatisticas(self) -> Dict:
        """Retorna estatísticas do cache"""
        total_entradas = len(self.cache)
        entradas_validas = sum(1 for e in self.cache.values() if self._esta_valido(e))
        total_acessos = sum(e["acessos"] for e in self.cache.values())
        
        return {
            "total_entradas": total_entradas,
            "entradas_validas": entradas_validas,
            "entradas_expiradas": total_entradas - entradas_validas,
            "total_acessos": total_acessos,
            "taxa_hit": total_acessos / max(total_entradas, 1)
        }

# Decorator para cache automático
def cache_resultado(ttl: int = 3600, invalidar_em: list = None):
    """Decorator para cache automático de métodos"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_cache'):
                self._cache = CacheInteligente()
            
            chave = self._cache._gerar_chave(func.__name__, args, kwargs)
            
            # Tentar obter do cache
            resultado = self._cache.obter(chave)
            if resultado is not None:
                logger.debug(f"🎯 Cache HIT para {func.__name__}")
                return resultado
            
            # Executar função e cachear
            logger.debug(f"⚡ Cache MISS para {func.__name__} - executando")
            resultado = func(self, *args, **kwargs)
            self._cache.armazenar(chave, resultado, ttl)
            
            return resultado
        return wrapper
    return decorator

# Agente com cache automático
class AgenteComCache(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = CacheInteligente(ttl_default=1800)  # 30 minutos
    
    @cache_resultado(ttl=3600)  # Cache por 1 hora
    def analisar_documento_cacheado(self, documento: str, tipo_analise: str):
        """Análise com cache automático"""
        return self.analyze_text(documento, f"Analisar: {tipo_analise}")
    
    @cache_resultado(ttl=7200)  # Cache por 2 horas
    def traduzir_cacheado(self, texto: str, idioma: str):
        """Tradução com cache automático"""
        return self.translate(texto, idioma)
    
    def invalidar_cache_analise(self):
        """Invalida cache de análises"""
        return self._cache.invalidar_por_padrao("analisar_documento")
```

### Pool de Agentes

```python
import queue
import threading
from typing import List, Callable, Any

class PoolDeAgentes:
    """Pool de agentes para processamento paralelo"""
    
    def __init__(self, 
                 fabrica_agente: Callable,
                 tamanho_inicial: int = 3,
                 tamanho_maximo: int = 10):
        self.fabrica_agente = fabrica_agente
        self.tamanho_maximo = tamanho_maximo
        
        # Pool de agentes disponíveis
        self.agentes_disponiveis = queue.Queue()
        self.agentes_em_uso = set()
        self.lock = threading.Lock()
        
        # Criar agentes iniciais
        for i in range(tamanho_inicial):
            agente = self.fabrica_agente(f"Agent-{i}")
            self.agentes_disponiveis.put(agente)
    
    def obter_agente(self, timeout: int = 10) -> MangabaAgent:
        """Obtém agente do pool"""
        try:
            agente = self.agentes_disponiveis.get(timeout=timeout)
            with self.lock:
                self.agentes_em_uso.add(agente)
            return agente
        except queue.Empty:
            # Pool esgotado - criar novo se possível
            with self.lock:
                total_agentes = (self.agentes_disponiveis.qsize() + 
                               len(self.agentes_em_uso))
                if total_agentes < self.tamanho_maximo:
                    agente = self.fabrica_agente(f"Agent-{total_agentes}")
                    self.agentes_em_uso.add(agente)
                    return agente
            
            raise RuntimeError("Pool de agentes esgotado")
    
    def devolver_agente(self, agente: MangabaAgent):
        """Devolve agente ao pool"""
        with self.lock:
            if agente in self.agentes_em_uso:
                self.agentes_em_uso.remove(agente)
                # Limpar contexto do agente para reuso
                if hasattr(agente, 'mcp_protocol'):
                    agente.mcp_protocol.clear_context()
                self.agentes_disponiveis.put(agente)
    
    def processar_lote(self, tarefas: List[Dict], max_workers: int = None) -> List[Any]:
        """Processa lote de tarefas em paralelo"""
        import concurrent.futures
        
        max_workers = max_workers or min(len(tarefas), self.tamanho_maximo)
        resultados = []
        
        def processar_tarefa(tarefa):
            agente = self.obter_agente()
            try:
                if tarefa["tipo"] == "chat":
                    resultado = agente.chat(tarefa["mensagem"])
                elif tarefa["tipo"] == "analise":
                    resultado = agente.analyze_text(
                        tarefa["texto"], 
                        tarefa["instrucao"]
                    )
                else:
                    resultado = f"Tipo {tarefa['tipo']} não suportado"
                
                return {"sucesso": True, "resultado": resultado}
            except Exception as e:
                return {"sucesso": False, "erro": str(e)}
            finally:
                self.devolver_agente(agente)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = [executor.submit(processar_tarefa, tarefa) for tarefa in tarefas]
            
            for futuro in concurrent.futures.as_completed(futuros):
                resultados.append(futuro.result())
        
        return resultados
    
    def estatisticas(self) -> Dict:
        """Retorna estatísticas do pool"""
        with self.lock:
            return {
                "disponiveis": self.agentes_disponiveis.qsize(),
                "em_uso": len(self.agentes_em_uso),
                "total": self.agentes_disponiveis.qsize() + len(self.agentes_em_uso),
                "capacidade_maxima": self.tamanho_maximo
            }

# Uso do pool
def criar_agente_analista(nome):
    return MangabaAgent(agent_name=nome)

pool = PoolDeAgentes(criar_agente_analista, tamanho_inicial=5)

# Processar múltiplas tarefas em paralelo
tarefas = [
    {"tipo": "analise", "texto": "Documento 1", "instrucao": "Extrair tópicos"},
    {"tipo": "analise", "texto": "Documento 2", "instrucao": "Análise de sentimento"},
    {"tipo": "chat", "mensagem": "Resumir conceitos de IA"},
]

resultados = pool.processar_lote(tarefas, max_workers=3)
print(f"📊 Processadas {len(resultados)} tarefas")
```

---

> 🎯 **Próximos Passos**: Continue para [Segurança e Confiabilidade](#-segurança-e-confiabilidade) para aprender sobre práticas seguras.

> 💡 **Dica de Performance**: Combine cache inteligente com pool de agentes para máxima eficiência em aplicações de alta demanda.