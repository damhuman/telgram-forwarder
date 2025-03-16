from typing import Dict, Tuple, Optional
from loguru import logger


class MessageStorage:
    """Storage for tracking forwarded messages to avoid duplicates."""
    
    def __init__(self):
        """Initialize the message storage."""
        # Map of source message IDs to destination message IDs
        # {(source_chat_id, source_message_id): (destination_chat_id, destination_message_id)}
        self._message_map: Dict[Tuple[int, int], Tuple[int, int]] = {}
    
    def add_message_mapping(self, source_chat_id: int, source_message_id: int, 
                           destination_chat_id: int, destination_message_id: int) -> None:
        """
        Add a mapping between a source message and its forwarded destination message.
        
        Args:
            source_chat_id: The ID of the source chat
            source_message_id: The ID of the source message
            destination_chat_id: The ID of the destination chat
            destination_message_id: The ID of the destination message
        """
        key = (source_chat_id, source_message_id)
        value = (destination_chat_id, destination_message_id)
        self._message_map[key] = value
        logger.debug(f"Added message mapping: {key} -> {value}")
    
    def get_destination_message_id(self, source_chat_id: int, source_message_id: int) -> Optional[int]:
        """
        Get the destination message ID for a given source message.
        
        Args:
            source_chat_id: The ID of the source chat
            source_message_id: The ID of the source message
            
        Returns:
            The ID of the destination message if it exists, None otherwise
        """
        key = (source_chat_id, source_message_id)
        if key in self._message_map:
            return self._message_map[key][1]
        return None
    
    def is_message_forwarded(self, source_chat_id: int, source_message_id: int) -> bool:
        """
        Check if a message has already been forwarded.
        
        Args:
            source_chat_id: The ID of the source chat
            source_message_id: The ID of the source message
            
        Returns:
            True if the message has already been forwarded, False otherwise
        """
        key = (source_chat_id, source_message_id)
        return key in self._message_map 