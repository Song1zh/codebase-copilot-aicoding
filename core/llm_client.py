from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI


class LLMClient:
    def __init__(self, model: str | None = None) -> None:
        load_dotenv()

        self.api_key = os.getenv("QWEN_API_KEY")
        self.base_url = os.getenv("QWEN_API_BASE")
        self.model = model or os.getenv("QWEN_MODEL")

        if not self.api_key:
            raise ValueError("QWEN_API_KEY 未设置，请检查 .env 文件。")

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned empty content.")

        return content
