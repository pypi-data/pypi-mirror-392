# 📚 Guia de Migração: Pip → UV

## Resumo Executivo

UV é um gerenciador de pacotes Python **ultra-moderno** escrito em Rust que oferece:

- ⚡ **10-100x mais rápido** que pip
- 🔒 **Lock file seguro** (uv.lock) para versões determinísticas
- 🐍 **Gerenciamento nativo** de versões Python
- 📦 **Padrão moderno**: PEP 517/518 (pyproject.toml)
- 🎯 **100% compatível** com pip e requirements.txt

---

## Comparação: Pip vs UV

### 1. **Instalação de Dependências**

#### Com Pip (Antigo)
```bash
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar (Windows)
.\.venv\Scripts\Activate.ps1

# 3. Instalar
pip install -r requirements.txt

# ⏱️  Tempo: ~15-30 segundos
```

#### Com UV (Moderno)
```bash
# 1. Sync automático (tudo em 1 comando!)
uv sync

# ⏱️  Tempo: ~1-3 segundos (10-20x mais rápido!)
```

### 2. **Estrutura de Arquivos**

#### Antes (Pip)
```
projeto/
├── setup.py              # Build script antigo
├── requirements.txt      # Dependências sem lock
├── requirements-dev.txt  # Dev deps
└── .venv/              # Ambiente virtual
```

#### Depois (UV + Modern Python)
```
projeto/
├── pyproject.toml       # Configuração moderna (PEP 517/518)
├── uv.lock             # Lock file determinístico
├── requirements.txt    # OPCIONAL (compatibilidade)
├── setup.py           # OPCIONAL (compatibilidade)
└── .venv/             # Ambiente virtual
```

### 3. **Adicionar Dependência**

#### Pip
```bash
pip install novo-pacote
# ⚠️  Não atualiza requirements.txt automaticamente
# Precisa fazer manualmente:
pip freeze > requirements.txt
```

#### UV
```bash
uv add novo-pacote
# ✅ Atualiza automaticamente pyproject.toml + uv.lock
```

### 4. **Remover Dependência**

#### Pip
```bash
pip uninstall novo-pacote
pip freeze > requirements.txt
# ⚠️  Manual e propenso a erros
```

#### UV
```bash
uv remove novo-pacote
# ✅ Automático
```

### 5. **Lock File**

#### Pip
```
❌ Não há lock file padrão
❌ Versões podem variar entre máquinas
❌ pip freeze cria lista, mas não é confiável
```

#### UV
```
✅ uv.lock cria lock file determinístico
✅ Versões garantidas em todas as máquinas
✅ Compatível com git (versionável)
```

### 6. **Execução de Scripts**

#### Pip
```bash
# Precisa ativar manualmente
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

python script.py
```

#### UV
```bash
# Executa diretamente (sem ativar!)
uv run python script.py
```

### 7. **Gerenciar Versões Python**

#### Pip
```bash
# ❌ Não gerencia Python
# Precisa de pyenv ou manual
pyenv install 3.11
pyenv local 3.11
python -m venv .venv
```

#### UV
```bash
# ✅ Gerencia automaticamente
uv python install 3.11
uv sync --python 3.11
```

---

## Tabela Comparativa Detalhada

| Característica | Pip | UV |
|---|---|---|
| **Velocidade** | ~15-30s | ~1-3s | 10-20x |
| **Lock file** | ❌ | ✅ uv.lock |
| **Determinístico** | ❌ | ✅ |
| **Python nativo** | ❌ | ✅ |
| **Cache paralelo** | ❌ | ✅ |
| **Padrão moderno** | ❌ | ✅ PEP 517/518 |
| **Suporte pip** | ✅ | ✅ |
| **Workspace** | ❌ | ✅ (Monorepo) |
| **Performance cache** | Médio | Excelente |
| **Comunidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Instalação do UV

### Windows (PowerShell)

```powershell
# Opção 1: WinGet (Recomendado)
winget install astral-sh.uv

# Opção 2: Python (Fallback)
pip install uv

# Verificar
uv --version
```

### macOS

```bash
# Opção 1: Homebrew (Recomendado)
brew install uv

# Opção 2: Curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Opção 3: Python
pip install uv
```

### Linux

```bash
# Opção 1: Curl (Recomendado)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Opção 2: Package Manager (APT, YUM, etc)
# https://docs.astral.sh/uv/guides/installation/

# Opção 3: Python
pip install uv
```

---

## Migrando um Projeto Existente

### Passo 1: Entender Estrutura Atual

```bash
# Ver dependências atuais
cat requirements.txt
cat requirements-dev.txt  # Se existir
```

