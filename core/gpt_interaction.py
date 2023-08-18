import json
import time
import re
import openai

from core import plugin_registry
from core import speech_utils

with open('openai_API_key.txt', 'r') as file:
    openai.api_key = file.readline().strip()

def sentence_stream_from_token_stream(response_stream):
    def find_sentence_end(buffer):
        # Identify potential sentence-ending positions
        positions = [buffer.find(p) for p in ['. ', '! ', '? ']]
        
        # Filter out positions that are either -1 or have a space right before them
        valid_positions = [pos for pos in positions if pos > 0 and buffer[pos-1] != ' ']
        
        return min(valid_positions) if valid_positions else -1

    buffer = ''
    chunk = next(response_stream)
    while chunk["choices"][0]["delta"].get("function_call") is not None:
        buffer += chunk["choices"][0]["delta"]["function_call"]["arguments"]
        first_end = find_sentence_end(buffer)

        while first_end != -1:
            sentence = buffer[:first_end+1].strip()  # +1 to include the punctuation
            # hack to remove the JSON mess that comes before the actual sentence
            json_start = "\"message\": \""
            if json_start in sentence:
                sentence = sentence[sentence.index(json_start)+len(json_start):]
            yield sentence

            # Remove the processed part from the buffer
            buffer = buffer[first_end+2:].strip()  # +2 to move past the punctuation and space

            # Find the next valid pattern match in the remaining buffer
            first_end = find_sentence_end(buffer)
        chunk = next(response_stream)

    # If there's anything left in the buffer after all tokens are processed, yield it too
    if buffer:
        # more hacky mess to remove JSON at the end. This is a little tricker than above because
        # the formatting is inconsistent and we need to match the whole terminating string, not just the "message" part
        json_end = r'["\']\s*\}'
        match = re.search(json_end, buffer)
        if match:
            buffer = buffer[:match.start()]
        yield buffer

def speak_streamed_response(response_stream):
    sentence_stream = sentence_stream_from_token_stream(response_stream)
    sentences = []
    for sentence in sentence_stream:
        speech_utils.speak_response(sentence)
        sentences.append(sentence)
    return " ".join(sentences)

def send_message_and_handle_response(user_text, interaction_history):
    model = "gpt-4"
    interaction_history.append({"role": "user", "content": user_text})

    token_stream = openai.ChatCompletion.create(
        model=model,
        messages=interaction_history,
        functions=plugin_registry.plugin_function_docs,
        function_call="auto",
        temperature=0,
        stream=True
    )

    message = ""
    chunk = next(token_stream)
    # sometimes non-null responses contain empty content. So explicitly check for None
    while chunk["choices"][0]["delta"].get("content") is not None:
        message += chunk["choices"][0]["delta"]["content"] 
        print(chunk["choices"][0]["delta"]["content"] , end="", flush=True)
        chunk = next(token_stream)

    # TODO: handle this more elegantly
    if chunk["choices"][0].get("finish_reason"):
        print("ERROR: DID NOT CALL A FUNCTION")

    # at this point we should be looking at the first chunk of the function call,
    # which always contains the full name of the function being called
    function_name = chunk["choices"][0]["delta"]["function_call"]["name"]

    interaction = {
        "role": "assistant",
        "content": message if message else None,
        "function_call": {
            "name": function_name,
        }
    }
    if function_name == "respond":
        full_response = speak_streamed_response(token_stream)
        interaction["function_call"]["arguments"] = json.dumps({"message": full_response})
    else:
        pass
        #handle regular function call


    interaction_history.append(interaction)
    return function_name == "respond"

def work_autonomously_until_done(user_text, interaction_history):
    responded_to_user = False
    while not responded_to_user:
        responded_to_user = send_message_and_handle_response(user_text, interaction_history)




    # while response["choices"][0]["message"].get("function_call"):

    #     function_name = response["choices"][0]["message"]["function_call"]["name"]
    #     if function_name not in plugin_registry.plugin_function_registry:
    #         break
    #     function_to_call = plugin_registry.plugin_function_registry[function_name]
    #     function_args = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
    #     function_response = function_to_call(**function_args)

    #     interaction_history.append(response["choices"][0]["message"])
    #     interaction_history.append({
    #         "role": "function",
    #         "name": function_name,
    #         "content": function_response,
    #     })
    #     response = openai.ChatCompletion.create(
    #         model=model,
    #         messages=interaction_history,
    #         functions=plugin_registry.plugin_function_docs,
    #         function_call="auto",
    #         temperature=0
    #     )
    #     # print("MESSAGE:")
    #     # print(second_response["choices"][0]["message"])
    #     # interaction_history.append(second_response["choices"][0]["message"])
    #     # return second_response["choices"][0]["message"]["content"]

    # interaction_history.append(response["choices"][0]["message"])
    # return response["choices"][0]["message"]["content"]