# 🎯 Primeiros Passos

Este guia prático irá te levar do zero ao seu primeiro agente de IA funcionando em poucos minutos. Perfeito para iniciantes que querem ver o Mangaba AI em ação rapidamente!

## 🚀 Seu Primeiro Agente em 5 Minutos

### Passo 1: Instalação Básica

```bash
# Clone o repositório
git clone https://github.com/Mangaba-ai/mangaba_ai.git
cd mangaba_ai

# Instale dependências
pip install -r requirements.txt

# Configure sua API key
cp .env.template .env
# Edite .env com sua GOOGLE_API_KEY
```

### Passo 2: Primeiro Chat

Crie um arquivo `meu_primeiro_agente.py`:

```python
from mangaba_agent import MangabaAgent

# Criar seu primeiro agente
agente = MangabaAgent(agent_name="MeuAssistente")

# Primeira conversa
resposta = agente.chat("Olá! Você pode me ajudar?")
print(f"🤖 Agente: {resposta}")

# Segunda mensagem com contexto
resposta2 = agente.chat("Qual é meu nome?", use_context=True)
print(f"🤖 Agente: {resposta2}")
```

### Passo 3: Execute e Veja a Mágica!

```bash
python meu_primeiro_agente.py
```

**🎉 Parabéns!** Você acabou de criar seu primeiro agente de IA com contexto!

---

## 🎓 Tutorial Completo - Do Básico ao Avançado

### 1. Entendendo o Básico

#### O que é um Agente?

Um agente é como um assistente digital inteligente que pode:
- **💬 Conversar** naturalmente com você
- **📝 Analisar** textos e documentos
- **🌍 Traduzir** entre idiomas
- **🧠 Lembrar** de conversas anteriores
- **🤝 Comunicar** com outros agentes

#### Exemplo Básico Comentado

```python
from mangaba_agent import MangabaAgent

# 1. Criar o agente (como contratar um assistente)
agente = MangabaAgent(agent_name="AssistentePersonal")

# 2. Chat simples (sem memória)
resposta = agente.chat("Que horas são?", use_context=False)
print(f"💬 Sem contexto: {resposta}")

# 3. Chat com memória (recomendado)
resposta = agente.chat("Meu nome é João", use_context=True)
print(f"🧠 Com contexto: {resposta}")

# 4. O agente agora lembra do seu nome!
resposta = agente.chat("Qual é meu nome?", use_context=True)
print(f"🧠 Lembrou: {resposta}")
```

### 2. Explorando Funcionalidades

#### Chat Inteligente

```python
from mangaba_agent import MangabaAgent

agente = MangabaAgent(agent_name="ChatBot")

# Simulando uma conversa real
conversas = [
    "Oi! Sou desenvolvedor Python iniciante",
    "Que linguagem devo aprender depois do Python?",
    "E sobre frameworks web?",
    "Pode me recomendar um projeto prático?"
]

print("🗣️ === CONVERSA INTERATIVA ===")
for i, mensagem in enumerate(conversas, 1):
    print(f"\n👤 Você ({i}): {mensagem}")
    
    resposta = agente.chat(mensagem, use_context=True)
    print(f"🤖 Agente: {resposta}")

# Ver resumo da conversa
print(f"\n📋 Resumo do contexto:")
resumo = agente.get_context_summary()
for tipo, contextos in resumo.items():
    print(f"  {tipo}: {len(contextos)} itens")
```

#### Análise de Texto

```python
# Analisando diferentes tipos de texto
textos_para_analise = {
    "sentimento": "Este produto é fantástico! Recomendo muito.",
    "topicos": """
    Inteligência Artificial está revolucionando diversos setores.
    Machine Learning permite automação inteligente.
    Deep Learning resolve problemas complexos de visão computacional.
    """,
    "resumo": """
    A economia brasileira mostrou sinais de recuperação no último trimestre.
    O PIB cresceu 2,1% em relação ao período anterior, superando expectativas.
    O setor de serviços foi o principal motor do crescimento.
    A inflação permaneceu controlada dentro da meta.
    """
}

agente = MangabaAgent(agent_name="Analisador")

print("📊 === ANÁLISES DE TEXTO ===")
for tipo, texto in textos_para_analise.items():
    print(f"\n🔍 Analisando {tipo}:")
    print(f"📝 Texto: {texto[:100]}...")
    
    if tipo == "sentimento":
        instrucao = "Analisar sentimento: positivo, negativo ou neutro"
    elif tipo == "topicos":
        instrucao = "Extrair principais tópicos e conceitos"
    elif tipo == "resumo":
        instrucao = "Criar resumo executivo em 2 frases"
    
    resultado = agente.analyze_text(texto, instrucao, use_context=True)
    print(f"🎯 Resultado: {resultado}")
```

