"""Reasoning management for tool calling sequences."""

from typing import Dict, List, Optional, Any
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class ReasoningManager:
    """
    Manage reasoning/thinking blocks in conversations.
    
    Rules:
    1. Keep reasoning in messages with tool_calls
    2. Keep reasoning in immediate message after tool response
    3. Keep reasoning in last message of conversation
    4. Remove reasoning from all other messages
    """
    
    @staticmethod
    def has_reasoning_blocks(message: Dict[str, Any]) -> bool:
        """
        Detect if message contains reasoning/thinking blocks.
        
        ONLY uses explicit API fields returned by providers (no tag parsing):
        - Anthropic: 'thinking' field (top-level)
        - Anthropic: content blocks with type='thinking' (in content array)
        - OpenAI o1: 'reasoning' field (top-level)
        - vLLM: 'reasoning_content' field (top-level)
        
        Does NOT parse tags like <thinking>, <reasoning>, <think> etc.
        Only uses structured fields from API responses.
        
        Args:
            message: Message dictionary from API response
            
        Returns:
            True if message contains reasoning in explicit fields
        """
        if not isinstance(message, dict):
            return False
        
        # Check for explicit reasoning fields (top-level keys)
        # Anthropic: 'thinking' field
        if 'thinking' in message and message['thinking']:
            return True
        
        # OpenAI o1: 'reasoning' field
        if 'reasoning' in message and message['reasoning']:
            return True
        
        # vLLM: 'reasoning_content' field
        if 'reasoning_content' in message and message['reasoning_content']:
            return True
        
        # OpenRouter reasoning_details field (shared structure across providers)
        reasoning_details = message.get('reasoning_details')
        if isinstance(reasoning_details, list) and reasoning_details:
            return True
        
        # Check for Anthropic content blocks with type='thinking'
        # This is a structured format, not tag parsing
        content = message.get('content')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'thinking':
                    return True
        
        return False
    
    @staticmethod
    def strip_reasoning_from_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove reasoning blocks from a message.
        
        ONLY removes explicit API fields (no tag parsing):
        - Removes top-level reasoning fields (thinking, reasoning, reasoning_content)
        - Removes thinking blocks from Anthropic content arrays
        
        Does NOT parse or remove tags from string content.
        Only removes structured reasoning fields.
        
        Args:
            message: Message dictionary from API response
            
        Returns:
            Cleaned message dictionary without reasoning fields
        """
        if not isinstance(message, dict):
            return message
        
        cleaned = message.copy()
        
        # Remove explicit reasoning fields (top-level keys only)
        cleaned.pop('thinking', None)            # Anthropic
        cleaned.pop('reasoning', None)           # OpenAI o1
        cleaned.pop('reasoning_content', None)   # vLLM
        cleaned.pop('reasoning_details', None)   # OpenRouter reasoning tokens structure
        
        # Filter out thinking blocks from Anthropic content arrays
        # This is structured data, not tag parsing
        content = cleaned.get('content')
        if isinstance(content, list):
            cleaned['content'] = [
                block for block in content
                if not (isinstance(block, dict) and block.get('type') == 'thinking')
            ]
        
        # Note: We do NOT parse or modify string content
        # Tags like <thinking>, <reasoning> etc. are left as-is
        
        return cleaned

    @staticmethod
    def extract_reasoning_as_string(message: Dict[str, Any]) -> str:
        """
        Extract reasoning content from structured provider fields as a single string.
        
        Args:
            message: Message dictionary from API response
            
        Returns:
            Aggregated reasoning content as a newline-separated string
        """
        if not isinstance(message, dict):
            return ''
        segments: List[str] = []
        seen: set = set()

        def add_segment(value: Any) -> None:
            if value is None:
                return
            text = str(value).strip()
            if not text:
                return
            if text in seen:
                return
            segments.append(text)
            seen.add(text)

        add_segment(message.get('thinking'))
        add_segment(message.get('reasoning'))
        add_segment(message.get('reasoning_content'))

        reasoning_details = message.get('reasoning_details')
        if isinstance(reasoning_details, list):
            for detail in reasoning_details:
                if not isinstance(detail, dict):
                    continue
                detail_type = detail.get('type')
                if detail_type == 'reasoning.summary':
                    add_segment(detail.get('summary'))
                elif detail_type == 'reasoning.text':
                    add_segment(detail.get('text'))
                elif detail_type == 'reasoning.encrypted':
                    data = detail.get('data')
                    if data:
                        add_segment(f"[encrypted reasoning: {data}]")
                else:
                    # Fallback - include any known textual fields
                    for key in ('summary', 'text', 'data'):
                        if key in detail:
                            add_segment(detail.get(key))

        content = message.get('content')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'thinking':
                    add_segment(block.get('thinking'))

        return "\n\n".join(segments)

    @staticmethod
    def normalize_reasoning_message(message: Dict[str, Any], keep_reasoning: bool) -> Dict[str, Any]:
        """
        Normalize reasoning fields based on whether reasoning should be preserved.
        
        Args:
            message: Original message
            keep_reasoning: Whether reasoning content should be retained
            
        Returns:
            Message dictionary with standardized reasoning handling
        """
        if not isinstance(message, dict):
            return message

        if not keep_reasoning:
            return ReasoningManager.strip_reasoning_from_message(message)

        reasoning_text = ReasoningManager.extract_reasoning_as_string(message)
        normalized = ReasoningManager.strip_reasoning_from_message(message)
        if reasoning_text:
            normalized['reasoning'] = reasoning_text
        else:
            normalized.pop('reasoning', None)
        return normalized
    
    @staticmethod
    def should_keep_reasoning(
        message: Dict[str, Any],
        index: int,
        conversation: List[Dict[str, Any]]
    ) -> bool:
        """
        Determine if reasoning should be kept for this message.
        
        Rules (in order of priority):
        1. Keep if message has tool_calls
        2. Keep if message is assistant AND previous message is tool
        3. Keep if message is the last message in conversation
        4. Otherwise, remove
        
        Args:
            message: Current message
            index: Index in conversation
            conversation: Full conversation history
            
        Returns:
            True if reasoning should be kept
        """
        if not isinstance(message, dict):
            return False
        
        # Safety check for empty conversation
        if not conversation or index < 0 or index >= len(conversation):
            return False
        
        # Rule 1: Message has tool_calls
        if message.get('tool_calls'):
            return True
        
        # Rule 2: Assistant message immediately after tool response
        if message.get('role') == 'assistant' and index > 0:
            prev_message = conversation[index - 1]
            if isinstance(prev_message, dict) and prev_message.get('role') == 'tool':
                return True
        
        # Rule 3: Last message in conversation
        if index == len(conversation) - 1:
            return True
        
        # Otherwise, remove reasoning
        return False
    
    @staticmethod
    def clean_conversation_reasoning(
        conversation: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Clean reasoning from conversation based on rules.
        
        Args:
            conversation: Full conversation history
            config: Optional config with reasoning_output_rules
            
        Returns:
            Cleaned conversation with reasoning properly managed
        """
        if not conversation or not isinstance(conversation, list):
            return conversation or []
        
        # Get config rules (or use defaults)
        if config:
            rules = config.get('reasoning_output_rules', {})
            save_all = rules.get('save_all_reasoning', True)  # Default: True (save all reasoning)
            keep_with_tools = rules.get('keep_with_tool_calls', True)
            keep_after_tool = rules.get('keep_immediate_after_tool', True)
            keep_last = rules.get('keep_last_message', True)
        else:
            save_all = True  # Default: save all reasoning
            keep_with_tools = keep_after_tool = keep_last = True
        
        # If save_all enabled, keep reasoning in ALL messages
        if save_all:
            logger.debug("save_all_reasoning enabled - preserving reasoning in all messages")
            return [
                ReasoningManager.normalize_reasoning_message(msg, keep_reasoning=True)
                for msg in conversation
                if msg is not None
            ]
        
        cleaned = []
        
        for idx, message in enumerate(conversation):
            if not isinstance(message, dict):
                cleaned.append(message)
                continue
            
            # Determine if we should keep reasoning
            should_keep = False
            
            # Rule 1: Has tool_calls
            if keep_with_tools and message.get('tool_calls'):
                should_keep = True
            
            # Rule 2: Immediate after tool
            if keep_after_tool and message.get('role') == 'assistant' and idx > 0 and idx < len(conversation):
                prev_msg = conversation[idx - 1]
                if isinstance(prev_msg, dict) and prev_msg.get('role') == 'tool':
                    should_keep = True
            
            # Rule 3: Last message
            if keep_last and idx == len(conversation) - 1:
                should_keep = True
            
            # Apply decision
            cleaned.append(
                ReasoningManager.normalize_reasoning_message(
                    message,
                    keep_reasoning=should_keep
                )
            )
        
        return cleaned
    
    @staticmethod
    def prepare_for_tool_sequence(
        conversation: List[Dict[str, Any]],
        interleaved_thinking: bool = False,
        enable_reasoning: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Prepare conversation for sending to LLM during tool sequence.
        
        With interleaved thinking enabled:
        - Preserve ALL reasoning blocks in assistant messages as-is
        - This allows the model to see its previous reasoning when processing tool results
        - Keep the original structure (Anthropic content arrays, etc.)
        
        Without interleaved thinking:
        - Strip reasoning as normal (standard behavior)
        
        Args:
            conversation: Conversation history
            interleaved_thinking: Whether interleaved thinking is enabled
            enable_reasoning: Whether reasoning is enabled at all
            
        Returns:
            Prepared conversation
        """
        if not conversation or not isinstance(conversation, list):
            return conversation or []
        
        # If reasoning disabled entirely, strip all
        if not enable_reasoning:
            return [
                ReasoningManager.normalize_reasoning_message(msg, keep_reasoning=False)
                for msg in conversation
                if msg is not None
            ]
        
        # If interleaved thinking enabled, keep ALL reasoning as-is
        # Don't normalize to single string - keep original structure for provider
        if interleaved_thinking:
            logger.debug("Interleaved thinking enabled - preserving all reasoning blocks")
            # Filter out None messages for safety
            return [msg for msg in conversation if msg is not None]
        
        # Normal reasoning - strip from intermediate messages
        # (Will be cleaned based on rules after generation completes)
        return [
            ReasoningManager.normalize_reasoning_message(msg, keep_reasoning=False)
            for msg in conversation
            if msg is not None
        ]
    
    @staticmethod
    def prepare_conversation_for_generation(
        conversation: List[Dict[str, Any]],
        enable_reasoning: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Prepare conversation for LLM generation (internal API calls).
        
        During generation, reasoning is kept to maintain context for the model.
        Only strip reasoning from final output.
        
        Args:
            conversation: Conversation history
            enable_reasoning: Whether reasoning is enabled
            
        Returns:
            Prepared conversation
        """
        if not conversation or not isinstance(conversation, list):
            return conversation or []
        
        if not enable_reasoning:
            # If reasoning disabled, strip all reasoning
            return [
                ReasoningManager.normalize_reasoning_message(msg, keep_reasoning=False)
                for msg in conversation
                if msg is not None
            ]
        
        # If reasoning enabled, keep it during generation for context
        return conversation
