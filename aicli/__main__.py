from .main import query_chatgpt
from argparse import ArgumentParser

parser = ArgumentParser(description="Query OpenAI's ChatGPT")
parser.add_argument('prompt', type=str, help='The prompt to send to ChatGPT')

args = parser.parse_args()

prompt = args.prompt
answer = query_chatgpt(prompt)
print(answer)


