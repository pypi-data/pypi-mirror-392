"""
Nodo Logger - Genera logs de eventos de la ejecución.

Este nodo analiza todo lo que sucedió durante la ejecución
y genera logs en formato texto plano para almacenamiento.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
# ✅ Import correcto
from sonika_langchain_bot.bot.nodes.base_node import BaseNode

class LoggerNode(BaseNode):
    """
    Nodo que genera logs de eventos de la ejecución.
    
    Este nodo es el último en el workflow y se encarga de:
    1. Analizar qué sucedió durante toda la ejecución
    2. Generar logs en formato texto plano
    3. Emitir callback con los logs generados
    
    Los logs son en formato simple para fácil almacenamiento
    y lectura tanto por humanos como por el LLM en futuras iteraciones.
    """
    
    def __init__(
        self,
        on_logs_generated: Optional[Callable[[List[str]], None]] = None,
        logger=None
    ):
        """
        Inicializa el nodo logger.
        
        Args:
            on_logs_generated: Callback que recibe la lista de logs generados
            logger: Logger opcional
        """
        super().__init__(logger)
        self.on_logs_generated = on_logs_generated
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera logs de la ejecución actual.
        
        Args:
            state: Estado actual del workflow
            
        Returns:
            Estado actualizado con logger_output
        """
        # Generar timestamp base
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Recolectar eventos
        logs = []
        
        # 1. Log de planificación
        # 1. Log de planificación
        planner_output = state.get("planner_output", {})
        if planner_output:
            decision = planner_output.get("decision")
            confidence = planner_output.get("confidence", "unknown")
            
            if decision == "execute_actions":
                actions = planner_output.get("actions") or []  # ✅ Protección contra None
                if actions:
                    actions_str = ", ".join([a.get("action", "unknown") for a in actions])
                    logs.append(f"{timestamp} - Planificador decidió ejecutar: {actions_str} (confianza: {confidence})")
                else:
                    logs.append(f"{timestamp} - Planificador decidió ejecutar (sin acciones especificadas)")
        
        # 2. Logs de ejecución de tools
        # 2. Logs de ejecución de tools
        executor_output = state.get("executor_output", {})
        if executor_output:
            tools_executed = executor_output.get("tools_executed") or []  # ✅ Protección
            
            for tool_exec in tools_executed:
                tool_name = tool_exec.get("tool_name", "unknown")
                status = tool_exec.get("status", "unknown")
                tool_timestamp = tool_exec.get("timestamp", timestamp)
                
                # Extraer solo el tiempo HH:MM:SS del timestamp ISO
                if 'T' in tool_timestamp:
                    tool_time = tool_timestamp.split('T')[1][:8]
                else:
                    tool_time = timestamp
                
                if status == "success":
                    duration = tool_exec.get("duration_ms", 0)
                    logs.append(f"{tool_time} - ✓ {tool_name} ejecutada exitosamente ({duration}ms)")
                else:
                    error = tool_exec.get("error", "error desconocido")
                    logs.append(f"{tool_time} - ✗ {tool_name} falló: {error}")
        
        # 3. Log de validación
        validator_output = state.get("validator_output", {})
        if validator_output and planner_output.get("decision") == "execute_actions":
            approved = validator_output.get("approved", True)
            
            if approved:
                logs.append(f"{timestamp} - Verificador aprobó la ejecución")
            else:
                violations = validator_output.get("violations", [])
                violations_str = "; ".join(violations)
                logs.append(f"{timestamp} - Verificador rechazó: {violations_str}")
        
        # 4. Log de respuesta generada
        output_response = state.get("output_node_response")
        if output_response:
            # Truncar respuesta si es muy larga
            response_preview = output_response[:100] if len(output_response) > 100 else output_response
            logs.append(f"{timestamp} - Bot generó respuesta: {response_preview}...")
        
        # 5. Detectar actualizaciones de datos (inferir de tools ejecutadas)
        if executor_output:
            tools_executed = executor_output.get("tools_executed", [])
            for tool_exec in tools_executed:
                tool_name = tool_exec.get("tool_name", "")
                
                if "create_or_update_contact" in tool_name and tool_exec.get("status") == "success":
                    tool_input = tool_exec.get("input", {})
                    # Listar campos actualizados
                    updated_fields = [k for k in tool_input.keys() if tool_input[k]]
                    if updated_fields:
                        fields_str = ", ".join(updated_fields)
                        logs.append(f"{timestamp} - Datos de contacto actualizados: {fields_str}")
                
                elif "accept_policies" in tool_name and tool_exec.get("status") == "success":
                    logs.append(f"{timestamp} - Usuario aceptó políticas de privacidad")
        
        # Emitir callback
        if self.on_logs_generated and logs:
            try:
                self.on_logs_generated(logs)
            except Exception as e:
                self.logger.error(f"Error en callback on_logs_generated: {e}")
        
        # Actualizar estado
        return {
            **state,
            "logger_output": logs
        }