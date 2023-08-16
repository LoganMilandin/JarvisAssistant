from plugins import gmail
from plugins import shell

# documentation supplied to GPT with each prompt
plugin_function_docs = [
    {
        "name": "send_email",
        "description": "Send an email to given email address. You should only use this if the user specifically asks you to send an email. The email will be encoded as HTML, not plaintext, so you should include appropriate tags for newlines and other formatting.",
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject of the email",
                },
                "content": {
                    "type": "string",
                    "description": "The email address of the recipient",
                },
                "recipient": {
                    "type": "string",
                    "description": "The email address of the recipient",
                },
                "attachments": {
                    "type": "string",
                    "description": "A comma-separated list of paths to files to attach to the email",
                }
            },
            "required": ["subject", "content", "recipient", "attachments"],
        },
    },

    {
        "name": "shell",
        "description": "Execute a shell command and return the output. The shell is a persistent process started with /bin/bash, so you can use shell variables and other shell features.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                }
            }
        },
        "required": ["command"]
    }
]

# GPT will respond with a string, this registry maps it to a function to call
plugin_function_registry = {
    "send_email": gmail.send_email,
    "shell": shell.execute_command_and_get_output,
}

