# ❓ FAQ - Perguntas Frequentes - Mangaba AI

Esta seção contém as **perguntas mais frequentes** sobre o projeto Mangaba AI, organizadas por categoria para facilitar sua consulta. Se você não encontrar sua dúvida aqui, consulte nosso [Glossário](GLOSSARIO.md) ou abra uma [discussion no GitHub](https://github.com/Mangaba-ai/mangaba_ai/discussions).

## 📋 Índice

1. [🚀 Primeiros Passos](#-primeiros-passos)
2. [⚙️ Configuração e Instalação](#️-configuração-e-instalação)
3. [📦 UV vs pip - Qual usar?](#-uv-vs-pip---qual-usar)
4. [🤖 Uso do Agente](#-uso-do-agente)
5. [🌐 Protocolos A2A e MCP](#-protocolos-a2a-e-mcp)
6. [🐛 Problemas Comuns](#-problemas-comuns)
7. [🔧 Desenvolvimento e Contribuição](#-desenvolvimento-e-contribuição)
8. [💰 Custos e Limites](#-custos-e-limites)
9. [🔐 Segurança e Privacidade](#-segurança-e-privacidade)

---

## 🚀 Primeiros Passos

### **❓ O que é o Mangaba AI?**

O **Mangaba AI** é um framework brasileiro para criação de agentes de inteligência artificial que combina:
- 🤖 **Agente Principal**: Baseado no Google Generative AI (Gemini)
- 🔗 **Protocolo A2A**: Para comunicação entre múltiplos agentes
- 🧠 **Protocolo MCP**: Para gerenciamento inteligente de contexto
- ⚡ **Performance**: Otimizado para alta escalabilidade

### **❓ Para que serve o Mangaba AI?**

O Mangaba AI é ideal para:
- 📄 **Análise de documentos**: Contratos, relatórios, artigos
- 🤝 **Assistentes virtuais**: Atendimento ao cliente, suporte técnico
- 🔄 **Automação de processos**: Fluxos de trabalho complexos
- 🌐 **Tradução**: Textos técnicos e especializados
- 📊 **Análise de dados**: Insights e relatórios automatizados

### **❓ Preciso saber programar para usar?**

**Depende do seu objetivo:**
- 🟢 **Uso básico**: Exemplos prontos, scripts de configuração automática
- 🟡 **Personalização**: Conhecimento básico de Python é recomendado
- 🔴 **Desenvolvimento avançado**: Conhecimento sólido de Python e APIs

### **❓ É gratuito?**

**Sim e não:**
- ✅ **Código do Mangaba AI**: Totalmente gratuito (MIT License)
- 💰 **API do Google**: Paga por uso (mas tem limite gratuito generoso)
- 📊 **Custos típicos**: R$ 10-50/mês para uso pessoal/pequeno

---

## ⚙️ Configuração e Instalação

### **❓ Quais são os requisitos mínimos?**

**Sistema:**
- 🐍 **Python**: 3.8 ou superior
- 💾 **RAM**: 2GB mínimo, 4GB recomendado
- 💿 **Espaço**: 1GB para instalação completa
- 🌐 **Internet**: Conexão estável para API calls

**Conta Google:**
- 🔑 **Google Cloud Account**: Para obter API key
- 💳 **Billing ativado**: Para usar além do limite gratuito

### **❓ Como obter a API key do Google?**

**Passo a passo:**
1. 🌐 Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 🔑 Faça login com sua conta Google
3. ➕ Clique em "Create API Key"
4. 📋 Copie a chave gerada
5. 🔐 Configure no arquivo `.env`:
   ```bash
   GOOGLE_API_KEY=sua_chave_aqui
   ```

### **❓ A instalação falhou. O que fazer?**

**Soluções comuns:**

**1. Problema com dependências:**

```bash
# Com UV (mais rápido):
uv sync --reinstall

# Com pip (tradicional):
# Atualizar pip
python -m pip install --upgrade pip

# Instalar com verbose para ver erros
pip install -r requirements.txt -v
```

**2. Python muito antigo:**
```bash
# Verificar versão (precisa ser 3.9+)
python --version

# Se menor que 3.9, instalar versão mais nova
```

**3. Problemas de permissão:**
```bash
# Use ambiente virtual (UV ou pip):

# Opção A: UV
uv venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows
uv sync

# Opção B: pip
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### **❓ Como validar se está tudo funcionando?**

**Execute nosso script de validação:**
```bash
python scripts/validate_env.py
```

**Teste básico:**
```bash
python examples/basic_example.py
```

**Se ambos funcionarem, está tudo certo! ✅**

---

## 📦 UV vs pip - Qual usar?

### **❓ Qual a diferença entre UV e pip?**

**UV** é um gerenciador de pacotes Python moderno, escrito em Rust, que é **10-100x mais rápido** que o pip tradicional. Veja a comparação:

| Característica | UV | pip |
|---|---|---|
| **Velocidade** | ⚡ 10-100x mais rápido | 🐢 Tradicional |
| **Resolução de dependências** | 🎯 Muito mais rápida | ⏳ Pode ser lenta |
| **Lock file** | ✅ uv.lock (determinístico) | ❌ Não nativo |
| **Cache inteligente** | ✅ Global e eficiente | 🔄 Básico |
| **Compatibilidade** | ✅ 100% compatível com pip | ✅ Padrão Python |
| **Maturidade** | 🆕 Novo (2024+) | 🏛️ Estabelecido |

### **❓ Devo usar UV ou pip?**

**Use UV se:**
- ⚡ Você quer velocidade máxima
- 🔄 Trabalha com CI/CD
- 📦 Gerencia muitos projetos
- 🆕 Está confortável com ferramentas modernas

**Use pip se:**
- 🏢 Seu ambiente corporativo exige pip
- 🛠️ Você prefere ferramentas estabelecidas
- 📚 Quer máxima compatibilidade histórica
- 🎯 Simplicidade é prioridade

**Ambos funcionam perfeitamente com Mangaba AI!** 🎉

### **❓ Como migrar de pip para UV?**

```bash
# 1. Instalar UV
pip install uv

# 2. Criar .venv com UV
uv venv

# 3. Ativar ambiente
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

# 4. Sincronizar dependências
uv sync

# Pronto! Tudo instalado 10-100x mais rápido 🚀
```

### **❓ Como voltar de UV para pip?**

```bash
# 1. Desativar ambiente atual
deactivate

# 2. Remover .venv
rm -rf .venv  # Linux/Mac
Remove-Item -Recurse -Force .venv  # Windows

# 3. Criar novo .venv com venv padrão
python -m venv .venv

# 4. Ativar
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# 5. Instalar com pip
pip install -r requirements.txt
```

### **❓ Posso ter projetos com UV e pip ao mesmo tempo?**

**Sim!** Cada projeto pode usar o gerenciador que preferir:

```bash
# Projeto A com UV
cd projeto-a
uv sync

# Projeto B com pip
cd ../projeto-b
pip install -r requirements.txt
```

Mangaba AI suporta ambos igualmente! 🎯

---

## 🤖 Uso do Agente

### **❓ Como criar meu primeiro agente?**

**Exemplo mais simples:**
```python
from mangaba_agent import MangabaAgent

# Criar agente
agente = MangabaAgent(
    api_key="sua_chave_google",
    agent_id="meu_primeiro_agente"
)

# Usar
resposta = agente.chat("Olá! Como você pode me ajudar?")
print(resposta)
```

### **❓ Como fazer o agente "lembrar" de conversas anteriores?**

**O contexto MCP faz isso automaticamente:**
```python
# Primeira interação
agente.chat("Meu nome é João e trabalho com marketing")

# Segunda interação - ele lembrará do contexto
agente.chat("Que estratégias você recomenda para minha área?")
# Resposta considerará que você trabalha com marketing!
```

### **❓ Posso usar o agente sem contexto?**

**Sim, desabilitando o MCP:**
```python
# Sem contexto
resposta = agente.chat("Sua pergunta", use_context=False)

# Ou criando agente sem MCP
agente = MangabaAgent(
    api_key="sua_chave",
    enable_mcp=False
)
```

### **❓ Como analisar documentos grandes?**

**Para textos longos:**
```python
# Ler arquivo
with open("documento.txt", "r", encoding="utf-8") as f:
    texto = f.read()

# Análise especializada
resultado = agente.analyze_text(
    text=texto,
    instruction="Faça um resumo executivo destacando pontos principais"
)

print(resultado)
```

### **❓ Como traduzir textos técnicos?**

**Tradução especializada:**
```python
# Texto técnico
texto_original = "Machine learning algorithms require extensive data preprocessing"

# Tradução contextualizada
traducao = agente.translate(
    text=texto_original,
    target_language="português brasileiro técnico"
)

print(traducao)
# Output: "Algoritmos de aprendizado de máquina requerem pré-processamento extensivo de dados"
```

---

## 🌐 Protocolos A2A e MCP

### **❓ O que é o protocolo A2A?**

**A2A (Agent-to-Agent)** permite que múltiplos agentes se comuniquem:
- 🔄 **Comunicação bidirecional**: Agentes podem conversar entre si
- 📡 **Broadcast**: Um agente pode falar com vários simultaneamente
- 🎯 **Handlers específicos**: Cada agente pode ter especialidades
- 🌐 **Rede distribuída**: Agentes podem estar em máquinas diferentes

### **❓ Como conectar dois agentes?**

**Exemplo prático:**
```python
# Agente 1 (Analista)
agente1 = MangabaAgent(agent_id="analista_financeiro")
agente1.setup_a2a_protocol(port=8080)

# Agente 2 (Redator)
agente2 = MangabaAgent(agent_id="redator_relatorios")
agente2.setup_a2a_protocol(port=8081)

# Conectar agente1 ao agente2
agente1.a2a_protocol.connect_to_agent("localhost", 8081)

# Comunicação
resultado = agente1.send_agent_request(
    target_agent_id="redator_relatorios",
    action="chat",
    params={"message": "Preciso de um resumo executivo dos dados financeiros"}
)

print(resultado)
```

### **❓ O que é o protocolo MCP?**

**MCP (Model Context Protocol)** gerencia o contexto das conversas:
- 🧠 **Memória inteligente**: Lembra informações relevantes
- 🏷️ **Tags e categorias**: Organiza contextos por tipo
- 🔍 **Busca avançada**: Encontra contextos relevantes automaticamente
- ⏰ **Gestão temporal**: Remove contextos antigos automaticamente

### **❓ Como controlar o contexto MCP?**

**Operações básicas:**
```python
# Ver contexto atual
resumo = agente.get_context_summary()
print(resumo)

# Limpar contexto da sessão
agente.mcp.clear_session(agente.current_session_id)

# Adicionar contexto específico
from protocols.mcp import MCPContext, ContextType

contexto = MCPContext.create(
    context_type=ContextType.USER,
    content="Usuário é desenvolvedor Python sênior",
    tags=["perfil", "usuario", "desenvolvedor"]
)
agente.mcp.add_context(contexto, agente.current_session_id)
```

### **❓ Os agentes podem ter especialidades diferentes?**

**Sim! Exemplo de especialização:**
```python
class AgenteMedico(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handler especializado
        @self.a2a_protocol.register_handler("diagnosticar")
        def handle_diagnostico(message):
            sintomas = message.content.get("sintomas")
            return self.analyze_text(
                sintomas,
                "Análise médica: liste possíveis diagnósticos"
            )

class AgenteJuridico(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        @self.a2a_protocol.register_handler("analisar_contrato")
        def handle_contrato(message):
            contrato = message.content.get("texto")
            return self.analyze_text(
                contrato,
                "Análise jurídica: identifique cláusulas importantes e riscos"
            )
```

---

## 🐛 Problemas Comuns

### **❓ Erro "API key inválida" - o que fazer?**

**Soluções:**

**1. Verificar a chave:**
```bash
# No terminal
echo $GOOGLE_API_KEY
```

**2. Testar a chave manualmente:**
```python
import google.generativeai as genai

genai.configure(api_key="sua_chave")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Teste")
print(response.text)
```

**3. Problemas comuns:**
- ❌ Chave com espaços ou caracteres especiais
- ❌ Chave expirada ou desativada
- ❌ Billing não configurado no Google Cloud

### **❓ Agente responde muito devagar - como otimizar?**

**Estratégias de otimização:**

**1. Use cache:**
```python
# Cache automático para respostas repetidas
from utils.cache import ResponseCache

cache = ResponseCache()
agente = CachedMangabaAgent(cache=cache)
```

**2. Reduza o contexto:**
```python
# Chat sem contexto para respostas rápidas
resposta = agente.chat("pergunta", use_context=False)
```

**3. Use modelo mais rápido:**
```python
agente = MangabaAgent(
    model="gemini-pro",  # Mais rápido que gemini-pro-vision
    api_key="sua_chave"
)
```

### **❓ Erro de conexão A2A - agentes não se comunicam?**

**Troubleshooting A2A:**

**1. Verificar portas:**
```python
# Usar portas diferentes para cada agente
agente1.setup_a2a_protocol(port=8080)
agente2.setup_a2a_protocol(port=8081)
```

**2. Verificar firewall:**
```bash
# Linux: verificar se portas estão abertas
sudo ufw status
sudo ufw allow 8080
sudo ufw allow 8081
```

**3. Teste de conectividade:**
```python
# Testar se agente está respondendo
import requests
response = requests.get("http://localhost:8080/health")
print(response.status_code)  # Deve ser 200
```

### **❓ Contexto MCP crescendo muito - como limpar?**

**Gestão de contexto:**
```python
# Verificar tamanho do contexto
contextos = agente.mcp.get_contexts(agente.current_session_id)
print(f"Total de contextos: {len(contextos)}")

# Limpar contextos antigos (mais de 24h)
agente.mcp.cleanup_old_contexts(max_age_hours=24)

# Resumir contextos de baixa prioridade
agente.mcp.summarize_low_priority_contexts()

# Limpar tudo se necessário
agente.mcp.clear_session(agente.current_session_id)
```

### **❓ Erro "Rate limit exceeded" - muitas requisições?**

**Controle de rate limiting:**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=30):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# Uso
@rate_limit(calls_per_minute=20)
def fazer_requisicao_limitada():
    return agente.chat("sua pergunta")
```

---

## 🔧 Desenvolvimento e Contribuição

### **❓ Como contribuir com o projeto?**

**Consulte nosso guia completo:** [CONTRIBUICAO.md](CONTRIBUICAO.md)

**Primeiros passos:**
1. 🍴 Faça fork do repositório
2. 📥 Clone localmente
3. 🔧 Configure ambiente de desenvolvimento
4. 🧪 Execute testes
5. ✨ Implemente melhorias
6. 📤 Abra Pull Request

### **❓ Como executar os testes?**

**Testes básicos:**
```bash
# Instalar dependências de teste
pip install -r requirements-test.txt

# Executar todos os testes
python -m pytest tests/ -v

# Executar testes específicos
python -m pytest tests/test_agent.py -v

# Com cobertura
coverage run -m pytest tests/
coverage report -m
```

### **❓ Como criar um novo protocolo personalizado?**

**Estrutura básica:**
```python
# protocols/meu_protocolo.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class MeuProtocolo(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ativo = False
    
    @abstractmethod
    def start(self) -> bool:
        """Inicializar protocolo"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Parar protocolo"""
        pass
    
    @abstractmethod
    def send_message(self, message: str, target: str) -> Dict:
        """Enviar mensagem"""
        pass

# Implementação específica
class ProtocoloWebSocket(MeuProtocolo):
    def start(self):
        # Implementar lógica de WebSocket
        self.ativo = True
        return True
    
    def stop(self):
        self.ativo = False
        return True
    
    def send_message(self, message, target):
        # Implementar envio via WebSocket
        return {"success": True, "response": "Message sent"}
```

### **❓ Como debug problemas no desenvolvimento?**

**Debug do agente:**
```python
import logging

# Habilitar debug
logging.basicConfig(level=logging.DEBUG)

# Criar agente com debug
agente = MangabaAgent(
    api_key="sua_chave",
    agent_id="debug_agent"
)

# Log detalhado será exibido
agente.chat("teste de debug")
```

**Debug A2A:**
```python
# Habilitar logs A2A
agente.a2a_protocol.enable_debug = True

# Ver mensagens trocadas
agente.send_agent_request("outro_agente", "chat", {"message": "teste"})
```

---

## 💰 Custos e Limites

### **❓ Quanto custa usar o Mangaba AI?**

**Custo do Mangaba AI**: **Gratuito** (MIT License)

**Custo da API Google (Dezembro 2024):**
- 🆓 **Limite gratuito**: 15 RPM (requests por minuto)
- 💰 **Pago**: US$ 0.000125 por 1K caracteres de input
- 💰 **Output**: US$ 0.000375 por 1K caracteres de output

**Estimativa de uso típico:**
```
📱 Uso pessoal: R$ 0-10/mês
🏢 Pequena empresa: R$ 50-200/mês  
🏭 Empresa média: R$ 500-2000/mês
```

### **❓ Como monitorar os custos?**

**1. No Google Cloud Console:**
- 💰 Billing → View detailed charges
- 📊 APIs & Services → Quotas

**2. No código:**
```python
# Contador simples de tokens
class CostTracker:
    def __init__(self):
        self.total_input_chars = 0
        self.total_output_chars = 0
    
    def track_request(self, input_text: str, output_text: str):
        self.total_input_chars += len(input_text)
        self.total_output_chars += len(output_text)
    
    def estimate_cost(self):
        input_cost = (self.total_input_chars / 1000) * 0.000125
        output_cost = (self.total_output_chars / 1000) * 0.000375
        return input_cost + output_cost

# Uso
tracker = CostTracker()

# Integrar com agente
class CostAwareMangabaAgent(MangabaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cost_tracker = CostTracker()
    
    def chat(self, message: str, **kwargs) -> str:
        response = super().chat(message, **kwargs)
        self.cost_tracker.track_request(message, response)
        return response
```

### **❓ Como reduzir custos?**

**Estratégias de economia:**

**1. Cache inteligente:**
```python
# Evita chamar API para respostas idênticas
agente = CachedMangabaAgent(
    cache_duration=3600  # 1 hora
)
```

**2. Contexto otimizado:**
```python
# Limitar contexto quando não necessário
agente.chat("pergunta simples", use_context=False)
```

**3. Rate limiting:**
```python
# Controlar frequência de chamadas
@rate_limit(calls_per_minute=10)
def usar_agente_economico():
    return agente.chat("pergunta")
```

**4. Batch processing:**
```python
# Processar múltiplas perguntas de uma vez
perguntas = ["pergunta1", "pergunta2", "pergunta3"]
prompt = "Responda todas as perguntas:\n" + "\n".join(perguntas)
resposta_batch = agente.chat(prompt)
```

---

## 🔐 Segurança e Privacidade

### **❓ Meus dados estão seguros?**

**Fluxo de dados:**
1. 📱 **Seu dispositivo** → Envia texto para API Google
2. 🌐 **Google AI** → Processa e retorna resposta
3. 💾 **Contexto MCP** → Armazenado localmente (opcional)

**Dados NÃO são:**
- ❌ Enviados para servidores do Mangaba AI
- ❌ Compartilhados com terceiros
- ❌ Usados para treinamento por padrão

### **❓ Como proteger informações sensíveis?**

**1. Sanitização de dados:**
```python
import re

def sanitizar_dados_sensiveis(texto):
    """Remove informações sensíveis do texto"""
    # CPF
    texto = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF_REMOVIDO]', texto)
    
    # Email
    texto = re.sub(r'\S+@\S+\.\S+', '[EMAIL_REMOVIDO]', texto)
    
    # Telefone
    texto = re.sub(r'\(\d{2}\)\s*\d{4,5}-?\d{4}', '[TELEFONE_REMOVIDO]', texto)
    
    return texto

# Uso
texto_original = "Meu CPF é 123.456.789-00"
texto_limpo = sanitizar_dados_sensiveis(texto_original)
resposta = agente.chat(texto_limpo)
```

**2. Contexto temporário:**
```python
# Usar sessão temporária para dados sensíveis
sessao_temp = agente.mcp.create_temporary_session()
agente.current_session_id = sessao_temp

# Usar agente normalmente
resposta = agente.chat("análise de dados sensíveis")

# Limpar sessão após uso
agente.mcp.delete_session(sessao_temp)
```

**3. Modo offline (futuro):**
```python
# Planejado para próximas versões
agente = MangabaAgent(
    mode="offline",  # Usar modelo local
    model_path="./models/gemini-local"
)
```

### **❓ Como configurar logs seguros?**

**Log sanitizado:**
```python
import logging
import re

class SecureLogFormatter(logging.Formatter):
    def format(self, record):
        # Sanitizar mensagem do log
        if hasattr(record, 'msg'):
            record.msg = self.sanitize_message(str(record.msg))
        return super().format(record)
    
    def sanitize_message(self, message):
        # Remover informações sensíveis
        message = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF]', message)
        message = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', message)
        return message

# Configurar logger seguro
logger = logging.getLogger('mangaba.secure')
handler = logging.StreamHandler()
handler.setFormatter(SecureLogFormatter())
logger.addHandler(handler)
```

### **❓ Como implementar controle de acesso?**

**Sistema de permissões básico:**
```python
from enum import Enum
from typing import Set

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class SecureAgent:
    def __init__(self, agent: MangabaAgent, user_permissions: Set[Permission]):
        self.agent = agent
        self.permissions = user_permissions
    
    def require_permission(self, required: Permission):
        if required not in self.permissions:
            raise PermissionError(f"Permissão {required.value} necessária")
    
    def chat(self, message: str) -> str:
        self.require_permission(Permission.READ)
        return self.agent.chat(message)
    
    def analyze_text(self, text: str, instruction: str) -> str:
        self.require_permission(Permission.WRITE)
        return self.agent.analyze_text(text, instruction)
    
    def clear_context(self):
        self.require_permission(Permission.ADMIN)
        self.agent.mcp.clear_session(self.agent.current_session_id)

# Uso
user_permissions = {Permission.READ, Permission.WRITE}
secure_agent = SecureAgent(agente, user_permissions)

# Funcionará
response = secure_agent.chat("pergunta")

# Falhará - sem permissão admin
# secure_agent.clear_context()  # PermissionError
```

---

## 🆘 Ainda Tem Dúvidas?

### **📞 Canais de Suporte**

| Canal | Melhor Para | Tempo de Resposta |
|-------|-------------|-------------------|
| 📚 [Wiki](WIKI.md) | Consulta geral | Imediato |
| 📖 [Documentação](README.md) | Referência técnica | Imediato |
| 💬 [GitHub Discussions](https://github.com/Mangaba-ai/mangaba_ai/discussions) | Perguntas da comunidade | 1-3 dias |
| 🐛 [GitHub Issues](https://github.com/Mangaba-ai/mangaba_ai/issues) | Bugs e problemas | 1-7 dias |

### **📚 Recursos Adicionais**

- 🎓 **Iniciante**: Comece pelo [Curso Básico](CURSO_BASICO.md)
- 🔧 **Configuração**: Consulte [Setup Detalhado](SETUP.md)
- ⭐ **Avançado**: Leia [Melhores Práticas](MELHORES_PRATICAS.md)
- 🤝 **Contribuir**: Veja [Como Contribuir](CONTRIBUICAO.md)
- 📝 **Termos**: Consulte o [Glossário](GLOSSARIO.md)

### **🎯 Dicas Finais**

1. 📖 **Sempre consulte a documentação primeiro**
2. 🧪 **Teste em ambiente de desenvolvimento**
3. 💰 **Monitore custos da API Google**
4. 🔐 **Proteja informações sensíveis**
5. 🤝 **Contribua com a comunidade**

---

> 💡 **Lembrete**: Esta FAQ é atualizada regularmente. Marque nos favoritos!

> 🆘 **Não encontrou sua dúvida?** Abra uma [discussion](https://github.com/Mangaba-ai/mangaba_ai/discussions) - sua pergunta pode ajudar outros usuários!

---

*Última atualização: Dezembro 2024 | Versão: 1.0*