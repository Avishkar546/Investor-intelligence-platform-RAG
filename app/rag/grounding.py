import logging


logger = logging.getLogger(__name__)


class GroundingValidator:

    def validate(
        self,
        answer: str,
        context: str,
    ) -> bool:

        if not answer.strip():
            return False

        if not context.strip():
            return False

        refusal_phrases = [
            "i don't have enough information",
            "insufficient information",
            "cannot determine",
            "not enough information",
        ]

        if any(
            phrase in answer.lower()
            for phrase in refusal_phrases
        ):
            return True

        # Basic grounding check.
        # We are not claiming this is semantic
        # factual verification.
        context_terms = set(
            context.lower().split()
        )

        answer_terms = set(
            answer.lower().split()
        )

        overlap = (
            len(
                context_terms.intersection(
                    answer_terms
                )
            )
            / max(len(answer_terms), 1)
        )

        if overlap < 0.05:

            logger.warning(
                "[GROUNDING] Very low context overlap"
            )

            return False

        return True