#### Tradução Inteligente

```python
agente = MangabaAgent(agent_name="Tradutor")

# Textos em português para traduzir
textos_pt = [
    "Bom dia! Como você está?",
    "O projeto Mangaba AI é muito interessante.",
    "Inteligência artificial vai mudar o mundo."
]

idiomas = ["inglês", "espanhol", "francês"]

print("🌍 === TRADUÇÕES ===")
for texto in textos_pt:
    print(f"\n📝 Original (PT): {texto}")
    
    for idioma in idiomas:
        traducao = agente.translate(texto, idioma)
        print(f"🔄 {idioma}: {traducao}")
```

### 3. Personalizando Seu Agente

#### Criando um Agente Especializado

```python
class AgenteProfessor(MangabaAgent):
    """Agente especializado em educação e ensino"""
    
    def __init__(self):
        super().__init__(agent_name="Professor")
        
        # Adicionar contexto de especialização
        self.mcp_protocol.add_context(
            content="""Sou um professor experiente e paciente. 
            Sempre explico conceitos de forma clara e didática, 
            usando exemplos práticos e analogias simples.""",
            context_type="personality",
            priority=10  # Alta prioridade
        )
    
    def explicar_conceito(self, conceito, nivel="iniciante"):
        """Explica conceitos de forma didática"""
        niveis = {
            "iniciante": "de forma muito simples, com analogias do dia a dia",
            "intermediario": "com exemplos práticos e alguns detalhes técnicos",
            "avancado": "com profundidade técnica e teoria completa"
        }
        
        instrucao = f"""
        Explique o conceito '{conceito}' {niveis[nivel]}.
        Use uma linguagem adequada para o nível {nivel}.
        Inclua um exemplo prático no final.
        """
        
        return self.analyze_text(conceito, instrucao, use_context=True)
    
    def criar_exercicio(self, topico):
        """Cria exercícios práticos"""
        instrucao = f"""
        Crie um exercício prático sobre '{topico}' com:
        1. Enunciado claro
        2. Passos para resolução
        3. Resposta esperada
        4. Dica para quem errar
        """
        
        return self.chat(instrucao, use_context=True)

# Usando o agente especializado
professor = AgenteProfessor()

print("👨‍🏫 === AGENTE PROFESSOR ===")

# Explicar conceitos em diferentes níveis
conceitos = ["Machine Learning", "API", "Banco de Dados"]

for conceito in conceitos:
    print(f"\n📚 Explicando: {conceito}")
    
    explicacao = professor.explicar_conceito(conceito, nivel="iniciante")
    print(f"🎯 Explicação: {explicacao}")
    
    # Criar exercício relacionado
    exercicio = professor.criar_exercicio(conceito)
    print(f"📝 Exercício: {exercicio}")
```

### 4. Trabalhando com Contexto Avançado

#### Sessões e Contexto Persistente

```python
class GerenciadorSessoes:
    """Gerencia diferentes sessões de usuários"""
    
    def __init__(self):
        self.sessoes = {}
    
    def obter_agente(self, user_id):
        """Obtém ou cria agente para usuário específico"""
        if user_id not in self.sessoes:
            agente = MangabaAgent(agent_name=f"Agent-{user_id}")
            
            # Contexto inicial personalizado
            agente.mcp_protocol.add_context(
                content=f"Usuário ID: {user_id}. Primeira sessão iniciada.",
                context_type="user_session",
                priority=5
            )
            
            self.sessoes[user_id] = agente
        
        return self.sessoes[user_id]
    
    def chat_multiusuario(self, user_id, mensagem):
        """Chat que mantém contexto separado por usuário"""
        agente = self.obter_agente(user_id)
        return agente.chat(mensagem, use_context=True)

# Simulando múltiplos usuários
gerenciador = GerenciadorSessoes()

usuarios = {
    "joao": [
        "Oi, sou João e gosto de Python",
        "Que framework web você recomenda?",
        "E para machine learning?"
    ],
    "maria": [
        "Olá, sou Maria e trabalho com dados",
        "Preciso analisar grandes datasets",
        "Que ferramentas posso usar?"
    ]
}

print("👥 === MÚLTIPLOS USUÁRIOS ===")
for user_id, mensagens in usuarios.items():
    print(f"\n🙋‍♂️ === USUÁRIO: {user_id.upper()} ===")
    
    for mensagem in mensagens:
        print(f"💬 {user_id}: {mensagem}")
        
        resposta = gerenciador.chat_multiusuario(user_id, mensagem)
        print(f"🤖 Agente: {resposta}")
```

