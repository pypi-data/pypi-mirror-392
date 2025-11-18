"""Nodo de Salida - genera respuestas naturales."""

from typing import Dict, Any
# ✅ Import correcto
from sonika_langchain_bot.bot.nodes.base_node import BaseNode

class OutputNode(BaseNode):
    """Genera respuesta final al usuario."""
    
    def __init__(self, model, logger=None):
        super().__init__(logger)
        self.model = model
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        response_type, data = self._determine_response_type(
            state.get("planner_output", {}),
            state.get("executor_output", {}),
            state.get("validator_output", {})
        )
        
        try:
            response_text, tokens = self._generate_response(state, response_type, data)
            self._accumulate_tokens(state, tokens)
            return {**state, "output_node_response": response_text}
        except:
            return {**state, "output_node_response": "Disculpa, tuve un problema."}
    
    def _determine_response_type(self, planner, executor, validator):
        if planner.get("decision") == "request_data":
            return "request_data", {
                "field_needed": planner.get("field_needed"),
                "context_for_user": planner.get("context_for_user")
            }
        if validator and not validator.get("approved", True):
            return "validation_rejected", {}
        if executor and executor.get("status") == "failed":
            return "execution_failed", {}
        if executor and executor.get("status") == "success":
            return "execution_success", {"tools_executed": executor.get("tools_executed", [])}
        return "generic", {}
    
    def _generate_response(self, state, response_type, data):
        """Genera la respuesta según el tipo usando métodos especializados."""
        response_generators = {
            "request_data": self._generate_request_data_response,
            "execution_success": self._generate_success_response,
            "execution_failed": self._generate_failure_response,
            "validation_rejected": self._generate_rejection_response,
            "generic": self._generate_generic_response
        }
        
        generator = response_generators.get(response_type, self._generate_generic_response)
        prompt = generator(state, data)
        
        response = self.model.invoke([{"role": "system", "content": prompt}])
        tokens = self._extract_token_usage(response)
        return response.content.strip(), tokens
    
    def _generate_request_data_response(self, state: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Prompt para solicitar información faltante al usuario."""
        planner_output = state.get("planner_output", {})
        field_needed = data.get("field_needed", "información adicional")
        context = data.get("context_for_user", "ayudarte mejor")
        reasoning = planner_output.get("reasoning", [])
        
        return f"""{state.get('personality_tone', '')}

# CONTEXT
{state.get('dynamic_info', '')}

# USER REQUEST
{state.get('user_input', '')}

# PLANNER ANALYSIS
{chr(10).join(f"- {r}" for r in reasoning)}

# YOUR TASK
The planner determined we need to request: "{field_needed}"
Context for user: {context}

Generate a friendly response (1-2 sentences) asking the user for the "{field_needed}".
Be specific about WHY you need it and what you CAN already do.

Example: "Perfecto, puedo enviarte el email. Para guardar a Erley como contacto, ¿me compartes su teléfono?"
"""
    
    def _generate_success_response(self, state: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Prompt para confirmar ejecución exitosa."""
        tools_executed = data.get("tools_executed", [])
        tools_summary = ", ".join([t.get("tool_name", "tool") for t in tools_executed])
        tools_details = chr(10).join(
            f"- {t.get('tool_name')}: {t.get('output', 'completed')[:100]}" 
            for t in tools_executed
        )
        
        return f"""{state.get('personality_tone', '')}

# CONTEXT
{state.get('dynamic_info', '')}

# USER REQUEST
{state.get('user_input', '')}

# WHAT WAS EXECUTED
Successfully executed: {tools_summary}

Results:
{tools_details}

# YOUR TASK
Generate a friendly confirmation (1-2 sentences) mentioning ONLY the actions that were actually executed.
Do NOT mention actions that were not executed.
"""
    
    def _generate_failure_response(self, state: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Prompt para informar fallo en ejecución."""
        errors = state.get("executor_output", {}).get("errors", [])
        
        return f"""{state.get('personality_tone', '')}

# CONTEXT
{state.get('dynamic_info', '')}

# USER REQUEST
{state.get('user_input', '')}

# WHAT FAILED
Errors: {', '.join(errors[:3])}

# YOUR TASK
Generate a friendly apology (1-2 sentences) explaining there was a problem.
Do NOT give technical details. Offer to help in another way.
"""
    
    def _generate_rejection_response(self, state: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Prompt para explicar rechazo por validación."""
        violations = state.get("validator_output", {}).get("violations", [])
        
        return f"""{state.get('personality_tone', '')}

# CONTEXT
{state.get('dynamic_info', '')}

# USER REQUEST
{state.get('user_input', '')}

# LIMITATION
The request was rejected because: {', '.join(violations[:2])}

# YOUR TASK
Generate a polite explanation (1-2 sentences) of what you cannot do and why.
Offer an alternative if possible.
"""
    
    def _generate_generic_response(self, state: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Prompt genérico para casos no específicos."""
        return f"""{state.get('personality_tone', '')}

# CONTEXT
{state.get('dynamic_info', '')}

# USER REQUEST
{state.get('user_input', '')}

# YOUR TASK
Generate a friendly response (1-2 sentences).
"""