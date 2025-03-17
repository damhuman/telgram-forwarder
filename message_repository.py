from typing import Optional, Tuple, Any
from telethon import TelegramClient
from telethon.tl.types import Message, User
from loguru import logger

from message_storage import MessageStorage


class MessageRepository:
    """Repository for handling Telegram message operations."""
    
    def __init__(self, client: TelegramClient, destination_chat_id: int, source_chat_id: int):
        """
        Initialize the MessageRepository.
        
        Args:
            client: An authenticated TelegramClient instance
            destination_chat_id: The ID of the chat to forward messages to
            source_chat_id: The ID of the source chat being monitored
        """
        self._client = client
        self._destination_chat_id = destination_chat_id
        self._source_chat_id = source_chat_id
        self._message_storage = MessageStorage()
    
    async def get_replied_message(self, message: Message) -> Optional[Message]:
        """
        Get the message that a message is replying to.
        
        Args:
            message: The message to check for a reply
            
        Returns:
            The replied-to message if it exists, None otherwise
        """
        if message.reply_to is None:
            return None
        
        try:
            # Get the message that this message is replying to
            replied_message = await self._client.get_messages(
                message.peer_id,
                ids=message.reply_to.reply_to_msg_id
            )
            return replied_message
        except Exception as e:
            logger.error(f"Error retrieving replied message: {e}")
            return None
    
    def _get_message_link(self, message_id: int) -> str:
        """
        Generate a link to the original message.
        
        Args:
            message_id: The ID of the message
            
        Returns:
            A link to the original message
        """
        # Format the chat ID for the link
        # For supergroups/channels, we need to remove the -100 prefix if it exists
        chat_id_for_link = str(self._source_chat_id)
        if chat_id_for_link.startswith('-100'):
            chat_id_for_link = chat_id_for_link[4:]
            
        return f"https://t.me/c/{chat_id_for_link}/{message_id}"
    
    async def get_user_identifier(self, user_id: int) -> str:
        """
        Get a user's username or ID as a string for display.
        
        Args:
            user_id: The user ID to look up
            
        Returns:
            The username without @ prefix if available, otherwise the user ID as a string
        """
        try:
            user = await self._client.get_entity(user_id)
            if user.username and user.username.strip():
                logger.info(f"Found valid username '{user.username}' for user {user_id}")
                return f"{user.username}"
            
            # Якщо username порожній або None, використовуємо ID
            logger.info(f"Username is empty or None for user {user_id}, using ID instead")
            return f"{user_id}"
        except Exception as e:
            logger.error(f"Error getting user entity: {e}")
            return f"{user_id}"
    
    async def forward_message(self, message: Message) -> Optional[Message]:
        """
        Process a message by creating a new formatted message in the destination chat.
        
        Args:
            message: The message to process
            
        Returns:
            The new message if successful, None otherwise
        """
        # Check if this message was already forwarded
        if self._message_storage.is_message_forwarded(self._source_chat_id, message.id):
            logger.info(f"Message {message.id} already forwarded, skipping")
            return None
        
        try:
            # Get user identifier (username or ID)
            user_identifier = await self.get_user_identifier(message.sender_id)
            
            # Get message link
            message_link = self._get_message_link(message.id)
            
            # Format the message with wrapped link
            formatted_text = f"#{user_identifier} - {message.text or ''} - [to_chat]({message_link})"
            
            logger.info(f"Sending formatted message with user identifier: #{user_identifier}")
            
            # Send new message
            new_message = await self._client.send_message(
                self._destination_chat_id,
                formatted_text,
                file=message.media if message.media else None,
                parse_mode='markdown'
            )
            
            # Store the mapping
            self._message_storage.add_message_mapping(
                self._source_chat_id, 
                message.id, 
                self._destination_chat_id, 
                new_message.id
            )
            
            logger.info(f"Sent formatted message for {message.id} to chat {self._destination_chat_id}")
            return new_message
            
        except Exception as e:
            logger.error(f"Error sending formatted message for {message.id}: {e}")
            return None
    
    async def forward_message_with_reply(self, message: Message, replied_message: Message) -> Tuple[Optional[Message], Optional[Message]]:
        """
        Process a message that is a reply to another message.
        
        Args:
            message: The message to process
            replied_message: The message that the original message is replying to
            
        Returns:
            A tuple containing the processed replied message and the processed original message
        """
        try:
            # Check if the replied message was already forwarded
            dest_replied_id = self._message_storage.get_destination_message_id(
                self._source_chat_id, 
                replied_message.id
            )
            
            # If not, send the replied message first
            if dest_replied_id is None:
                forwarded_replied_message = await self.forward_message(replied_message)
                if forwarded_replied_message is None:
                    # If we couldn't forward the replied message, just forward the original message
                    forwarded_message = await self.forward_message(message)
                    return None, forwarded_message
                    
                dest_replied_id = forwarded_replied_message.id
            
            # Get user identifier (username or ID)
            user_identifier = await self.get_user_identifier(message.sender_id)
            
            # Get message link
            message_link = self._get_message_link(message.id)
            
            # Format the message with wrapped link
            formatted_text = f"#{user_identifier} - {message.text or ''} - [to_chat]({message_link})"
            
            logger.info(f"Sending formatted reply with user identifier: #{user_identifier}")
            
            # Send as a reply to the forwarded replied message
            new_message = await self._client.send_message(
                self._destination_chat_id,
                formatted_text,
                file=message.media if message.media else None,
                reply_to=dest_replied_id,
                parse_mode='markdown'
            )
            
            # Store the mapping
            self._message_storage.add_message_mapping(
                self._source_chat_id, 
                message.id, 
                self._destination_chat_id, 
                new_message.id
            )
            
            logger.info(f"Sent formatted reply for message {message.id} to chat {self._destination_chat_id}")
            
            # Return the replied message ID and the new message
            return await self._client.get_messages(self._destination_chat_id, ids=dest_replied_id), new_message
            
        except Exception as e:
            logger.error(f"Error sending formatted reply for message {message.id}: {e}")
            return None, None 