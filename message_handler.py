from typing import Optional
from telethon.tl.types import Message
from loguru import logger

from user_service import UserService
from message_repository import MessageRepository


class MessageHandler:
    """Handler for processing incoming messages and determining forwarding actions."""
    
    def __init__(self, user_service: UserService, message_repository: MessageRepository, enable_message_links: bool = True):
        """
        Initialize the MessageHandler.
        
        Args:
            user_service: Service for checking if users should be tracked
            message_repository: Repository for message operations
            enable_message_links: Whether to enable the feature to send links to original messages
        """
        self._user_service = user_service
        self._message_repository = message_repository
        # Message links are now always included in the formatted message, so this parameter is no longer used
        
    async def handle_message(self, message: Message) -> None:
        """
        Handle an incoming message.
        
        Args:
            message: The message to handle
        """
        # Check if message is from a tracked user
        if not self._should_forward_message(message):
            return
        
        logger.info(f"Processing message {message.id} from user {message.sender_id}")
        
        # Check if message is a reply
        replied_message = await self._message_repository.get_replied_message(message)
        
        if replied_message:
            logger.info(f"Message {message.id} is a reply to message {replied_message.id}")
            await self._message_repository.forward_message_with_reply(message, replied_message)
        else:
            await self._message_repository.forward_message(message)
    
    def _should_forward_message(self, message: Message) -> bool:
        """
        Determine if a message should be forwarded.
        
        Args:
            message: The message to check
            
        Returns:
            True if the message should be forwarded, False otherwise
        """
        # Check if sender is in tracked users
        if not message.sender_id:
            return False
        
        return self._user_service.is_tracked(message.sender_id) 