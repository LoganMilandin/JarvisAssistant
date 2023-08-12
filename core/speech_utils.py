import azure.cognitiveservices.speech as speechsdk


with open('Azure_api_key.txt', 'r') as file:
    azure_api_key = file.readline().strip()

region = "eastus"
speech_config = speechsdk.SpeechConfig(subscription=azure_api_key, region=region)
speech_config.speech_synthesis_voice_name='en-GB-EthanNeural'
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)


speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


def get_user_speech():

    got_whole_speech = False
    speech = ""
    def recognized_cb(evt):

        nonlocal speech
        speech += f" {evt.result.text}"
        if "long input" not in speech.lower() or "thank you" in evt.result.text.lower():
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