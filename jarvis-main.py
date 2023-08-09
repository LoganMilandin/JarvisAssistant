import json
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import openai
import os
import azure.cognitiveservices.speech as speechsdk
import time


with open('openai_API_key.txt', 'r') as file:
    openai.api_key = file.readline().strip()
with open('Azure_api_key.txt', 'r') as file:
    azure_api_key = file.readline().strip()

region = "eastus"
speech_config = speechsdk.SpeechConfig(subscription=azure_api_key, region=region)
speech_config.speech_synthesis_voice_name='en-GB-EthanNeural'
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)


speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


# mock function
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)

def get_license_plate(person):
    license_plates = {"logan": "AWP7813"}
    return license_plates[person.lower()]

def get_email(person):
    emails = {"amrit": "amrit@banga.us"}
    return emails[person.lower()]

def append_to_conversation(text, messages):
    functions = [
        {
            "name": "get_current_weather",
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
            "name": "get_license_plate",
            "description": "Get the license plate of a given person",
            "parameters": {
                "type": "object",
                "properties": {
                    "person": {
                        "type": "string",
                        "description": "The name of the person",
                    }
                },
                "required": ["person"],
            },
        },

        {
            "name": "get_email",
            "description": "Get the email of a given person",
            "parameters": {
                "type": "object",
                "properties": {
                    "person": {
                        "type": "string",
                        "description": "The name of the person",
                    },
                },
                "required": ["person"]
            }
        }
    ]
    messages.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )

    if response["choices"][0]["message"].get("function_call"):
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_license_plate": get_license_plate,
            "get_email": get_email,
        }
        function_name = response["choices"][0]["message"]["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
        function_response = function_to_call(**function_args)

        messages.append(response["choices"][0]["message"])
        messages.append({
            "role": "function",
            "name": function_name,
            "content": function_response,
        })
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )
        return second_response["choices"][0]["message"]["content"], messages

    messages.append(response["choices"][0]["message"])
    return response["choices"][0]["message"]["content"], messages


def get_user_speech():

    got_whole_speech = False
    speech = ""
    def recognized_cb(evt):

        nonlocal speech
        speech += f" {evt.result.text}"
        if "long input" not in speech or "thank you" in evt.result.text.lower():
            nonlocal got_whole_speech
            got_whole_speech = True

    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.canceled.connect(lambda evt: print(f"CANCELED: {evt.reason}"))

    try:
        speech_recognizer.start_continuous_recognition()
        while not got_whole_speech:
            pass
        speech_recognizer.stop_continuous_recognition()
    except KeyboardInterrupt:
        speech_recognizer.stop_continuous_recognition()
    print(speech)
    return speech


def wait_for_keyphrase():
    """runs keyword spotting locally, with direct access to the result audio"""

    model = speechsdk.KeywordRecognitionModel("449eacf4-d6ff-4032-91b7-6723a303463a.table")
    # Create a local keyword recognizer with the default microphone device for input.
    keyword_recognizer = speechsdk.KeywordRecognizer()

    print("waiting for keyword")
    result_future = keyword_recognizer.recognize_once_async(model)
    result = result_future.get()
    print("recognized keyword")

    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        result_stream = speechsdk.AudioDataStream(result)
        result_stream.detach_input() # stop any more data from input getting to the stream

def speak_response(response_text):
    speech_synthesis_result = speech_synthesizer.speak_text_async(response_text).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(response_text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")




# Initialize the conversation history
messages = [{"role": "system", "content": "You are an assistant designed to emulate Tony Stark's assistant Jarvis. You should treat the user as if they're Tony Stark."}]

keyword_required = True

while True:
    # if the keyword is required, listen for it
    if keyword_required:
        wait_for_keyphrase()
    speech = get_user_speech()
    response_text, messages = append_to_conversation(speech, messages)
    speak_response(response_text)
#     print(response_text)
#     speak(response_text)



