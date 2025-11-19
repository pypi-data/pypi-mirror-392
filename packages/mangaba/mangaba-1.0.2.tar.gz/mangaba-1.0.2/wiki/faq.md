# ❓ Perguntas Frequentes (FAQ)

Esta seção responde às dúvidas mais comuns sobre o Mangaba AI, organizadas por categorias para facilitar a navegação.

## 📋 Índice de Categorias

1. [🚀 Instalação e Configuração](#-instalação-e-configuração)
2. [🤖 Agentes e Funcionalidades](#-agentes-e-funcionalidades)
3. [🧠 Protocolo MCP](#-protocolo-mcp)
4. [🔗 Protocolo A2A](#-protocolo-a2a)
5. [⚡ Performance e Otimização](#-performance-e-otimização)
6. [🛡️ Segurança](#-segurança)
7. [🐛 Problemas Comuns](#-problemas-comuns)
8. [💰 Custos e Limitações](#-custos-e-limitações)
9. [🔧 Desenvolvimento e Integração](#-desenvolvimento-e-integração)
10. [🤝 Contribuição e Comunidade](#-contribuição-e-comunidade)

---

## 🚀 Instalação e Configuração

### ❓ Como obter uma API key do Google Generative AI gratuita?

**R:** Siga estes passos:
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Escolha seu projeto do Google Cloud (ou crie um novo)
5. Copie a chave gerada (começará com `AIza...`)

**💡 Dica**: A API gratuita tem limites de uso, mas é suficiente para desenvolvimento e testes.

### ❓ O que fazer se o `pip install` falhar?

**R:** Tente estas soluções em ordem:

```bash
# 1. Atualize pip, setuptools e wheel
pip install --upgrade pip setuptools wheel

# 2. Use ambiente virtual limpo
python -m venv venv_novo
source venv_novo/bin/activate  # Linux/Mac
# ou venv_novo\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Se persistir, instale dependências uma por uma
pip install google-generativeai
pip install python-dotenv
pip install loguru
# ... continue com outras dependências
```

### ❓ Posso usar outros provedores de IA além do Google?

**R:** Sim! O Mangaba AI é agnóstico ao provedor. Para usar outros:

```python
# Exemplo com OpenAI (requer openai package)
from mangaba_agent import MangabaAgent
import openai

class AgenteOpenAI(MangabaAgent):
    def __init__(self, api_key):
        super().__init__(agent_name="OpenAI-Agent")
        openai.api_key = api_key
    
    def chat(self, message, use_context=True):
        # Implementar chamada para OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
```

### ❓ Como configurar múltiplos ambientes (dev, prod)?

**R:** Use arquivos `.env` separados:

```bash
# .env.development
GOOGLE_API_KEY=sua_chave_dev
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# .env.production
GOOGLE_API_KEY=sua_chave_prod
LOG_LEVEL=WARNING
ENVIRONMENT=production
RATE_LIMIT_PER_MINUTE=120
```

```python
# config.py
import os
from dotenv import load_dotenv

# Carregar arquivo específico do ambiente
env = os.getenv('ENVIRONMENT', 'development')
load_dotenv(f'.env.{env}')
```

---

## 🤖 Agentes e Funcionalidades

### ❓ Qual a diferença entre `chat()` e `analyze_text()`?

**R:** 
- **`chat()`**: Para conversação natural, mantém contexto conversacional
- **`analyze_text()`**: Para análise específica de textos com instruções precisas

```python
# Chat - conversação natural
resposta = agent.chat("Como está o tempo hoje?")

# Análise - tarefa específica
analise = agent.analyze_text(
    "Este produto é excelente!",
    "Analisar sentimento do comentário"
)
```

### ❓ Como criar um agente especializado?

**R:** Estenda a classe `MangabaAgent`:

```python
class AgenteContabil(MangabaAgent):
    def __init__(self):
        super().__init__(agent_name="Contabilista")
        
        # Adicionar contexto de especialização
        self.mcp_protocol.add_context(
            content="Especialista em contabilidade e finanças brasileiras",
            context_type="specialization",
            priority=1
        )
    
    def analisar_balanco(self, balanco_patrimonial):
        """Método especializado para análise contábil"""
        return self.analyze_text(
            balanco_patrimonial,
            "Analisar balanço patrimonial conforme normas brasileiras"
        )
    
    def calcular_indicadores(self, dados_financeiros):
        """Calcular indicadores financeiros"""
        return self.analyze_text(
            dados_financeiros,
            "Calcular ROI, ROE, liquidez corrente e margem líquida"
        )
```

### ❓ Como limitar o uso de tokens/custos?

**R:** Implemente controles de rate limiting:

```python
import time
from collections import defaultdict

class ControladorCusto:
    def __init__(self, limite_por_minuto=60):
        self.limite = limite_por_minuto
        self.historico = defaultdict(list)
    
    def pode_executar(self, user_id):
        agora = time.time()
        um_minuto_atras = agora - 60
        
        # Limpar histórico antigo
        self.historico[user_id] = [
            t for t in self.historico[user_id] 
            if t > um_minuto_atras
        ]
        
        # Verificar limite
        if len(self.historico[user_id]) >= self.limite:
            return False
        
        self.historico[user_id].append(agora)
        return True

# Uso no agente
controlador = ControladorCusto(limite_por_minuto=30)

def chat_com_limite(agent, message, user_id):
    if not controlador.pode_executar(user_id):
        return "Limite de uso excedido. Tente novamente em 1 minuto."
    
    return agent.chat(message)
```

---

## 🧠 Protocolo MCP

### ❓ O contexto MCP consome muita memória?

**R:** Por padrão, não. O MCP usa SQLite para armazenamento eficiente:

```python
# Verificar uso de memória do contexto
def verificar_contexto(agent):
    contextos = agent.mcp_protocol.contexts
    tamanho_mb = sum(len(str(ctx)) for ctx in contextos) / (1024 * 1024)
    
    print(f"📊 Contextos: {len(contextos)}")
    print(f"💾 Memória: {tamanho_mb:.2f} MB")
    
    return tamanho_mb

# Limpeza automática se necessário
if verificar_contexto(agent) > 50:  # 50MB
    agent.mcp_protocol.clear_old_contexts(max_age_hours=24)
```

### ❓ Como funciona a busca de contexto relevante?

**R:** O MCP usa busca semântica baseada em similaridade:

```python
# O processo interno é algo como:
# 1. Nova mensagem chega
# 2. MCP busca contextos similares
# 3. Seleciona os mais relevantes
# 4. Inclui no prompt para a IA

# Você pode personalizar a busca:
agent.mcp_protocol.add_context(
    content="Informação importante",
    context_type="business_rule",
    priority=10,  # Alta prioridade
    tags=["regra", "importante"]  # Para busca específica
)
```

### ❓ Posso compartilhar contexto entre agentes?

**R:** Sim, de várias formas:

```python
# 1. Exportar/Importar contexto
contexto_agent1 = agent1.mcp_protocol.export_context()
agent2.mcp_protocol.import_context(contexto_agent1)

# 2. Contexto compartilhado via banco
class ContextoCompartilhado:
    def __init__(self, db_path="shared_context.db"):
        self.db_path = db_path
    
    def sincronizar_agentes(self, agentes):
        """Sincroniza contexto entre múltiplos agentes"""
        for agent in agentes:
            # Implementar sincronização bidirecional
            pass
```

### ❓ Como debugar problemas de contexto?

**R:** Use estas ferramentas de debug:

```python
# 1. Visualizar contexto atual
def debug_contexto(agent):
    resumo = agent.get_context_summary()
    
    print("🔍 DEBUG - Contexto Atual:")
    for tipo, contextos in resumo.items():
        print(f"  {tipo}: {len(contextos)} itens")
        for ctx in contextos[:3]:  # Mostrar primeiros 3
            print(f"    - {ctx[:100]}...")

# 2. Rastrear adições de contexto
class MCPDebug:
    def __init__(self, agent):
        self.agent = agent
        self.original_add = agent.mcp_protocol.add_context
        agent.mcp_protocol.add_context = self.add_context_debug
    
    def add_context_debug(self, content, context_type, priority=1, tags=None):
        print(f"➕ Adicionando contexto: {context_type} (prioridade: {priority})")
        print(f"   Conteúdo: {content[:100]}...")
        return self.original_add(content, context_type, priority, tags)

# Uso
debug = MCPDebug(agent)
```

---

## 🔗 Protocolo A2A

### ❓ Como agentes descobrem uns aos outros?

**R:** Use um registro centralizado ou discovery pattern:

```python
class RegistroDeAgentes:
    def __init__(self):
        self.agentes = {}
    
    def registrar(self, agent_id, endereco, porta, capacidades):
        """Registra agente no discovery service"""
        self.agentes[agent_id] = {
            "endereco": endereco,
            "porta": porta,
            "capacidades": capacidades,
            "status": "ativo",
            "ultimo_ping": time.time()
        }
    
    def descobrir(self, capacidade_necessaria):
        """Descobre agentes com capacidade específica"""
        return [
            agent_id for agent_id, info in self.agentes.items()
            if capacidade_necessaria in info["capacidades"]
        ]

# Uso
registro = RegistroDeAgentes()

# Agente se registra
registro.registrar(
    "AgenteTradutorPT", 
    "localhost", 
    8080, 
    ["traducao", "portugues", "ingles"]
)

# Outro agente descobre tradutor
tradutores = registro.descobrir("traducao")
```

### ❓ Como implementar timeout e retry em A2A?

**R:** Use o padrão circuit breaker (veja [Melhores Práticas](melhores-praticas.md)):

```python
def requisicao_com_retry(agent, destino, acao, params, max_tentativas=3):
    """Requisição A2A com retry automático"""
    for tentativa in range(max_tentativas):
        try:
            resultado = agent.send_agent_request(
                destino, acao, params, timeout=30
            )
            return {"sucesso": True, "resultado": resultado}
        
        except TimeoutError:
            if tentativa == max_tentativas - 1:
                return {"sucesso": False, "erro": "Timeout após todas as tentativas"}
            
            # Backoff exponencial
            time.sleep(2 ** tentativa)
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
```

### ❓ Como balancear carga entre múltiplos agentes?

**R:** Implemente um load balancer:

```python
import random
from collections import deque

class LoadBalancerA2A:
    def __init__(self, algoritmo="round_robin"):
        self.agentes = {}
        self.algoritmo = algoritmo
        self.round_robin_index = 0
    
    def adicionar_agente(self, agent_id, peso=1):
        """Adiciona agente ao pool com peso"""
        self.agentes[agent_id] = {
            "peso": peso,
            "requisicoes_ativas": 0,
            "total_requisicoes": 0,
            "tempo_resposta_medio": 0
        }
    
    def selecionar_agente(self):
        """Seleciona agente baseado no algoritmo"""
        if not self.agentes:
            return None
        
        if self.algoritmo == "round_robin":
            agentes_list = list(self.agentes.keys())
            agente = agentes_list[self.round_robin_index % len(agentes_list)]
            self.round_robin_index += 1
            return agente
        
        elif self.algoritmo == "least_connections":
            return min(
                self.agentes.keys(),
                key=lambda k: self.agentes[k]["requisicoes_ativas"]
            )
        
        elif self.algoritmo == "weighted_random":
            pesos = [info["peso"] for info in self.agentes.values()]
            return random.choices(list(self.agentes.keys()), weights=pesos)[0]
    
    def executar_balanceado(self, agent_origem, acao, params):
        """Executa requisição com balanceamento"""
        agente_selecionado = self.selecionar_agente()
        if not agente_selecionado:
            return {"sucesso": False, "erro": "Nenhum agente disponível"}
        
        # Atualizar métricas
        self.agentes[agente_selecionado]["requisicoes_ativas"] += 1
        
        try:
            inicio = time.time()
            resultado = agent_origem.send_agent_request(
                agente_selecionado, acao, params
            )
            tempo_resposta = time.time() - inicio
            
            # Atualizar estatísticas
            info = self.agentes[agente_selecionado]
            info["total_requisicoes"] += 1
            info["tempo_resposta_medio"] = (
                (info["tempo_resposta_medio"] * (info["total_requisicoes"] - 1) + tempo_resposta) /
                info["total_requisicoes"]
            )
            
            return {"sucesso": True, "resultado": resultado, "agente": agente_selecionado}
        
        finally:
            self.agentes[agente_selecionado]["requisicoes_ativas"] -= 1
```

---

## ⚡ Performance e Otimização

### ❓ Como otimizar performance para muitos usuários?

**R:** Use múltiplas estratégias:

```python
# 1. Pool de agentes
pool = PoolDeAgentes(
    fabrica_agente=lambda nome: MangabaAgent(agent_name=nome),
    tamanho_inicial=10,
    tamanho_maximo=50
)

# 2. Cache de respostas
cache = CacheInteligente(ttl_default=1800)

# 3. Rate limiting por usuário
rate_limiter = ControladorCusto(limite_por_minuto=60)

# 4. Processamento assíncrono
import asyncio

async def processar_multiplas_requisicoes(requisicoes):
    """Processa múltiplas requisições em paralelo"""
    tarefas = []
    
    for req in requisicoes:
        tarefa = asyncio.create_task(processar_requisicao(req))
        tarefas.append(tarefa)
    
    resultados = await asyncio.gather(*tarefas)
    return resultados
```

### ❓ Como monitorar performance em produção?

**R:** Implemente métricas detalhadas:

```python
import time
from collections import defaultdict

class MonitorPerformance:
    def __init__(self):
        self.metricas = defaultdict(list)
        self.contadores = defaultdict(int)
    
    def cronometrar(self, operacao):
        """Decorator para cronometrar operações"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                inicio = time.time()
                try:
                    resultado = func(*args, **kwargs)
                    sucesso = True
                except Exception as e:
                    resultado = str(e)
                    sucesso = False
                finally:
                    duracao = time.time() - inicio
                    self.registrar_metrica(operacao, duracao, sucesso)
                
                return resultado
            return wrapper
        return decorator
    
    def registrar_metrica(self, operacao, duracao, sucesso):
        """Registra métrica de performance"""
        self.metricas[operacao].append({
            "duracao": duracao,
            "sucesso": sucesso,
            "timestamp": time.time()
        })
        
        self.contadores[f"{operacao}_total"] += 1
        if sucesso:
            self.contadores[f"{operacao}_sucesso"] += 1
    
    def relatorio(self):
        """Gera relatório de performance"""
        relatorio = {}
        
        for operacao, medicoes in self.metricas.items():
            duracoes = [m["duracao"] for m in medicoes]
            sucessos = sum(1 for m in medicoes if m["sucesso"])
            
            relatorio[operacao] = {
                "total_execucoes": len(medicoes),
                "taxa_sucesso": sucessos / len(medicoes) if medicoes else 0,
                "tempo_medio": sum(duracoes) / len(duracoes) if duracoes else 0,
                "tempo_min": min(duracoes) if duracoes else 0,
                "tempo_max": max(duracoes) if duracoes else 0
            }
        
        return relatorio

# Uso
monitor = MonitorPerformance()

class AgenteMonitorado(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = monitor
    
    @monitor.cronometrar("chat")
    def chat(self, *args, **kwargs):
        return super().chat(*args, **kwargs)
    
    @monitor.cronometrar("analyze_text")
    def analyze_text(self, *args, **kwargs):
        return super().analyze_text(*args, **kwargs)
```

---

## 🛡️ Segurança

### ❓ Como proteger a API key?

**R:** Siga estas práticas:

```python
# ❌ NUNCA faça isso
API_KEY = "AIzaSyC123..."  # Hard-coded

# ✅ Use variáveis de ambiente
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API_KEY não encontrada!")

# ✅ Para produção, use serviços de secrets
# AWS Secrets Manager, Azure Key Vault, etc.
```

### ❓ Como validar entrada de usuários?

**R:** Implemente validação rigorosa:

```python
import re
from typing import Optional

class ValidadorEntrada:
    @staticmethod
    def limpar_texto(texto: str, max_length: int = 5000) -> Optional[str]:
        """Limpa e valida texto de entrada"""
        if not texto or not isinstance(texto, str):
            return None
        
        # Remover caracteres perigosos
        texto_limpo = re.sub(r'[<>"\']', '', texto)
        
        # Limitar tamanho
        if len(texto_limpo) > max_length:
            texto_limpo = texto_limpo[:max_length]
        
        # Verificar se não é só espaços
        if not texto_limpo.strip():
            return None
        
        return texto_limpo.strip()
    
    @staticmethod
    def validar_comando(comando: str) -> bool:
        """Valida se comando é seguro"""
        comandos_perigosos = [
            "rm ", "del ", "format", "exec", "eval",
            "import os", "subprocess", "__import__"
        ]
        
        comando_lower = comando.lower()
        return not any(perigo in comando_lower for perigo in comandos_perigosos)

# Uso no agente
def chat_seguro(agent, mensagem_raw, user_id):
    # 1. Validar entrada
    mensagem = ValidadorEntrada.limpar_texto(mensagem_raw)
    if not mensagem:
        return "Mensagem inválida"
    
    # 2. Verificar rate limiting
    if not rate_limiter.pode_executar(user_id):
        return "Muitas requisições. Tente novamente em 1 minuto."
    
    # 3. Verificar comando perigoso
    if not ValidadorEntrada.validar_comando(mensagem):
        return "Comando não permitido por segurança"
    
    # 4. Executar com timeout
    try:
        return agent.chat(mensagem)
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        return "Erro interno. Tente novamente."
```

---

## 🐛 Problemas Comuns

### ❓ "Connection refused" em A2A

**R:** Verifique estes pontos:

```python
# 1. Verificar se porta está livre
import socket

def verificar_porta(porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    resultado = sock.connect_ex(('localhost', porta))
    sock.close()
    return resultado == 0  # True se porta estiver em uso

# 2. Configurar portas diferentes
if verificar_porta(8080):
    print("Porta 8080 em uso, usando 8081")
    porta = 8081
else:
    porta = 8080

# 3. Aguardar inicialização do servidor
import time

def conectar_com_retry(agent_origem, host, porta, max_tentativas=5):
    for tentativa in range(max_tentativas):
        try:
            agent_origem.protocols["a2a"].connect_to_agent(host, porta)
            return True
        except:
            time.sleep(1)
    return False
```

### ❓ Consumo excessivo de memória

**R:** Implemente limpeza automática:

```python
import psutil
import gc

class GerenciadorMemoria:
    def __init__(self, limite_mb=500):
        self.limite_mb = limite_mb
    
    def verificar_memoria(self):
        """Verifica uso atual de memória"""
        processo = psutil.Process()
        memoria_mb = processo.memory_info().rss / 1024 / 1024
        return memoria_mb
    
    def limpar_se_necessario(self, agent):
        """Limpa memória se necessário"""
        memoria_atual = self.verificar_memoria()
        
        if memoria_atual > self.limite_mb:
            print(f"⚠️ Memória alta ({memoria_atual:.1f}MB), limpando...")
            
            # Limpar contexto antigo
            agent.mcp_protocol.clear_old_contexts(max_age_hours=1)
            
            # Força garbage collection
            gc.collect()
            
            memoria_nova = self.verificar_memoria()
            print(f"✅ Memória após limpeza: {memoria_nova:.1f}MB")

# Uso automático
gerenciador = GerenciadorMemoria(limite_mb=200)

# Verificar a cada 100 operações
contador = 0
def operacao_com_monitoramento(agent, operacao):
    global contador
    contador += 1
    
    resultado = operacao()
    
    if contador % 100 == 0:
        gerenciador.limpar_se_necessario(agent)
    
    return resultado
```

### ❓ Timeouts frequentes da API

**R:** Implemente backoff e cache:

```python
import random
import time

class GerenciadorAPI:
    def __init__(self, timeout_base=30, max_retries=3):
        self.timeout_base = timeout_base
        self.max_retries = max_retries
        self.ultima_chamada = 0
        self.intervalo_minimo = 1  # segundo entre chamadas
    
    def chamar_com_backoff(self, funcao, *args, **kwargs):
        """Chama API com backoff exponencial"""
        
        # Rate limiting simples
        agora = time.time()
        tempo_desde_ultima = agora - self.ultima_chamada
        if tempo_desde_ultima < self.intervalo_minimo:
            time.sleep(self.intervalo_minimo - tempo_desde_ultima)
        
        for tentativa in range(self.max_retries):
            try:
                self.ultima_chamada = time.time()
                return funcao(*args, **kwargs)
            
            except Exception as e:
                if "timeout" in str(e).lower() and tentativa < self.max_retries - 1:
                    # Backoff exponencial com jitter
                    delay = (2 ** tentativa) + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                raise e

# Aplicar ao agente
gerenciador_api = GerenciadorAPI()

class AgenteResilienteAPI(MangabaAgent):
    def chat(self, *args, **kwargs):
        return gerenciador_api.chamar_com_backoff(
            super().chat, *args, **kwargs
        )
```

---

## 💰 Custos e Limitações

### ❓ Como controlar custos da API?

**R:** Monitore uso e implemente limites:

```python
class ControladorCusto:
    def __init__(self, limite_diario_usd=10):
        self.limite_diario = limite_diario_usd
        self.uso_diario = 0
        self.data_atual = time.strftime("%Y-%m-%d")
    
    def estimar_custo(self, operacao, tamanho_input):
        """Estima custo da operação"""
        # Valores aproximados para Google Gemini (verificar preços atuais)
        custos = {
            "chat": 0.001,      # por 1k caracteres
            "analysis": 0.002,  # análise é mais complexa
            "translation": 0.001
        }
        
        custo_estimado = (tamanho_input / 1000) * custos.get(operacao, 0.001)
        return custo_estimado
    
    def pode_executar(self, operacao, texto):
        """Verifica se operação está dentro do limite"""
        # Reset diário
        data_hoje = time.strftime("%Y-%m-%d")
        if data_hoje != self.data_atual:
            self.uso_diario = 0
            self.data_atual = data_hoje
        
        custo_estimado = self.estimar_custo(operacao, len(texto))
        
        if self.uso_diario + custo_estimado > self.limite_diario:
            return False, f"Limite diário excedido (${self.limite_diario})"
        
        self.uso_diario += custo_estimado
        return True, f"Custo estimado: ${custo_estimado:.4f}"

# Integração com agente
controlador = ControladorCusto(limite_diario_usd=5)

def chat_com_controle_custo(agent, mensagem):
    pode, info = controlador.pode_executar("chat", mensagem)
    
    if not pode:
        return f"❌ {info}"
    
    print(f"💰 {info}")
    return agent.chat(mensagem)
```

### ❓ Quais são os limites da API gratuita?

**R:** Limites típicos (verificar documentação atual):

- **Google Gemini (gratuito)**:
  - 60 requisições por minuto
  - 1.500 requisições por dia
  - 32.000 caracteres por requisição

```python
# Monitorar limites
class MonitorLimites:
    def __init__(self):
        self.requisicoes_minuto = []
        self.requisicoes_dia = []
    
    def registrar_requisicao(self):
        agora = time.time()
        self.requisicoes_minuto.append(agora)
        self.requisicoes_dia.append(agora)
        
        # Limpar histórico antigo
        um_minuto_atras = agora - 60
        um_dia_atras = agora - 86400
        
        self.requisicoes_minuto = [
            t for t in self.requisicoes_minuto if t > um_minuto_atras
        ]
        self.requisicoes_dia = [
            t for t in self.requisicoes_dia if t > um_dia_atras
        ]
    
    def verificar_limites(self):
        return {
            "requisicoes_ultimo_minuto": len(self.requisicoes_minuto),
            "limite_minuto": 60,
            "requisicoes_ultimo_dia": len(self.requisicoes_dia),
            "limite_dia": 1500
        }

monitor = MonitorLimites()
```

---

## 🔧 Desenvolvimento e Integração

### ❓ Como integrar com Django/Flask?

**R:** Exemplo com Flask:

```python
from flask import Flask, request, jsonify
from mangaba_agent import MangabaAgent

app = Flask(__name__)
agent = MangabaAgent(agent_name="WebAgent")

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Mensagem obrigatória"}), 400
    
    try:
        resposta = agent.chat(data['message'])
        return jsonify({
            "response": resposta,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    data = request.get_json()
    
    try:
        resultado = agent.analyze_text(
            data['text'], 
            data.get('instruction', 'Analisar texto')
        )
        return jsonify({
            "analysis": resultado,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### ❓ Como fazer deploy em produção?

**R:** Exemplo com Docker:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV ENVIRONMENT=production
ENV LOG_LEVEL=WARNING

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  mangaba-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### ❓ Como implementar WebSockets para real-time?

**R:** Exemplo com Socket.IO:

```python
from flask_socketio import SocketIO, emit
from flask import Flask

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
agent = MangabaAgent(agent_name="RealtimeAgent")

@socketio.on('chat_message')
def handle_chat(data):
    user_id = data.get('user_id')
    message = data.get('message')
    
    try:
        response = agent.chat(message)
        emit('chat_response', {
            'response': response,
            'user_id': user_id,
            'timestamp': time.time()
        })
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('connected', {'status': 'Conectado ao Mangaba AI'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
```

---

## 🤝 Contribuição e Comunidade

### ❓ Como contribuir com o projeto?

**R:** Siga estes passos:

1. **Fork o repositório**
2. **Crie uma branch para sua feature**:
   ```bash
   git checkout -b feature/minha-feature
   ```
3. **Faça suas alterações e testes**
4. **Commit com mensagem clara**:
   ```bash
   git commit -m "feat: adiciona funcionalidade X"
   ```
5. **Abra um Pull Request**

### ❓ Como reportar bugs?

**R:** Abra uma [issue](https://github.com/Mangaba-ai/mangaba_ai/issues) com:

- **Descrição clara** do problema
- **Passos para reproduzir**
- **Comportamento esperado vs atual**
- **Ambiente** (SO, Python, versões)
- **Logs de erro** se disponíveis

```python
# Template para reproduzir bugs
from mangaba_agent import MangabaAgent

# Configuração do ambiente
agent = MangabaAgent(agent_name="TestAgent")

# Código que reproduz o bug
try:
    resultado = agent.chat("mensagem que causa erro")
    print(resultado)
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
```

### ❓ Como sugerir melhorias?

**R:** Abra uma [issue](https://github.com/Mangaba-ai/mangaba_ai/issues) de feature request com:

- **Descrição da melhoria**
- **Justificativa** (por que é útil)
- **Exemplo de uso** (como seria usado)
- **Possível implementação** (se tiver ideias)

---

## 🆘 Precisa de Mais Ajuda?

Se sua dúvida não foi respondida aqui:

1. **📖 Consulte a [Documentação Completa](README.md)**
2. **🔍 Busque no [Glossário](glossario.md)** por termos técnicos
3. **💡 Veja os [Exemplos Práticos](exemplos-protocolos.md)**
4. **🐛 Abra uma [Issue](https://github.com/Mangaba-ai/mangaba_ai/issues)** no GitHub
5. **💬 Participe da comunidade** (Discord, Telegram, etc.)

---

> 💡 **Dica**: Esta FAQ é atualizada regularmente. Marque esta página e consulte frequentemente para novidades!

> 🤝 **Contribua**: Encontrou uma pergunta não coberta? Abra uma issue para adicionarmos à FAQ!