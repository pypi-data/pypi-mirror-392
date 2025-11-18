"""
Modelos Pydantic para el workflow multi-nodo.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class PlannerDecision(BaseModel):
    """Output estructurado del nodo Planificador."""
    
    decision: Literal["execute_actions", "request_data"] = Field(
        description="Decisión final"
    )
    reasoning: List[str] = Field(
        description="Pasos de razonamiento"
    )
    actions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Acciones a ejecutar"
    )
    field_needed: Optional[str] = Field(
        default=None,
        description="Campo que se necesita"
    )
    context_for_user: Optional[str] = Field(
        default=None,
        description="Contexto para el usuario"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Nivel de confianza"
    )
    
    def validate_consistency(self) -> tuple[bool, Optional[str]]:
        """Valida consistencia interna del plan."""
        if self.decision == "execute_actions":
            if not self.actions or len(self.actions) == 0:
                return False, "Decision is execute_actions but no actions provided"
        elif self.decision == "request_data":
            if not self.field_needed:
                return False, "Decision is request_data but no field_needed provided"
        return True, None


class ExecutionResult(BaseModel):
    """Output del nodo Ejecutor."""
    
    status: Literal["success", "failed"] = Field(
        description="Estado general"
    )
    tools_executed: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tools ejecutadas"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Errores encontrados"
    )


class ValidationResult(BaseModel):
    """Output del nodo Verificador."""
    
    approved: bool = Field(
        description="Si es aprobado"
    )
    violations: List[str] = Field(
        default_factory=list,
        description="Violaciones detectadas"
    )
    feedback_for_planner: Optional[str] = Field(
        default=None,
        description="Feedback para corrección"
    )


class TokenUsage(BaseModel):
    """Tracking de tokens del LLM."""
    
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    
    def add(self, other: 'TokenUsage') -> 'TokenUsage':
        """Suma dos instancias."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens
        )