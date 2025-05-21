from flask import Flask, request, Response, session
from twilio.twiml.voice_response import VoiceResponse
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key")  # Use a secure one in production

@app.route("/voice", methods=["POST"])
def voice():
    user_input = request.form.get('SpeechResult')
    response = VoiceResponse()

    # Initialize history if new session
    if "history" not in session:
        session["history"] = [
            {
                "role": "system",
                "content": (
                    "You're Ava, a quick and friendly voice assistant. "
                    "Speak clearly and casually like a helpful human on a phone call."
                )
            }
        ]

    if not user_input:
        # First-time interaction
        gather = response.gather(input="speech", timeout=3)
        gather.say("Hi, I'm Ava. How can I help you?", voice="Polly.Joanna")
    else:
        try:
            # Add user message to history
            session["history"].append({"role": "user", "content": user_input})

            # Trim history to last 5 messages
            history_trimmed = session["history"][-6:]

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history_trimmed,
                max_tokens=80,
                temperature=0.6,
            )

            reply = completion['choices'][0]['message']['content']
            session["history"].append({"role": "assistant", "content": reply})

            ssml_reply = f"<speak>{reply}<break time='300ms'/>Anything else?</speak>"
            gather = response.gather(input="speech", timeout=3)
            gather.say(ssml_reply, voice="Polly.Joanna", language="en-US", ssml=True)

        except Exception as e:
            response.say("Sorry, I had trouble with that. Can you say it again?", voice="Polly.Joanna")

    return Response(str(response), mimetype='application/xml')

@app.route("/", methods=["GET"])
def home():
    return "Voice bot running"

if __name__ == "__main__":
    app.run(debug=True)
