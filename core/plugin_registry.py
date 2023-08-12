from plugins import gmail
from plugins import shell

# documentation supplied to GPT with each prompt
plugin_function_docs = [
    {
        "name": "send_email",
        "description": "Send an email to given email address",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "The email address of the recipient",
                }
            },
            "required": ["person"],
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
        }
    }
]

# GPT will respond with a string, this registry maps it to a function to call
plugin_function_registry = {
    "send_email": gmail.send_email,
    "shell": shell.execute_command_and_get_output,
}

