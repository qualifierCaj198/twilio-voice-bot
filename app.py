from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    user_input = request.form.get('SpeechResult')
    response = VoiceResponse()

    if not user_input:
        gather = response.gather(input="speech", timeout=3)
        gather.say("Hi, I'm Ava. How can I help you?", voice="Polly.Joanna")
    else:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You're Ava, a quick, friendly voice assistant. "
                            "Keep replies short, casual, and clear."
                        )
                    },
                    {"role": "user", "content": user_input}
                ],
                max_tokens=80,
                temperature=0.7
            )
            reply = completion['choices'][0]['message']['content']
            ssml_reply = f"<speak>{reply}<break time='200ms'/>Anything else?</speak>"
            gather = response.gather(input="speech", timeout=3)
            gather.say(ssml_reply, voice="Polly.Joanna", language="en-US", ssml=True)

        except Exception:
            response.say("Sorry, something went wrong.", voice="Polly.Joanna")

    return Response(str(response), mimetype='application/xml')

@app.route("/", methods=["GET"])
def home():
    return "Voice bot running"

if __name__ == "__main__":
    app.run(debug=True)
