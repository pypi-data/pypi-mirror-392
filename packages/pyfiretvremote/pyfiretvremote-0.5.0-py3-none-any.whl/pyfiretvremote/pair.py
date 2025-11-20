import argparse
import asyncio
import logging
import sys

from pyfiretvremote import FireTvRemote

_LOGGER = logging.getLogger(__name__)


async def async_input(string: str) -> str:
    await asyncio.to_thread(lambda: print(string, end="", flush=True))
    return (await asyncio.to_thread(sys.stdin.readline)).rstrip('\n')

async def _pair(args) -> None:
    api_key = args.api_key or ""

    async with FireTvRemote(
        friendly_name=args.client_name,
        host=args.host,
        port=args.port,
        api_key=api_key,
        client_token=""
    ) as remote:
        _LOGGER.info("Pairing")
        await remote.show_authentication_challenge()
        pin = await async_input("Please enter the pin displayed on your TV? ")
        client_token = await remote.verify_pin(pin)
        _LOGGER.info(f"Your client token is: {client_token}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", help="IP address of the Fire TV to connect to", required=True)
    parser.add_argument("--port", help="Port to connect to defaults to 8080", default=8080, type=int)
    parser.add_argument(
        "--client_name",
        help="Unique name for this pairing connection",
        default="Fire TV Remote-Pair",
    )
    parser.add_argument(
        "--api_key",
        help="The API Key to use for the connection",
        default="0987654321"
    )

    parser.add_argument(
        "-v", "--verbose", help="enable verbose logging", action="store_true"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        asyncio.run(_pair(args), debug=args.verbose)
    except Exception:
        _LOGGER.exception("An error occurred during pairing.")
        sys.exit(1)

if __name__ == "__main__":
    main()