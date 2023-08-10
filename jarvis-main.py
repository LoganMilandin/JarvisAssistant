from core import speech_utils
from core import gpt_interaction

# Initialize the conversation history
messages = [{"role": "system", "content": "You are an assistant designed to emulate Tony Stark's assistant Jarvis. You should treat the user as if they're Tony Stark."}]
keyword_required = True

while True:
    # if the keyword is required, listen for it
    if keyword_required:
        speech_utils.wait_for_keyphrase()
    speech = speech_utils.get_user_speech()
    response_text = gpt_interaction.append_to_interaction_history(speech, messages)
    speech_utils.speak_response(response_text)



