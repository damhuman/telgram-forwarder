import asyncio
import signal
import sys
import argparse
from loguru import logger

from config import TelegramConfig, ForwarderConfig
from telegram_forwarder import TelegramForwarder


def setup_logging():
    """Configure logging settings."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/forwarder.log",
        rotation="10 MB",
        retention="1 week",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Telegram Message Forwarding System")
    
    # Add any new command-line arguments here if needed in the future
    
    return parser.parse_args()


async def main():
    """Main entry point for the application."""
    setup_logging()
    
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Load configuration
        telegram_config = TelegramConfig()
        forwarder_config = ForwarderConfig()
        
        # Message links are now always included in the formatted message format
        logger.info("Message links are now always included in the message format")
        
        # Create and start forwarder
        forwarder = TelegramForwarder(telegram_config, forwarder_config)
        
        # Handle shutdown signals
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(forwarder)))
        
        await forwarder.start()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


async def shutdown(forwarder: TelegramForwarder):
    """Gracefully shut down the application."""
    logger.info("Shutting down...")
    await forwarder.stop()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    asyncio.get_event_loop().stop()


if __name__ == "__main__":
    asyncio.run(main()) 