# 📦 Como Usar UV com Mangaba AI

**UV** é um gerenciador de pacotes Python **ultra-rápido** (10-100x mais rápido que pip). Este guia mostra como usá-lo no seu projeto.

## 🚀 Início Rápido

### 1️⃣ **Sincronizar Dependências** (Equivalente a `pip install`)
```bash
uv sync
```
✅ Instala todas as dependências do `pyproject.toml`
✅ Cria arquivo `uv.lock` (para builds determinísticos)
✅ **Muito mais rápido que pip!**

### 2️⃣ **Executar Scripts com UV**
```bash
# Executar arquivo Python
uv run python examples/basic_example.py

# Executar script específico
uv run python scripts/validate_env.py

# Com argumentos
uv run python scripts/quick_setup.py --verbose
```

### 3️⃣ **Instalar Novo Pacote**
```bash
# Adiciona ao pyproject.toml e instala
uv pip install pandas

# Instalar versão específica
uv pip install "numpy==1.24.0"

# Instalar grupo de desenvolvimento
uv pip install -e ".[dev]"
```

### 4️⃣ **Remover Pacote**
```bash
uv pip uninstall pandas
```

---

## 📋 Comandos Essenciais

### **Sincronização e Instalação**

| Comando | O que faz |
|---------|-----------|
| `uv sync` | Instala todas as dependências (padrão) |
| `uv sync --upgrade` | Atualiza para versões mais recentes |
| `uv sync --refresh` | Gera novo `uv.lock` |
| `uv pip install <pacote>` | Instala pacote específico |
| `uv pip uninstall <pacote>` | Remove pacote |

### **Executar Código**

| Comando | O que faz |
|---------|-----------|
| `uv run python script.py` | Executa script Python |
| `uv run python -c "print('hello')"` | Executa comando inline |
| `uv python --version` | Verifica versão Python |

### **Gerenciar Ambientes**

| Comando | O que faz |
|---------|-----------|
| `uv venv` | Cria novo ambiente virtual |
| `uv venv --python 3.12` | Cria com versão específica |
| `uv pip freeze` | Lista pacotes instalados |
| `uv pip show <pacote>` | Info sobre pacote |

---

## 🎯 Fluxo de Trabalho Typical

### **Primeira Vez (Setup)**

```bash
# 1. Clonar/abrir o projeto
cd mangaba_ai

# 2. Sincronizar dependências
uv sync

# 3. Pronto! Você pode usar
uv run python examples/basic_example.py
```

### **Desenvolvimento**

```bash
# Trabalhe normalmente com seu código
# ... edit files ...

# Quando precisar instalar dependência nova
uv pip install nova-lib

# Execute com UV
uv run python seu_script.py

# Para desenvolver, ative o ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Depois use Python normalmente
python seu_script.py
```

### **Compartilhar Projeto**

```bash
# Quando fizer mudanças, gere novo lock
uv sync --refresh

# Commit de pyproject.toml e uv.lock
git add pyproject.toml uv.lock
git commit -m "Update dependencies"

# Outros desenvolvedores só precisam fazer:
uv sync
```

---

## 🔧 Exemplos Práticos

### **Exemplo 1: Usar o Agente Mangaba**

```bash
# Opção A: Com uv run
uv run python examples/basic_example.py

# Opção B: Ativar ambiente e usar Python direto
.venv\Scripts\activate
python examples/basic_example.py
```

### **Exemplo 2: Instalar Novo Pacote para Desenvolvimento**

```bash
# Instalar pandas para análise
uv pip install pandas

# Usar em seu código
uv run python -c "import pandas as pd; print(pd.__version__)"
```

### **Exemplo 3: Rodar Testes**

```bash
# Com uv run
uv run python -m pytest tests/

# Ou direto (após .venv\Scripts\activate)
pytest tests/
```

### **Exemplo 4: Atualizar Todas as Dependências**

```bash
# Atualizar para versões mais recentes
uv sync --upgrade

# Verificar mudanças
git diff uv.lock
```

---

## 💡 Dicas e Truques

