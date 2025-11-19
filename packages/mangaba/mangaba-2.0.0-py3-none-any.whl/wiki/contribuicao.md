# 🤲 Diretrizes de Contribuição

Bem-vindo à comunidade Mangaba AI! Este guia explica como você pode contribuir para o projeto de forma efetiva e colaborativa.

## 🎯 Como Contribuir

### 📋 Tipos de Contribuição

Valorizamos todas as formas de contribuição:

- **🐛 Reportar Bugs**: Encontrou um problema? Nos ajude a corrigir!
- **💡 Sugerir Funcionalidades**: Tem uma ideia legal? Queremos ouvir!
- **📝 Melhorar Documentação**: Documentação clara ajuda todos
- **🔧 Contribuir com Código**: Implemente features e correções
- **🧪 Escrever Testes**: Testes garantem qualidade e confiabilidade
- **🎨 Melhorar UX/UI**: Interfaces melhores beneficiam todos
- **🌍 Traduzir**: Ajude a tornar o projeto mais acessível
- **📢 Divulgar**: Compartilhe o projeto com a comunidade

## 🚀 Primeiros Passos

### 1. Configure o Ambiente de Desenvolvimento

```bash
# 1. Fork o repositório no GitHub
# 2. Clone seu fork
git clone https://github.com/SEU_USUARIO/mangaba_ai.git
cd mangaba_ai

# 3. Configure o repositório upstream
git remote add upstream https://github.com/Mangaba-ai/mangaba_ai.git

# 4. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 5. Instale dependências de desenvolvimento
pip install -r requirements.txt
pip install -r requirements-test.txt

# 6. Configure pre-commit hooks
pre-commit install
```

### 2. Verifique se Tudo Está Funcionando

```bash
# Execute os testes
python -m pytest

# Execute linting
flake8 .
black --check .
isort --check-only .

# Execute validação do ambiente
python scripts/validate_env.py
```

## 📝 Processo de Contribuição

### Fluxo Git Recomendado

```bash
# 1. Mantenha seu fork atualizado
git fetch upstream
git checkout main
git merge upstream/main

# 2. Crie uma branch para sua contribuição
git checkout -b feature/minha-funcionalidade
# ou
git checkout -b fix/correcao-bug
# ou
git checkout -b docs/melhorar-documentacao

# 3. Faça suas alterações
# ... código, testes, documentação ...

# 4. Commit suas mudanças
git add .
git commit -m "feat: adiciona funcionalidade X"

# 5. Push para seu fork
git push origin feature/minha-funcionalidade

# 6. Abra um Pull Request no GitHub
```

### Convenção de Commits

