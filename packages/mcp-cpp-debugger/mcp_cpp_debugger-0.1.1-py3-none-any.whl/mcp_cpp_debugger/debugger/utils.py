from enum import Enum
from typing import TypedDict
import json
class Session_State(Enum):
    UNSTARTED = "unstarted"
    IDLE = "idle"
    RUNNING = "running"

class Debug_Mode(Enum):  
    UNKNOWN = "unknown"
    LAUNCH = "launch"
    ATTACH = "attach"
    DUMP_ANALYSIS = "dump_analysis"

class Target_Process_State(Enum):
    UNSTARTED = "unstarted"
    RUNNING = "running"
    PAUSED = "paused"

class Debugger_Response(TypedDict, total=False):
    success: bool
    command: str
    error_message: str
    debug_output: str

def create_debugger_response(
    success: bool,
    command: str,
    debug_output: str = "",
    error_message: str=""
) -> str:
    response: Debugger_Response = {
        "success": success,
        "command": command
    }
    
    if error_message:
        response["error_message"] = error_message
    if debug_output:
        response["debug_output"] = debug_output
    
    return json.dumps(response, indent=4, ensure_ascii=False)