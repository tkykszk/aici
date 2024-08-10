# aici 🚀

a command line i/f tool for the AI like ChatGPT. 🤖💬

Use Case: would like to use ChatGPT with editors and tools like Emacs.

# 📦 Installation:

`pip install aici`

## 📥 input

💻 std input
💬 command parameter

## 📤output

💻 std output (streaming, beffering)
📋 clipboard

# 📖 Overview:

This program is a Python script 🐍 that queries OpenAI’s ChatGPT model. It takes a user’s prompt as input and outputs the response from ChatGPT. The output can be directed to either standard output or the clipboard ✂️. Additionally, you can specify the model to use and set a custom system message .

# 💻 Command-Line Description:

prompt: The prompt for ChatGPT. If "-" is specified, it reads from standard input.
-m, --model: The OpenAI model to use. The default is read from the environment variable.
-c, --complete: Whether or not to retrieve the complete message. The default is False 🚫.
-s, --system: Specifies the system message. The default is “You are a helpful assistant.” 👍.
-o, --output: Specifies the output destination 🏁. The default is stdout, but if “clip” is specified, it outputs to the clipboard 🗒️.

# 🔧 Config Environment Variables or File:

🔑 it can be chosen using environment variable OPENAI_API_KEY or config file

```
set OPENAI_API_KEY sk-xxxxxxxxxxxxxxxxx
```

~/.aici

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
```

🖥️ On windows file path, it is expanded like `C:\Users\{USERNAME}\.aici`

# 👋 Examples:

💨 input from cli

```
$ aici Hello
```

💨 read from stdin

```
$ echo Hello | aici -
```

💨 output to clipboard 📋

```
$ echo Hello | aici - --output clip
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) ✅ file for details.
