from flask import Flask, render_template, request, session, redirect, url_for
from google import genai
import random
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "prompt_engineering_project_secret")

FEEDBACK_FILE = "feedback_log.csv"

# -----------------------------------------------------
# The Gemini API key is read from an environment variable
# called GEMINI_API_KEY instead of being written directly in
# this file. This keeps the key out of the code, which matters
# once this project is uploaded somewhere like GitHub.
#
# Locally: you can set it in your terminal before running, e.g.
#   set GEMINI_API_KEY=your_key_here      (Windows)
#   export GEMINI_API_KEY=your_key_here   (Mac/Linux)
#
# On Render: set it in the dashboard under Environment Variables.
#
# If it's not set at all, the app falls back to offline mode.
# -----------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

USE_REAL_AI = False
if GEMINI_API_KEY.strip() != "":
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        USE_REAL_AI = True
    except Exception as e:
        print("Could not set up Gemini, using offline mode instead:", e)


# instructions we give the AI depending on which function the user picked
FUNCTION_INSTRUCTIONS = {
    "qa": "You are a helpful assistant. Answer the user's question clearly and factually in a few sentences.",
    "summarize": "You are a helpful assistant. Summarize the text the user gives you in 2-4 short sentences, keeping only the main points.",
    "creative": "You are a creative writing assistant. Write something imaginative based on what the user asks for (story, poem, or idea). Keep it under 150 words.",
    "advice": "You are a helpful assistant giving practical advice. Give clear, useful, and friendly advice for the user's situation in a short paragraph.",
}


def ask_gemini(function_type, user_message, chat_history):
    """Sends the message to Gemini along with a short system style instruction
    and the recent chat history so it remembers context."""

    instruction = FUNCTION_INSTRUCTIONS.get(function_type, FUNCTION_INSTRUCTIONS["qa"])

    # build a simple text version of the last few messages so Gemini has context
    history_text = ""
    for msg in chat_history[-6:]:  # only keep last 6 messages to keep it short
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += role + ": " + msg["text"] + "\n"

    full_prompt = instruction + "\n\nConversation so far:\n" + history_text + "\nUser: " + user_message

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return "Sorry, something went wrong calling the AI model: " + str(e)


# -----------------------------------------------------
# OFFLINE BACKUP MODE
# This is only used if no API key is set, or if the API call fails.
# It's the same idea as before, just kept as a fallback now.
# -----------------------------------------------------

def offline_response(function_type, user_message):
    if function_type == "qa":
        return offline_qa(user_message)
    elif function_type == "summarize":
        return offline_summarize(user_message)
    elif function_type == "creative":
        return offline_creative(user_message)
    elif function_type == "advice":
        return offline_advice(user_message)
    else:
        return "I didn't understand that function."


def offline_qa(prompt):
    prompt_lower = prompt.lower()
    facts = {
        "capital of france": "The capital of France is Paris.",
        "capital of india": "The capital of India is New Delhi.",
        "eiffel tower": "The Eiffel Tower is a famous iron tower in Paris, built in 1889 for the World's Fair.",
        "paris": "Paris is the capital of France, known for the Eiffel Tower and the Louvre Museum.",
    }
    for key in facts:
        if key in prompt_lower:
            return facts[key]
    return "(Offline mode) I don't have a saved answer for that. Add a Gemini API key to get real answers."


def offline_summarize(text):
    if text.strip() == "":
        return "Please give me some text to summarize."
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip() != ""]
    if len(sentences) <= 2:
        return "Summary: " + ". ".join(sentences) + "."
    return "Summary: " + sentences[0] + ". " + sentences[-1] + "."


def offline_creative(prompt):
    prompt_lower = prompt.lower()
    if "poem" in prompt_lower:
        return random.choice([
            "Leaves of gold fall to the ground,\nAutumn whispers without a sound.",
            "Stars come out to greet the night,\nTime moves on in soft moonlight.",
        ])
    elif "story" in prompt_lower or "dragon" in prompt_lower:
        return random.choice([
            "Once there was a young dragon named Ember who became friends with a nearby village after saving their crops from a storm.",
            "Princess Elara found a sleeping dragon in a cave, sang it a song, and the two became lifelong friends.",
        ])
    else:
        return "(Offline mode) Here's a generic creative idea based on your prompt: \"" + prompt + "\""


def offline_advice(prompt):
    return ("(Offline mode) General tip: break your problem into smaller steps, focus on one "
            "thing at a time, and don't be afraid to ask for help. Add a Gemini API key for "
            "real, personalized advice.")


# -----------------------------------------------------
# ROUTES
# -----------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []

    selected_function = request.form.get("function", "qa") if request.method == "POST" else "qa"

    if request.method == "POST":
        user_message = request.form.get("user_prompt", "").strip()

        if user_message != "":
            chat_history = session["chat_history"]

            if USE_REAL_AI:
                reply = ask_gemini(selected_function, user_message, chat_history)
            else:
                reply = offline_response(selected_function, user_message)

            chat_history.append({"role": "user", "text": user_message})
            chat_history.append({"role": "assistant", "text": reply})

            session["chat_history"] = chat_history

    return render_template(
        "index.html",
        chat_history=session.get("chat_history", []),
        selected_function=selected_function,
        using_real_ai=USE_REAL_AI,
    )


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return redirect(url_for("index"))


@app.route("/feedback", methods=["POST"])
def feedback():
    was_helpful = request.form.get("helpful")
    prompt = request.form.get("prompt")
    response_text = request.form.get("response")

    file_exists = os.path.isfile(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "prompt", "response", "helpful"])
        writer.writerow([datetime.now(), prompt, response_text, was_helpful])

    return "ok"


if __name__ == "__main__":
    # locally this still runs the normal Flask dev server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
