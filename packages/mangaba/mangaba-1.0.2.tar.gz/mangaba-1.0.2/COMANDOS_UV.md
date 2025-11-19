# 📚 Guia de Comandos UV - Mangaba AI

## 🚀 Comandos Essenciais

### **1. Sincronizar Dependências**
```powershell
.\uv sync
```
✅ Instala todas as dependências do `pyproject.toml`
✅ Cria arquivo `uv.lock` para builds determinísticos
✅ Atualiza o ambiente virtual

**Variações:**
```powershell
.\uv sync --upgrade          # Atualiza para versões mais recentes
.\uv sync --refresh          # Regenera o arquivo uv.lock
.\uv sync --all-groups       # Instala todas as dependências (incluindo dev/test)
```

---

### **2. Executar Scripts Python**
```powershell
.\uv run python exemplos/basic_example.py
```
✅ Executa arquivo Python diretamente
✅ Usa o ambiente virtual automaticamente
✅ Sem precisar ativar `.venv`

**Exemplos:**
```powershell
# Executar exemplo básico
.\uv run python examples/basic_example.py

# Executar com argumentos
.\uv run python examples/basic_example.py --demo

# Executar script de validação
.\uv run python check_setup.py

# Executar teste
.\uv run python -m pytest tests/
```

---

### **3. Gerenciar Pacotes**
```powershell
# Instalar novo pacote
.\uv pip install pandas

# Instalar versão específica
.\uv pip install "numpy==1.24.0"

# Remover pacote
.\uv pip uninstall pandas

# Listar pacotes instalados
.\uv pip freeze

# Informações sobre pacote
.\uv pip show google-generativeai
```

---

## 📦 Comandos de Gerenciamento

### **Versão do UV**
```powershell
.\uv --version
```

### **Atualizar UV**
```powershell
.\uv self update
```

### **Ver Ajuda**
```powershell
.\uv --help              # Ajuda geral
.\uv run --help          # Ajuda de 'run'
.\uv pip --help          # Ajuda de 'pip'
.\uv sync --help         # Ajuda de 'sync'
```

---

## 🎯 Comandos Comuns para Mangaba AI

| Comando | Descrição |
|---------|-----------|
| `.\uv sync` | Sincronizar todas as dependências |
| `.\uv run python examples/basic_example.py` | Rodar exemplo básico |
| `.\uv run python check_setup.py` | Verificar configuração |
| `.\uv run python -m pytest tests/` | Rodar testes |
| `.\uv pip install novo-pacote` | Instalar novo pacote |
| `.\uv pip freeze` | Listar pacotes |
| `.\uv --version` | Ver versão do UV |

---

## 🔧 Ambientes e Grupos de Dependências

### **Instalar Dependências de Desenvolvimento**
```powershell
# Instalar grupo 'dev'
.\uv pip install -e ".[dev]"

# Instalar múltiplos grupos
.\uv pip install -e ".[dev,test]"
```

### **Sincronizar Apenas Dependências Base**
```powershell
.\uv sync --no-dev
```

---

## 💡 Dicas e Atalhos

### **1. Ativar Ambiente Virtual (Alternativa ao `.\uv run`)**
```powershell
# Ativar manualmente
.\.venv\Scripts\Activate.ps1

# Depois usar Python direto
python examples/basic_example.py

# Desativar
deactivate
```

### **2. Criar Alias para Comandos Frequentes**
```powershell
# Abra seu perfil PowerShell
code $PROFILE

# Adicione estas funções:
function uv-sync { .\uv sync }
function uv-run { .\uv run python $args }
function uv-test { .\uv run python -m pytest $args }

# Salve, feche e abra um novo PowerShell
# Agora use:
uv-sync
uv-run examples/basic_example.py
uv-test tests/
```

### **3. Usar Python com Versão Específica**
```powershell
.\uv run --python 3.12 python seu_script.py
```

---

## 📋 Fluxo de Trabalho Typical

### **Primeira Configuração:**
```powershell
# 1. Sincronizar dependências
.\uv sync

# 2. Verificar configuração
.\uv run python check_setup.py

# 3. Rodar exemplo
.\uv run python examples/basic_example.py
```

### **Desenvolvimento Diário:**
```powershell
# 1. (Opcional) Ativar venv para usar Python direto
.\.venv\Scripts\Activate.ps1

# 2. Editar seu código
code mangaba_agent.py

# 3. Testar
.\uv run python seu_teste.py

# 4. Instalar nova dependência se preciso
.\uv pip install nova-lib

# 5. Rodar testes
.\uv run python -m pytest tests/

# 6. Desativar venv (se ativou)
deactivate
```

### **Compartilhar Projeto:**
```powershell
# 1. Fazer mudanças
# ... editar código ...

# 2. Sincronizar lock file
.\uv sync --refresh

# 3. Commit (Git)
git add pyproject.toml uv.lock
git commit -m "Update dependencies"

# 4. Push
git push

# Outros desenvolvedores executam:
.\uv sync
```

---

## 🆚 UV vs PIP - Comparação de Comandos

| Tarefa | PIP | UV |
|--------|-----|-----|
| Instalar deps | `pip install -r requirements.txt` | `.\uv sync` |
| Instalar pacote | `pip install pandas` | `.\uv pip install pandas` |
| Rodar script | `python script.py` | `.\uv run python script.py` |
| Listar pacotes | `pip freeze` | `.\uv pip freeze` |
| Remover pacote | `pip uninstall pandas` | `.\uv pip uninstall pandas` |
| **Velocidade** | 🐢 Lento | ⚡ 10-100x mais rápido |
| **Lock file** | ❌ Não | ✅ `uv.lock` |

---

## ❓ Troubleshooting

### **Problema: ".\uv não reconhecido"**
```powershell
# Solução 1: Use o caminho completo
.\.venv\Scripts\uv.exe sync

# Solução 2: Configure alias conforme dica acima

# Solução 3: Adicione ao PATH do Windows (avançado)
```

### **Problema: "ModuleNotFoundError: No module named..."**
```powershell
# Solução: Sincronizar novamente
.\uv sync --refresh

# Ou instalar a dependência
.\uv pip install nome-do-modulo
```

### **Problema: Quer voltar para pip?**
```powershell
# Tudo bem! UV é 100% compatível
# Você pode usar:
pip install -r requirements.txt

# Mas UV é mais rápido, então considere usar!
```

---

## 📚 Referência Rápida

```powershell
# Sincronização
.\uv sync                    # Sincronizar
.\uv sync --upgrade          # Atualizar pacotes
.\uv sync --refresh          # Regenerar lock

# Execução
.\uv run python arquivo.py   # Rodar script
.\uv run python -c "..."     # Rodar comando

# Pacotes
.\uv pip install pacote      # Instalar
.\uv pip uninstall pacote    # Desinstalar
.\uv pip freeze              # Listar
.\uv pip show pacote         # Info

# Utilitários
.\uv --version               # Versão
.\uv self update             # Atualizar UV
.\uv --help                  # Ajuda
```

---

## 🎓 Próximos Passos

1. **Leia o guia completo:** [COMO_USAR_UV.md](COMO_USAR_UV.md)
2. **Teste os exemplos:** `.\uv run python examples/basic_example.py`
3. **Leia a documentação:** [Documentação UV Oficial](https://docs.astral.sh/uv/)
4. **Explore o projeto:** Veja a estrutura em [ESTRUTURA.md](ESTRUTURA.md)

---

**Pronto para começar?** Execute:
```powershell
.\uv sync
.\uv run python examples/basic_example.py
```

🚀 Aproveite a velocidade do UV!
