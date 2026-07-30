# AICHATT

Telegram bot with Gemini AI, ready for Railway deployment.

## What is included
- FastAPI app with Telegram webhook support
- Gemini integration
- SQLite database by default
- Railway deployment configuration
- Automatic webhook URL resolution for Railway

## Required Variables
Set these in Railway:
- GEMINI_API_KEY
- TELEGRAM_BOT_TOKEN
- GEMINI_MODEL_NAME (optional, defaults to gemini-flash-latest)
- WEBHOOK_URL (optional, auto-detected by Railway if not set)
- ENABLE_SECURE_WEBHOOK_TOKEN (optional, defaults to True)
- TELEGRAM_WEBHOOK_SECRET (optional)
- PORT (Railway sets this automatically)

## Deployment
1. Connect this repo to Railway.
2. Add the required variables above.
3. Deploy.
4. The app will automatically configure Telegram webhook using the Railway public URL.