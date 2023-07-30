# numberUtils.py
from num2words import num2words
import re


def number_to_currency(text):
    pattern = r"(\d+[\.,]?\d*)m"
    matches = re.findall(pattern, text)
    for match in matches:
        number_as_currency = num2words(
            float(match.replace(",", ".")), lang="pt_BR", to="currency"
        )
        # Replace dots with commas
        number_as_currency = number_as_currency.replace(".", ",")
        text = text.replace(match + "m", f"{match} ({number_as_currency})")
    return text


def number_to_words(text):
    pattern = r"(\d+[\.,]?\d*)e"
    matches = re.findall(pattern, text)
    for match in matches:
        if "." in match:
            # If the number contains a dot, it is considered a thousands separator
            match_without_dot = match.replace(".", "")
            number_as_word = num2words(int(match_without_dot), lang="pt_BR")
        elif "," in match:
            # If the number contains a comma, it is considered a decimal separator
            match_with_dot = match.replace(",", ".")
            number_as_word = num2words(float(match_with_dot), lang="pt_BR")
            # Replace the dot in the number with a comma
            number_as_word = number_as_word.replace(".", ",")
        else:
            # If the number does not contain any separator, it is considered an integer
            number_as_word = num2words(int(match), lang="pt_BR")

        text = text.replace(match + "e", f"{match} ({number_as_word})")
    return text


def is_number(s):
    try:
        float(s.replace(",", "."))
        return True
    except ValueError:
        return False
