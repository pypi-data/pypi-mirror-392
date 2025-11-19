"""
Agent implementation with role, goal, and backstory support
"""

import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import google.generativeai as genai
from datetime import datetime

from config import config
from utils.logger import get_logger
from protocols.a2a import A2AAgent, A2AMessage, MessageType
from protocols.mcp import MCPProtocol, MCPContext, ContextType, ContextPriority

if TYPE_CHECKING:
    from mangaba.tools.base import BaseTool


class Agent(A2AAgent):
    """
    Agente de IA com role, goal e backstory para especialização.
    
    Exemplo:
        agent = Agent(
            role="Senior Data Analyst",
            goal="Analyze market trends and provide insights",
            backstory="You are an expert in financial markets with 15 years of experience",
            tools=[WebSearchTool(), DataAnalysisTool()],
            verbose=True
        )
    """
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List['BaseTool']] = None,
        llm: Optional[str] = None,
        api_key: Optional[str] = None,
        verbose: bool = False,
        memory: bool = True,
        max_iterations: int = 10,
        allow_delegation: bool = True,
        agent_id: Optional[str] = None
    ):
        """
        Inicializa um agente especializado.
        
        Args:
            role: Papel do agente (ex: "Senior Data Analyst")
            goal: Objetivo do agente (ex: "Analyze market trends")
            backstory: História/contexto do agente (ex: "You are an expert...")
            tools: Lista de ferramentas disponíveis para o agente
            llm: Nome do modelo LLM a usar (padrão: config.model)
            api_key: Chave API (padrão: config.api_key)
            verbose: Se True, imprime logs detalhados
            memory: Se True, habilita protocolo MCP
            max_iterations: Número máximo de iterações para tarefas
            allow_delegation: Se True, permite delegar tarefas para outros agentes
            agent_id: ID único do agente (gerado automaticamente se None)
        """
        # Validações
        if not role or not role.strip():
            raise ValueError("Role cannot be empty")
        if not goal or not goal.strip():
            raise ValueError("Goal cannot be empty")
        if not backstory or not backstory.strip():
            raise ValueError("Backstory cannot be empty")
        
        # Configuração básica
        self.role = role.strip()
        self.goal = goal.strip()
        self.backstory = backstory.strip()
        self.tools = tools or []
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.allow_delegation = allow_delegation
        
        # ID do agente
        self.agent_id = agent_id or f"agent_{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Inicializa A2A
        super().__init__(self.agent_id)
        
        # Configuração do LLM
        self.api_key = api_key or config.api_key
        self.model_name = llm or config.model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Protocolo MCP (Memory)
        self.memory_enabled = memory
        if self.memory_enabled:
            self.mcp = MCPProtocol()
            self.current_session_id = self.mcp.create_session(f"session_{self.agent_id}")
        
        # Logger
        self.logger = get_logger(f"Agent[{self.role}]")
        
        if self.verbose:
            self.logger.info(f"✅ Agent initialized - Role: {self.role}")
            self.logger.info(f"   Goal: {self.goal}")
            self.logger.info(f"   Tools: {len(self.tools)} available")
        
        # Configura handlers A2A
        self._setup_handlers()
    
    def _build_system_prompt(self) -> str:
        """
        Constrói o prompt do sistema baseado em role, goal e backstory.
        """
        prompt = f"""You are: {self.role}

Your goal is: {self.goal}

Background: {self.backstory}
"""
        
        # Adiciona informações sobre ferramentas disponíveis
        if self.tools:
            tools_desc = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
            prompt += f"\n\nAvailable tools:\n{tools_desc}"
        
        # Adiciona informações sobre delegação
        if self.allow_delegation:
            prompt += "\n\nYou can delegate tasks to other specialized agents when needed."
        
        return prompt
    
    def execute_task(self, task_description: str, context: Optional[str] = None) -> str:
        """
        Executa uma tarefa usando o agente.
        
        Args:
            task_description: Descrição da tarefa
            context: Contexto adicional (opcional)
        
        Returns:
            Resultado da execução da tarefa
        """
        # Constrói o prompt completo
        system_prompt = self._build_system_prompt()
        
        full_prompt = f"{system_prompt}\n\n"
        
        if context:
            full_prompt += f"Context:\n{context}\n\n"
        
        full_prompt += f"Task:\n{task_description}\n\nPlease complete this task according to your role and goal."
        
        # Adiciona contexto MCP se habilitado
        if self.memory_enabled:
            # Salva tarefa no contexto
            task_context = MCPContext.create(
                context_type=ContextType.TASK,
                content={
                    "task": task_description,
                    "agent_role": self.role,
                    "timestamp": datetime.now().isoformat()
                },
                priority=ContextPriority.HIGH,
                tags=["task", "execution"]
            )
            self.mcp.add_context(task_context, self.current_session_id)
            
            # Busca contexto relevante
            relevant = self.mcp.get_relevant_contexts(task_description, max_results=3)
            if relevant:
                context_info = "\n".join([str(ctx.content) for ctx in relevant])
                full_prompt += f"\n\nRelevant context from memory:\n{context_info}"
        
        if self.verbose:
            self.logger.info(f"🎯 Executing task: {task_description[:100]}...")
        
        try:
            # Executa com ferramentas se disponíveis
            result = self._execute_with_tools(full_prompt, task_description)
            
            # Salva resultado no contexto
            if self.memory_enabled:
                result_context = MCPContext.create(
                    context_type=ContextType.TASK,
                    content={
                        "task": task_description,
                        "result": result,
                        "agent_role": self.role,
                        "timestamp": datetime.now().isoformat()
                    },
                    priority=ContextPriority.HIGH,
                    tags=["task_result", "execution"]
                )
                self.mcp.add_context(result_context, self.current_session_id)
            
            if self.verbose:
                self.logger.info(f"✅ Task completed: {result[:100]}...")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error executing task: {e}")
            raise
    
    def _execute_with_tools(self, prompt: str, task: str) -> str:
        """
        Executa a tarefa usando ferramentas se necessário.
        """
        # Por enquanto, execução básica sem ferramentas
        # TODO: Implementar lógica de seleção e uso de ferramentas
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _setup_handlers(self):
        """Configura handlers A2A específicos"""
        self.a2a_protocol.register_handler(MessageType.REQUEST, self._handle_agent_request)
        self.a2a_protocol.register_handler(MessageType.RESPONSE, self._handle_agent_response)
    
    def _handle_agent_request(self, message: A2AMessage):
        """Handler para requisições de outros agentes"""
        action = message.content.get("action")
        params = message.content.get("params", {})
        
        if self.verbose:
            self.logger.info(f"📨 Received request: {action} from {message.sender_id}")
        
        try:
            if action == "execute_task":
                result = self.execute_task(
                    params.get("task_description", ""),
                    params.get("context")
                )
            else:
                result = f"Unknown action: {action}"
            
            response = self.a2a_protocol.create_response(message, result, True)
            self.a2a_protocol.send_message(response)
            
        except Exception as e:
            response = self.a2a_protocol.create_response(message, str(e), False)
            self.a2a_protocol.send_message(response)
    
    def _handle_agent_response(self, message: A2AMessage):
        """Handler para respostas de outros agentes"""
        if self.verbose:
            self.logger.info(f"📬 Received response from {message.sender_id}")
        
        # Salva no contexto se memory habilitado
        if self.memory_enabled:
            response_context = MCPContext.create(
                context_type=ContextType.CONVERSATION,
                content={
                    "from_agent": message.sender_id,
                    "response": message.content,
                    "correlation_id": message.correlation_id
                },
                priority=ContextPriority.MEDIUM,
                tags=["agent_response", "collaboration"]
            )
            self.mcp.add_context(response_context, self.current_session_id)
    
    def __repr__(self) -> str:
        return f"Agent(role='{self.role}', goal='{self.goal[:50]}...', tools={len(self.tools)})"
