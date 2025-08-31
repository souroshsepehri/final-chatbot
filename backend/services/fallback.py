"""
Fallback service to handle unanswered questions and log them.
"""

import os
from datetime import datetime
from typing import Optional


class FallbackService:
    """Service to handle fallback responses for unanswered questions."""
    
    def __init__(self, log_file_path: str = "data/fallback_logs.txt"):
        """
        Initialize the fallback service.
        
        Args:
            log_file_path (str): Path to the fallback logs file
        """
        self.log_file_path = log_file_path
        self.fallback_message = "فعلاً پاسخ مناسبی برای این سوال ندارم."
    
    def log_question(self, question: str) -> None:
        """
        Log an unanswered question to the fallback logs file.
        
        Args:
            question (str): The unanswered question to log
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format log entry
            log_entry = f"[{timestamp}] Question: {question}\n"
            
            # Append to log file
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            # If logging fails, we don't want to break the main flow
            print(f"Warning: Failed to log question: {e}")
    
    def get_fallback_response(self, question: str) -> str:
        """
        Get the fallback response for an unanswered question.
        
        Args:
            question (str): The unanswered question
            
        Returns:
            str: The fallback response message
        """
        # Log the question
        self.log_question(question)
        
        # Return the fallback message
        return self.fallback_message
    
    def get_logs(self, limit: Optional[int] = None) -> list:
        """
        Get recent fallback logs.
        
        Args:
            limit (Optional[int]): Maximum number of logs to return
            
        Returns:
            list: List of log entries
        """
        try:
            if not os.path.exists(self.log_file_path):
                return []
            
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                logs = f.readlines()
            
            # Filter out comment lines and empty lines
            logs = [log.strip() for log in logs if log.strip() and not log.strip().startswith("#")]
            
            if limit:
                logs = logs[-limit:]
            
            return logs
            
        except Exception as e:
            print(f"Warning: Failed to read logs: {e}")
            return [] 