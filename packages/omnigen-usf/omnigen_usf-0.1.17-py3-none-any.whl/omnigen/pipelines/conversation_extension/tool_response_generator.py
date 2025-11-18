"""Tool Response Generator for realistic API simulation."""

import random
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from omnigen.core.base import BaseLLMProvider
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class ToolResponseGenerator:
    """
    Generate realistic simulated tool/API responses.
    
    Features:
    - OpenAI tool format validation
    - Success/failure ratio configuration
    - Variable substitution in prompts
    - Schema-aware response generation
    - Realistic error simulation
    """
    
    def __init__(
        self,
        provider: BaseLLMProvider,
        config: Dict[str, Any]
    ):
        """
        Initialize tool response generator.
        
        Args:
            provider: LLM provider for generating responses
            config: Configuration dictionary
        """
        self.provider = provider
        self.config = config
        
        # Core settings
        self.failure_ratio = config.get('failure_ratio', 0.2)
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2048)
        
        # Default prompts
        self.default_success_system = self._get_default_success_system_prompt()
        self.default_success_user = self._get_default_success_user_prompt()
        self.default_failure_system = self._get_default_failure_system_prompt()
        self.default_failure_user = self._get_default_failure_user_prompt()
        
        # Custom prompts (if provided)
        self.success_system_template = config.get('success_system_prompt', self.default_success_system)
        self.success_user_template = config.get('success_user_prompt', self.default_success_user)
        self.failure_system_template = config.get('failure_system_prompt', self.default_failure_system)
        self.failure_user_template = config.get('failure_user_prompt', self.default_failure_user)
        
        # Per-tool custom prompts
        self.tool_specific_prompts = config.get('tool_specific_prompts', {})
        
        logger.info(f"ToolResponseGenerator initialized with {self.failure_ratio*100:.0f}% failure rate")
    
    @staticmethod
    def validate_tool_schema(tool: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate tool definition against OpenAI format.
        
        OpenAI tool format:
        {
            "type": "function",
            "function": {
                "name": "function_name",
                "description": "...",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }
        
        Args:
            tool: Tool definition dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(tool, dict):
            return False, "Tool must be a dictionary"
        
        # Check type field
        if 'type' not in tool:
            return False, "Tool missing 'type' field"
        
        if tool['type'] != 'function':
            return False, f"Tool type must be 'function', got '{tool['type']}'"
        
        # Check function field
        if 'function' not in tool:
            return False, "Tool missing 'function' field"
        
        function = tool['function']
        if not isinstance(function, dict):
            return False, "'function' must be a dictionary"
        
        # Check function name
        if 'name' not in function:
            return False, "Function missing 'name' field"
        
        name = function['name']
        if not isinstance(name, str) or not name.strip():
            return False, "Function name must be a non-empty string"
        
        # Validate name format (alphanumeric, underscore, dash)
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False, f"Function name '{name}' contains invalid characters"
        
        # Check description (optional but recommended)
        if 'description' in function:
            if not isinstance(function['description'], str):
                return False, "Function description must be a string"
        
        # Check parameters
        if 'parameters' not in function:
            return False, "Function missing 'parameters' field"
        
        parameters = function['parameters']
        if not isinstance(parameters, dict):
            return False, "'parameters' must be a dictionary"
        
        # Validate parameters schema
        if 'type' not in parameters:
            return False, "Parameters missing 'type' field"
        
        if parameters['type'] != 'object':
            return False, f"Parameters type must be 'object', got '{parameters['type']}'"
        
        # Check properties (optional)
        if 'properties' in parameters:
            if not isinstance(parameters['properties'], dict):
                return False, "'properties' must be a dictionary"
        
        # Check required (optional)
        if 'required' in parameters:
            if not isinstance(parameters['required'], list):
                return False, "'required' must be a list"
            
            # Validate required fields exist in properties
            if 'properties' in parameters:
                properties = parameters['properties']
                for req_field in parameters['required']:
                    if req_field not in properties:
                        return False, f"Required field '{req_field}' not in properties"
        
        return True, None
    
    @staticmethod
    def validate_tools_list(tools: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate a list of tool definitions.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        if not isinstance(tools, list):
            return False, ["Tools must be a list"]
        
        if len(tools) == 0:
            return False, ["Tools list cannot be empty"]
        
        errors = []
        tool_names = set()
        
        for idx, tool in enumerate(tools):
            is_valid, error_msg = ToolResponseGenerator.validate_tool_schema(tool)
            
            if not is_valid:
                errors.append(f"Tool[{idx}]: {error_msg}")
            else:
                # Check for duplicate names
                tool_name = tool['function']['name']
                if tool_name in tool_names:
                    errors.append(f"Tool[{idx}]: Duplicate tool name '{tool_name}'")
                tool_names.add(tool_name)
        
        return len(errors) == 0, errors
    
    def _get_default_success_system_prompt(self) -> str:
        """Default system prompt for successful responses."""
        return """You are simulating a successful API response.

Generate realistic data that:
1. Matches the tool's expected output format
2. Uses the provided arguments appropriately
3. Contains realistic values (not placeholders like "example.com" or "placeholder")
4. Is valid JSON

CRITICAL: Return ONLY raw JSON data - no markdown code blocks, no explanations, no extra text.
Do not wrap response in ```json or ``` tags."""
    
    def _get_default_success_user_prompt(self) -> str:
        """Default user prompt for successful responses."""
        return """Generate successful API response.

Tool: {tool_name}
Description: {tool_description}
Arguments: {arguments}
Parameters Schema: {parameters_schema}

Return ONLY valid JSON data. No markdown, no explanations."""
    
    def _get_default_failure_system_prompt(self) -> str:
        """Default system prompt for failed responses."""
        return """You are simulating a realistic API error.

Common error types:
- rate_limit_exceeded: API rate limits hit
- invalid_parameter: Invalid or missing parameter
- not_found: Resource not found
- timeout: Request timeout
- auth_error: Authentication/authorization failure
- server_error: Internal server error (500)
- service_unavailable: Service temporarily down (503)

Generate realistic errors with helpful messages.

CRITICAL: Return ONLY raw JSON error object - no markdown, no explanations.
Format: {"error": {"type": "error_type", "message": "detailed message"}}"""
    
    def _get_default_failure_user_prompt(self) -> str:
        """Default user prompt for failed responses."""
        return """Generate realistic API error.

Tool: {tool_name}
Description: {tool_description}
Arguments: {arguments}

Return ONLY valid JSON error object in format:
{"error": {"type": "error_type", "message": "detailed message"}}"""
    
    def should_fail(self, tool_name: Optional[str] = None) -> bool:
        """
        Determine if this tool call should fail.
        
        Args:
            tool_name: Tool name for tool-specific failure ratio
            
        Returns:
            True if should generate failure response
        """
        # Check for tool-specific failure ratio
        if tool_name and tool_name in self.tool_specific_prompts:
            tool_config = self.tool_specific_prompts[tool_name]
            failure_ratio = tool_config.get('failure_ratio', self.failure_ratio)
        else:
            failure_ratio = self.failure_ratio
        
        return random.random() < failure_ratio
    
    def _substitute_variables(self, template: str, variables: Dict[str, str]) -> str:
        """
        Substitute variables in prompt template.
        
        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values
            
        Returns:
            Template with variables substituted
        """
        result = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result
    
    def _prepare_variables(
        self,
        tool_call: Dict[str, Any],
        tool_schema: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Prepare variables for prompt substitution.
        
        Args:
            tool_call: Tool call dictionary (OpenAI format: {'name': ..., 'arguments': ...})
            tool_schema: Tool schema dictionary (function definition)
            
        Returns:
            Dictionary of variables for substitution
        """
        # Extract tool info - handle both direct format and nested function format
        if 'name' in tool_call:
            tool_name = tool_call.get('name', 'unknown')
            arguments = tool_call.get('arguments', {})
        else:
            # Nested function format
            function = tool_call.get('function', {})
            tool_name = function.get('name', 'unknown')
            arguments = function.get('arguments', {})
        
        # Parse arguments if string
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse arguments as JSON: {arguments}")
                arguments = {"raw": arguments}
        
        # Get schema info - tool_schema is the function definition
        # (already extracted from tool['function'] by caller)
        description = tool_schema.get('description', 'No description provided')
        parameters = tool_schema.get('parameters', {})
        
        # Format arguments for display
        if isinstance(arguments, dict):
            arguments_formatted = "\n".join([
                f"  {k} = {v}" for k, v in arguments.items()
            ])
        else:
            arguments_formatted = str(arguments)
        
        # Return all available variables
        return {
            'tool_name': tool_name,
            'tool_description': description,
            'tool_schema': json.dumps(tool_schema, indent=2),
            'parameters_schema': json.dumps(parameters, indent=2),
            'arguments': json.dumps(arguments, indent=2) if isinstance(arguments, dict) else str(arguments),
            'arguments_formatted': arguments_formatted
        }
    
    def _get_prompts_for_tool(
        self,
        tool_name: str,
        is_success: bool
    ) -> Tuple[str, str]:
        """
        Get system and user prompts for a specific tool.
        
        Args:
            tool_name: Name of the tool
            is_success: Whether this is a success or failure scenario
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Check for tool-specific prompts
        if tool_name in self.tool_specific_prompts:
            tool_config = self.tool_specific_prompts[tool_name]
            if is_success:
                system = tool_config.get('success_system_prompt', self.success_system_template)
                user = tool_config.get('success_user_prompt', self.success_user_template)
            else:
                system = tool_config.get('failure_system_prompt', self.failure_system_template)
                user = tool_config.get('failure_user_prompt', self.failure_user_template)
        else:
            # Use default prompts
            if is_success:
                system = self.success_system_template
                user = self.success_user_template
            else:
                system = self.failure_system_template
                user = self.failure_user_template
        
        return system, user
    
    def generate_tool_response(
        self,
        tool_call: Dict[str, Any],
        tool_schema: Dict[str, Any],
        force_success: Optional[bool] = None
    ) -> Tuple[str, bool]:
        """
        Generate realistic tool response.
        
        Args:
            tool_call: Tool call dict with 'name', 'arguments' or 'function': {'name', 'arguments'}
            tool_schema: Tool schema (function definition) with 'name', 'description', 'parameters'
            force_success: If True/False, override random selection
            
        Returns:
            Tuple of (response_content, is_success)
        """
        # Extract tool name - handle both formats
        if 'name' in tool_call:
            tool_name = tool_call.get('name', 'unknown')
        else:
            function = tool_call.get('function', {})
            tool_name = function.get('name', 'unknown')
        
        # Determine success or failure
        is_success = not self.should_fail(tool_name) if force_success is None else force_success
        
        # Prepare variables for substitution
        variables = self._prepare_variables(tool_call, tool_schema)
        
        # Get prompts (tool-specific or default)
        system_template, user_template = self._get_prompts_for_tool(tool_name, is_success)
        
        # Substitute variables
        system_prompt = self._substitute_variables(system_template, variables)
        user_prompt = self._substitute_variables(user_template, variables)
        
        # Get temperature and max_tokens (tool-specific or default)
        tool_config = self.tool_specific_prompts.get(tool_name, {})
        temperature = tool_config.get('temperature', self.temperature)
        max_tokens = tool_config.get('max_tokens', self.max_tokens)
        
        # Log if using tool-specific settings
        if tool_config:
            logger.debug(f"Using tool-specific settings for '{tool_name}': temp={temperature}, max_tokens={max_tokens}")
        
        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.provider.chat_completion(
                messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract content from response
            if isinstance(response, dict):
                content = response.get('content', str(response))
            else:
                content = str(response)
            
            # Clean response (remove markdown, extra text)
            cleaned_response = self._clean_response(content)
            
            logger.debug(
                f"Generated {'success' if is_success else 'failure'} response for "
                f"tool '{tool_name}'"
            )
            
            return cleaned_response, is_success
            
        except Exception as e:
            logger.error(f"Error generating tool response for '{tool_name}': {e}")
            # Fallback to simple error
            fallback = json.dumps({
                "error": {
                    "type": "generation_error",
                    "message": f"Failed to generate tool response: {str(e)}"
                }
            })
            return fallback, False
    
    def _clean_response(self, response: str) -> str:
        """
        Clean and validate generated response.
        
        Removes:
        - Markdown code blocks
        - Leading/trailing text
        - Extra whitespace
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Cleaned JSON string
        """
        if not response:
            return json.dumps({"error": {"type": "empty_response", "message": "No response generated"}})
        
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Find first { or [ and last } or ]
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(cleaned):
            if char in ['{', '[']:
                start_idx = i
                break
        
        for i in range(len(cleaned) - 1, -1, -1):
            if cleaned[i] in ['}', ']']:
                end_idx = i + 1
                break
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            cleaned = cleaned[start_idx:end_idx]
        
        # Validate JSON
        try:
            # Try to parse and re-serialize for consistency
            parsed = json.loads(cleaned)
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            logger.warning(f"Response not valid JSON: {e}, attempting to wrap...")
            # Try to salvage by wrapping
            try:
                wrapped = json.dumps({"result": cleaned})
                return wrapped
            except Exception:
                # Last resort: return error
                return json.dumps({
                    "error": {
                        "type": "invalid_json",
                        "message": f"Generated response was not valid JSON: {str(e)}"
                    }
                })
    
    def generate_batch_responses(
        self,
        tool_calls: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate responses for multiple tool calls.
        
        Args:
            tool_calls: List of tool call dictionaries
            tools_schema: List of tool schema definitions
            
        Returns:
            List of tool response messages
        """
        if not tool_calls:
            return []
        
        responses = []
        
        for tool_call in tool_calls:
            # Extract function info
            function = tool_call.get('function', tool_call)
            tool_name = function.get('name')
            
            # Get tool_call_id early for error cases
            tool_call_id = tool_call.get('id', f"call_{random.randint(10000, 99999)}")
            
            if not tool_name:
                # CRITICAL ERROR: Tool call missing name - this is invalid and conversation must fail
                error_msg = f"Tool call missing function name - conversation cannot continue. Tool call: {tool_call}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Find matching schema
            schema = None
            for s in tools_schema:
                schema_func = s.get('function', s)
                if schema_func.get('name') == tool_name:
                    schema = schema_func
                    break
            
            if not schema:
                logger.warning(f"No schema found for tool '{tool_name}'")
                # Generate error response
                content = json.dumps({
                    "error": {
                        "type": "schema_not_found",
                        "message": f"Tool '{tool_name}' not found in schema definitions"
                    }
                })
                is_success = False
            else:
                # Generate response
                content, is_success = self.generate_tool_response(function, schema)
            
            # Format as tool response message
            response = {
                'role': 'tool',
                'tool_call_id': tool_call_id,  # Already extracted above
                'name': tool_name,
                'content': content
            }
            
            responses.append(response)
        
        return responses