### 5. Casos de Uso Práticos

#### Assistente de Produtividade

```python
class AssistenteProdutividade(MangabaAgent):
    """Assistente para organização e produtividade"""
    
    def __init__(self):
        super().__init__(agent_name="Produtividade")
        
        # Configurar personalidade focada em organização
        self.mcp_protocol.add_context(
            content="""Sou especializado em produtividade e organização.
            Ajudo a criar listas, organizar tarefas, definir prioridades
            e sugerir métodos de gestão de tempo.""",
            context_type="expertise",
            priority=10
        )
    
    def organizar_tarefas(self, lista_tarefas):
        """Organiza lista de tarefas por prioridade"""
        instrucao = """
        Organize essas tarefas por prioridade (Alta, Média, Baixa):
        1. Considere urgência e importância
        2. Agrupe tarefas similares
        3. Sugira ordem de execução
        4. Estime tempo necessário
        """
        
        return self.analyze_text(lista_tarefas, instrucao, use_context=True)
    
    def criar_cronograma(self, tarefas, tempo_disponivel):
        """Cria cronograma otimizado"""
        prompt = f"""
        Tenho estas tarefas: {tarefas}
        Tempo disponível: {tempo_disponivel}
        
        Crie um cronograma realista com:
        - Horários específicos
        - Pausas adequadas
        - Buffer para imprevistos
        """
        
        return self.chat(prompt, use_context=True)

# Exemplo de uso
assistente = AssistenteProdutividade()

# Lista de tarefas do usuário
tarefas = """
- Responder emails importantes
- Terminar relatório mensal
- Reunião com equipe
- Revisar proposta do cliente
- Estudar nova tecnologia
- Fazer exercícios
- Planejar próxima semana
"""

print("📅 === ASSISTENTE DE PRODUTIVIDADE ===")

# Organizar tarefas
print("\n📋 Organizando tarefas...")
organizacao = assistente.organizar_tarefas(tarefas)
print(f"🎯 Organização: {organizacao}")

# Criar cronograma
print("\n⏰ Criando cronograma...")
cronograma = assistente.criar_cronograma(tarefas, "8 horas de trabalho")
print(f"📅 Cronograma: {cronograma}")
```

#### Analisador de Documentos

```python
class AnalisadorDocumentos(MangabaAgent):
    """Especialista em análise de documentos"""
    
    def __init__(self):
        super().__init__(agent_name="AnalisadorDocs")
    
    def analisar_relatorio(self, documento):
        """Análise completa de relatório"""
        analises = {}
        
        # 1. Resumo executivo
        analises['resumo'] = self.analyze_text(
            documento,
            "Criar resumo executivo em 3 frases principais",
            use_context=True
        )
        
        # 2. Pontos principais
        analises['pontos_principais'] = self.analyze_text(
            documento,
            "Listar 5 pontos mais importantes do documento",
            use_context=True
        )
        
        # 3. Análise de sentimento
        analises['sentimento'] = self.analyze_text(
            documento,
            "Analisar tom geral: positivo, negativo ou neutro",
            use_context=True
        )
        
        # 4. Recomendações
        analises['recomendacoes'] = self.analyze_text(
            documento,
            "Sugerir 3 ações práticas baseadas no conteúdo",
            use_context=True
        )
        
        return analises

# Exemplo com relatório fictício
analisador = AnalisadorDocumentos()

relatorio_exemplo = """
RELATÓRIO DE VENDAS Q4 2023

As vendas do quarto trimestre superaram expectativas, com crescimento de 18% 
em relação ao mesmo período do ano anterior. O setor de tecnologia foi o 
principal motor desse crescimento, representando 45% do faturamento total.

Principais destaques:
- Produto A: Aumento de 25% nas vendas
- Produto B: Crescimento estável de 8%
- Novos clientes: 150 empresas adquiridas
- Retenção de clientes: 92%

Desafios identificados:
- Concorrência acirrada no segmento B2B
- Necessidade de melhorar suporte pós-venda
- Demanda por personalização aumentou 40%

Próximos passos recomendados:
- Investir em equipe de suporte
- Desenvolver soluções personalizadas
- Expandir para mercados regionais
"""

print("📄 === ANÁLISE DE DOCUMENTO ===")

analise_completa = analisador.analisar_relatorio(relatorio_exemplo)

for secao, conteudo in analise_completa.items():
    print(f"\n📊 {secao.upper()}:")
    print(f"   {conteudo}")
```

