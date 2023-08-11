import re
from docx import Document
import sqlite3


# Function to convert a Roman numeral to a decimal number
# Function to convert a Roman numeral to a decimal number
def roman_to_decimal(roman):
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev_value = 0
    for char in reversed(roman):
        value = values[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total


# Function to extract fields from the text
def extract_fields(doc, prefix):
    pattern = re.compile(r"\*")
    text = "\n".join([p.text for p in doc.paragraphs])
    articles = pattern.split(text)
    fields = []

    for i in range(1, len(articles)):
        article = articles[i].strip()
        shortcut_match = re.search(r"(\d+)(-\s*[a-zA-Z])?", article)
        if shortcut_match:
            shortcut = shortcut_match.group().replace("-", "").replace(" ", "").lower()

            if article.startswith("*Art."):
                expansion = (
                    article.replace("*", "")
                    .replace("#", "\n")
                    .replace("%", "\n")
                    .replace("@", "\n")
                    .replace("$", "\n")
                )
            else:
                expansion = article

            expansion = re.sub(r"\s+", " ", expansion).strip()
            fields.append((prefix, prefix + shortcut, expansion, False, "true"))

            # Split the article into incisos at the '$' delimiter
            incisos = re.split(r"\$", expansion)

            for k, inciso in enumerate(incisos, start=1):
                if k == 1:  # Skip the first inciso because it's already added
                    continue

                new_expansion = inciso.strip()
                if "Parágrafo único." in new_expansion:
                    inciso, _ = new_expansion.split("Parágrafo único.", 1)

                roman_numeral = re.search(r"[IVXLCDM]+", inciso)
                if roman_numeral:
                    decimal_number = roman_to_decimal(roman_numeral.group())
                    new_shortcut_inciso = shortcut + "i" + str(decimal_number)
                    fields.append(
                        (
                            prefix,
                            prefix + new_shortcut_inciso,
                            inciso.strip(),
                            False,
                            "true",
                        )
                    )

                # Split the inciso into alíneas at the '@' delimiter
                alineas = re.split(r"\@", inciso)

                for j, alinea in enumerate(alineas, start=1):
                    if j == 1:  # Skip the first alinea because it's already added
                        continue

                    new_expansion = alinea.strip()
                    new_shortcut_alinea = (
                        new_shortcut_inciso + "a" + alinea.strip()[0].lower()
                    )
                    fields.append(
                        (
                            prefix,
                            prefix + new_shortcut_alinea,
                            new_expansion,
                            False,
                            "true",
                        )
                    )

            # Check if '#' delimiter is present in the 'expansion'
            if "#" in expansion:
                # Split the 'expansion' into two parts at the '#' delimiter
                _, after_delimiter = expansion.split("#", 1)
                new_shortcut = shortcut + "pu"
                new_expansion = after_delimiter.strip()
                fields.append(
                    (prefix, prefix + new_shortcut, new_expansion, False, "true")
                )

            # Split the article into paragraphs at the '%' delimiter
            paragraphs = re.split(r"%", article)

            for j, paragraph in enumerate(paragraphs, start=1):
                if j == 1:  # Skip the first paragraph because it's already added
                    continue

                new_expansion = paragraph.strip()
                new_shortcut_paragraph = shortcut + "p" + str(j)
                fields.append(
                    (
                        prefix,
                        prefix + new_shortcut_paragraph,
                        new_expansion,
                        False,
                        "true",
                    )
                )

    return fields


# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# Load the Word file
doc = Document("E:/cf88_v2.docx")


def create_db(fields, db_name="E:/cf88.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE aTable
        (id INTEGER PRIMARY KEY AUTOINCREMENT, prefix text, shortcut text, expansion text, label text, format boolean, "case" text)
        """
    )
    c.executemany(
        """
        INSERT INTO aTable (prefix, shortcut, expansion, label, format, "case")
        VALUES (?,?,?,?,?)
        """,
        fields,
    )
    conn.commit()
    conn.close()


# Extract the fields from the Word file
prefix = "ce"
fields = extract_fields(doc, prefix)

create_db(fields)
