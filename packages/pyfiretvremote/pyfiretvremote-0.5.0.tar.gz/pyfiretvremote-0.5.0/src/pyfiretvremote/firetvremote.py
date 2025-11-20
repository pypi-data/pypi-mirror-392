import httpx
import logging
from .const import KEY_MAPPING, MEDIA_KEY_MAPPING

_LOGGER = logging.getLogger(__name__)


class FireTvRemote:

    # client: httpx.AsyncClient | None

    def __init__(self, friendly_name, host, port=8080, api_key="", client_token=""):
        self.host = host
        self.port = port
        self.base_url = f"https://{host}:{port}"
        self.friendly_name = friendly_name
        self.headers = {
            "x-api-key": api_key
        }
        if client_token:
            self.headers["x-client-token"] = client_token
        self._verify = False  # Fire TV uses self-signed certificates, so SSL verification is disabled.
        self.client = None

    async def __aenter__(self):
        """Connect to the Fire TV."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from the Fire TV."""
        await self.disconnect()

    async def send_command(self, command, key_action_type=None):
        if command in KEY_MAPPING:
            await self._key_command(KEY_MAPPING[command], key_action_type=key_action_type)
        elif command in MEDIA_KEY_MAPPING:
            await self._media_command(MEDIA_KEY_MAPPING[command], key_action_type=key_action_type)
        else:
            _LOGGER.warning(f"Unrecognised command {command}")

    async def _key_command(self, action, key_action_type=None):
        url = f"{self.base_url}/v1/FireTV?action={action}"
        payload = None
        if key_action_type:
            payload = {
                "keyActionType": key_action_type
            }
        response = await self._post(url, payload)
        _LOGGER.debug(f"{response}")

    async def _media_command(self, media_command, key_action_type=None, body=None):
        action, payload = media_command
        url = f"{self.base_url}/v1/media?action={action}"
        if key_action_type:
            if payload:
                payload["keyAction"] = {
                    "keyActionType": key_action_type
                }
            else:
                payload = {
                    "keyActionType": key_action_type
                }
        response = await self._post(url, payload)
        _LOGGER.debug(f"{response}")

    async def connect(self):
        if not self.client:
            self.client = httpx.AsyncClient(
                verify=self._verify
            )

    async def disconnect(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def send_keyboard_string(self, keyboard_text_request_body):
        # TODO implement this
        url = f"{self.base_url}/v1/FireTV/keyboard"

    async def send_keyboard_text(self, keyboard_text_request_body):
        # TODO implement this
        url = f"{self.base_url}/v1/FireTV/text"

    async def show_authentication_challenge(self):
        url = f"{self.base_url}/v1/FireTV/pin/display"
        payload = {
            "friendlyName": self.friendly_name
        }
        response = await self._post(
            url,
            payload,
        )

    async def verify_pin(self, pin):
        url = f"{self.base_url}/v1/FireTV/pin/verify"
        payload = {
            "pin": pin
        }
        response_as_json = await self._post(
            url,
            payload
        )
        client_token = response_as_json["description"]
        self.headers["x-client-token"] = client_token
        return client_token

    async def get_apps(self):
        url = f"{self.base_url}/v1/FireTV/apps"
        response = await self._get(url)

    async def open_app(self, app_id):
        # TODO implement this - phase 2
        url = f"{self.base_url}/v1/FireTV/app/{app_id}"

    async def get_device_info(self):
        url = f"{self.base_url}/v1/FireTV"
        response = await self._get(url)

    async def get_keyboard_info(self):
        url = f"{self.base_url}/v1/FireTV/keyboard"
        response = await self._get(url)

    async def open_firetv_settings(self):
        # Phase 2
        url = f"{self.base_url}/v1/FireTV/app/settings"
        response = await self._post(url)

    async def ring_remotes(self):
        url = f"{self.base_url}/v1/FireTV/ringRemotes"
        response = await self._post(url)

    async def voice_command(self, action):
        # TODO implement this - phase 2
        url = f"{self.base_url}/v1/FireTV/voiceCommand"

    async def _get(self, url):
        try:
            response = await self.client.get(
                headers=self.headers,
                url=url,
            )
            response.raise_for_status()
            response_as_json = response.json()
            _LOGGER.debug(response_as_json)
            return response_as_json
        except httpx.ConnectError as exc:
            _LOGGER.error(f"Connection error to {exc.request.url!r}: {exc}")
            raise
        except httpx.TimeoutException as exc:
            _LOGGER.error(f"Timeout error for {exc.request.url!r}: {exc}")
            raise
        except httpx.HTTPStatusError as exc:
            _LOGGER.error(f"HTTP status error for {exc.request.url!r}: {exc.response.status_code} - {exc.response.text}")
            raise
        except Exception:
            _LOGGER.exception("An unexpected error occurred during GET request")
            raise

    async def _post(self, url, payload=None):
        try:
            response = await self.client.post(
                headers=self.headers,
                url=url,
                json=payload,
            )
            response.raise_for_status()
            response_as_json = response.json()
            _LOGGER.debug(response_as_json)
            return response_as_json
        except httpx.ConnectError as exc:
            _LOGGER.error(f"Connection error to {exc.request.url!r}: {exc}")
            raise
        except httpx.TimeoutException as exc:
            _LOGGER.error(f"Timeout error for {exc.request.url!r}: {exc}")
            raise
        except httpx.HTTPStatusError as exc:
            _LOGGER.error(f"HTTP status error for {exc.request.url!r}: {exc.response.status_code} - {exc.response.text}")
            raise
        except Exception:
            _LOGGER.exception("An unexpected error occurred during POST request")
            raise
