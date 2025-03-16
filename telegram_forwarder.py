import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Message
from loguru import logger

from config import TelegramConfig, ForwarderConfig
from user_service import UserService
from message_repository import MessageRepository
from message_handler import MessageHandler


class TelegramForwarder:
    """Main application class for the Telegram message forwarding system."""
    
    def __init__(self, telegram_config: TelegramConfig, forwarder_config: ForwarderConfig):
        """
        Initialize the TelegramForwarder.
        
        Args:
            telegram_config: Configuration for Telegram API authentication
            forwarder_config: Configuration for message forwarding
        """
        self._telegram_config = telegram_config
        self._forwarder_config = forwarder_config
        
        # Initialize client
        self._client = TelegramClient(
            'forwarder_session',
            telegram_config.api_id,
            telegram_config.api_hash
        )
        
        # Initialize services
        self._user_service = UserService(forwarder_config.tracked_users)
        self._message_repository = None
        self._message_handler = None
    
    async def start(self):
        """Start the forwarder and begin listening for messages."""
        try:
            logger.info("Starting Telegram Forwarder")
            
            # Connect to Telegram
            await self._client.start(phone=self._telegram_config.phone_number)
            logger.info("Connected to Telegram")
            
            # Initialize repositories and handlers after client is connected
            self._message_repository = MessageRepository(
                self._client,
                self._forwarder_config.destination_chat_id,
                self._forwarder_config.source_chat_id
            )
            
            self._message_handler = MessageHandler(
                self._user_service,
                self._message_repository,
                self._forwarder_config.enable_message_links
            )
            
            # Log feature status
            if self._forwarder_config.enable_message_links:
                logger.info("Message link feature is enabled")
            else:
                logger.info("Message link feature is disabled")
            
            # Register event handlers
            self._register_event_handlers()
            
            # Keep the client running
            await self._run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Error starting Telegram Forwarder: {e}")
            raise
    
    def _register_event_handlers(self):
        """Register event handlers for the client."""
        @self._client.on(events.NewMessage(chats=[self._forwarder_config.source_chat_id]))
        async def on_new_message(event):
            """Handle new message events."""
            message: Message = event.message
            await self._message_handler.handle_message(message)
    
    async def _run_until_disconnected(self):
        """Run the client until disconnected."""
        logger.info("Listening for messages")
        await self._client.run_until_disconnected()
    
    async def stop(self):
        """Stop the forwarder and disconnect from Telegram."""
        try:
            logger.info("Stopping Telegram Forwarder")
            await self._client.disconnect()
            logger.info("Disconnected from Telegram")
        except Exception as e:
            logger.error(f"Error stopping Telegram Forwarder: {e}")
            raise 