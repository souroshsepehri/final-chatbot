"""
GPT service to handle OpenAI API requests.
"""

import os
import time
from typing import Optional
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GPTService:
    """Service to handle GPT-4 API requests."""

    def __init__(self):
        """Initialize the GPT service. Does not hard-fail if API key is missing."""
        api_key = os.getenv("OPENAI_API_KEY")
        self.available = bool(api_key)
        if api_key:
            # Configure OpenAI for older version compatibility
            openai.api_key = api_key
        self.model = "gpt-4"
        self.max_tokens = 100  # Reduced for faster responses
        self.temperature = 0.7
        self.timeout = 10  # 10 second timeout
    
    def get_response(self, message: str) -> Optional[str]:
        """
        Get a response from GPT-4 for the given message.
        
        Args:
            message (str): The user's message
            
        Returns:
            Optional[str]: The GPT response, or None if failed
        """
        if not self.available:
            return None
        try:
            start_time = time.time()
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Provide clear, concise, and accurate answers. Keep responses brief and to the point."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            print(f"GPT response time: {response_time:.2f}s")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error: Failed to get GPT response: {e}")
            return None
    
    def get_response_with_context(self, message: str, context: str = "") -> Optional[str]:
        """
        Get a response from GPT-4 with additional context.
        
        Args:
            message (str): The user's message
            context (str): Additional context for the response
            
        Returns:
            Optional[str]: The GPT response, or None if failed
        """
        if not self.available:
            return None
        try:
            start_time = time.time()
            
            system_prompt = "You are a helpful assistant. Provide clear, concise, and accurate answers. Keep responses brief and to the point."
            
            if context:
                system_prompt += f"\n\nContext: {context}"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            print(f"GPT response time: {response_time:.2f}s")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error: Failed to get GPT response: {e}")
            return None
    
    def set_model(self, model: str) -> None:
        """
        Set the GPT model to use.
        
        Args:
            model (str): The model name (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        self.model = model
    
    def set_max_tokens(self, max_tokens: int) -> None:
        """
        Set the maximum number of tokens for responses.
        
        Args:
            max_tokens (int): Maximum number of tokens
        """
        self.max_tokens = max_tokens
    
    def set_temperature(self, temperature: float) -> None:
        """
        Set the temperature for response generation.
        
        Args:
            temperature (float): Temperature value (0.0 to 2.0)
        """
        self.temperature = temperature 