Usamos a convenção [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Tipos de commit:
feat: nova funcionalidade
fix: correção de bug
docs: mudanças na documentação
style: formatação, ponto e vírgula, etc.
refactor: refatoração sem mudança de funcionalidade
test: adição ou correção de testes
chore: tarefas de manutenção

# Exemplos:
git commit -m "feat: adiciona protocolo WebSocket para A2A"
git commit -m "fix: corrige timeout em requisições MCP"
git commit -m "docs: atualiza README com exemplos de uso"
git commit -m "test: adiciona testes para cache inteligente"
```

## 🐛 Reportando Bugs

### Template para Report de Bug

Ao abrir uma issue de bug, inclua:

```markdown
## 🐛 Descrição do Bug
Descrição clara e concisa do problema.

## 🔄 Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Execute '...'
4. Veja o erro

## ✅ Comportamento Esperado
O que deveria acontecer.

## ❌ Comportamento Atual
O que está acontecendo.

## 🖥️ Ambiente
- OS: [Windows 10, macOS 12, Ubuntu 20.04]
- Python: [3.8, 3.9, 3.10, 3.11]
- Versão do Mangaba AI: [0.1.0]
- Provedor de IA: [Google Gemini, OpenAI, etc.]

## 📋 Logs/Códigos de Erro
```python
# Cole aqui códigos de erro ou logs relevantes
```

## 📎 Informações Adicionais
Qualquer contexto adicional sobre o problema.
```

### Exemplo de Bug Report

```python
# Código para reproduzir o bug
from mangaba_agent import MangabaAgent

agent = MangabaAgent(agent_name="TestAgent")

# Isso deveria funcionar mas está dando erro
try:
    resultado = agent.chat("teste")
    print(resultado)
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
```

## 💡 Sugerindo Funcionalidades

### Template para Feature Request

```markdown
## 🚀 Resumo da Funcionalidade
Descrição concisa da funcionalidade proposta.

## 🎯 Problema que Resolve
Que problema esta funcionalidade resolve? Por que é útil?

## 💭 Solução Proposta
Como você imagina que esta funcionalidade deveria funcionar?

## 🔧 Exemplo de Uso
```python
# Como seria usado na prática
agent = MangabaAgent()
resultado = agent.nova_funcionalidade(parametros)
```

## 🔄 Alternativas Consideradas
Que outras abordagens você considerou?

## 📊 Impacto
- Performance: [Positivo/Negativo/Neutro]
- Compatibilidade: [Breaking/Backward Compatible]
- Complexidade: [Baixa/Média/Alta]
```

## 🔧 Contribuindo com Código

### Padrões de Código

#### Python Style Guide

Seguimos o [PEP 8](https://pep8.org/) com algumas extensões:

```python
# ✅ Bom exemplo
class MeuAgente(MangabaAgent):
    """Agente especializado em análise de dados.
    
    Este agente implementa capacidades avançadas de análise
    usando técnicas de processamento de linguagem natural.
    """
    
    def __init__(self, nome: str, configuracao: Dict[str, Any] = None):
        """Inicializa o agente com configurações específicas.
        
        Args:
            nome: Nome identificador do agente
            configuracao: Dicionário com configurações opcionais
        """
        super().__init__(agent_name=nome)
        self.configuracao = configuracao or {}
        self._setup_capacidades()
    
    def _setup_capacidades(self) -> None:
        """Configura capacidades específicas do agente."""
        # Implementação privada
        pass
    
    def analisar_sentimento(self, texto: str) -> Dict[str, float]:
        """Analisa sentimento do texto fornecido.
        
        Args:
            texto: Texto para análise de sentimento
            
        Returns:
            Dicionário com scores de sentimento
            
        Raises:
            ValueError: Se texto estiver vazio ou inválido
        """
        if not texto or not texto.strip():
            raise ValueError("Texto não pode estar vazio")
        
        resultado = self.analyze_text(
            texto, 
            "Analisar sentimento e retornar scores numéricos"
        )
        
        return self._processar_resultado_sentimento(resultado)
```

#### Checklist de Qualidade

- [ ] **Docstrings**: Todas as classes e métodos públicos têm docstrings
- [ ] **Type Hints**: Tipos declarados para parâmetros e retornos
- [ ] **Error Handling**: Tratamento adequado de exceções
- [ ] **Logging**: Logs apropriados para debugging
- [ ] **Testes**: Cobertura de testes para nova funcionalidade
- [ ] **Validação**: Validação de entrada de dados
- [ ] **Performance**: Considerações de performance implementadas

### Estrutura de Testes

```python
# tests/test_minha_funcionalidade.py
import pytest
from unittest.mock import Mock, patch
from mangaba_agent import MangabaAgent

class TestMinhaFuncionalidade:
    """Testes para a nova funcionalidade."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.agent = MangabaAgent(agent_name="TestAgent")
    
    def test_funcionalidade_basica(self):
        """Testa funcionamento básico da funcionalidade."""
        # Arrange
        entrada = "dados de teste"
        
        # Act
        resultado = self.agent.minha_funcionalidade(entrada)
        
        # Assert
        assert resultado is not None
        assert "esperado" in resultado
    
    def test_funcionalidade_com_entrada_invalida(self):
        """Testa comportamento com entrada inválida."""
        with pytest.raises(ValueError, match="Entrada inválida"):
            self.agent.minha_funcionalidade("")
    
    @patch('mangaba_agent.MangabaAgent.chat')
    def test_funcionalidade_com_mock(self, mock_chat):
        """Testa funcionalidade com mock de dependências."""
        # Arrange
        mock_chat.return_value = "resposta mockada"
        
        # Act
        resultado = self.agent.minha_funcionalidade("teste")
        
        # Assert
        mock_chat.assert_called_once()
        assert resultado == "resposta esperada"
    
    def test_funcionalidade_performance(self, benchmark):
        """Teste de performance usando pytest-benchmark."""
        def executar():
            return self.agent.minha_funcionalidade("dados")
        
        resultado = benchmark(executar)
        assert resultado is not None
```

### Executando Testes

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/test_minha_funcionalidade.py

# Com cobertura
python -m pytest --cov=mangaba_agent --cov-report=html

# Testes de performance
python -m pytest --benchmark-only

# Testes com output verboso
python -m pytest -v -s
```

## 📚 Contribuindo com Documentação

### Tipos de Documentação

1. **📖 Wiki**: Guias compreensivos e tutoriais
2. **📝 README**: Visão geral e quick start
3. **🔧 API Docs**: Documentação de código
4. **📋 Examples**: Exemplos práticos
5. **❓ FAQ**: Perguntas frequentes

### Padrões de Documentação

```markdown
# ✅ Estrutura recomendada para páginas da wiki

# 🎯 Título da Página

Breve descrição do que a página cobre.

## 📋 Índice

1. [Seção 1](#seção-1)
2. [Seção 2](#seção-2)

## 🚀 Seção Principal

### Subseção

Explicação clara com exemplos práticos.

```python
# Exemplo de código bem comentado
agente = MangabaAgent(agent_name="Exemplo")
resultado = agente.funcionalidade()
```

### 💡 Dicas e Notas

> 💡 **Dica**: Use blocos de citação para destacar informações importantes.

> ⚠️ **Atenção**: Para avisos e cuidados especiais.

> 🎯 **Exemplo Prático**: Para casos de uso específicos.

## 🔗 Links Relacionados

- [Link para página relacionada](pagina.md)
- [Link externo](https://exemplo.com)
```

## 🧪 Padrões de Qualidade

### Code Review Checklist

#### Para Reviewers

- [ ] **Funcionalidade**: O código faz o que deveria fazer?
- [ ] **Testes**: Há testes adequados para as mudanças?
- [ ] **Documentação**: Documentação foi atualizada?
- [ ] **Performance**: Não há regressões de performance?
- [ ] **Segurança**: Não há vulnerabilidades introduzidas?
- [ ] **Compatibilidade**: Mantém compatibilidade backwards?
- [ ] **Style**: Segue padrões de código do projeto?

#### Para Contributors

- [ ] **Testes Passando**: Todos os testes estão passando
- [ ] **Linting Clean**: Sem warnings de linting
- [ ] **Documentação**: Docstrings e wiki atualizadas
- [ ] **Changelog**: Entrada adicionada se necessário
- [ ] **Breaking Changes**: Documentadas e justificadas
- [ ] **Examples**: Exemplos atualizados se necessário

### Critérios de Aceitação

Para um PR ser aceito, deve:

1. **✅ Passar em todos os testes automatizados**
2. **📝 Ter documentação adequada**
3. **🔍 Receber aprovação de pelo menos 1 maintainer**
4. **📋 Seguir convenções de commit**
5. **🎯 Resolver completamente a issue relacionada**
6. **⚡ Não degradar performance significativamente**
7. **🛡️ Não introduzir vulnerabilidades de segurança**

## 🏆 Reconhecimento

### Hall da Fama dos Contribuidores

Reconhecemos contribuições através de:

- **📜 Contributors.md**: Lista de todos os contribuidores
- **🎖️ All Contributors**: Bot que reconhece diferentes tipos de contribuição
- **📊 GitHub Insights**: Estatísticas públicas de contribuições
- **🏅 Special Thanks**: Reconhecimento especial em releases

### Tipos de Contribuições Reconhecidas

| Emoji | Tipo | Descrição |
|-------|------|-----------|
| 💻 | code | Código |
| 📖 | doc | Documentação |
| 🎨 | design | Design |
| 💡 | ideas | Ideias |
| 🐛 | bug | Relatórios de bug |
| 🤔 | questions | Respondeu perguntas |
| ⚠️ | test | Testes |
| 🌍 | translation | Tradução |
| 💬 | review | Code review |

## 📞 Comunicação e Suporte

### Canais de Comunicação

- **🐛 GitHub Issues**: Bugs e feature requests
- **💬 GitHub Discussions**: Discussões gerais
- **📧 Email**: contato@mangaba-ai.com (para questões privadas)
- **🐦 Twitter**: @MangabaAI (atualizações do projeto)

### Diretrizes de Comunicação

1. **🤝 Seja Respeitoso**: Trate todos com respeito e cortesia
2. **🎯 Seja Específico**: Forneça detalhes suficientes para entendimento
3. **📝 Use Templates**: Use os templates fornecidos para issues
4. **🔍 Pesquise Primeiro**: Verifique se a questão já foi discutida
5. **🌍 Idioma**: Português ou inglês são bem-vindos
6. **⏰ Seja Paciente**: Maintainers são voluntários, respostas podem demorar

## 🚫 Código de Conduta

### Nossos Valores

- **🤝 Inclusividade**: Todos são bem-vindos, independente de background
- **🎓 Aprendizado**: Erros são oportunidades de aprendizado
- **🔄 Colaboração**: Trabalhamos juntos para melhorar o projeto
- **🎯 Foco**: Mantemos discussões construtivas e relevantes
- **🌟 Excelência**: Buscamos qualidade em tudo que fazemos

### Comportamentos Inaceitáveis

- Linguagem ofensiva ou discriminatória
- Assédio de qualquer tipo
- Spam ou autopromoção excessiva
- Compartilhamento de informações privadas
- Conduta não profissional

### Enforcement

Violações do código de conduta podem resultar em:

1. **⚠️ Aviso formal**
2. **🚫 Suspensão temporária**
3. **❌ Banimento permanente**

## 🎉 Primeiras Contribuições

### Issues para Iniciantes

Procure por issues marcadas com:

- `good first issue`: Adequadas para iniciantes
- `help wanted`: Precisam de ajuda da comunidade
- `documentation`: Melhorias na documentação
- `easy`: Baixa complexidade

### Mentoria

Oferecemos mentoria para novos contribuidores:

- **👥 Buddy System**: Pareamento com contribuidor experiente
- **📚 Learning Resources**: Links para recursos de aprendizado
- **🎯 Guided Tours**: Tour guiado pelo codebase
- **💬 Office Hours**: Horários para tirar dúvidas

## 🎯 Roadmap e Prioridades

### Áreas Prioritárias para Contribuição

1. **🧪 Testes**: Aumentar cobertura de testes
2. **📝 Documentação**: Melhorar e expandir documentação
3. **⚡ Performance**: Otimizações de performance
4. **🌍 Internacionalização**: Suporte a mais idiomas
5. **🔌 Integrações**: Novos provedores de IA e APIs
6. **🛡️ Segurança**: Melhorias de segurança
7. **📊 Observabilidade**: Métricas e monitoramento

### Como Influenciar o Roadmap

- **💬 Participar das discussões** no GitHub Discussions
- **🗳️ Votar em features** que considera importantes
- **💡 Propor novas ideias** com justificativa clara
- **📊 Compartilhar dados** de uso que apoiem suas sugestões

---

## 🙏 Agradecimentos

Agradecemos a todos que contribuem para tornar o Mangaba AI melhor! Cada contribuição, por menor que seja, faz diferença na comunidade.

### Contributors

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- Será automaticamente atualizado pelo bot all-contributors -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

---

> 🚀 **Pronto para Contribuir?** Comece escolhendo uma [good first issue](https://github.com/Mangaba-ai/mangaba_ai/labels/good%20first%20issue) e siga este guia!

> ❓ **Dúvidas?** Abra uma [discussão](https://github.com/Mangaba-ai/mangaba_ai/discussions) - a comunidade está aqui para ajudar!