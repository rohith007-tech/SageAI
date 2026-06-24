# SageAI - AI Assistant (Prompt Engineering Major Project)

A chat-style AI Assistant called SageAI, built with Flask, with real AI responses
using the free Gemini API.

## What it does

The assistant works like a chat (it remembers what you said earlier in the
conversation). You can pick one of 4 functions before sending a message:

1. **Answer Questions** - factual Q&A
2. **Summarize Text** - paste a paragraph and get a short summary
3. **Generate Creative Content** - stories, poems, ideas
4. **Get Advice** - practical advice on a topic

There's also a Yes/No feedback button under every response, which gets
saved to `feedback_log.csv`.

## Setting up the real AI (Gemini - free)

By default, the app runs in **offline mode** (a few built-in canned answers)
so it works immediately with no setup. To get real AI responses, the app
reads your key from an environment variable called `GEMINI_API_KEY`
(instead of being written directly in the code - this matters once the
project is uploaded to GitHub, since code on GitHub can be seen by others).

**Running locally:**

1. Go to **https://aistudio.google.com/apikey**, sign in, and create a free key
2. Set the environment variable before running the app:
   - Windows (Command Prompt):
     ```
     set GEMINI_API_KEY=your_key_here
     python app.py
     ```
   - Mac/Linux:
     ```
     export GEMINI_API_KEY=your_key_here
     python app.py
     ```

You'll know it worked because the banner at the top of the page will turn
green and say "Connected to Gemini API - responses are live."

**Don't share your API key publicly or upload it to GitHub.**

## Deploying it online (so it has a real, working link)

Running on your own laptop only works for people using that exact laptop -
a link like `http://127.0.0.1:5000` does not work for anyone else. To get a
real public link that works for anyone, deploy it for free on Render:

1. Push this project to a GitHub repository (public or private both work)
2. Go to **https://render.com**, sign up free, click **New Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Under **Environment Variables**, add `GEMINI_API_KEY` with your key as the value
6. Click **Deploy**

After a couple of minutes, Render gives you a real link like
`https://sageai-yourname.onrender.com` that works from any device, anytime.

Note: the free tier "sleeps" after periods of inactivity, so the first
visit after a while might take 30-60 seconds to wake up - that's normal.

## How to run it

**Option A - double-click (easiest):**
Just double-click `run_app.bat` in this folder. It opens a terminal and your
browser automatically. Keep the terminal window open while using the app.

Note: the browser tab sometimes opens a second or two before Flask has
finished starting up, so you might briefly see a "Unable to connect" or
"This site can't be reached" page. If that happens, just wait a moment and
click **Try Again** (or refresh) - it will connect once Flask is ready.

**Option B - using the command line:**

1. Install the requirements:
   ```
   pip install flask google-genai
   ```

2. Run the app:
   ```
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Files

- `app.py` - main Flask app (routes, Gemini integration, offline backup logic)
- `templates/index.html` - the chat interface
- `feedback_log.csv` - created automatically once feedback is submitted

## Notes

- Chat memory is stored in the Flask session, so it resets if you restart
  the server or click "Clear chat."
- If the Gemini API call fails for any reason (no internet, bad key, quota
  limit), the app does not crash — it just shows an error message in the
  chat instead of the AI's reply.
- The free Gemini tier has a rate limit (a small number of requests per
  minute), so if you send messages too quickly you might see an error -
  just wait a few seconds and try again.
