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
import time
import random
from . import __version__
from .i18n import get_message

# Log configuration
logging.basicConfig(level=logging.WARNING, format='%(message)s')
logger = logging.getLogger("aici")

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = os.getenv("OPENAI_CHATGPT_MODEL", "gpt-4o")
DEFAULT_SYSTEM = os.getenv("OPENAI_CHATGPT_SYSTEM", "You are a helpful assistant.")
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
INITIAL_RETRY_DELAY = float(os.getenv("OPENAI_INITIAL_RETRY_DELAY", "1.0"))
MAX_RETRY_DELAY = float(os.getenv("OPENAI_MAX_RETRY_DELAY", "60.0"))


def retry_with_exponential_backoff(func):
    """Decorator function to implement retry logic

    Args:
        func: Function to retry

    Returns:
        wrapper: Wrapper function implementing retry logic
    """
    def wrapper(*args, **kwargs):
        retry_count = 0
        retry_delay = INITIAL_RETRY_DELAY
        
        while True:
            try:
                return func(*args, **kwargs)
            except openai.RateLimitError as e:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    # Display user-friendly error message
                    print(f"\n{get_message('error_api_quota')}")
                    print(f"\n{get_message('solutions_header')}")
                    print(get_message('solution_check_dashboard'))
                    print(get_message('solution_check_billing'))
                    print(get_message('solution_upgrade_plan'))
                    print(get_message('solution_contact_support'))
                    # Log detailed information for debugging
                    logger.debug(f"API quota limit error details: {str(e)}", exc_info=False)
                    # Exit the program instead of re-raising the exception
                    sys.exit(1)
                
                # Add jitter to avoid collision of simultaneous requests
                jitter = random.uniform(0, 0.1) * retry_delay
                sleep_time = retry_delay + jitter
                
                # Display user-friendly message
                print(f"\n{get_message('rate_limit_retry', sleep_time=sleep_time, retry_count=retry_count, max_retries=MAX_RETRIES)}")
                time.sleep(sleep_time)
                
                # Exponential backoff with maximum value
                retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
            except Exception as e:
                # Do not retry other errors
                raise e
    
    return wrapper


@retry_with_exponential_backoff
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
        # Display user-friendly error message
        print(f"\n{get_message('error_api_connection')}")
        print(f"\n{get_message('check_internet')}")
        # Log detailed information for debugging
        logger.debug(f"Connection error details: {str(e)}", exc_info=False)
        sys.exit(1)
    except openai.RateLimitError:
        # Do nothing here as it will be handled by the retry logic
        # If maximum retries are exceeded, it will be handled within the retry logic
        raise
    except openai.APIStatusError as e:
        # Display user-friendly error message
        print(f"\n{get_message('error_api_status', status_code=e.status_code)}")
        print(f"\n{get_message('api_retry_later')}")
        # Log detailed information for debugging
        logger.debug(f"API error details: {str(e.response)}", exc_info=False)
        sys.exit(1)


def main() -> None:
    # Declare that we'll use the global variable within the function
    global MAX_RETRIES

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
        parser.add_argument(
            "-V", "--verbose", action="store_true", help="Show detailed error information (for debugging)"
        )
        parser.add_argument(
            "-o",
            "--output",
            help='output destination, "clip" for clipboard',
            default=sys.stdout,
        )
        parser.add_argument(
            "--max-retries",
            type=int,
            default=MAX_RETRIES,
            help="Maximum number of retries when API rate limit is reached",
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
            
        # Update the global MAX_RETRIES with the value specified in command line arguments
        MAX_RETRIES = args.max_retries
        
        # Configure detailed logging
        if args.verbose:
            logger.setLevel(logging.DEBUG)
            # Add a handler to output detailed logs to the console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            logger.addHandler(console_handler)
        
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
        # Display user-friendly error message
        print(f"\n{get_message('error_unexpected')}")
        print(f"\n{str(e)}")
        print(f"\n{get_message('verbose_info')}")
        # Log detailed information for debugging
        logger.debug(f"Error details: {str(e)}", exc_info=args.verbose if 'args' in locals() and hasattr(args, 'verbose') else False)
        sys.exit(1)


if __name__ == "__main__":
    main()
