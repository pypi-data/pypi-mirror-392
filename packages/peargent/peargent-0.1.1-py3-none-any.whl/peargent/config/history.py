"""
History configuration module for peargent.

Provides HistoryConfig class for configuring conversation history management.
"""

from typing import Optional, Union, Literal
from dataclasses import dataclass

from peargent.core.history import ConversationHistory, StorageType


@dataclass
class HistoryConfig:
    """
    Configuration class for conversation history management.
    
    This class provides a streamlined DSL for configuring how agents manage
    their conversation history and context windows.
    
    Attributes:
        auto_manage_context: Whether to automatically manage context window size
        max_context_messages: Maximum messages before auto-management triggers (typo corrected from max_cnotext_message)
        strategy: Strategy for context management ("smart", "trim_last", "trim_first", "summarize")
        summarize_model: Model to use for summarization (only used when strategy involves summarization)
        store: Storage backend configuration (Memory(), File(), Sqlite(), etc.) - better name than "history_object"
    
    Examples:
        Basic configuration with smart strategy:
        ```python
        config = HistoryConfig(
            auto_manage_context=True,
            max_context_messages=10,
            strategy="smart",
            summarize_model=groq(),
            store=File(storage_dir="./conversations")
        )
        
        agent = create_agent(..., history=config)
        ```
        
        Memory-only configuration:
        ```python
        config = HistoryConfig(
            auto_manage_context=True,
            max_context_messages=15,
            strategy="trim_last", 
            store=Memory()
        )
        ```
    """
    auto_manage_context: bool = True
    max_context_messages: int = 10  # Fixed typo: was max_cnotext_message
    strategy: Literal["smart", "trim_last", "trim_first", "summarize"] = "smart"
    summarize_model: Optional[object] = None
    store: Optional[Union[StorageType, ConversationHistory]] = None  # Better name than history_object
    
    def create_history(self) -> Optional[ConversationHistory]:
        """
        Create a ConversationHistory instance based on the configuration.
        
        Returns:
            ConversationHistory instance or None if store is not configured
        """
        if self.store is None:
            return None
            
        # If it's already a ConversationHistory instance, return it
        if isinstance(self.store, ConversationHistory):
            return self.store
            
        # If it's a StorageType, create the history
        if isinstance(self.store, StorageType):
            from peargent import create_history
            return create_history(store_type=self.store)
            
        raise ValueError(f"Invalid store type: {type(self.store)}")