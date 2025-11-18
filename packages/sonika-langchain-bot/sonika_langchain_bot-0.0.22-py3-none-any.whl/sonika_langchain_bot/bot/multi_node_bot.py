"""
Bot Multi-Nodo con LangGraph - Arquitectura Modular.

Este módulo implementa un bot conversacional con arquitectura de nodos separados,
permitiendo razonamiento estructurado, ejecución controlada de herramientas,
y validación de limitaciones.
"""

from typing import List, Dict, Any, Optional, Callable, Generator
import logging
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_community.tools import BaseTool
from langgraph.graph import StateGraph, END

# Importar componentes
from sonika_langchain_bot.bot.state import ChatState
from sonika_langchain_bot.bot.nodes.planner_node import PlannerNode
from sonika_langchain_bot.bot.nodes.executor_node import ExecutorNode
from sonika_langchain_bot.bot.nodes.validator_node import ValidatorNode
from sonika_langchain_bot.bot.nodes.output_node import OutputNode
from sonika_langchain_bot.bot.nodes.logger_node import LoggerNode


class MultiNodeBot:
    """
    Bot conversacional con arquitectura multi-nodo.
    
    Este bot separa las responsabilidades en nodos especializados:
    - Planificador: Decide qué hacer
    - Ejecutor: Ejecuta herramientas
    - Verificador: Valida cumplimiento de reglas
    - Salida: Genera respuestas naturales
    - Logger: Registra eventos
    
    Features:
        - Razonamiento estructurado
        - Ejecución controlada de tools con reintentos
        - Validación de limitaciones
        - Callbacks para monitoreo en tiempo real
        - Streaming de respuestas
        - Tracking completo de tokens
        - Configuración flexible
    """
    
    def __init__(
        self,
        # Core
        language_model,
        embeddings,
        
        # Instrucciones (3 tipos)
        function_purpose: str,
        personality_tone: str,
        limitations: str,
        
        # Tools
        tools: Optional[List[BaseTool]] = None,
        mcp_servers: Optional[Dict[str, Any]] = None,
        
        # Configuración
        max_messages: int = 10,
        max_logs: int = 20,
        planner_max_retries: int = 2,
        executor_max_retries: int = 2,
        
        # Callbacks
        on_planner_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_tool_start: Optional[Callable[[str, str], None]] = None,
        on_tool_end: Optional[Callable[[str, str], None]] = None,
        on_tool_error: Optional[Callable[[str, str], None]] = None,
        on_logs_generated: Optional[Callable[[List[str]], None]] = None,
        
        # Logger
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa el bot multi-nodo.
        
        Args:
            language_model: Modelo de lenguaje (debe tener .model attribute)
            embeddings: Modelo de embeddings (para futura compatibilidad)
            function_purpose: Instrucciones de función y propósito
            personality_tone: Instrucciones de personalidad y tono
            limitations: Instrucciones de limitaciones
            tools: Lista de herramientas disponibles
            mcp_servers: Configuración de servidores MCP (futuro)
            max_messages: Máximo de mensajes históricos a mantener
            max_logs: Máximo de logs históricos a mantener
            planner_max_retries: Reintentos del planificador
            executor_max_retries: Reintentos del ejecutor
            on_planner_update: Callback con plan del planificador
            on_tool_start: Callback cuando empieza una tool
            on_tool_end: Callback cuando termina una tool
            on_tool_error: Callback cuando falla una tool
            on_logs_generated: Callback con logs generados
            logger: Logger opcional
        """
        # Configurar logger
        self.logger = logger or logging.getLogger(__name__)
        if logger is None:
            self.logger.addHandler(logging.NullHandler())
        
        # Guardar configuración
        self.language_model = language_model
        self.embeddings = embeddings
        self.function_purpose = function_purpose
        self.personality_tone = personality_tone
        self.limitations = limitations
        self.tools = tools or []
        self.max_messages = max_messages
        self.max_logs = max_logs
        self.planner_max_retries = planner_max_retries
        self.executor_max_retries = executor_max_retries
        
        # Guardar callbacks
        self.on_planner_update = on_planner_update
        self.on_tool_start = on_tool_start
        self.on_tool_end = on_tool_end
        self.on_tool_error = on_tool_error
        self.on_logs_generated = on_logs_generated
        
        # Preparar modelo
        self.model = language_model.model
        
        # Construir workflow
        self.graph = self._build_workflow()
        
        self.logger.info("MultiNodeBot inicializado correctamente")
    
    def _build_workflow(self) -> StateGraph:
        """
        Construye el workflow de LangGraph con todos los nodos.
        
        Returns:
            StateGraph compilado
        """
        # Crear nodos
        planner_node = PlannerNode(
            model=self.model,
            tools=self.tools,
            max_retries=self.planner_max_retries,
            on_planner_update=self.on_planner_update,
            logger=self.logger
        )
        
        executor_node = ExecutorNode(
            tools=self.tools,
            max_retries=self.executor_max_retries,
            on_tool_start=self.on_tool_start,
            on_tool_end=self.on_tool_end,
            on_tool_error=self.on_tool_error,
            logger=self.logger
        )
        
        validator_node = ValidatorNode(
            model=self.model,
            logger=self.logger
        )
        
        output_node = OutputNode(
            model=self.model,
            logger=self.logger
        )
        
        logger_node = LoggerNode(
            on_logs_generated=self.on_logs_generated,
            logger=self.logger
        )
        
        # Crear grafo
        workflow = StateGraph(ChatState)
        
        # Agregar nodos
        workflow.add_node("planner", planner_node)
        workflow.add_node("executor", executor_node)
        workflow.add_node("validator", validator_node)
        workflow.add_node("output", output_node)
        workflow.add_node("logger", logger_node)
        
        # Entry point
        workflow.set_entry_point("planner")
        
        # Edges condicionales después del planificador
        def route_after_planner(state: ChatState) -> str:
            """Decide si ejecutar tools o ir directo a output."""
            decision = state["planner_output"]["decision"]
            if decision == "execute_actions":
                return "executor"
            else:  # request_data
                return "output"
        
        workflow.add_conditional_edges(
            "planner",
            route_after_planner,
            {
                "executor": "executor",
                "output": "output"
            }
        )
        
        # Edges condicionales después del ejecutor
        # Edges condicionales después del ejecutor
        def route_after_executor(state: ChatState) -> str:
            """Decide si validar o ir a output si falló."""
            executor_output = state.get("executor_output")
            
            # Si no hay executor_output, algo falló - ir a output
            if not executor_output:
                return "output"
            
            # Si falló explícitamente, ir a output
            if executor_output.get("status") == "failed":
                return "output"
            
            # Si todo bien, validar
            return "validator"
        
        workflow.add_conditional_edges(
            "executor",
            route_after_executor,
            {
                "validator": "validator",
                "output": "output"
            }
        )
        
        # Edges condicionales después del validador
        def route_after_validator(state: ChatState) -> str:
            """Decide si aprobar o replanificar."""
            validator_output = state.get("validator_output")
            
            # Si no hay validator_output, ir a output (safety)
            if not validator_output:
                return "output"
            
            # Si aprobado, generar respuesta
            if validator_output.get("approved", False):
                return "output"
            
            # Rechazado - verificar si aún hay reintentos
            if state.get("planning_attempts", 0) < self.planner_max_retries:
                return "planner"
            
            # Max reintentos, terminar
            return "output"
                
        workflow.add_conditional_edges(
            "validator",
            route_after_validator,
            {
                "planner": "planner",
                "output": "output"
            }
        )
        
        # Output siempre va a logger
        workflow.add_edge("output", "logger")
        
        # Logger es el final
        workflow.add_edge("logger", END)
        
        # Compilar
        return workflow.compile()
    
    def get_response(
        self,
        user_input: str,
        messages: List[BaseMessage],
        logs: List[str],
        dynamic_info: str
    ) -> Dict[str, Any]:
        """
        Genera una respuesta completa al mensaje del usuario.
        
        Args:
            user_input: Mensaje actual del usuario
            messages: Historial de mensajes de la conversación
            logs: Logs de eventos previos
            dynamic_info: Información contextual en formato markdown
            
        Returns:
            Dict con:
                - content: Respuesta generada
                - logs: Nuevos logs generados
                - tools_executed: Tools ejecutadas en esta iteración
                - token_usage: Tokens consumidos
        """
        # Limitar tamaño de mensajes y logs
        limited_messages = self._limit_messages(messages)
        limited_logs = self._limit_logs(logs)
        
        # Construir estado inicial
        initial_state: ChatState = {
            "user_input": user_input,
            "messages": limited_messages,
            "logs": limited_logs,
            "dynamic_info": dynamic_info,
            "function_purpose": self.function_purpose,
            "personality_tone": self.personality_tone,
            "limitations": self.limitations,
            "planner_output": None,
            "executor_output": None,
            "validator_output": None,
            "output_node_response": None,
            "logger_output": None,
            "planning_attempts": 0,
            "execution_attempts": 0,
            "tools_executed": [],
            "token_usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        # Ejecutar workflow
        result = self.graph.invoke(initial_state)
        
        # Extraer respuesta
        content = result.get("output_node_response", "")
        new_logs = result.get("logger_output", [])
        tools_executed = result.get("tools_executed", [])
        token_usage = result.get("token_usage", {})
        
        return {
            "content": content,
            "logs": new_logs,
            "tools_executed": tools_executed,
            "token_usage": token_usage
        }
    
    def get_response_stream(
        self,
        user_input: str,
        messages: List[BaseMessage],
        logs: List[str],
        dynamic_info: str
    ) -> Generator[str, None, None]:
        """
        Genera una respuesta en modo streaming.
        
        Args:
            user_input: Mensaje actual del usuario
            messages: Historial de mensajes
            logs: Logs de eventos previos
            dynamic_info: Información contextual
            
        Yields:
            Chunks de la respuesta a medida que se generan
        """
        # Limitar tamaño
        limited_messages = self._limit_messages(messages)
        limited_logs = self._limit_logs(logs)
        
        # Construir estado inicial
        initial_state: ChatState = {
            "user_input": user_input,
            "messages": limited_messages,
            "logs": limited_logs,
            "dynamic_info": dynamic_info,
            "function_purpose": self.function_purpose,
            "personality_tone": self.personality_tone,
            "limitations": self.limitations,
            "planner_output": None,
            "executor_output": None,
            "validator_output": None,
            "output_node_response": None,
            "logger_output": None,
            "planning_attempts": 0,
            "execution_attempts": 0,
            "tools_executed": [],
            "token_usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        # Ejecutar workflow con streaming
        accumulated_response = ""
        
        for chunk in self.graph.stream(initial_state):
            # Buscar respuesta en el nodo de output
            if "output" in chunk:
                response = chunk["output"].get("output_node_response")
                if response and response != accumulated_response:
                    # Yield solo la parte nueva
                    new_part = response[len(accumulated_response):]
                    accumulated_response = response
                    yield new_part
    
    def _limit_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Limita el número de mensajes históricos."""
        if len(messages) <= self.max_messages:
            return messages
        return messages[-self.max_messages:]
    
    def _limit_logs(self, logs: List[str]) -> List[str]:
        """Limita el número de logs históricos."""
        if len(logs) <= self.max_logs:
            return logs
        return logs[-self.max_logs:]
    
