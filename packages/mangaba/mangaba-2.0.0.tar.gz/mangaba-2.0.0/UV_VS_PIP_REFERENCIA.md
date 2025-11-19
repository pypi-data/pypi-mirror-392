# ⚡ Referência Rápida: UV vs pip

Guia lado a lado para comandos equivalentes. Use como consulta rápida!

## 📦 Instalação Inicial

| Tarefa | UV | pip |
|--------|----|----|
| **Instalar gerenciador** | `pip install uv` | (já vem com Python) |
| **Criar ambiente** | `uv venv` | `python -m venv .venv` |
| **Ativar (Windows)** | `.\.venv\Scripts\Activate.ps1` | `.\.venv\Scripts\Activate.ps1` |
| **Ativar (Linux/Mac)** | `source .venv/bin/activate` | `source .venv/bin/activate` |
| **Instalar projeto** | `uv sync` | `pip install -r requirements.txt` |

### 💡 Uso direto via PyPI
Quer apenas consumir o agente Mangaba em outro projeto? Ambos os gerenciadores usam o mesmo comando:

```bash
pip install mangaba
uv pip install mangaba
python -c "from mangaba_ai import MangabaAgent; print(MangabaAgent)"
```

Isso garante que a correção do módulo `mangaba_ai` chegue imediatamente independentemente do gerenciador escolhido.

## 🔧 Gerenciamento de Pacotes

| Tarefa | UV | pip |
|--------|----|----|
| **Instalar pacote** | `uv add requests` | `pip install requests` |
| **Remover pacote** | `uv remove requests` | `pip uninstall requests` |
| **Listar instalados** | `uv pip list` | `pip list` |
| **Mostrar info** | `uv pip show requests` | `pip show requests` |
| **Buscar pacote** | `uv pip search numpy` | `pip search numpy` |
| **Atualizar pacote** | `uv sync --upgrade` | `pip install --upgrade requests` |
| **Atualizar tudo** | `uv sync --upgrade` | `pip install -r requirements.txt --upgrade` |

## 📋 Gerenciamento de Dependências

| Tarefa | UV | pip |
|--------|----|----|
| **Gerar requirements** | `uv pip freeze > requirements.txt` | `pip freeze > requirements.txt` |
| **Instalar dev deps** | `uv sync --extra dev` | `pip install -r requirements-test.txt` |
| **Lock file** | `uv lock` | (precisa pip-tools) |
| **Instalar de lock** | `uv sync` | `pip-sync requirements.txt` |

## 🔍 Informações

| Tarefa | UV | pip |
|--------|----|----|
| **Versão** | `uv --version` | `pip --version` |
| **Verificar outdated** | `uv pip list --outdated` | `pip list --outdated` |
| **Verificar deps** | `uv tree` | `pipdeptree` (precisa instalar) |
| **Cache info** | `uv cache dir` | `pip cache dir` |
| **Limpar cache** | `uv cache clean` | `pip cache purge` |

## 🧹 Limpeza

| Tarefa | UV | pip |
|--------|----|----|
| **Desinstalar tudo** | `uv pip uninstall -r requirements.txt` | `pip uninstall -r requirements.txt -y` |
| **Limpar cache** | `uv cache clean` | `pip cache purge` |
| **Remover .venv** | `rm -rf .venv` | `rm -rf .venv` |

## 🚀 Workflows Completos

### Iniciar Novo Projeto

**Com UV:**
```bash
# 1. Criar diretório
mkdir meu_projeto && cd meu_projeto

# 2. Criar ambiente
uv venv

# 3. Ativar
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# 4. Instalar Mangaba AI
uv add google-generativeai pydantic loguru python-dotenv

# 5. Criar pyproject.toml
uv init
```

**Com pip:**
```bash
# 1. Criar diretório
mkdir meu_projeto && cd meu_projeto

# 2. Criar ambiente
python -m venv .venv

# 3. Ativar
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# 4. Instalar Mangaba AI
pip install google-generativeai pydantic loguru python-dotenv

# 5. Salvar dependências
pip freeze > requirements.txt
```

### Clonar Projeto Existente

**Com UV:**
```bash
# 1. Clonar
git clone <repo-url>
cd mangaba_ai

# 2. Sincronizar (cria .venv + instala tudo)
uv sync

# 3. Ativar
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# Pronto! ✅
```

