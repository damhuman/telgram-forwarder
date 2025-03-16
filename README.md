# Telegram Message Forwarding System

A Python application that monitors a Telegram chat for messages from specific users and sends them to another chat in a formatted way.

## Features

- Monitor a specified Telegram chat for new messages
- Track messages from specific users and send them to a destination chat
- Messages are sent in a formatted way: `#username - message content - [to_chat]` (where "to_chat" is a link to the original message)
- Avoid duplicate messages by tracking previously processed messages
- Properly handle replies using the reply functionality in the destination chat
- Include media content from the original messages
- Proper error handling and logging
- Follows SOLID principles and KISS methodology

## Requirements

- Python 3.7+
- Telethon library
- Telegram API credentials (API ID, API Hash)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd telegram-forwarder
   ```

2. Create and activate a virtual environment:
   ```
   # On Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update it with your settings:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file and add your Telegram API credentials, chat IDs, and tracked users.

## Configuration

Create a `.env` file in the root directory with the following content:

```
# Telegram API credentials
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number

# Chat IDs
SOURCE_CHAT_ID=-10012345678  # ID of the chat to monitor
DESTINATION_CHAT_ID=-10087654321  # ID of the chat to forward messages to

# Users to track (comma-separated list of Telegram user IDs)
TRACKED_USERS=123456789,987654321

# Feature toggles
ENABLE_MESSAGE_LINKS=true  # This setting is now deprecated as links are always included in the message format
```

### How to get Telegram API credentials

1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Click on "API development tools"
4. Create a new application
5. Copy the API ID and API Hash

### How to get chat IDs and user IDs

You can use services like @username_to_id_bot on Telegram or use tools like https://github.com/Pyrogram/ID-Bot to get chat and user IDs.

## Usage

Run the forwarder with:

```
python main.py
```

The first time you run the application, you'll need to authenticate with Telegram. Follow the prompts to enter the verification code sent to your Telegram account.

When you're done using the application, you can deactivate the virtual environment by running:

```
# On any operating system
deactivate
```

## Running as a Service

To run the forwarder as a service on a Linux system using systemd, create a systemd service file:

```
[Unit]
Description=Telegram Message Forwarder
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/path/to/telegram-forwarder
ExecStart=/usr/bin/python3 /path/to/telegram-forwarder/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save this file to `/etc/systemd/system/telegram-forwarder.service`, then enable and start the service:

```
sudo systemctl enable telegram-forwarder
sudo systemctl start telegram-forwarder
```

## License

MIT

## Disclaimer

This project is for educational purposes only. Make sure to comply with Telegram's Terms of Service when using this application. 