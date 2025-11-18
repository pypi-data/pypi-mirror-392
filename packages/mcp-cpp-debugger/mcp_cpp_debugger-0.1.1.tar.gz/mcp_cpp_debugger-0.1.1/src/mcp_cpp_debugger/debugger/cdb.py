import subprocess
import threading
import logging
import re
import os
import json
import shutil
from pathlib import Path
from time import sleep
from typing import Optional

from .utils import Session_State, Debug_Mode, Target_Process_State, create_debugger_response

session_logger = logging.getLogger("cdb_session")
cdb_output_logger = logging.getLogger("debugger_output")
default_cdb_path = "cdb.exe"

ERROR_SESSION_NOT_STARTED = "CDB debug session is not running, please start a debug session first"
ERROR_SESSION_RUNNING = "CDB debug session is currently running, please wait"
ERROR_SESSION_UNSTARTED = "CDB debug session not started"

ERROR_PROCESS_NOT_STARTED = "CDB process not started, please start a debug session first"
ERROR_SESSION_IDLE = "CDB debug session is idle, target is not running"

class CDB_Session:
    def __init__(self) -> None:
        self.process: subprocess.Popen = None
        self.output_lines: list[str] = []
        self.lock: threading.Lock = threading.Lock()
        self.ready_event = threading.Event()
        self.reader_thread: threading.Thread = None
        self.session_state=Session_State.UNSTARTED
        self.debug_mode=Debug_Mode.UNKNOWN 
        self.target_process_state=Target_Process_State.UNSTARTED
        
        self.source_path_map: dict[str, str] = {}

    def launch(
        self,
        executable_path:str,
        cdb_path: str = default_cdb_path,
        args: str = None,
        symbol_path: str = None,
    ) -> str:
        self.debug_mode = Debug_Mode.LAUNCH
        self.cdb_path = cdb_path
        self.executable_path = executable_path.replace('\\', '/') if executable_path else None
        self.args = args.split(' ') if args else None
        self.symbol_path = symbol_path.replace('\\', '/') if symbol_path else None
        start_args = [self.executable_path]
        if self.args:
            start_args.extend(self.args)

        return self._start_cdb_process(
            start_args=start_args,
            post_start_commands=['l+t'],
        )

    def attach(
        self, 
        process_id: int = -1, 
        process_name: str = None,
        cdb_path: str = default_cdb_path,
        symbol_path: str = None,
    ) -> str:
        if process_id == -1 and not process_name:
            return "Error: Either process_id or process_name must be provided"
        
        if process_id != -1:
            start_args = ['-p', str(process_id)]
            session_logger.info(f"Attaching to process by PID: {process_id}")
        else:
            start_args = ['-pn', process_name]
            session_logger.info(f"Attaching to process by name: {process_name}")

        self.symbol_path = symbol_path.replace('\\', '/') if symbol_path else None
        self.debug_mode = Debug_Mode.ATTACH
        self.cdb_path = cdb_path
        
        return self._start_cdb_process(
            start_args=start_args,
            post_start_commands=['l+t'],
        )

    def analyze_dump(self, dump_file_path: str,symbol_path: str = None,cdb_path: str = default_cdb_path,source_path_map: dict[str,str] = {}) -> str:
        self.source_path_map = source_path_map
        self.debug_mode = Debug_Mode.DUMP_ANALYSIS
        self.dump_file_path = dump_file_path.replace('\\', '/') if dump_file_path else None
        self.symbol_path = symbol_path.replace('\\', '/') if symbol_path else None
        self.cdb_path = cdb_path
        return self._start_cdb_process(
            start_args=['-z', self.dump_file_path],
            post_start_commands=['.ecxr'],
        )


    def _start_cdb_process(
        self, 
        start_args: list[str], 
        post_start_commands: list[str]=None,
    ) -> str:

        if self.session_state != Session_State.UNSTARTED:
            return "CDB Session already started,please terminate the session first"
        
        try:
            self.session_state = Session_State.RUNNING
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            self.process = subprocess.Popen(
                self._build_start_cmdline(start_args),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,
                bufsize=0,
                creationflags=creation_flags,
            )

            self.start_cmdline=' '.join(self._build_start_cmdline(start_args))
            session_logger.info(f"CDB process start cmdline: {self.start_cmdline}")
            self.reader_thread = threading.Thread(target=self._read_output)
            self.reader_thread.daemon = True
            self.reader_thread.start()
            output = self._wait_for_prompt()

            if self.process.poll() is None:
                try:
                    self._load_natvis_files()
                    for cmd in post_start_commands:
                        output+=self.execute_command(cmd)

                    return create_debugger_response(
                        success=True,
                        command=self.start_cmdline,
                        debug_output=f"CDB process started successfully,output: {output}"
                    )
                except Exception as e:
                    raise Exception(f"CDB process startup failed: {str(e)}")
            else:
                if output:
                    raise Exception(f"CDB process terminated with output: {output}")
                else:
                    raise Exception(f"CDB process terminated with code: {self.process.poll()}")

        except Exception as e:
            self._reset_status() 
            return create_debugger_response(
                success=False,
                command=self.start_cmdline,
                error_message=f"CDB process startup failed: {str(e)}"
            )

    def _load_natvis_files(self):
        cdb_path_obj = Path(self.cdb_path)
        if cdb_path_obj.is_absolute():
            actual_cdb_path = str(cdb_path_obj)
        else:
            actual_cdb_path = shutil.which(self.cdb_path)
        
        if actual_cdb_path:
            cdb_dir = Path(actual_cdb_path).parent
            visualizers_dir = cdb_dir / "Visualizers"
            if visualizers_dir.exists() and visualizers_dir.is_dir():
                natvis_files = list(visualizers_dir.glob("*.natvis"))
                for natvis_file in natvis_files:
                    load_result = self.execute_command(f'.nvload "{natvis_file}"')
                    session_logger.info(f"Loaded {natvis_file.name}: {load_result}")
            else:
                session_logger.warning(f"Visualizers directory not found: {visualizers_dir}")
        else:
            session_logger.warning(f"Cannot find cdb executable: {self.cdb_path}")
    
    def _send_ctrl_c(self) -> bool:
        if not self.process or self.process.poll() is not None:
            return False
        
        try:
            if os.name == 'nt':
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    
                    result = kernel32.GenerateConsoleCtrlEvent(1, self.process.pid)
                    if result:
                        session_logger.info(f"Successfully sent CTRL_BREAK_EVENT to process group {self.process.pid}")
                        return True
                    else:
                        error_code = kernel32.GetLastError()
                        session_logger.warning(f"GenerateConsoleCtrlEvent(CTRL_BREAK_EVENT) failed with error code: {error_code}")
                        
                except Exception as e:
                    session_logger.warning(f"GenerateConsoleCtrlEvent method failed: {e}")
            else:
                #todo: send signal to process group
                raise Exception("Not implemented")
                
        except Exception as e:
            session_logger.error(f"Failed to interrupt target program: {str(e)}")
            return False

    def interrupt_target_program(self) -> str:
        if self.session_state == Session_State.UNSTARTED:
            return create_debugger_response(
                success=False,
                command="ctrl-c",
                error_message=ERROR_SESSION_NOT_STARTED
            )
        elif self.session_state == Session_State.IDLE:
            return create_debugger_response(
                success=False,
                command="ctrl-c",
                error_message=ERROR_SESSION_IDLE
            )
        else:
            if self._send_ctrl_c():
                result = self._wait_for_prompt()
                self.target_process_state = Target_Process_State.PAUSED
                #todo:don't return debug_output
                return create_debugger_response(
                    success=True,
                    command="ctrl-c",
                    debug_output=result
                )
            else:
                return create_debugger_response(
                    success=False,
                    command="ctrl-c",
                    error_message="Failed to interrupt target program"
                )
    
    def execute_command(self, command: str) -> str:
        timeout:int=None
        if not self.process or self.process.poll() is not None or self.session_state == Session_State.UNSTARTED:
            return create_debugger_response(
                success=False,
                command=command,
                error_message=ERROR_PROCESS_NOT_STARTED
            )

        if self.session_state == Session_State.RUNNING:
            return create_debugger_response(
                success=False,
                command=command,
                error_message=ERROR_SESSION_RUNNING
            )
            
        self.session_state = Session_State.RUNNING
        self._send_command(command)
        
        if command == "q":
            self._reset_status()
            return create_debugger_response(
                success=True,
                command=command,
                debug_output="CDB debug session is terminating"
            ) 
        
        #return immediately
        if command == "g":
            self.target_process_state = Target_Process_State.RUNNING
            return create_debugger_response(
                success=True,
                command=command,
                debug_output="Target program is now running"
            )

        if command=='p' or command=='t' or command=='gu':
            timeout=10

        try:
            result = self._wait_for_prompt(timeout=timeout)
            if self.source_path_map and self.debug_mode == Debug_Mode.DUMP_ANALYSIS:
                result = self.transform_output_paths(result)
            return create_debugger_response(
                success=True,
                command=command,
                debug_output=result
            )
        except Exception as e:
            return create_debugger_response(
                success=False,
                command=command,
                error_message=f"Command execution failed: {str(e)}"
            )

    def terminate(self) -> str:
        try:
            if self.debug_mode is not Debug_Mode.DUMP_ANALYSIS:
                self.interrupt_target_program()
            self.execute_command('q')
            self._reset_status()
            return create_debugger_response(
                success=True,
                command="terminate",
                debug_output="CDB debug session terminated successfully"
            )
        except Exception as e:
            return create_debugger_response(
                success=False,
                command="terminate",
                error_message=f"Failed to terminate session: {str(e)}"
            )

    def set_breakpoint(self, file_path: str, line_number: int) -> str:
        return self.execute_command(f"bp `{file_path}:{line_number}`")

    def get_breakpoint_list(self) -> str:
        return self.execute_command('bl')

    def enable_bp(self, num: int) -> str:
        return self.execute_command(f'be {num}')
    
    def disable_bp(self, num: int) -> str:
        return self.execute_command(f'bd {num}')

    def delete_bp(self, num: int) -> str:
        return self.execute_command(f'bc {num}')
    
    def get_stack_trace(self) -> str:
        return self.execute_command('kv')

    def continue_execution(self) -> str:
        if self.debug_mode is Debug_Mode.DUMP_ANALYSIS:
            return create_debugger_response(
                success=False,
                command="g",
                error_message="Cannot continue execution in dump analysis mode"
            )
        return self.execute_command('g')
    
    def step_over(self) -> str:
        return self.execute_command('p')
    
    def step_into(self) -> str:
        return self.execute_command('t')
    
    def step_out(self) -> str:
        return self.execute_command('gu')

    def apply_source_path_mapping(self, remote_path: str) -> str:
        if not self.source_path_map:
            return remote_path
        
        normalized_path = remote_path.replace('\\', '/')
        
        for pattern, local_base in self.source_path_map.items():
            pattern_key = pattern.rstrip('/')
            
            if pattern_key.startswith('*/'):
                target_dir = pattern_key[2:]  
                parts = normalized_path.split('/')
                
                for i in range(len(parts) - 1, -1, -1):
                    if parts[i] == target_dir:
                        remaining_path = '/'.join(parts[i+1:])
                        local_path = local_base.rstrip('/') + '/' + remaining_path
                        return local_path
            else:
                if normalized_path.startswith(pattern_key):
                    remaining = normalized_path[len(pattern_key):].lstrip('/')
                    local_path = local_base.rstrip('/') + '/' + remaining
                    return local_path
        
        return remote_path
    
    def transform_output_paths(self, output: str) -> str:
        if not self.source_path_map or not output:
            return output
        
        import re
        path_pattern = r'[A-Za-z]:[^\s\[\]<>"\'\|]+?\.(cpp|h|hpp|c|cc|cxx)'
        
        def replace_path(match):
            original_path = match.group(0)
            mapped_path = self.apply_source_path_mapping(original_path)
            return mapped_path
        
        transformed = re.sub(path_pattern, replace_path, output, flags=re.IGNORECASE)
        
        return transformed
    
    def get_current_status(self) -> str:
        if self.session_state is Session_State.UNSTARTED:
            return "CDB debug session is unstarted"

        current_status: dict[str, str] = {
            "session_state": self.session_state.value,
            "debug_mode": self.debug_mode.value,
            "start_cmdline": self.start_cmdline if self.start_cmdline else "",
        }
        if self.debug_mode is Debug_Mode.LAUNCH:
            current_status["executable_path"] = self.executable_path if self.executable_path else ""
            current_status["target_process_state"] = self.target_process_state.value
        elif self.debug_mode is Debug_Mode.ATTACH:
            current_status["target_process_state"] = self.target_process_state.value
        elif self.debug_mode is Debug_Mode.DUMP_ANALYSIS:
            current_status["dump_file_path"] = self.dump_file_path if self.dump_file_path else ""
        return json.dumps(current_status,indent=4, ensure_ascii=False)
    

    def _build_start_cmdline(self,start_args:list[str]) -> list[str]:
        
        cmdline=[self.cdb_path]
        cmdline.extend(['-lines']) 
        if self.symbol_path:
            cmdline.extend(['-y', self.symbol_path])
        if start_args:
            cmdline.extend(start_args)
        return cmdline

    def _send_command(self,command:str)->str:
        try:
            session_logger.info(f"_ _ _ _ _ _ _send command: {command}")
            self.process.stdin.write(f"{command}\n".encode('utf-8'))
            self.process.stdin.flush()
        except Exception as e:
            session_logger.error(f"Failed to send command: {command} - {str(e)}", exc_info=True)

    def _read_output(self):
        if not self.process or not self.process.stdout:
            session_logger.error("try read CDB output, but CDB process is None or stdout is None")
            return
        
        buffer = []
        raw_buffer = b""
        
        def handle_line_buffer(line):
            nonlocal buffer,raw_buffer
            if not line:
                return
            line_str = line.decode('utf-8', errors='ignore').strip()
            if line_str:
                cdb_output_logger.debug(f"{line_str}")
                buffer.append(line_str)
                if re.search(r'[0-9]:[0-9]+>', line_str):
                    self.session_state = Session_State.IDLE
                    self.target_process_state = Target_Process_State.PAUSED
                    with self.lock:
                        self.output_lines = buffer[:-1]
                        self.ready_event.set()
                    session_logger.debug("dected prompt")
                    buffer = []
                    raw_buffer=b""

        try:
            while self.process and self.process.poll() is None:
                chunk = self.process.stdout.read(1024)
                if self.process.poll() is not None:
                    #todo:need to notify mcp-server,let mcp-server notify mcp-client
                    line_str = chunk.decode('utf-8', errors='ignore').strip()
                    if line_str:
                        cdb_output_logger.debug(f"{line_str}")
                        buffer.append(line_str)
                        with self.lock:
                            self.output_lines=buffer
                            sleep(0.01)
                            self.ready_event.set()
                    buffer=[]
                    raw_buffer=[]
                    break   

                raw_buffer += chunk
                while b'\n' in raw_buffer:
                    line, raw_buffer = raw_buffer.split(b'\n', 1)
                    handle_line_buffer(line)
                handle_line_buffer(raw_buffer)
                    
        except Exception as e:
            session_logger.error(f"CDB output reader error: {e}")

    def _wait_for_prompt(self, timeout:int=None):
        self.ready_event.clear()
        if self.ready_event.wait(timeout=timeout):
            with self.lock:
                output = self.output_lines.copy()
                self.output_lines = []
            return "\n".join(output)
        else:
            return "wait timeout, target program may be running,please wait for the running to complete"

    def _reset_status(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                session_logger.warning("Process termination timeout, killing forcefully")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                session_logger.error(f"Error terminating process: {e}")
        self.process = None
        
        if self.reader_thread and self.reader_thread.is_alive():
            try:
                self.reader_thread.join(timeout=3)
                if self.reader_thread.is_alive():
                    session_logger.warning("Reader thread did not terminate in time")
            except Exception as e:
                session_logger.error(f"Error joining reader thread: {e}")
        self.reader_thread = None

        self.session_state = Session_State.UNSTARTED
        self.debug_mode = Debug_Mode.UNKNOWN
        self.target_process_state = Target_Process_State.UNSTARTED

        self.output_lines = []
        self.lock = threading.Lock()
        self.ready_event = threading.Event()
        
        self.cdb_path = default_cdb_path
        self.executable_path = None
        self.args = None
        self.symbol_path = None
        self.source_path_map = {}
        
        if hasattr(self, 'dump_file_path'):
            self.dump_file_path = None
    
        session_logger.info("CDB session status has been reset")