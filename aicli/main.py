import os
import argparse
from openai import OpenAI
import sys

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

DEFAULT_MODEL = "gpt-4-0613"
DEFAULT_SYSTEM = "You are a helpful assistant."

def query_chatgpt(prompt, complete=False, model=DEFAULT_MODEL, system=DEFAULT_SYSTEM):
    try:
        if complete == False:
            # Streaming response from OpenAI's API
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                stream=True  # Enable streaming mode
            )
        
            # Collecting and printing the streamed response
            collected_response = ""
            for chunk in stream:
                chunk_message = chunk.choices[0].delta.content or ""
                print(chunk_message, end="", flush=True)
                collected_response += chunk_message
        
            return collected_response
    
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content

    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)        
        
def main():
    parser = argparse.ArgumentParser(description="Query OpenAI's ChatGPT")
    parser.add_argument('prompt', type=str, help='The prompt to send to ChatGPT or "-" to read from stdin')
    parser.add_argument('-m', '--model', default=DEFAULT_MODEL, help='model name')
    parser.add_argument('-c', '--complete', default=False, action='store_true', help='get a message when completed')
    parser.add_argument('-s', '--system', default=DEFAULT_SYSTEM, help='spcify a system content')

    args = parser.parse_args()

    # Check if the prompt is "-" and read from stdin if so
    if args.prompt == "-":
        print("Enter your prompt: ", end="")
        prompt = sys.stdin.read().strip()
    else:
        prompt = args.prompt

    answer = query_chatgpt(prompt, model=args.model, complete=args.complete, system=args.system)

if __name__ == "__main__":
    main()

    
