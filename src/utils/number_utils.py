# numberUtils.py
from num2words import num2words
import re


def number_to_words(text):
    pattern = r"(\d+[\.,]?\d*)e"
    matches = re.findall(pattern, text)
    for match in matches:
        number_as_word = num2words(float(match.replace(",", ".")), lang="pt_BR")
        text = text.replace(match + "e", f"{match} ({number_as_word})")
    return text


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
