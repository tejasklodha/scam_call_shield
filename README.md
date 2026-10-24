# 🛡️ Scam Call Shield

Garbathon 2026 by GDG Ahmedabad · Voice AI track

An AI assistant that listens to a phone call as it happens, spots Indian phone scams (digital arrest, fake KYC, fake courier) and warns elderly users in simple Gujarati or Hindi, with a spoken warning.

## How it works
1. The call audio is split into short parts. Each part is sent to **Gemini audio understanding** while it plays, together with notes from earlier parts.
2. Gemini returns structured JSON: transcript, risk score (0–100), scam type, warning signs, and warnings in Gujarati and Hindi.
3. When risk reaches 70, the call is paused, a red warning appears, and **Gemini speech generation** speaks the warning in Gujarati.
4. A "Behind the scenes" panel shows every Gemini API call live: model, request, response, time and tokens.
5. If a model is busy or out of quota, the app automatically switches to a backup Gemini model.

## Built with (Google only)
Gemini API (audio understanding, structured output, speech generation), Google AI Studio, Firebase Hosting, Google Cloud Shell.

## Mocked for the demo
- "Alert my family" calls a mock webhook (logged on screen), not a real messaging service.
- Sample calls are scripted and were generated with Gemini speech generation (`gen_audio.py`).
- Offline mode replays a saved real Gemini run (`cached.json`) in case of Wi-Fi or quota problems.

## Run it
1. Copy `public/config.example.js` to `public/config.js` and add your Gemini API key.
2. `firebase serve` to test, `firebase deploy` to publish.