### **1. Usar Aliase para Comandos Comuns**

No PowerShell (Windows):
```powershell
# Adicione ao seu perfil PowerShell
function uv-sync { uv sync }
function uv-run { uv run python $args }
function uv-test { uv run python -m pytest $args }

# Use depois
uv-run examples/basic_example.py
uv-test tests/
```

### **2. Diferenciar Dependências (Grupos)**

No seu `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = ["pytest", "black", "mypy"]  # Apenas para desenvolvimento
cli = ["typer"]                     # Apenas para CLI
```

Instalar grupo específico:
```bash
uv pip install -e ".[dev]"      # Instala dependências dev
uv pip install -e ".[dev,cli]"  # Múltiplos grupos
```

### **3. Usar Versão Específica do Python**

```bash
# Com Python 3.12
uv run --python 3.12 python seu_script.py

# Ou criar venv com versão específica
uv venv --python 3.12
```

### **4. Verificar Lock File**

```bash
# Ver dependências bloqueadas
cat uv.lock  # Linux/Mac
type uv.lock # Windows

# Gerar novo lock
uv sync --refresh
```

---

## 🆚 UV vs PIP - Comparação

| Aspecto | UV | PIP |
|---------|----|----|
| **Velocidade** | ⚡ 10-100x mais rápido | 🐢 Lento |
| **Lock File** | ✅ Determinístico (`uv.lock`) | ❌ Não nativo |
| **Compatibilidade** | ✅ 100% compatível com pip | ✅ Padrão |
| **Curva Aprendizado** | ✅ Fácil (mesmo que pip) | ✅ Conhecido |
| **Erro Handling** | ✅ Melhor | ⚠️ Menos claro |
| **Recomendado** | ✅ SIM | ⚠️ Apenas legado |

---

## ❓ Perguntas Comuns

### **P: Como desativar o ambiente virtual?**
```bash
deactivate
```

### **P: Como saber qual versão do UV tenho?**
```bash
uv --version
```

### **P: Preciso usar UV ou posso usar pip?**
Pode usar pip! Mas UV é **muito mais rápido**. Use UV para novos projetos.

### **P: O `uv.lock` é necessário?**
Não é obrigatório, mas **altamente recomendado** para:
- ✅ Determinismo (todos com mesmas versões)
- ✅ CI/CD confiável
- ✅ Compartilhar ambiente com time

### **P: Como atualizar UV?**
```bash
uv self update
```

### **P: Posso usar UV em um projeto existente com pip?**
Sim! UV é 100% compatível. Basta fazer:
```bash
uv sync
# Seu projeto agora usa UV!
```

---

## 🚨 Troubleshooting

### **Problema: "uv não reconhecido"**
```bash
# Solução: Instalar UV
pip install uv

# Ou verificar se está no PATH
uv --version
```

### **Problema: Dependência não encontrada**
```bash
# Solução: Sincronizar novamente
uv sync --refresh
```

### **Problema: Conflito de dependências**
```bash
# Solução: Usar --upgrade para resolver
uv sync --upgrade
```

### **Problema: Quer usar pip mesmo assim?**
```bash
# Tudo bem! Use pip
.venv\Scripts\activate
pip install seu_pacote
```

---

## 📚 Mais Informações

- 📖 [Documentação oficial UV](https://docs.astral.sh/uv/)
- 🌐 [GitHub do UV](https://github.com/astral-sh/uv)
- 📝 [PEP 517 (Build System)](https://www.python.org/dev/peps/pep-0517/)
- 📝 [PEP 518 (pyproject.toml)](https://www.python.org/dev/peps/pep-0518/)

---

## ✅ Checklist para Começar

- [ ] UV instalado: `uv --version`
- [ ] Dependências sincronizadas: `uv sync`
- [ ] Teste básico: `uv run python examples/basic_example.py`
- [ ] Entenda o `uv.lock` (versionamento determinístico)
- [ ] Pronto para usar! 🎉

---

**Pronto para usar UV?** Comece com:
```bash
uv sync
uv run python examples/basic_example.py
```

🚀 Aproveite a velocidade!
