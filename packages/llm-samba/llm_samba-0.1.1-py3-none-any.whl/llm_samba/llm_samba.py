import click
import httpx
import json
import llm
from pydantic import Field
from typing import Optional

DEFAULT_MODEL = "Meta-Llama-3.3-70B-Instruct"
MODEL_1 = "gpt-oss-120b"
MODEL_2 = "DeepSeek-V3.1-Terminus"
MODEL_3 = "Meta-Llama-3.3-70B-Instruct"
MODEL_4 = "Meta-Llama-Guard-3-8B"
MODEL_5 = "Qwen2.5-72B-Instruct"
MODEL_6 = "Qwen2.5-Coder-32B-Instruct"
MODEL_7 = "QwQ-32B-Preview"


@llm.hookimpl
def register_models(register):
    register(Samba(DEFAULT_MODEL))
    register(Samba(MODEL_1))
    register(Samba(MODEL_2))
    register(Samba(MODEL_3))
    register(Samba(MODEL_4))
    register(Samba(MODEL_5))
    register(Samba(MODEL_6))
    register(Samba(MODEL_7))

class Samba(llm.Model):
    can_stream = True
    needs_key = "samba"
    key_env_var = "SAMBA_API_KEY"

    class Options(llm.Options):
        temperature: Optional[float] = Field(
            description=(
                "Determines the sampling temperature. Higher values like 0.8 increase randomness, "
                "while lower values like 0.2 make the output more focused and deterministic."
            ),
            ge=0,
            le=1,
            default=0.0,
        )
        max_tokens: Optional[int] = Field(
            description="The maximum number of tokens to generate in the completion.",
            ge=0,
            default=None,
        )

    def __init__(self, model_id):
        self.model_id = model_id

    def build_messages(self, prompt, conversation):
        messages = []
        
        if prompt.system:
            messages.append({"role": "system", "content": prompt.system})
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful assistant"
            })
        
        if conversation:
            for prev_response in conversation.responses:
                if prev_response.prompt.system:
                    messages.append(
                        {"role": "system", "content": prev_response.prompt.system}
                    )
                messages.append(
                    {"role": "user", "content": prev_response.prompt.prompt}
                )
                messages.append(
                    {"role": "assistant", "content": prev_response.text()}
                )

        messages.append({"role": "user", "content": prompt.prompt})
        return messages

    def execute(self, prompt, stream, response, conversation):
        key = self.get_key()
        messages = self.build_messages(prompt, conversation)
        response._prompt_json = {"messages": messages}

        if not hasattr(prompt, 'options') or not isinstance(prompt.options, self.Options):
            options = self.Options()
        else:
            options = prompt.options

        body = {
            "model": self.model_id,
            "messages": messages,
            "stream": stream,
            "temperature": options.temperature,
        }

        if options.max_tokens is not None:
            body["max_tokens"] = options.max_tokens

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }

        try:
            if stream:
                buffer = ""
                with httpx.Client() as client:
                    with client.stream(
                        "POST",
                        "https://api.sambanova.ai/v1/chat/completions",
                        headers=headers,
                        json=body,
                        timeout=None,
                    ) as r:
                        r.raise_for_status()
                        for chunk in r.iter_raw():
                            if chunk:
                                buffer += chunk.decode('utf-8')
                                while '\n\n' in buffer:
                                    message, buffer = buffer.split('\n\n', 1)
                                    if message.startswith('data: '):
                                        data = message[6:]
                                        if data == '[DONE]':
                                            break
                                        try:
                                            parsed = json.loads(data)
                                            if "choices" in parsed and parsed["choices"]:
                                                delta = parsed["choices"][0].get("delta", {})
                                                if "content" in delta:
                                                    content = delta["content"]
                                                    if content:
                                                        yield content
                                        except json.JSONDecodeError:
                                            continue
            else:
                with httpx.Client() as client:
                    r = client.post(
                        "https://api.sambanova.ai/v1/chat/completions",
                        headers=headers,
                        json=body,
                        timeout=None,
                    )
                    r.raise_for_status()
                    response_data = r.json()
                    response.response_json = response_data
                    if "choices" in response_data and response_data["choices"]:
                        yield response_data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            error_body = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                except:
                    error_body = e.response.text
            raise Exception(f"API Error: {str(e)}\nResponse: {error_body}")

@llm.hookimpl
def register_commands(cli):
    @cli.group()
    def samba():
        "Commands for the Samba model"

    @samba.command()
    def models():
        "Show available Samba models"
        click.echo(f"Available models: {DEFAULT_MODEL}")
        click.echo(f"Available models: {MODEL_1}")
        click.echo(f"Available models: {MODEL_2}")
        click.echo(f"Available models: {MODEL_3}")
        click.echo(f"Available models: {MODEL_4}")
        click.echo(f"Available models: {MODEL_5}")
        click.echo(f"Available models: {MODEL_6}")
        click.echo(f"Available models: {MODEL_7}")
