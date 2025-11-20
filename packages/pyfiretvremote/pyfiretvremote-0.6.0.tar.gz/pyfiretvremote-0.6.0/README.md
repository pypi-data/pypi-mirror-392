# pyfiretvremote

`pyfiretvremote` is an asynchronous Python library designed to provide robust control over your Amazon Fire TV devices. It allows you to send remote commands, manage applications, and handle the pairing process programmatically, making it ideal for home automation, custom remote applications, or integration into larger systems.

## Features

*   **Asynchronous Operations**: Built with `asyncio` and `httpx` for non-blocking network requests.
*   **Remote Control**: Send key presses (up, down, select, home, back, volume, etc.) and media commands (play/pause, next/previous, rewind/fast-forward).
*   **Pairing and Authentication**: Programmatically handle the pairing process with your Fire TV.
*   **Device Information**: Retrieve information about connected Fire TV devices and installed applications.
*   **Context Manager**: Use `FireTvRemote` as an asynchronous context manager for reliable connection management.

## Installation

```bash
# Installing from PyPI
$ pip install pyfiretvremote
```

## Usage

### Pairing a New Device

The easiest way to pair a new device is to use the `firetv-pair` command-line tool. After installing the package, run the following command and follow the prompts:

```bash
$ firetv-pair --host YOUR_FIRETV_IP_ADDRESS
```

The tool will display a PIN on your TV. Enter the PIN in the terminal, and the tool will print a `client_token`. Save this token for future use.

### Basic Control

Here's how to connect to your Fire TV and send a command using the `client_token` you obtained during pairing:

```python
import asyncio
from pyfiretvremote import FireTvRemote

async def main():
    # Replace with your Fire TV's IP address and your saved client token
    firetv_host = "YOUR_FIRETV_IP_ADDRESS"
    api_key = "YOUR_API_KEY" # Use the API key configured on your Fire TV
    saved_client_token = "YOUR_SAVED_CLIENT_TOKEN"

    async with FireTvRemote(
        host=firetv_host, 
        api_key=api_key, 
        client_token=saved_client_token
    ) as remote:
        print(f"Connected to Fire TV at {firetv_host}")

        # Example: Send a 'KEY_HOMEPAGE' command
        await remote.send_command("KEY_HOMEPAGE")
        print("Sent KEY_HOMEPAGE command.")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

For more advanced usage examples, including how to bind keyboard keys to remote control actions, please see the demo script in the `scripts/` directory of the project repository.

## FireTvRemote API Overview

The `FireTvRemote` class provides the following key asynchronous methods:

*   `async with FireTvRemote(...)`: Connects to the Fire TV and ensures proper disconnection.
*   `send_command(command: str, key_action_type: Optional[str] = None)`: Sends a key or media command.
    *   `command`: A string representing the key (e.g., "KEY_UP", "KEY_ENTER", "KEY_PLAYPAUSE").
    *   `key_action_type`: Optional, can be "keyDown" or "keyUp" for specific key actions.
*   `show_authentication_challenge()`: Initiates the pairing process, displaying a PIN on the Fire TV.
*   `verify_pin(pin: str)`: Verifies the entered PIN and returns a `client_token`.
*   `get_apps()`: Retrieves a list of installed applications.
*   `open_app(app_id: str)`: Opens a specific application by its ID (TODO: Phase 2).
*   `get_device_info()`: Retrieves information about the Fire TV device.
*   `get_keyboard_info()`: Retrieves keyboard-related information.
*   `open_firetv_settings()`: Opens the Fire TV settings (TODO: Phase 2).
*   `ring_remotes()`: Makes connected remotes ring.
*   `voice_command(action: str)`: Sends a voice command (TODO: Phase 2).
*   `send_keyboard_string(keyboard_text_request_body)`: Sends a string to the Fire TV keyboard (TODO).
*   `send_keyboard_text(keyboard_text_request_body)`: Sends text to the Fire TV keyboard (TODO).

## Contributing

Contributions are welcome! Please refer to the `DEVELOPMENT.md` for setup and contribution guidelines.