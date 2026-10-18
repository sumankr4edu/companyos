import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class LLMService:
    """
    Unified LLM service for CompanyOS.

    CompanyOS uses Gemini for final reasoning while
    FalkorDB remains the primary context layer.
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini")
        self.model = os.getenv("LLM_MODEL", "gemini-3.8-flash")

        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured."
                )

            self.client = genai.Client(api_key=api_key)

        else:
            raise RuntimeError(
                f"Unsupported LLM provider: {self.provider}"
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        if self.provider != "gemini":
            raise RuntimeError(
                f"Unsupported LLM provider: {self.provider}"
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=2000,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text

llm_service = LLMService()