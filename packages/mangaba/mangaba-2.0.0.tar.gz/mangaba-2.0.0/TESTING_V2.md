# 🧪 Testing Mangaba AI 2.0

Guia de testes para as novas funcionalidades.

## ✅ Checklist de Testes

### 1. Agent Tests

```python
# test_agent.py
from mangaba import Agent

def test_agent_creation():
    """Testa criação de agente"""
    agent = Agent(
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory"
    )
    
    assert agent.role == "Test Agent"
    assert agent.goal == "Test goal"
    assert agent.backstory == "Test backstory"
    print("✅ Agent creation test passed")

def test_agent_execution():
    """Testa execução de tarefa"""
    agent = Agent(
        role="Calculator",
        goal="Solve math problems",
        backstory="Math expert"
    )
    
    result = agent.execute_task("What is 2 + 2?")
    assert result is not None
    assert len(result) > 0
    print("✅ Agent execution test passed")

if __name__ == "__main__":
    test_agent_creation()
    test_agent_execution()
```

### 2. Task Tests

```python
# test_task.py
from mangaba import Agent, Task

def test_task_creation():
    """Testa criação de task"""
    agent = Agent(
        role="Worker",
        goal="Complete tasks",
        backstory="Diligent worker"
    )
    
    task = Task(
        description="Test task",
        expected_output="Test output",
        agent=agent
    )
    
    assert task.description == "Test task"
    assert task.agent == agent
    print("✅ Task creation test passed")

def test_task_execution():
    """Testa execução de task"""
    agent = Agent(
        role="Analyst",
        goal="Analyze data",
        backstory="Data expert"
    )
    
    task = Task(
        description="Analyze the number {number}",
        expected_output="Analysis result",
        agent=agent
    )
    
    output = task.execute(inputs={"number": "42"})
    assert output is not None
    assert output.success
    print("✅ Task execution test passed")

if __name__ == "__main__":
    test_task_creation()
    test_task_execution()
```

### 3. Crew Tests

```python
# test_crew.py
from mangaba import Agent, Task, Crew, Process

def test_sequential_crew():
    """Testa crew sequential"""
    agent1 = Agent(
        role="First Agent",
        goal="Start process",
        backstory="Starter"
    )
    
    agent2 = Agent(
        role="Second Agent",
        goal="Complete process",
        backstory="Finisher"
    )
    
    task1 = Task(
        description="Step 1",
        expected_output="Result 1",
        agent=agent1
    )
    
    task2 = Task(
        description="Step 2",
        expected_output="Result 2",
        agent=agent2,
        context=[task1]
    )
    
    crew = Crew(
        agents=[agent1, agent2],
        tasks=[task1, task2],
        process=Process.SEQUENTIAL
    )
    
    result = crew.kickoff()
    assert result is not None
    assert len(result.tasks_outputs) == 2
    print("✅ Sequential crew test passed")

def test_hierarchical_crew():
    """Testa crew hierarchical"""
    manager = Agent(
        role="Manager",
        goal="Manage team",
        backstory="Leader",
        allow_delegation=True
    )
    
    worker = Agent(
        role="Worker",
        goal="Execute tasks",
        backstory="Executor"
    )
    
    task = Task(
        description="Complete assignment",
        expected_output="Completed work",
        agent=worker
    )
    
    crew = Crew(
        agents=[manager, worker],
        tasks=[task],
        process=Process.HIERARCHICAL
    )
    
    result = crew.kickoff()
    assert result is not None
    print("✅ Hierarchical crew test passed")

if __name__ == "__main__":
    test_sequential_crew()
    test_hierarchical_crew()
```

### 4. Tools Tests

```python
# test_tools.py
from mangaba.tools.web_search import DuckDuckGoSearchTool
from mangaba.tools.file_tools import FileReaderTool, FileWriterTool

def test_file_tools():
    """Testa ferramentas de arquivo"""
    writer = FileWriterTool()
    reader = FileReaderTool()
    
    # Escreve
    result = writer.run("test_file.txt", "Test content")
    assert "Successfully" in result
    
    # Lê
    content = reader.run("test_file.txt")
    assert content == "Test content"
    
    # Limpa
    import os
    os.remove("test_file.txt")
    
    print("✅ File tools test passed")

def test_web_search():
    """Testa busca web (se configurado)"""
    try:
        tool = DuckDuckGoSearchTool()
        result = tool.run("Python programming")
        assert result is not None
        assert len(result) > 0
        print("✅ Web search test passed")
    except Exception as e:
        print(f"⚠️ Web search test skipped: {e}")

if __name__ == "__main__":
    test_file_tools()
    test_web_search()
```

## 🏃 Running Tests

### Teste Individual
```bash
python test_agent.py
python test_task.py
python test_crew.py
python test_tools.py
```

### Teste com Pytest
```bash
# Instalar pytest
pip install pytest

# Executar todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=mangaba --cov-report=html
```

### Teste Rápido
```bash
# Executar exemplo completo
python examples/crew_example.py
```

## 📊 Test Coverage

Áreas críticas que devem ser testadas:

- ✅ Agent initialization
- ✅ Agent task execution
- ✅ Task creation and validation
- ✅ Task dependencies (context)
- ✅ Crew sequential process
- ✅ Crew hierarchical process
- ✅ Tools functionality
- ✅ A2A communication
- ✅ MCP memory management
- ✅ Error handling

## 🔍 Manual Testing

### Test 1: Simple Agent
```bash
python -c "
from mangaba import Agent
agent = Agent(
    role='Assistant',
    goal='Help users',
    backstory='Friendly assistant'
)
print(agent.execute_task('Say hello'))
"
```

### Test 2: Simple Crew
```bash
python examples/crew_example.py
```

### Test 3: With Tools
```python
from mangaba import Agent
from mangaba.tools.file_tools import FileWriterTool

agent = Agent(
    role="Writer",
    goal="Save content",
    backstory="File manager",
    tools=[FileWriterTool()]
)

result = agent.execute_task("Create a file called test.txt")
print(result)
```

## ✅ Validation Checklist

Antes de considerar estável:

- [ ] Agents criam corretamente com role/goal/backstory
- [ ] Tasks executam e retornam outputs
- [ ] Crew sequential funciona com múltiplas tasks
- [ ] Crew hierarchical delega corretamente
- [ ] Tools se integram aos agents
- [ ] Template variables ({var}) são substituídas
- [ ] Context entre tasks funciona
- [ ] Output files são salvos
- [ ] Error handling funciona
- [ ] Logging verboso mostra informações úteis

## 📝 Reportar Issues

Se encontrar problemas:

1. Verifique a versão: `python -c "import mangaba; print(mangaba.__version__)"`
2. Execute testes: `python test_agent.py`
3. Abra issue em: https://github.com/Mangaba-ai/mangaba_ai/issues

Include:
- Código que reproduz o erro
- Output completo do erro
- Versão do Python e Mangaba
- Sistema operacional
