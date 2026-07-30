import os

from src.services.telegram_service import resolve_webhook_url


def test_resolve_webhook_url_prefers_explicit_url(monkeypatch):
    monkeypatch.setenv("WEBHOOK_URL", "https://example.com/custom/webhook")
    monkeypatch.delenv("RAILWAY_PUBLIC_DOMAIN", raising=False)
    assert resolve_webhook_url("/webhook") == "https://example.com/custom/webhook"


def test_resolve_webhook_url_uses_railway_domain(monkeypatch):
    monkeypatch.delenv("WEBHOOK_URL", raising=False)
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "mybot.up.railway.app")
    assert resolve_webhook_url("/webhook") == "https://mybot.up.railway.app/webhook"


def test_resolve_webhook_url_uses_localhost_when_no_domain(monkeypatch):
    monkeypatch.delenv("WEBHOOK_URL", raising=False)
    monkeypatch.delenv("RAILWAY_PUBLIC_DOMAIN", raising=False)
    monkeypatch.setenv("PORT", "8000")
    assert resolve_webhook_url("/webhook") == "http://127.0.0.1:8000/webhook"
