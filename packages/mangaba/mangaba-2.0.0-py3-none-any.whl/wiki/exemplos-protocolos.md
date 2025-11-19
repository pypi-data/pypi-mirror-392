# 🌐 Exemplos dos Protocolos A2A e MCP

Este guia apresenta exemplos práticos e detalhados dos protocolos **A2A (Agent-to-Agent)** e **MCP (Model Context Protocol)** que são o coração do Mangaba AI.

## 📋 Índice

1. [Protocolo MCP](#-protocolo-mcp)
2. [Protocolo A2A](#-protocolo-a2a)
3. [Integração dos Protocolos](#-integração-dos-protocolos)
4. [Casos de Uso Avançados](#-casos-de-uso-avançados)
5. [Troubleshooting](#-troubleshooting)

---

## 🧠 Protocolo MCP

O **Model Context Protocol** gerencia automaticamente o contexto e memória do agente, permitindo conversas contínuas e inteligentes.

### Exemplo Básico - Chat com Contexto

```python
from mangaba_agent import MangabaAgent

# Criar agente com MCP automático
agent = MangabaAgent(agent_name="Assistente")

# Primeira mensagem - estabelece contexto
resposta1 = agent.chat("Meu nome é João e trabalho com Python", use_context=True)
print(f"🤖: {resposta1}")

# Segunda mensagem - usa contexto anterior
resposta2 = agent.chat("Que linguagem eu uso no trabalho?", use_context=True)
print(f"🤖: {resposta2}")
# Resultado: "Você trabalha com Python, João!"

# Terceira mensagem - contexto acumulativo
resposta3 = agent.chat("Recomendar uma biblioteca para análise de dados", use_context=True)
print(f"🤖: {resposta3}")
# Resultado: "Para Python, recomendo pandas, numpy e matplotlib..."
```

### Contexto Personalizado e Sessões

```python
from mangaba_agent import MangabaAgent
from protocols.mcp import MCPContext

# Criar agente
agent = MangabaAgent()

# Adicionar contexto personalizado
agent.mcp_protocol.add_context(
    content="Usuário é desenvolvedor senior especializado em IA",
    context_type="user_profile",
    priority=1,  # Alta prioridade
    tags=["perfil", "especialização"]
)

agent.mcp_protocol.add_context(
    content="Projeto atual: Sistema de recomendação usando ML",
    context_type="project_info",
    priority=1,
    tags=["projeto", "ml", "recomendação"]
)

# Chat que usa contexto personalizado
resposta = agent.chat("Como posso melhorar a acurácia do meu modelo?")
print(f"🤖: {resposta}")
# Resultado personalizado baseado no perfil e projeto
```

### Análise com Contexto Persistente

```python
from mangaba_agent import MangabaAgent

agent = MangabaAgent(agent_name="Analista")

# Primeira análise
documento1 = """
Relatório de vendas Q1: Aumento de 15% nas vendas.
Principais produtos: Software (40%), Hardware (35%), Serviços (25%).
"""

resultado1 = agent.analyze_text(
    documento1, 
    "Extrair métricas principais",
    use_context=True
)
print(f"📊 Análise 1: {resultado1}")

# Segunda análise - compara com anterior automaticamente
documento2 = """
Relatório de vendas Q2: Aumento de 22% nas vendas.
Principais produtos: Software (45%), Hardware (30%), Serviços (25%).
"""

resultado2 = agent.analyze_text(
    documento2,
    "Comparar com período anterior e identificar tendências",
    use_context=True
)
print(f"📊 Análise 2: {resultado2}")
# Resultado: Incluirá comparação automática com Q1
```

### Resumo e Gestão de Contexto

```python
# Obter resumo do contexto atual
resumo = agent.get_context_summary()
print("📝 Resumo do Contexto:")
for tipo, dados in resumo.items():
    print(f"  {tipo}: {len(dados)} itens")

# Exemplo de saída:
# 📝 Resumo do Contexto:
#   chat_history: 5 itens
#   analysis_results: 2 itens
#   user_profile: 1 itens
#   project_info: 1 itens

# Limpeza seletiva de contexto
agent.mcp_protocol.clear_context(context_type="chat_history")

# Exportar contexto para backup
contexto_backup = agent.mcp_protocol.export_context()
```

---

## 🔗 Protocolo A2A

O **Agent-to-Agent Protocol** permite comunicação estruturada entre múltiplos agentes especializados.

### Exemplo Básico - Dois Agentes

```python
from mangaba_agent import MangabaAgent
from protocols.a2a import A2AProtocol

# Criar dois agentes especializados
agente_pesquisa = MangabaAgent(agent_name="Pesquisador")
agente_redator = MangabaAgent(agent_name="Redator")

# Configurar protocolos A2A
a2a_pesquisa = A2AProtocol(agent_id="Pesquisador", port=8080)
a2a_redator = A2AProtocol(agent_id="Redator", port=8081)

# Adicionar protocolos aos agentes
agente_pesquisa.add_protocol(a2a_pesquisa)
agente_redator.add_protocol(a2a_redator)

# Conectar agentes
a2a_pesquisa.connect_to_agent("localhost", 8081)

# Pesquisador envia tarefa para redator
resposta = agente_pesquisa.send_agent_request(
    agent_id="Redator",
    action="criar_artigo",
    params={
        "topico": "Inteligência Artificial em 2024",
        "palavras": 500,
        "tom": "técnico mas acessível"
    }
)

print(f"📝 Artigo criado: {resposta}")
```

### Sistema Multi-Agente Complexo

```python
from mangaba_agent import MangabaAgent
from protocols.a2a import A2AProtocol, A2AMessage

class SistemaAnaliseDocumentos:
    def __init__(self):
        # Criar agentes especializados
        self.coordenador = MangabaAgent(agent_name="Coordenador")
        self.extrator = MangabaAgent(agent_name="Extrator")
        self.analisador = MangabaAgent(agent_name="Analisador")
        self.relatorio = MangabaAgent(agent_name="Relatorio")
        
        # Configurar rede A2A
        self.setup_a2a_network()
        self.setup_handlers()
    
    def setup_a2a_network(self):
        """Configura a rede de comunicação A2A"""
        # Protocolos A2A para cada agente
        portas = {"Coordenador": 8080, "Extrator": 8081, 
                 "Analisador": 8082, "Relatorio": 8083}
        
        self.protocolos = {}
        for nome, porta in portas.items():
            protocolo = A2AProtocol(agent_id=nome, port=porta)
            self.protocolos[nome] = protocolo
            getattr(self, nome.lower()).add_protocol(protocolo)
        
        # Conectar todos os agentes
        for nome1, proto1 in self.protocolos.items():
            for nome2, porta2 in portas.items():
                if nome1 != nome2:
                    proto1.connect_to_agent("localhost", porta2)
    
    def setup_handlers(self):
        """Configura handlers personalizados"""
        
        # Handler do Extrator
        def handler_extrator(message):
            if message.content.get("action") == "extrair_texto":
                documento = message.content.get("documento")
                # Simulação de extração
                texto = f"Texto extraído de: {documento[:100]}..."
                return {"texto": texto, "status": "sucesso"}
        
        # Handler do Analisador
        def handler_analisador(message):
            if message.content.get("action") == "analisar_sentimento":
                texto = message.content.get("texto")
                # Simulação de análise
                sentimento = "positivo" if "bom" in texto.lower() else "neutro"
                return {"sentimento": sentimento, "confianca": 0.85}
        
        # Registrar handlers
        self.protocolos["Extrator"].register_handler("REQUEST", handler_extrator)
        self.protocolos["Analisador"].register_handler("REQUEST", handler_analisador)
    
    def processar_documento(self, documento):
        """Pipeline completo de processamento"""
        print("🔄 Iniciando pipeline de análise...")
        
        # 1. Coordenador → Extrator
        resultado_extracao = self.coordenador.send_agent_request(
            "Extrator", "extrair_texto", {"documento": documento}
        )
        
        # 2. Coordenador → Analisador
        resultado_analise = self.coordenador.send_agent_request(
            "Analisador", "analisar_sentimento", 
            {"texto": resultado_extracao["texto"]}
        )
        
        # 3. Coordenador → Relatório
        relatorio_final = self.coordenador.send_agent_request(
            "Relatorio", "gerar_relatorio", {
                "extracao": resultado_extracao,
                "analise": resultado_analise
            }
        )
        
        return relatorio_final

# Uso do sistema
sistema = SistemaAnaliseDocumentos()
documento = "Este é um documento muito bom sobre IA..."
resultado = sistema.processar_documento(documento)
print(f"📄 Relatório: {resultado}")
```

### Broadcast e Notificações

```python
from mangaba_agent import MangabaAgent

# Agente coordenador
coordenador = MangabaAgent(agent_name="Coordenador")

# Broadcast para múltiplos agentes
agentes_alvo = ["Agente1", "Agente2", "Agente3"]
coordenador.broadcast_message(
    message="Sistema será reiniciado em 5 minutos",
    target_agents=agentes_alvo,
    priority="high"
)

# Broadcast com tags
coordenador.broadcast_message(
    message="Nova tarefa disponível: análise de dados",
    tags=["analise", "dados", "urgente"],
    message_type="task_assignment"
)
```

---

## 🔄 Integração dos Protocolos

### Agente com MCP e A2A Simultâneos

```python
from mangaba_agent import MangabaAgent

class AgenteAvancado:
    def __init__(self, nome, porta_a2a):
        # Inicializar agente com ambos os protocolos
        self.agent = MangabaAgent(agent_name=nome)
        
        # MCP já é automático, configurar A2A
        self.setup_a2a(porta_a2a)
        
        # Configurar contexto inicial
        self.setup_initial_context()
    
    def setup_a2a(self, porta):
        """Configura protocolo A2A"""
        from protocols.a2a import A2AProtocol
        
        a2a = A2AProtocol(agent_id=self.agent.agent_name, port=porta)
        self.agent.add_protocol(a2a)
        
        # Handler que usa contexto MCP
        def handler_com_contexto(message):
            acao = message.content.get("action")
            params = message.content.get("params", {})
            
            if acao == "conversar":
                # Usar chat com contexto MCP
                resposta = self.agent.chat(
                    params.get("mensagem", ""), 
                    use_context=True
                )
                return {"resposta": resposta}
            
            elif acao == "analisar_com_historico":
                # Análise que considera histórico via MCP
                texto = params.get("texto")
                resultado = self.agent.analyze_text(
                    texto, 
                    "Analisar considerando contexto anterior",
                    use_context=True
                )
                return {"analise": resultado}
        
        a2a.register_handler("REQUEST", handler_com_contexto)
    
    def setup_initial_context(self):
        """Configura contexto inicial"""
        self.agent.mcp_protocol.add_context(
            content=f"Agente {self.agent.agent_name} especializado em análise",
            context_type="agent_profile",
            priority=1
        )
    
    def colaborar_com_contexto(self, outro_agente_id, tarefa):
        """Colaboração que mantém contexto"""
        # Obter contexto atual
        contexto = self.agent.get_context_summary()
        
        # Enviar requisição com contexto
        resposta = self.agent.send_agent_request(
            outro_agente_id,
            "colaborar",
            {
                "tarefa": tarefa,
                "meu_contexto": contexto,
                "timestamp": "2024-01-01T10:00:00"
            }
        )
        
        # Armazenar resultado no contexto MCP
        self.agent.mcp_protocol.add_context(
            content=f"Colaboração com {outro_agente_id}: {resposta}",
            context_type="collaboration_history",
            priority=1
        )
        
        return resposta

# Uso prático
agente1 = AgenteAvancado("Especialista1", 8080)
agente2 = AgenteAvancado("Especialista2", 8081)

# Conectar agentes
agente1.agent.protocols["a2a"].connect_to_agent("localhost", 8081)

# Colaboração com contexto
resultado = agente1.colaborar_com_contexto(
    "Especialista2", 
    "Analisar tendências de mercado"
)
```

---

## 🚀 Casos de Uso Avançados

### 1. Sistema de Atendimento Multi-Agente

```python
class AtendimentoInteligente:
    def __init__(self):
        # Agentes especializados
        self.triagem = MangabaAgent(agent_name="Triagem")
        self.tecnico = MangabaAgent(agent_name="Tecnico")
        self.comercial = MangabaAgent(agent_name="Comercial")
        self.supervisor = MangabaAgent(agent_name="Supervisor")
        
        self.setup_network()
    
    def atender_cliente(self, mensagem_cliente, historico_cliente=None):
        """Pipeline de atendimento inteligente"""
        
        # 1. Adicionar histórico do cliente ao contexto (MCP)
        if historico_cliente:
            self.triagem.mcp_protocol.add_context(
                content=f"Histórico do cliente: {historico_cliente}",
                context_type="customer_history",
                priority=1
            )
        
        # 2. Triagem decide encaminhamento
        classificacao = self.triagem.analyze_text(
            mensagem_cliente,
            "Classificar como: tecnico, comercial, ou complexo",
            use_context=True
        )
        
        # 3. Encaminhamento via A2A
        if "tecnico" in classificacao.lower():
            resposta = self.triagem.send_agent_request(
                "Tecnico", "resolver_problema", 
                {"problema": mensagem_cliente}
            )
        elif "comercial" in classificacao.lower():
            resposta = self.triagem.send_agent_request(
                "Comercial", "atender_venda",
                {"interesse": mensagem_cliente}
            )
        else:
            # Caso complexo → supervisor
            resposta = self.triagem.send_agent_request(
                "Supervisor", "avaliar_caso",
                {"caso": mensagem_cliente, "contexto": historico_cliente}
            )
        
        return resposta

# Uso
atendimento = AtendimentoInteligente()
resposta = atendimento.atender_cliente(
    "Meu software não está funcionando após a atualização",
    historico_cliente="Cliente premium há 2 anos, última compra em dezembro"
)
```

### 2. Rede de Agentes de Pesquisa

```python
class RedeIAdePesquisa:
    def __init__(self):
        # Especialistas em diferentes áreas
        self.especialistas = {
            "tecnologia": MangabaAgent(agent_name="Tech"),
            "mercado": MangabaAgent(agent_name="Market"),
            "academia": MangabaAgent(agent_name="Academic"),
            "sintese": MangabaAgent(agent_name="Synthesizer")
        }
        
        self.setup_research_network()
    
    def pesquisar_topico(self, topico, profundidade="media"):
        """Pesquisa colaborativa multi-agente"""
        
        resultados = {}
        
        # 1. Cada especialista pesquisa sua área
        for area, agente in self.especialistas.items():
            if area != "sintese":  # Síntese vai por último
                # Contexto específico da área
                agente.mcp_protocol.add_context(
                    content=f"Especialização: {area}",
                    context_type="specialization"
                )
                
                # Pesquisa via A2A coordenada
                resultado = agente.send_agent_request(
                    "Coordinator", "pesquisar_area",
                    {
                        "topico": topico,
                        "area": area,
                        "profundidade": profundidade
                    }
                )
                
                resultados[area] = resultado
        
        # 2. Síntese dos resultados
        sintese_final = self.especialistas["sintese"].send_agent_request(
            "Synthesizer", "sintetizar_pesquisa",
            {
                "topico": topico,
                "resultados_areas": resultados
            }
        )
        
        return {
            "topico": topico,
            "resultados_por_area": resultados,
            "sintese": sintese_final
        }

# Uso
rede = RedeIAdePesquisa()
relatorio = rede.pesquisar_topico(
    "Impacto da IA Generativa no Mercado de Trabalho",
    profundidade="alta"
)
```

---

## 🔍 Troubleshooting

### Problemas Comuns MCP

#### Contexto Não Persistindo
```python
# ❌ Problema: contexto não funciona
agent.chat("Mensagem 1")  # use_context=False por padrão
agent.chat("Mensagem 2")  # Não lembra da anterior

# ✅ Solução: sempre usar use_context=True
agent.chat("Mensagem 1", use_context=True)
agent.chat("Mensagem 2", use_context=True)
```

#### Memória Excessiva
```python
# ✅ Limpeza periódica de contexto
if len(agent.mcp_protocol.contexts) > 1000:
    agent.mcp_protocol.clear_old_contexts(max_age_hours=24)
```

### Problemas Comuns A2A

#### Agentes Não Se Conectam
```python
# ❌ Problema: portas em conflito
a2a1 = A2AProtocol(agent_id="Agent1", port=8080)
a2a2 = A2AProtocol(agent_id="Agent2", port=8080)  # Mesma porta!

# ✅ Solução: portas diferentes
a2a1 = A2AProtocol(agent_id="Agent1", port=8080)
a2a2 = A2AProtocol(agent_id="Agent2", port=8081)
```

#### Timeout em Requisições
```python
# ✅ Configurar timeout apropriado
resposta = agent.send_agent_request(
    "OutroAgente", "acao_demorada",
    params={"dados": "..."},
    timeout=60  # 60 segundos
)
```

### Debug e Monitoramento

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor de contexto MCP
def monitor_mcp(agent):
    contextos = agent.mcp_protocol.get_context_stats()
    print(f"📊 Contextos: {contextos}")

# Monitor de conexões A2A
def monitor_a2a(agent):
    conexoes = agent.protocols["a2a"].get_connection_status()
    print(f"🔗 Conexões A2A: {conexoes}")
```

---

> 🎯 **Próximos Passos**: Agora que você domina os protocolos, explore as [Melhores Práticas](melhores-praticas.md) para otimizar seus agentes!

> 💡 **Dica Avançada**: Combine MCP e A2A para criar sistemas verdadeiramente inteligentes - use MCP para memória individual dos agentes e A2A para coordenação entre eles.