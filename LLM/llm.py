# LLM/llm.py
from datetime import datetime
import json
import os
import logging
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from colorama import Fore, Style, init
from typing import List, Dict, Any, Optional, Union, Type
from pydantic import BaseModel
from .prompts import TNC_SYSTEM_PROMPT
from .tools import (
    get_media_accounts,
    get_website_structure,
    visit_any_web_site,
    search_TNC_knowledge_base,
    event_search,
    news_search,
    TOOLS
)

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("llm_debug.log"),
        logging.StreamHandler()
    ]
)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

logger = logging.getLogger("GenerativeAI")

class _SingletonMeta(type):
    """
    A thread-safe implementation of Singleton.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class GenerativeAI(metaclass=_SingletonMeta):
    """
    Singleton class for Generative AI functions using OpenAI's API.
    """

    def __init__(self, debug_mode=True):
        """
        Initialize the GenerativeAI instance with an API key from environment variables.
        
        Args:
            debug_mode: Whether to enable detailed debugging output
        """
        self.debug_mode = debug_mode
        logger.info("Initializing GenerativeAI instance")
        
        # api_key = st.secrets["GEMINI_API_KEY"]
        api_key = st.secrets["OPENAI_API_KEY"]
        if not api_key:
            logger.error("API_KEY environment variable is not set")
            raise ValueError("API_KEY environment variable is not set")
        
        self.client = OpenAI(
                        api_key=api_key,
                        # base_url=GEMINI_BASE_URL
                    )
        self.system_message = TNC_SYSTEM_PROMPT
        # self.model = "gemini-1.5-pro"
        self.model = "gpt-4o"
        logger.info(f"Using model: {self.model}")
        
        self.available_tools = TOOLS
        
        logger.info(f"Registered {len(self.available_tools)} tools")
        
        # Map function names to their implementations
        self.tool_functions = {
            "get_media_accounts": get_media_accounts,
            "get_website_structure": get_website_structure,
            "visit_any_web_site": visit_any_web_site,
            "search_TNC_knowledge_base": search_TNC_knowledge_base,
            "news_search": news_search,
            "event_search": event_search
        }
        
        logger.info("GenerativeAI initialization completed")
    
    def _debug_print(self, title: str, content: Any, is_function_call: bool = False) -> None:
        """
        Print debug information if debug mode is enabled.
        
        Args:
            title: Description of the debug content
            content: The content to print/log
            is_function_call: Whether this debug message is related to a function call
        """
        if self.debug_mode:
            if isinstance(content, (dict, list)):
                content_str = json.dumps(content, indent=2)
            else:
                content_str = str(content)
            
            # Log to file
            logger.info(f"{title}:\n{content_str}")
            
            # Print to console with formatting
            if is_function_call:
                print(f"\n{Fore.CYAN}===== {title} ====={Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{content_str}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}===== {title} ====={Style.RESET_ALL}")
                print(f"{content_str}")
    
    def _serialize_pydantic_model(self, obj: Any) -> Any:
        """
        Recursively convert Pydantic models to dictionaries for JSON serialization.

        Args:
            obj: The object to serialize (could be a model, list, dict, or primitive)

        Returns:
            JSON serializable version of the object
        """
        # If it's a Pydantic model, convert to dict
        if isinstance(obj, BaseModel):
            return obj.model_dump()

        # If it's a list, recursively process its items
        elif isinstance(obj, list):
            return [self._serialize_pydantic_model(item) for item in obj]

        # If it's a dict, recursively process its values
        elif isinstance(obj, dict):
            return {key: self._serialize_pydantic_model(value) for key, value in obj.items()}

        # Otherwise, return the object as is
        else:
            return obj
    
    def generate_ai_response(self, question: str) -> str:
        """
        Generate a response to a single question without chat history.
        """
        try:
            logger.info(f"Generating response for question: {question[:50]}...")
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": question}
            ]

            self._debug_print("Initial Messages", messages)
            return self._process_completion_with_tools(messages)
        except Exception as e:
            logger.exception("Error in generate_ai_response")
            return f"Oops, something went wrong with the AI service: {str(e)}"
    
    def process_message_and_get_response(self, prompt: str, session_state) -> str:
        """
        Process a new user message, update session state, and get AI response.
        
        Args:
            prompt: The user's input message
            session_state: Streamlit's session state containing message history
            
        Returns:
            The AI response string
        """
        try:
            logger.info(f"Processing new message: {prompt[:50]}...")
            self._debug_print("Session state before processing", 
                             {"message_count": len(session_state.messages) if hasattr(session_state, 'messages') else 0})
            
            # Add user message to session
            session_state.messages.append({"role": "user", "content": prompt})
            
            # Format messages with chat history
            formatted_messages = [
                {"role": "system", "content": self.system_message}
            ]
            
            # Add all previous messages from session state
            for msg in session_state.messages:
                formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
            self._debug_print("Formatted Messages for AI", formatted_messages)
            
            # Get AI response
            start_time = time.time()
            response = self._process_completion_with_tools(formatted_messages)
            elapsed_time = time.time() - start_time
            
            logger.info(f"Response generated in {elapsed_time:.2f} seconds")
            
            # Add assistant response to session
            session_state.messages.append({"role": "assistant", "content": response})
            
            self._debug_print("Session state after processing", 
                             {"message_count": len(session_state.messages)})
            
            return response
            
        except Exception as e:
            logger.exception("Error in process_message_and_get_response")
            return f"Oops, something went wrong: {str(e)}"
    
    def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> Any:
        """
        Execute a tool function with the provided arguments.

        Args:
            function_name: Name of the function to execute
            function_args: Arguments to pass to the function

        Returns:
            The result of the function execution (serialized for JSON)
        """
        try:
            logger.info(f"Executing tool: {function_name} with args: {function_args}")

            # Get the function implementation
            function = self.tool_functions.get(function_name)

            if not function:
                logger.error(f"Function {function_name} not implemented")
                return {"error": f"Function {function_name} not implemented"}

            # Execute the function with the provided arguments
            if function_args:
                result = function(**function_args)
            else:
                result = function()

            # Convert any Pydantic models to dictionaries
            serialized_result = self._serialize_pydantic_model(result)

            # Log the conversion if debug mode is on
            if self.debug_mode:
                logger.info(f"Serialized result from Pydantic model(s) for {function_name}")

            return serialized_result

        except Exception as e:
            logger.exception(f"Error executing function {function_name}")
            return {"error": str(e)}
    
    def _process_completion_with_tools(self, messages: List[Dict[str, str]], max_turns: int = 3) -> str:
        """
        Process a completion request with tool calling capabilities.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            max_turns: Maximum number of tool-calling iterations
            
        Returns:
            String response from the AI
        """
        turn_count = 0
        
        logger.info(f"Starting tool-calling process with max {max_turns} turns")
        
        while turn_count < max_turns:
            turn_count += 1
            logger.info(f"Tool-calling turn {turn_count}/{max_turns}")
            
            try:
                self._debug_print(f"Turn {turn_count}: Sending request to AI Agent", 
                                 {"message_count": len(messages)})
                
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    tools=self.available_tools
                )
                elapsed_time = time.time() - start_time
                
                logger.info(f"LLM API response received in {elapsed_time:.2f} seconds")
                
                # Get the message from the response
                response_message = response.choices[0].message
                
                # Debug information about the response
                has_tool_calls = bool(response_message.tool_calls)
                tool_call_count = len(response_message.tool_calls) if has_tool_calls else 0
                
                self._debug_print(f"Turn {turn_count}: Response from LLM", {
                    "has_content": bool(response_message.content),
                    "content_preview": response_message.content[:100] + "..." if response_message.content else None,
                    "has_tool_calls": has_tool_calls,
                    "tool_call_count": tool_call_count,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "args_preview": tc.function.arguments[:100] + "..." 
                                if len(tc.function.arguments) > 100 else tc.function.arguments
                        } for tc in (response_message.tool_calls or [])
                    ]
                }, is_function_call=has_tool_calls)
                
                # Add the assistant's response to messages
                messages.append({
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": response_message.tool_calls or []
                })
                
                # If no tool calls were made, return the content
                if not response_message.tool_calls:
                    logger.info("No tool calls made, returning final response")
                    return response_message.content or ""
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    # Extract function details
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Processing tool call: {function_name}")
                    self._debug_print(f"Function {function_name} arguments", function_args, is_function_call=True)
                    
                    # Execute the appropriate function
                    if function_name in self.tool_functions:
                        start_time = time.time()
                        function_response = self._execute_tool(function_name, function_args)
                        elapsed_time = time.time() - start_time
                        
                        logger.info(f"Function {function_name} executed in {elapsed_time:.2f} seconds")
                        
                        # Debug the function response (truncate if too long)
                        function_response_str = json.dumps(function_response)
                        self._debug_print(
                            f"Function {function_name} response", 
                            function_response_str[:500] + "..." if len(function_response_str) > 500 else function_response_str,
                            is_function_call=True
                        )
                        
                        # Add the function response to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(function_response)
                        })
                    else:
                        logger.warning(f"Function {function_name} not found in tool registry")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps({"error": f"Function {function_name} not found"})
                        })
            except Exception as e:
                logger.exception(f"Error in tool-calling turn {turn_count}")
                return f"Oops, something went wrong with the AI service: {str(e)}"
        
        # Get final response from OpenAI
        try:
            logger.info("Requesting final response after tool calls")
            
            start_time = time.time()
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0
            )
            elapsed_time = time.time() - start_time
            
            logger.info(f"Final response received in {elapsed_time:.2f} seconds")
            
            final_content = final_response.choices[0].message.content.strip()
            self._debug_print("Final response content", final_content[:500] + "..." if len(final_content) > 500 else final_content)
            
            return final_content
        except Exception as e:
            logger.exception("Error getting final response")
            return f"Oops, something went wrong with the AI service: {str(e)}"
    
    def chat_with_history(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response based on the full conversation history.
        
        Args:
            messages: List of message objects with 'role' and 'content'
        
        Returns:
            String response from the AI
        """
        logger.info("Processing chat with history")
        self._debug_print("Chat history messages", messages)
        return self._process_completion_with_tools(messages)
    
    def clean_json_string(self, json_data: str) -> str:
        """
        Clean and format JSON strings returned by the AI.
        """
        logger.info("Cleaning JSON string")
        if json_data.startswith("```"):
            json_data = json_data.strip('`')
        
        lines = json_data.split('\n')
        if lines and lines[0].lower() in ['json', 'json\n']:
            lines = lines[1:]
        
        json_data = '\n'.join(lines)
        return json_data.replace('```', '')
    
    def set_system_message(self, system_message: str) -> None:
        """
        Set a custom system message for the AI.
        """
        logger.info("Setting new system message")
        self._debug_print("New system message", system_message)
        self.system_message = system_message