import json
import openai

from core import plugin_registry

with open('openai_API_key.txt', 'r') as file:
    openai.api_key = file.readline().strip()


def append_to_interaction_history(user_text, interaction_history):
    interaction_history.append({"role": "user", "content": user_text})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=interaction_history,
        functions=plugin_registry.plugin_function_docs,
        function_call="auto",
    )

    if response["choices"][0]["message"].get("function_call"):

        function_name = response["choices"][0]["message"]["function_call"]["name"]
        function_to_call = plugin_registry.plugin_function_registry[function_name]
        function_args = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
        function_response = function_to_call(**function_args)

        interaction_history.append(response["choices"][0]["message"])
        interaction_history.append({
            "role": "function",
            "name": function_name,
            "content": function_response,
        })
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=interaction_history,
        )
        return second_response["choices"][0]["message"]["content"]

    interaction_history.append(response["choices"][0]["message"])
    return response["choices"][0]["message"]["content"]