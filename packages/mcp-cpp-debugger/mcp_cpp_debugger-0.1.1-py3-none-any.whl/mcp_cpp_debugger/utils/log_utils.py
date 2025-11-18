import logging
from pathlib import Path
from datetime import datetime
import os

def init_logging(level: str = "INFO", log_dir: str = None):
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    if log_dir is None:
        appdata_dir = os.getenv('APPDATA')
        if appdata_dir:
            log_dir = os.path.join(appdata_dir, 'mcp-cpp-debugger', 'logs')
        else:
            log_dir = 'logs'
    
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"mcp_debugger_{timestamp}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level)
    
    debugger_output_logger = logging.getLogger("debugger_output")
    debugger_output_logger.handlers.clear()
    debugger_output_logger.setLevel(level)
    debugger_output_logger.propagate = False
    debugger_output_console = logging.StreamHandler()
    debugger_output_console.setFormatter(formatter)
    debugger_output_logger.addHandler(debugger_output_console)
    
    root_logger.info(f"Logging initialized at {level.upper()} level")
    root_logger.info(f"Log file: {log_file.absolute()}")