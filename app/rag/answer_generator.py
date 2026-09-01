import logging

from google import genai

from app.core.config import get_settings
from app.rag.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)


logger = logging.getLogger(__name__)


class AnswerGenerator:

    def __init__(self):

        settings = get_settings()

        self.client = genai.Client(
            api_key=settings.google_api_key,
        )

        self.model = settings.extraction_model

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:

        if not context.strip():

            return (
                "I don't have sufficient information "
                "in the available financial data to "
                "answer this question."
            )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{build_user_prompt(question, context)}"
        )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as exc:

            logger.exception(
                "[ANSWER_GENERATION] Gemini failed"
            )

            raise RuntimeError(
                "Failed to generate financial answer."
            ) from exc