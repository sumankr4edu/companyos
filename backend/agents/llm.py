import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class LLMService:
    """
    Unified LLM service for CompanyOS.

    CompanyOS uses Gemini for final reasoning while
    FalkorDB remains the primary context layer.

    Reliability behavior:
    - Retries transient Gemini 5xx/503 failures.
    - Uses exponential backoff.
    - Does not retry configuration/authentication errors.
    - Raises a clear RuntimeError after retries are exhausted.
    """

    MAX_RETRIES = 3
    INITIAL_BACKOFF_SECONDS = 1.0

    def __init__(self):
        self.provider = os.getenv(
            "LLM_PROVIDER",
            "gemini",
        )

        self.model = os.getenv(
            "LLM_MODEL",
            "gemini-3.8-flash",
        )

        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured."
                )

            self.client = genai.Client(
                api_key=api_key
            )

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

        last_error = None

        for attempt in range(
            self.MAX_RETRIES + 1
        ):
            try:
                response = (
                    self.client.models.generate_content(
                        model=self.model,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            max_output_tokens=2000,
                        ),
                    )
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response.text

            except Exception as exc:
                last_error = exc

                if not self._is_retryable(exc):
                    raise

                if attempt >= self.MAX_RETRIES:
                    break

                backoff = (
                    self.INITIAL_BACKOFF_SECONDS
                    * (2 ** attempt)
                )

                time.sleep(backoff)

        raise RuntimeError(
            "Gemini is temporarily unavailable "
            "after multiple retry attempts."
        ) from last_error

    @staticmethod
    def _is_retryable(
        error: Exception,
    ) -> bool:
        """
        Retry only transient provider failures.

        We intentionally avoid retrying authentication,
        invalid-request, quota/configuration, or other
        permanent errors indefinitely.
        """

        status_code = getattr(
            error,
            "status_code",
            None,
        )

        if status_code in {
            429,
            500,
            502,
            503,
            504,
        }:
            return True

        error_text = str(error).upper()

        transient_markers = (
            "503 UNAVAILABLE",
            "500 INTERNAL",
            "502 BAD GATEWAY",
            "504 GATEWAY",
            "SERVICE UNAVAILABLE",
            "TEMPORARILY UNAVAILABLE",
            "INTERNAL SERVER ERROR",
        )

        return any(
            marker in error_text
            for marker in transient_markers
        )


llm_service = LLMService()