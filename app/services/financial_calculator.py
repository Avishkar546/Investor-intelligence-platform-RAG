from decimal import Decimal, InvalidOperation


class FinancialCalculator:

    @staticmethod
    def percentage_change(
        previous: str | None,
        current: str | None,
    ) -> float | None:

        if previous is None or current is None:
            return None

        try:
            previous_value = Decimal(previous)
            current_value = Decimal(current)

        except InvalidOperation:
            return None

        if previous_value == 0:
            return None

        change = (
            (current_value - previous_value)
            / abs(previous_value)
        ) * 100

        return round(float(change), 2)