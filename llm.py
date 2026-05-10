import os
import anthropic
import openai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import json

load_dotenv()

class LLMClient:
    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        if provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = os.getenv("DEFAULT_MODEL", "claude-3-opus-20240229")
        else:
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4-turbo-preview"

    def completion(self, messages: List[Dict[str, str]], stream: bool = False, response_model: Any = None) -> Any:
        if self.provider == "anthropic":
            return self._anthropic_completion(messages, stream)
        else:
            return self._openai_completion(messages, stream)

    def _anthropic_completion(self, messages: List[Dict[str, str]], stream: bool) -> str:
        # Convert messages to Anthropic format
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        
        if stream:
            return self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=user_messages,
                max_tokens=4096,
                stream=True
            )
        else:
            response = self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=user_messages,
                max_tokens=4096
            )
            return response.content[0].text

    def _openai_completion(self, messages: List[Dict[str, str]], stream: bool) -> str:
        if stream:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content

    def parse_json(self, text: str) -> Dict[str, Any]:
        try:
            # Find JSON block
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return json.loads(text)
        except:
            return {}
