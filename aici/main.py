"""
aici  CLI for AI

This module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

Functions:
    def query_chatgpt(prompt:str, complete:bool=False, model:str=DEFAULT_MODEL, 
                  system:str=DEFAULT_SYSTEM, output=sys.stdout) -> None:

    def main() -> None:

Examples:
    >>> sys.argv = ['/path/to/aici', 'Hello']
    >>> aici.main()
    Hello! How can I assist you today

"""

import os
import io
import sys
import argparse
import openai
from openai import OpenAI
import pyperclip
import logging
from . import __version__

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("aici")

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = os.getenv("OPENAI_CHATGPT_MODEL", "gpt-4o")
DEFAULT_SYSTEM = os.getenv("OPENAI_CHATGPT_SYSTEM", "You are a helpful assistant.")


def query_chatgpt(
    prompt: str,
    complete: bool = False,
    model: str = DEFAULT_MODEL,
    system: str = DEFAULT_SYSTEM,
    output=sys.stdout,
) -> None:
    """Sends a prompt to the OpenAI ChatGPT API and handles the response, either streaming or complete.

    Args:
        prompt (str): The prompt to send to the ChatGPT API.
        complete (bool): If False, the response will be streamed; if True, the complete response will be retrieved at once. Default is False.
        model (str): The model name to use for the API call. Default is set to the module's DEFAULT_MODEL.
        system (str): The system message to send as context to the API. Default is set to the module's DEFAULT_SYSTEM.
        output (file-like object): The output stream where the response will be written. Default is sys.stdout.

    Returns:
        None: This function doesn't return a value, but it prints the API response to the specified output stream.

    Raises:
        openai.APIConnectionError: If the server could not be reached.
        openai.RateLimitError: If the API rate limit is exceeded (429 status code).
        openai.APIStatusError: If any other non-200-range status code is received.
    """

    try:
        if complete == False:
            # Streaming response from OpenAI's API
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                stream=True,  # Enable streaming mode
            )

            # Collecting and printing the streamed response
            collected_response = ""
            for chunk in stream:
                chunk_message = chunk.choices[0].delta.content or ""
                print(chunk_message, end="", flush=True, file=output)
                collected_response += chunk_message

            print()  # Print a newline at the end
            return collected_response
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            # Print a newline at the end
            print(response.choices[0].message.content, flush=True, file=output)

    except openai.APIConnectionError as e:
        logger.error("The server could not be reached", exc_info=e)
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except openai.RateLimitError as e:
        logger.error(
            "A 429 status code was received; we should back off a bit.", exc_info=e
        )
    except openai.APIStatusError as e:
        logger.error("Another non-200-range status code was received", exc_info=e)
        print(e.status_code)
        print(e.response)


def main() -> None:

    try:
        parser = argparse.ArgumentParser(description="Query OpenAI's ChatGPT")
        parser.add_argument(
            "prompt",
            type=str,
            nargs="?",
            default=argparse.SUPPRESS,
            help='The prompt to send to ChatGPT or "-" to read from stdin',
        )
        parser.add_argument(
            "-v", "--version", action="store_true", help="Show version and exit"
        )
        parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="model name")
        parser.add_argument(
            "-c",
            "--complete",
            default=False,
            action="store_true",
            help="get a message when completed",
        )
        parser.add_argument(
            "-s", "--system", default=DEFAULT_SYSTEM, help="spcify a system content"
        )
        parser.add_argument("-V", "--VERBOSE", help="spcify a verbose output")
        parser.add_argument(
            "-o",
            "--output",
            help='output destination, "clip" for clipboard',
            default=sys.stdout,
        )
        args = parser.parse_args()

        if args.version:
            print(__version__)
            sys.exit(0)

        # Check if 'prompt' exists and is not None
        if getattr(args, "prompt", None) is None or args.prompt is None:
            parser.error("the following arguments are required: prompt")

        # Check if the prompt is "-" and read from stdin if so
        if args.prompt == "-":
            prompt = sys.stdin.read().strip()
        else:
            prompt = args.prompt

        if args.output == "clip" or args.output == "clipboard":
            buffer = io.StringIO()
        else:
            buffer = sys.stdout

        query_chatgpt(
            prompt,
            model=args.model,
            complete=args.complete,
            system=args.system,
            output=buffer,
        )

        if args.output == "clip" or args.output == "clipboard":
            pyperclip.copy(buffer.getvalue())

    except Exception as e:
        logger.error(f"Error", exc_info=e)
        raise Exception(f"Error: {e}")


if __name__ == "__main__":
    main()
