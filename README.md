# AICHATT

Telegram bot with OpenAI ChatGPT support, ready for Railway deployment.

## What is included
- FastAPI app with Telegram webhook support
- OpenAI ChatGPT integration
- SQLite database by default
- Railway deployment configuration
- Automatic webhook URL resolution for Railway

## Required Variables
Set these in Railway:
- OPENAI_API_KEY
- TELEGRAM_BOT_TOKEN
- OPENAI_MODEL (optional, defaults to gpt-4o-mini)
- WEBHOOK_URL (optional, auto-detected by Railway if not set)
- ENABLE_SECURE_WEBHOOK_TOKEN (optional, defaults to True)
- TELEGRAM_WEBHOOK_SECRET (optional)
- PORT (Railway sets this automatically)

## Deployment
1. Connect this repo to Railway.
2. Add the required variables above.
3. Deploy.
4. The app will automatically configure Telegram webhook using the Railway public URL.