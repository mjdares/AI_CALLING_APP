import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai  # Import OpenAI library
from dotenv import load_dotenv

# Load API Keys
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/twilio", methods=["POST"])
def twilio_webhook():
    """Handles Twilio Calls through ElevenLabs Webhook"""
    response = VoiceResponse()

    # Enable Twilio speech recognition and loop conversation
    response.gather(input="speech", action="/twilio-process", timeout=5)

    return Response(str(response), mimetype="text/xml")

@app.route("/twilio-process", methods=["POST"])
def process_speech():
    """Processes speech input from Twilio and generates AI responses"""
    response = VoiceResponse()

    # Get caller's speech input
    user_speech = request.form.get("SpeechResult", "")
    print(f"🔹 Caller said: {user_speech}")

    if not user_speech:
        response.say("I couldn't hear you. Please speak again.")
        response.redirect("/twilio")  # Redirect back to listen again
        return Response(str(response), mimetype="text/xml")

    # Generate AI response using OpenAI GPT-4
    ai_response = get_ai_response(user_speech)

    # Send AI response back to the caller
    response.say(ai_response)

    # 🔥 Redirect to /twilio to keep the conversation going
    response.redirect("/twilio")

    return Response(str(response), mimetype="text/xml")

def get_ai_response(user_text):
    """Generates AI response using OpenAI GPT-4 (Correct API Format)."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # New API format
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. Answer in a clear and concise way."},
                {"role": "user", "content": user_text}
            ]
        )
        return response.choices[0].message.content  # Correct response parsing
    except Exception as e:
        print(f"❌ Error in OpenAI API: {e}")
        return "Sorry, I had trouble understanding your question. Please try again."
    
if __name__ == "__main__":
    app.run(port=5000, debug=True)