## 🎮 Exercícios Práticos

### Exercício 1: Chatbot de Atendimento

Crie um chatbot que simula atendimento ao cliente:

```python
# Seu desafio: implementar esta classe
class ChatbotAtendimento(MangabaAgent):
    def __init__(self):
        # TODO: Configurar agente especializado em atendimento
        pass
    
    def atender_cliente(self, problema):
        # TODO: Analisar problema e fornecer solução
        pass
    
    def escalar_problema(self, problema):
        # TODO: Decidir se problema deve ser escalado
        pass

# Teste com diferentes problemas
problemas = [
    "Não consigo fazer login na minha conta",
    "Quero cancelar minha assinatura",
    "O produto chegou defeituoso"
]

# Implementar e testar!
```

### Exercício 2: Assistente de Estudos

```python
# Desafio: criar assistente que ajuda nos estudos
class AssistenteEstudos(MangabaAgent):
    def criar_resumo(self, texto_complexo):
        # TODO: Criar resumo didático
        pass
    
    def gerar_questoes(self, topico):
        # TODO: Gerar questões de múltipla escolha
        pass
    
    def explicar_duvida(self, duvida):
        # TODO: Explicar conceito de forma simples
        pass

# Teste com conteúdo de estudo real
```

### Exercício 3: Analisador de Código

```python
# Desafio avançado: analisar código Python
class AnalisadorCodigo(MangabaAgent):
    def revisar_codigo(self, codigo):
        # TODO: Sugerir melhorias no código
        pass
    
    def detectar_problemas(self, codigo):
        # TODO: Identificar bugs potenciais
        pass
    
    def sugerir_testes(self, funcao):
        # TODO: Sugerir casos de teste
        pass
```

## 🔍 Troubleshooting Rápido

### Problemas Comuns e Soluções

#### ❌ "API Key não encontrada"
```python
# Solução: verificar arquivo .env
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Configure GOOGLE_API_KEY no arquivo .env")
else:
    print("✅ API Key configurada!")
```

#### ❌ "Timeout na resposta"
```python
# Solução: configurar timeout maior
agente = MangabaAgent(agent_name="Test")

try:
    resposta = agente.chat("Pergunta complexa", timeout=60)
    print(f"✅ Resposta: {resposta}")
except TimeoutError:
    print("⏰ Timeout - tente uma pergunta mais simples")
```

#### ❌ "Contexto não funciona"
```python
# Problema comum: esquecer use_context=True
# ❌ Errado
resposta1 = agente.chat("Meu nome é João")
resposta2 = agente.chat("Qual é meu nome?")  # Não vai lembrar

# ✅ Correto
resposta1 = agente.chat("Meu nome é João", use_context=True)
resposta2 = agente.chat("Qual é meu nome?", use_context=True)  # Vai lembrar!
```

## 🎯 Próximos Passos

### Agora que você domina o básico:

1. **🌐 Explore [Exemplos dos Protocolos](exemplos-protocolos.md)** - Aprenda A2A e MCP avançados
2. **✨ Leia [Melhores Práticas](melhores-praticas.md)** - Técnicas profissionais
3. **❓ Consulte o [FAQ](faq.md)** - Soluções para problemas comuns
4. **📝 Veja o [Glossário](glossario.md)** - Entenda todos os termos técnicos
5. **🤝 Considere [Contribuir](contribuicao.md)** - Ajude a melhorar o projeto

### Projetos Sugeridos para Praticar

- **📱 App de Chat**: Interface web para conversar com agentes
- **📊 Dashboard Analytics**: Análise automática de dados
- **🤖 Bot do Discord/Telegram**: Integração com plataformas sociais
- **📚 Sistema de Tutoria**: Assistente educacional personalizado
- **🏢 Automação Empresarial**: Workflows automatizados

---

> 🎉 **Parabéns!** Você concluiu o guia de primeiros passos. Agora você tem a base sólida para criar agentes de IA incríveis!

> 💡 **Dica Final**: A melhor forma de aprender é praticando. Experimente, teste, quebre e conserte - é assim que se torna expert em IA!