import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

class TelegramConfig:
    """Configuration for Telegram API authentication."""
    
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.phone_number = os.getenv('PHONE_NUMBER')
        
        # Validate required fields
        if not all([self.api_id, self.api_hash, self.phone_number]):
            raise ValueError("API_ID, API_HASH, and PHONE_NUMBER must be provided")
        
        # Convert API_ID to integer
        try:
            self.api_id = int(self.api_id)
        except ValueError:
            raise ValueError("API_ID must be an integer")


class ForwarderConfig:
    """Configuration for message forwarding functionality."""
    
    def __init__(self):
        self.source_chat_id = os.getenv('SOURCE_CHAT_ID')
        self.destination_chat_id = os.getenv('DESTINATION_CHAT_ID')
        tracked_users = os.getenv('TRACKED_USERS', '')
        enable_message_links = os.getenv('ENABLE_MESSAGE_LINKS', 'true').lower()
        
        # Validate required fields
        if not all([self.source_chat_id, self.destination_chat_id]):
            raise ValueError("SOURCE_CHAT_ID and DESTINATION_CHAT_ID must be provided")
        
        # Convert chat IDs to integer
        try:
            self.source_chat_id = int(self.source_chat_id)
            self.destination_chat_id = int(self.destination_chat_id)
        except ValueError:
            raise ValueError("Chat IDs must be integers")
        
        # Parse tracked users
        self.tracked_users: List[int] = []
        if tracked_users:
            try:
                self.tracked_users = [int(user_id.strip()) for user_id in tracked_users.split(',')]
            except ValueError:
                raise ValueError("TRACKED_USERS must be a comma-separated list of integers")
        
        # Parse feature toggles
        self.enable_message_links = enable_message_links in ('true', 'yes', '1', 'on') 