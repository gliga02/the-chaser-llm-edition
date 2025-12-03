import os

from typing import Optional
from dotenv import load_dotenv

from openai import OpenAI

class OpenAIClient:
    def __init__(self, model: str = "gpt-4.1-mini"):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY env variable not set")
        
        self.model = model
        self.client = OpenAI(api_key = api_key)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        message = response.choices[0].message.content
        return message or ""