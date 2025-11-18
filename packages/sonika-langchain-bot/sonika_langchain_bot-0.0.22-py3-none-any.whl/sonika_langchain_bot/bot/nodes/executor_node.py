"""Nodo Ejecutor - ejecuta herramientas."""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import time
# ✅ Import correcto
from sonika_langchain_bot.bot.nodes.base_node import BaseNode


class ExecutorNode(BaseNode):
    """Ejecuta herramientas con reintentos."""
    
    def __init__(self, tools: List[Any], max_retries: int = 2,
                 on_tool_start=None, on_tool_end=None, on_tool_error=None, logger=None):
        super().__init__(logger)
        self.tools = tools
        self.max_retries = max_retries
        self.on_tool_start = on_tool_start
        self.on_tool_end = on_tool_end
        self.on_tool_error = on_tool_error
        self.tools_dict = {t.name: t for t in tools}
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        planner_output = state.get("planner_output", {})
        actions = planner_output.get("actions", [])
        
        if not actions:
            return state
        
        tools_executed = []
        errors = []
        overall_status = "success"
        
        for action in actions:
            action_name = action.get("action")
            action_args = action.get("args", {})
            tool = self.tools_dict.get(action_name)
            
            if not tool:
                errors.append(f"Tool '{action_name}' not found")
                overall_status = "failed"
                continue
            
            result = self._execute_with_retry(tool, action_args)
            tools_executed.append(result)
            
            if result["status"] == "failed":
                overall_status = "failed"
                errors.append(f"{action_name}: {result.get('error', 'Unknown')}")
        
        executor_output = {
            "status": overall_status,
            "tools_executed": tools_executed,
            "errors": errors
        }
        
        return {
            **state,
            "executor_output": executor_output,
            "tools_executed": state.get("tools_executed", []) + tools_executed
        }
    
    def _execute_with_retry(self, tool, args):
        tool_name = tool.name
        start_time = time.time()
        
        if self.on_tool_start:
            try: self.on_tool_start(tool_name, str(args))
            except: pass
        
        for attempt in range(self.max_retries + 1):
            try:
                if hasattr(tool, 'invoke'):
                    output = tool.invoke(args)
                elif hasattr(tool, '_run'):
                    output = tool._run(**args)
                else:
                    raise AttributeError("No invoke/run method")
                
                output_str = output.content if hasattr(output, 'content') else str(output)
                duration_ms = int((time.time() - start_time) * 1000)
                
                if self.on_tool_end:
                    try: self.on_tool_end(tool_name, output_str)
                    except: pass
                
                return {
                    "tool_name": tool_name,
                    "input": args,
                    "output": output_str,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "duration_ms": duration_ms,
                    "attempts": attempt + 1
                }
            except Exception as e:
                if attempt >= self.max_retries:
                    if self.on_tool_error:
                        try: self.on_tool_error(tool_name, str(e))
                        except: pass
                    
                    return {
                        "tool_name": tool_name,
                        "input": args,
                        "output": None,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "duration_ms": int((time.time() - start_time) * 1000),
                        "attempts": attempt + 1
                    }
                time.sleep(0.5)