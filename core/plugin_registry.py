from plugins import gmail

# documentation supplied to GPT with each prompt
plugin_function_docs = [
    {
        "name": "send",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },

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
]

# GPT will respond with a string, this registry maps it to a function to call
plugin_function_registry = {
    "send_email": gmail.send_email
}

