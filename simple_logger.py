import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SimpleLogger:
    def __init__(self, log_file: str = "data/execution_logs.json"):
        self.log_file = log_file
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Ensure the log file and directory exist"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def log_execution(self, script_name: str, status: str, details: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """Log script execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "script": script_name,
            "status": status,  # "started", "completed", "failed"
            "details": details or {},
            "error": error
        }
        
        # Read existing logs
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Keep only last 100 entries to avoid file getting too large
        if len(logs) > 100:
            logs = logs[-100:]
        
        # Write back to file
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return log_entry
    
    def get_recent_logs(self, limit: int = 20) -> list:
        """Get recent log entries"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            return logs[-limit:] if len(logs) > limit else logs
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_logs_by_script(self, script_name: str, limit: int = 10) -> list:
        """Get logs for a specific script"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            script_logs = [log for log in logs if log.get('script') == script_name]
            return script_logs[-limit:] if len(script_logs) > limit else script_logs
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"total_executions": 0, "successful": 0, "failed": 0, "scripts": {}}
        
        stats = {
            "total_executions": len(logs),
            "successful": len([log for log in logs if log.get('status') == 'completed']),
            "failed": len([log for log in logs if log.get('status') == 'failed']),
            "scripts": {}
        }
        
        # Group by script
        for log in logs:
            script = log.get('script', 'unknown')
            if script not in stats['scripts']:
                stats['scripts'][script] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "last_execution": None
                }
            
            stats['scripts'][script]['total'] += 1
            if log.get('status') == 'completed':
                stats['scripts'][script]['successful'] += 1
            elif log.get('status') == 'failed':
                stats['scripts'][script]['failed'] += 1
            
            # Update last execution
            if not stats['scripts'][script]['last_execution'] or log.get('timestamp') > stats['scripts'][script]['last_execution']:
                stats['scripts'][script]['last_execution'] = log.get('timestamp')
        
        return stats

# Global logger instance
logger = SimpleLogger() 