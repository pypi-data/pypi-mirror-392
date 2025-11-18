import json
import pytest
import llm
import httpx
from pytest_httpx import HTTPXMock
#from llm_samba import Samba
################## Work in progress #######################

@pytest.fixture(autouse=True)
def ignore_warnings():
    """Ignore known warnings."""
    warnings = [
        # pydantic warning
        "Support for class-based `Config` is deprecated",
        # datetime warning
        "datetime.datetime.utcnow() is deprecated"
    ]
    for warning in warnings:
        pytest.mark.filterwarnings(f"ignore:{warning}")

@pytest.fixture
def samba_model():
    """Fixture to create a Samba model instance."""
    return Samba("Meta-Llama-3.3-70B-Instruct")

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables and API key for testing."""
    monkeypatch.setenv("SAMBA_API_KEY", "samba-test-key-mock")
    monkeypatch.setattr(llm.Model, "get_key", lambda self: "samba-test-key-mock")

@pytest.fixture
def mock_response():
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Test response"
            },
            "finish_reason": "stop"
        }]
    }

def test_model_initialization(samba_model):
    assert samba_model.model_id == "Meta-Llama-3.3-70B-Instruct"
    assert samba_model.can_stream == True
    assert samba_model.needs_key == "samba"
    assert samba_model.key_env_var == "SAMBA_API_KEY"

def test_build_messages_with_system_prompt(samba_model):
    prompt = llm.Prompt(model=samba_model, prompt="Test message", system="Custom system message")
    messages = samba_model.build_messages(prompt, None)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "Custom system message"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Test message"

def test_build_messages_without_system_prompt(samba_model):
    prompt = llm.Prompt(model=samba_model, prompt="Test message")
    messages = samba_model.build_messages(prompt, None)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Test message"

def test_build_messages_with_conversation(samba_model, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer samba-test-key-mock"},
        json={
            "id": "chatcmpl-123",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Previous response"
                }
            }]
        }
    )

    conversation = llm.Conversation(model=samba_model)
    prev_prompt = llm.Prompt(model=samba_model, prompt="Previous message")

    prev_response = llm.Response(model=samba_model, prompt=prev_prompt, stream=False)
    prev_response._response_json = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Previous response"
            }
        }]
    }

    conversation.responses.append(prev_response)

    prompt = llm.Prompt(model=samba_model, prompt="New message")
    messages = samba_model.build_messages(prompt, conversation)

    assert len(messages) == 4
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Previous message"
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "Previous response"
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == "New message"

def test_non_streaming_request(samba_model, mock_response, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer samba-test-key-mock"},
        json=mock_response,
        headers={"Content-Type": "application/json"}
    )

    response = samba_model.prompt("Test message", stream=False)
    result = response.text()
    assert result == "Test response"

    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "Bearer samba-test-key-mock"
    assert json.loads(request.content) == {
        "model": "Meta-Llama-3.3-70B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Test message"}
        ],
        "stream": False,
        "temperature": 0.0
    }

def test_streaming_request(samba_model, httpx_mock: HTTPXMock):
    def response_callback(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer samba-test-key-mock"
        stream_content = [
            'data: {"id":"chatcmpl-123","choices":[{"delta":{"role":"assistant"}}]}\n\n',
            'data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"Test"}}]}\n\n',
            'data: {"id":"chatcmpl-123","choices":[{"delta":{"content":" response"}}]}\n\n',
            'data: [DONE]\n\n'
        ]
        return httpx.Response(
            status_code=200,
            headers={"Content-Type": "text/event-stream"},
            content="".join(stream_content).encode()
        )

    httpx_mock.add_callback(
        response_callback,
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions"
    )

    response = samba_model.prompt("Test message", stream=True)
    chunks = list(response)
    assert "".join(chunks) == "Test response"

def test_temperature_option(samba_model, mock_response, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer samba-test-key-mock"},
        json=mock_response,
        headers={"Content-Type": "application/json"}
    )

    response = samba_model.prompt("Test message", temperature=0.8)
    response.text()  # trigger the request

    request = httpx_mock.get_requests()[0]
    assert json.loads(request.content)["temperature"] == 0.8

def test_max_tokens_option(samba_model, mock_response, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions", 
        match_headers={"Authorization": "Bearer samba-test-key-mock"},
        json=mock_response,
        headers={"Content-Type": "application/json"}
    )

    response = samba_model.prompt("Test message", max_tokens=100)
    response.text()  # trigger the request

    request = httpx_mock.get_requests()[0]
    assert json.loads(request.content)["max_tokens"] == 100

def test_api_error(samba_model, httpx_mock: HTTPXMock):
    error_response = {
        "error": {
            "message": "Invalid request",
            "type": "invalid_request_error",
            "code": "invalid_api_key"
        }
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer samba-test-key-mock"},
        status_code=400,
        json=error_response,
        headers={"Content-Type": "application/json"}
    )

    with pytest.raises(Exception) as exc_info:
        response = samba_model.prompt("Test message", stream=False)
        response.text()  # trigger the API call

    assert "API Error" in str(exc_info.value)
    assert "Invalid request" in str(exc_info.value)

def test_stream_parsing_error(samba_model, httpx_mock: HTTPXMock):
    def error_callback(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer samba-test-key-mock"
        return httpx.Response(
            status_code=200,
            headers={"Content-Type": "text/event-stream"},
            content=b'data: {invalid json}\n\n'
        )

    httpx_mock.add_callback(
        error_callback,
        method="POST",
        url="https://api.sambanova.ai/v1/chat/completions"
    )

    response = samba_model.prompt("Test message", stream=True)
    chunks = list(response)
    assert chunks == []
