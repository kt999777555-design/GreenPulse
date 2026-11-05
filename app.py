import os
import logging

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

MODEL = "openai/gpt-oss-20b"

SYSTEM_INSTRUCTION = """
You are GreenAI, the dedicated sustainability assistant
inside an application called GreenPulse.

Your purpose is to help people make environmentally
responsible decisions.

You specialise in:

1. ECO ADVICE
Water conservation, electricity saving and resource efficiency.

2. WASTE MANAGEMENT
Waste segregation, recycling, composting and responsible disposal.

3. CLIMATE AWARENESS
Climate change, global warming, pollution and biodiversity.

4. SUSTAINABLE LIVING
Practical everyday habits that reduce environmental impact.

5. ECO ANALYSIS
Understanding water, electricity and waste consumption data.

RULES:
- Stay focused on sustainability and environmental topics.
- Politely redirect unrelated questions towards sustainability.
- Give practical, realistic and easy-to-understand advice.
- Use headings and bullet points when helpful.
- Never invent statistics or pretend estimates are verified facts.
- Explain assumptions when making calculations.
- Keep answers concise but useful.
- Be friendly, encouraging and educational.
- Do not claim to have performed real-world actions.
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return jsonify({
            "error": "GreenAI is not configured. Check the API key."
        }), 503

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "error": "Please enter a message."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "error": "Your message is too long. Please keep it under 2000 characters."
        }), 400

    try:
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTION
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        reply = completion.choices[0].message.content

        return jsonify({
            "reply": reply or "I couldn't generate a response. Please try again."
        })

    except Exception:
        logging.exception("Groq API error")

        return jsonify({
            "error": "GreenAI couldn't connect right now. Please try again."
        }), 502


if __name__ == "__main__":
    app.run(debug=False)