**Com pip:**
```bash
# 1. Clonar
git clone <repo-url>
cd mangaba_ai

# 2. Criar ambiente
python -m venv .venv

# 3. Ativar
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# 4. Instalar dependências
pip install -r requirements.txt

# Pronto! ✅
```

### Adicionar Nova Dependência

**Com UV:**
```bash
# Adicionar (atualiza pyproject.toml e uv.lock)
uv add requests

# Commit
git add pyproject.toml uv.lock
git commit -m "Add requests dependency"
```

**Com pip:**
```bash
# Instalar
pip install requests

# Atualizar requirements
pip freeze > requirements.txt

# Commit
git add requirements.txt
git commit -m "Add requests dependency"
```

### Atualizar Todas as Dependências

**Com UV:**
```bash
# Atualizar tudo
uv sync --upgrade

# Ver o que mudou
git diff uv.lock
```

**Com pip:**
```bash
# Atualizar tudo
pip install -r requirements.txt --upgrade

# Salvar novas versões
pip freeze > requirements.txt

# Ver o que mudou
git diff requirements.txt
```

## 🎯 Mangaba AI - Comandos Específicos

### Setup Completo

**Com UV:**
```bash
git clone <repo-url>
cd mangaba_ai
uv sync
cp .env.example .env
# Editar .env com sua API key
.\.venv\Scripts\python.exe examples/basic_example.py
```

**Com pip:**
```bash
git clone <repo-url>
cd mangaba_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Editar .env com sua API key
python examples/basic_example.py
```

### Desenvolvimento

**Com UV:**
```bash
# Instalar com deps de dev
uv sync --all-extras

# Rodar testes
uv run pytest

# Rodar linter
uv run flake8

# Formatar código
uv run black .
uv run isort .
```

**Com pip:**
```bash
# Instalar com deps de dev
pip install -r requirements.txt
pip install -r requirements-test.txt

# Rodar testes
pytest

# Rodar linter
flake8

# Formatar código
black .
isort .
```

## ⚡ Performance Comparativa

| Operação | UV (tempo) | pip (tempo) | Speedup |
|----------|-----------|-------------|---------|
| **Criar .venv** | 0.5s | 2s | **4x** |
| **Instalar Mangaba AI** | 2s | 15s | **7.5x** |
| **Sync completo** | 3s | 25s | **8.3x** |
| **Adicionar pacote** | 1s | 5s | **5x** |
| **Resolver deps complexas** | 5s | 120s | **24x** |

*Tempos aproximados em máquina moderna com SSD*

## 🎓 Quando Usar Cada Um

### Use UV se você quer:
- ⚡ **Velocidade máxima** (10-100x mais rápido)
- 🔒 **Builds determinísticos** (uv.lock)
- 🔄 **CI/CD otimizado** (economia de tempo/custo)
- 📦 **Múltiplos projetos** (cache global eficiente)

### Use pip se você precisa:
- 🏢 **Compatibilidade corporativa** (ferramentas estabelecidas)
- 📚 **Máxima estabilidade** (maduro desde 2008)
- 🎯 **Simplicidade absoluta** (menos conceitos)
- 👥 **Onboarding fácil** (todos conhecem)

## 💡 Dicas Pro

### UV
- Use `uv sync` ao invés de `uv pip install` (gerencia lock file)
- Configure `UV_CACHE_DIR` para compartilhar cache entre projetos
- Use `uv add --dev` para dependências de desenvolvimento
- `uv lock --upgrade-package requests` para atualizar pacote específico

### pip
- Use `pip install -e .` para desenvolvimento local
- Configure `PIP_REQUIRE_VIRTUALENV=true` para evitar instalar globalmente
- Use `pip-tools` para gerenciar dependências complexas
- `pip install --no-deps` para evitar instalar sub-dependências

## 🔗 Recursos

**UV:**
- 📖 Documentação: https://github.com/astral-sh/uv
- 🎓 Guia oficial: `docs/COMO_USAR_UV.md`
- 🚀 Quick reference: `docs/COMANDOS_UV.md`

**pip:**
- 📖 Documentação: https://pip.pypa.io/
- 🎓 PyPA Guide: https://packaging.python.org/
- 📦 PyPI: https://pypi.org/

---

**💡 Lembre-se:** Ambos são excelentes! Escolha o que funciona melhor para você e seu time. 🚀

**Última atualização:** 2025-01-21
