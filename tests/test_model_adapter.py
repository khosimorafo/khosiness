import pytest

from khosiness.models.base import ModelResponse, ToolCall
from khosiness.models.fake import FakeModel
from khosiness.models.provider import CallableProviderAdapter


def test_fake_model_returns_queued_response():
    fake = FakeModel([ModelResponse(text="done")])
    messages = [{"role": "user", "content": "hello"}]
    tools = []

    result = fake.generate(messages=messages, tools=tools)

    assert result.text == "done"
    assert fake.calls == [{"messages": messages, "tools": tools}]


def test_fake_model_preserves_tool_call_structure():
    fake = FakeModel(
        [
            ModelResponse(
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="read_file",
                        arguments={"path": "README.md"},
                    )
                ]
            )
        ]
    )

    result = fake.generate(messages=[], tools=[])

    assert result.tool_calls[0].name == "read_file"
    assert result.tool_calls[0].arguments == {"path": "README.md"}


def test_fake_model_fails_when_queue_is_empty():
    fake = FakeModel([])

    with pytest.raises(RuntimeError, match="no queued response"):
        fake.generate(messages=[], tools=[])

    assert fake.calls == [{"messages": [], "tools": []}]


def test_callable_provider_normalizes_dictionary():
    def transport(messages, tools):
        return {
            "text": "provider answer",
            "tool_calls": [],
            "stop_reason": "end",
            "input_tokens": 10,
            "output_tokens": 3,
        }

    adapter = CallableProviderAdapter(transport)
    result = adapter.generate(messages=[], tools=[])

    assert isinstance(result, ModelResponse)
    assert result.text == "provider answer"
    assert result.input_tokens == 10
