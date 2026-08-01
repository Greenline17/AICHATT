from src.gemini import Gemini


def test_build_request_payload_converts_history(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Gemini()

    payload = client._build_request_payload(
        "hello",
        [{"role": "user", "parts": [{"text": "previous"}]}],
    )

    assert payload["model"] == "gpt-4o-mini"
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == "previous"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "hello"