### Passo 2: Instalar UV

```bash
# Windows
winget install astral-sh.uv

# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Passo 3: Criar pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "meu-projeto"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.25.0",
    "python-dotenv>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]
```

### Passo 4: Migrar Dependências

```bash
# Opção A: Manual (mais controle)
# Copie dados de requirements.txt para pyproject.toml

# Opção B: Automático com UV
uv pip compile requirements.txt -o requirements-compiled.txt
# Depois copie para pyproject.toml

# Opção C: Do zero (recomendado)
uv sync  # UV irá ler requirements.txt e criar pyproject.toml
```

### Passo 5: Sincronizar

```bash
# Cria .venv e instala tudo
uv sync

# Instala apenas prod (sem dev)
uv sync --no-dev

# Com grupo específico
uv sync --group dev
```

### Passo 6: Atualizar Scripts

**Antes:**
```bash
source .venv/bin/activate
python script.py
```

**Depois:**
```bash
uv run python script.py
```

### Passo 7: Committar Mudanças

```bash
git add pyproject.toml uv.lock
git remove setup.py requirements.txt  # Opcionais agora
git commit -m "chore: migrate to uv package manager"
```

---

## Comandos UV Essenciais

### Instalação e Sync

```bash
uv sync                    # Instala tudo
uv sync --no-dev          # Sem dev dependencies
uv sync --refresh         # Ignora cache
uv sync --python 3.11     # Com Python específico
```

### Gerenciar Pacotes

```bash
uv add requests            # Adiciona dependência
uv add -d pytest           # Adiciona dev dependency
uv remove requests         # Remove dependência
uv pip install requests    # Compatibilidade pip
uv pip show requests       # Info do pacote
```

### Executar Código

```bash
uv run python script.py    # Executa script
uv run pytest             # Roda testes
uv run python -c "..."    # Executa comando
uv run --help             # Ajuda
```

### Ambientes Virtuais

```bash
uv venv                    # Cria .venv
uv venv --python 3.11     # Com Python específico
source .venv/bin/activate # Ativa (Linux/Mac)
.\.venv\Scripts\Activate.ps1 # Ativa (Windows)
```

### Python

```bash
uv python list            # Versões disponíveis
uv python install 3.11    # Instala versão
uv python find 3.11       # Encontra versão
```

### Limpeza

```bash
uv cache clean            # Limpa cache local
uv cache prune            # Remove entradas antigas
```

---

## FAQ - Migração Pip → UV

### P: Preciso desinstalar pip?
**R:** Não! UV é compatível com pip. Você pode usar ambos.

### P: Como faço rollback para pip?
**R:** UV cria um `pyproject.toml` padrão que pip consegue ler:
```bash
pip install .
pip install -e .
```

### P: Meu projeto usa setup.py, devo manter?
**R:** Não é obrigatório. `pyproject.toml` é o padrão moderno. Mas pip ainda lê `setup.py`, então é seguro depreciar gradualmente.

### P: Como faço versionamento de dependências com UV?
**R:** UV gera `uv.lock` automaticamente com versions pinadas. Versione-o no git como qualquer arquivo.

### P: Posso usar diferentes versões Python?
**R:** Sim! UV gerencia versões Python nativamente:
```bash
uv sync --python 3.10
uv sync --python 3.11
```

### P: Como integro com CI/CD?
**R:** GitHub Actions:
```yaml
- uses: astral-sh/setup-uv@v1
- run: uv sync
- run: uv run pytest
```

### P: Qual a vantagem do uv.lock?
**R:** Garante que em todas as máquinas (dev, CI, produção) as versões sejam exatamente as mesmas.

### P: UV suporta extras/optional dependencies?
**R:** Sim!
```toml
[project.optional-dependencies]
dev = ["pytest"]
docs = ["sphinx"]
```

```bash
uv sync --group dev
uv add "pacote[extra]"
```

---

## Próximas Leituras

- 📖 [Documentação Oficial UV](https://docs.astral.sh/uv/)
- 📖 [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/)
- 📖 [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- 📖 [Guia UV do Mangaba AI](UV_SETUP.md)

---

## Checklist de Migração

- [ ] Instalar UV
- [ ] Criar `pyproject.toml`
- [ ] Executar `uv sync`
- [ ] Testar instalação (`uv run python script.py`)
- [ ] Gerar `uv.lock`
- [ ] Atualizar CI/CD
- [ ] Committar `pyproject.toml` + `uv.lock`
- [ ] Atualizar documentação
- [ ] Comunicar à equipe
- [ ] Opcional: Remover `setup.py` e `requirements.txt`

---

**Bem-vindo ao futuro do Python! 🚀**
