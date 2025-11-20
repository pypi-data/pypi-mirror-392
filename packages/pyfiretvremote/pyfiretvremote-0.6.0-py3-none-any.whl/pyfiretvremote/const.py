KEY_DOWN = "keyDown"
KEY_UP = "keyUp"
# Omitting keyActionType from the payload is interpreted as a key press.
KEY_PRESS = None

KEY_MAPPING = {
    "KEY_UP": "dpad_up",
    "KEY_DOWN": "dpad_down",
    "KEY_LEFT": "dpad_left",
    "KEY_RIGHT": "dpad_right",
    "KEY_ENTER": "select",
    "KEY_SELECT": "select",
    "KEY_HOMEPAGE": "home",
    "KEY_BACK": "back",
    "KEY_COMPOSE": "menu",
    "KEY_BACKSPACE": "backspace",
    "KEY_VOLUMEUP": "volume_up",
    "KEY_VOLUMEDOWN": "volume_down",
}

MEDIA_KEY_MAPPING = {
    "KEY_PLAYPAUSE": ("play", None),  # pause
    "KEY_NEXTSONG": ("MEDIA_NEXT", None),
    "KEY_PREVIOUSSONG": ("MEDIA_PREVIOUS", None),
    "KEY_REWIND": (
        "scan",
        {
            "speed": 1,
            "durationInSeconds": 10,
            "direction": "backward"
        }
    ),
    "KEY_FASTFORWARD": (
        "scan",
        {
            "speed": 1,
            "durationInSeconds": 10,
            "direction": "forward"
        }
    ),
}
