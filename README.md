# aici 🚀

[![PyPI version](https://img.shields.io/pypi/v/aici.svg)](https://pypi.org/project/aici/) [![Python Versions](https://img.shields.io/pypi/pyversions/aici.svg)](https://pypi.org/project/aici/) [![License](https://img.shields.io/pypi/l/aici.svg)](https://opensource.org/licenses/MIT)

A command line interface tool for AI models like OpenAI's ChatGPT and DeepSeek AI. 🤖💬

Use Case: would like to use AI models with editors like Emacs and/or automated tools.

![commandline](images/aicissv.webp)

![emacs](images/aiciemacsssv.webp)

# 📦 Installation:

`pip install aici`

# 📖 Overview:

This program is based on Python🐍 that queries AI models from OpenAI or DeepSeek. It takes a user's prompt as input and outputs the response from the selected AI model. The output can be directed to either standard output or the clipboard📋. Additionally, you can specify the model to use and set a custom system message either directly or from a file.

# 💻 Command-Line Description:

| Argument       | env val               | Default                      | Type | Description                                               |
| -------------- | --------------------- | ---------------------------- | ---- | --------------------------------------------------------- |
| -v, --version  |                       | -                            |      | Show version and exit                                     |
| prompt         |                       | -                            | str  | The prompt to send to the AI or "-" to read from stdin    |
| -m, --model    | AICI_MODEL            | gpt-3.5-turbo                | str  | Model name to use (e.g. gpt-3.5-turbo, gpt-4, gpt-4o, deepseek-chat) |
| -c, --complete |                       | False (default streaming)    | bool | Get a complete response at once instead of streaming      |
| -s, --system   | AICI_SYSTEM           | You are a helpful assistant. | str  | Specify a system message                                  |
| -sf, --system-file | AICI_SYSTEM_FILE   | -                            | str  | Specify a file containing the system message              |
| -V, --VERBOSE  |                       | False                        | bool | Show detailed debug information                           |
| -o, --output   |                       | stdout                       | str  | Output destination, "clip" for clipboard                  |

[OpenAI models documentation](https://platform.openai.com/docs/models)
[DeepSeek models documentation](https://platform.deepseek.com/api)

## 📥 input

💻 std input
💬 command parameter

## 📤output

💻 std output (streaming, beffering)
📋 clipboard

# 🔧 Config Environment Variables or File:

🔑 API keys can be set using environment variables or config files

## Environment Variables

```
# OpenAI API Key (either one can be used)
set AICI_OPENAI_KEY=sk-xxxxxxxxxxxxxxxxx
set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx

# DeepSeek API Key (either one can be used)
set AICI_DEEPSEEK_KEY=sk-xxxxxxxxxxxxxxxxx
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxx

# Model Selection
set AICI_MODEL=gpt-4o                # General model selection
set AICI_OPENAI_MODEL=gpt-4o         # OpenAI specific model
set AICI_DEEPSEEK_MODEL=deepseek-chat # DeepSeek specific model

# System Message
set AICI_SYSTEM="You are a helpful assistant."
set AICI_SYSTEM_FILE=~/path/to/system_message.txt
```

## Config Files

It will check the files in the following locations (in the order listed below).
~/.config/aici/config ~/.aici

```
# API Keys
AICI_OPENAI_KEY=sk-xxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
AICI_DEEPSEEK_KEY=sk-xxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxx

# Model Selection
AICI_MODEL=gpt-4o
AICI_OPENAI_MODEL=gpt-4o
AICI_DEEPSEEK_MODEL=deepseek-chat

# System Message
AICI_SYSTEM=You are a helpful assistant.
AICI_SYSTEM_FILE=~/path/to/system_message.txt
```

🖥️ On Windows file path, it is expanded like
| File path| Windows Specific|
|--------------------------------------------------|:--:|
| `C:\Users\{USERNAME}\AppData\Local\aici\config` |✔ |
| `C:\Users\{USERNAME}\AppData\Roaming\aici\config`|✔ |
| `C:\Users\{USERNAME}\.config\aici\config` | |
|`C:\Users\{USERNAME}\.aici` | |
(The priority of the applied config files is in the order listed from top to bottom.)

# 👋 Examples:

💨 Basic input from CLI

```
$ aici Hello
```

💨 Read from stdin

```
$ echo Hello | aici -
```

💨 Specify a model

```
$ aici -mgpt-4o "What's the weather like today?"
$ aici -mdeepseek-chat "Tell me about quantum computing"
```

💨 Use a system message from a file

```
$ echo "You are a helpful coding assistant." > system.txt
$ aici -sf system.txt "How do I write a Python function?"
```

💨 Enable debug mode

```
$ aici -V "Hello there"
```

## 🔄 Advanced Input Formats

## JSON Input Format

Aici supports advanced input formats through stdin, allowing you to provide conversation context and complex prompts using JSON. When using the `-` parameter to read from stdin, aici will automatically detect if the input is JSON and process it accordingly.

### JSON Conversation Format

You can provide a complete conversation context using the following JSON format:

```json
{
  "prompts": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
    {"role": "user", "content": "Tell me a joke."}
  ]
}
```

Each prompt in the array should contain a `role` and `content` field. The supported roles are:

- `system`: Sets the system instructions for the AI
- `user`: Represents messages from the user
- `assistant`: Represents previous responses from the AI

### Alternative JSON Format

For convenience, aici also supports an alternative format where the role is implied by the key name:

```json
{
  "prompts": [
    {"system": "You are a helpful assistant."},
    {"user": "Hello, how are you?"},
    {"assistant": "I'm doing well, thank you for asking!"},
    {"user": "Tell me a joke."}
  ]
}
```

### How JSON Input is Processed

When a JSON input is detected:

1. If the JSON contains a `prompts` array, aici will extract the conversation context
2. System messages are used to set the system instructions
3. The last user message is used as the primary prompt
4. All messages are preserved in the conversation context
5. The AI response will consider the entire conversation history

### Example Usage

```bash
# Using a JSON file with conversation context
$ cat conversation.json | aici -

# Creating a JSON conversation inline
$ echo '{"prompts": [{"system": "You are a helpful assistant."}, {"user": "Tell me a joke about programming."}]}' | aici -
```

### Fallback Behavior

If the input starts with `{` and ends with `}` but cannot be parsed as valid JSON, or if the JSON doesn't contain the expected structure, aici will treat the entire input as plain text.

💨 output to clipboard 📋

```
$ echo Hello | aici - --output clip
```

# 👋 emacs

## Emacs Lisp Code Example

Below is the content of `emacs/aici.el`

```elisp

(defun aici-call ()
  "Send selected region or prompt for input if no region is selected to the 'aici' command and insert the output in real-time."
  (interactive)
  (let* ((text (if (use-region-p)
                   (buffer-substring-no-properties (region-beginning) (region-end))
                 (read-string "Enter text: ")))
         ;; Attempt to create or get the output buffer
         (output-buffer (get-buffer-create "*AICI Output*")))

    ;; Check if the buffer creation was successful
    (if (not output-buffer)
        (error "Failed to create or access the output buffer")
      ;; Clear the output buffer
      (with-current-buffer output-buffer
        (erase-buffer)
        ;; Set the buffer to markdown-mode
        (markdown-mode))

      ;; Display a message indicating that processing is ongoing
      (message "Processing...")

      ;; Start the process and stream the output to the buffer
      (let ((process (start-process "aici-process" output-buffer "sh" "-c"
                                    (format "echo %s | aici -" (shell-quote-argument text)))))
        ;; Set a process filter to handle output streaming
        (set-process-filter process
                            (lambda (proc output)
                              ;; Explicitly reference the output-buffer by capturing it in the lambda
                              (let ((buffer (process-buffer proc)))
                                (when (buffer-live-p buffer)
                                  (with-current-buffer buffer
                                    (goto-char (point-max))
                                    (insert output)
                                    ;; Optionally display the buffer in real-time
                                    (display-buffer buffer))))))

        ;; Set a sentinel to handle process completion
        (set-process-sentinel process
                              (lambda (proc event)
                                ;; Again, ensure that output-buffer is properly referenced
                                (let ((buffer (process-buffer proc)))
                                  (when (buffer-live-p buffer)
                                    (if (string= event "finished\n")
                                        (message "Processing complete.")
                                      (message "Processing interrupted: %s" event))))))))

      ;; Ensure the output buffer is displayed after starting the process
      (display-buffer output-buffer)))

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
