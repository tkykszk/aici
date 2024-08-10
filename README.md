# AICLI

a command line i/f tool for the AI like ChatGPT.

input

    - std input
    - cli parameter

output

    - std output  (streaming, beffering)
    - clipboard

Overview:
This program is a Python script that queries OpenAI’s ChatGPT model. It takes a user’s prompt as input and outputs the response from ChatGPT. The output can be directed to either standard output or the clipboard. Additionally, you can specify the model to use and set a custom system message.

Command-Line Description:

    •	prompt: The prompt for ChatGPT. If "-" is specified, it reads from standard input.
    •	-m, --model: The OpenAI model to use. The default is read from the environment variable.
    •	-c, --complete: Whether or not to retrieve the complete message. The default is False.
    •	-s, --system: Specifies the system message. The default is “You are a helpful assistant.”
    •	-o, --output: Specifies the output destination. The default is stdout, but if “clip” is specified, it outputs to the clipboard.

Config:

it can be choosen using config file or environment variable OPENAI_API_KEY

~/.aicli

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
```

On windows, it is expanded like `C:\Users\{USERNAME}\.aicli`

Examples:

input from cli

```
$ aicli Hello
```

read from stdin

```
$ echo Hello | aicli -
```

output to clipboard

```
$ echo Hello | aicli - --output clip
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
