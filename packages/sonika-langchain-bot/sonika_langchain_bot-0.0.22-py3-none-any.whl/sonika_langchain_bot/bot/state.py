"""
Estado compartido para el workflow multi-nodo de LangGraph.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain.schema import BaseMessage


class ChatState(TypedDict):
    """Estado compartido entre todos los nodos del workflow."""
    
    # ===== ENTRADA =====
    user_input: str
    messages: List[BaseMessage]
    logs: List[str]
    dynamic_info: str
    
    # ===== INSTRUCCIONES =====
    function_purpose: str
    personality_tone: str
    limitations: str
    
    # ===== OUTPUTS DE CADA NODO =====
    planner_output: Optional[Dict[str, Any]]
    executor_output: Optional[Dict[str, Any]]
    validator_output: Optional[Dict[str, Any]]
    output_node_response: Optional[str]
    logger_output: Optional[List[str]]
    
    # ===== CONTROL DE FLUJO =====
    planning_attempts: int
    execution_attempts: int
    
    # ===== TRACKING =====
    tools_executed: List[Dict[str, Any]]
    token_usage: Dict[str, int]