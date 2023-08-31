##------------------------------------------------BASE


import re
import sqlite3


# Function to extract fields from the text
# Function to extract fields from the text
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


# Function to extract fields from the text
def extract_fields_from_txt(text_file, prefix):
    # Set default value for the "case" column
    default_case_value = "Diferenciar Maiúsculas/Minúsculas"
    # Read the text file
    with open(text_file, "r", encoding="utf-8") as file:
        text = file.read()

    pattern = re.compile(r"\*")
    articles = pattern.split(text)
    fields = []

    for i in range(1, len(articles)):
        article = articles[i].strip()
        shortcut_match = re.search(r"(\d+)(-\s*[a-zA-Z])?", article)
        if shortcut_match:
            # Extract and clean up the shortcut, converting letter to lowercase
            shortcut = shortcut_match.group().replace("-", "").replace(" ", "").lower()

            # Replace the delimiters with newlines only for the full articles
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

            # Remove extra whitespace
            expansion = re.sub(r"\s+", " ", expansion).strip()

            # Added an empty string for "label" field
            fields.append(
                (
                    prefix,
                    prefix + shortcut,
                    expansion,
                    "",
                    False,
                    default_case_value,
                )
            )

            # Split the article into incisos at the '$' delimiter
            incisos = re.split(r"\$", expansion)

            for k, inciso in enumerate(incisos, start=0):
                if k == 0:  # Skip the first inciso because it's already added
                    continue

                # The 'expansion' of the new row should be the text of the inciso
                new_expansion = inciso.strip()  # Removed "*" here

                # Extract the Roman numeral after the '$' delimiter and convert it to a decimal number
                roman_numeral = re.search(r"[IVXLCDM]+", inciso)
                if roman_numeral:
                    decimal_number = roman_to_decimal(roman_numeral.group())

                    # Create a new shortcut for the inciso with 'i' suffix and the inciso number
                    new_shortcut_inciso = shortcut + "i" + str(decimal_number)

                    fields.append(
                        (
                            prefix,
                            prefix + new_shortcut_inciso,
                            new_expansion,
                            "",
                            False,
                            default_case_value,
                        )
                    )  # Changed format to False here

                # Split the inciso into alíneas at the '@' delimiter
                alineas = re.split(r"\@", inciso)

                for j, alinea in enumerate(alineas, start=0):
                    if j == 0:  # Skip the first alinea because it's already added
                        continue

                    # The 'expansion' of the new row should be the text of the alinea
                    new_expansion = alinea.strip()  # Removed "*" here

                    # Create a new shortcut for the alinea with 'a' suffix and the alinea letter
                    new_shortcut_alinea = (
                        new_shortcut_inciso + "a" + alinea.strip()[0].lower()
                    )

                    fields.append(
                        (
                            prefix,
                            prefix + new_shortcut_alinea,
                            new_expansion,
                            "",
                            False,
                            default_case_value,
                        )
                    )  # Changed format to False here

            # Check if '#' delimiter is present in the 'expansion'
            if "#" in expansion:
                # Split the 'expansion' into two parts at the '#' delimiter
                before_delimiter, after_delimiter = expansion.split("#", 1)

                # Create a new shortcut for the article with 'pu' suffix
                new_shortcut = shortcut + "pu"

                # The 'expansion' of the new row should be the text after the '#' delimiter
                new_expansion = after_delimiter.strip()  # Removed "*" here

                fields.append(
                    (
                        prefix,
                        prefix + new_shortcut,
                        new_expansion,
                        "",
                        False,
                        default_case_value,
                    )
                )

            # Split the article into paragraphs at the '%' delimiter
            paragraphs = re.split(r"%", article)

            for j, paragraph in enumerate(paragraphs, start=0):
                if j == 0:  # Skip the first paragraph because it's already added
                    continue

                # The 'expansion' of the new row should be the text of the paragraph
                new_expansion = paragraph.strip()  # Removed "*" here

                # Create a new shortcut for the paragraph with 'p' suffix and the paragraph number
                new_shortcut_paragraph = shortcut + "p" + str(j)

                fields.append(
                    (
                        prefix,
                        prefix + new_shortcut_paragraph,
                        new_expansion,
                        "",
                        False,
                        default_case_value,
                    )
                )  # And here

    return fields


# Function to create the database and insert the data
def create_db(fields, db_name="E:/legal.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE aTable
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         prefix text, 
         shortcut text, 
         expansion text, 
         label text, 
         format boolean, 
         "case" text DEFAULT 'Diferenciar Maiúsculas/Minúsculas')
    """
    )
    c.executemany(
        """
        INSERT INTO aTable (prefix, shortcut, expansion, label, format, "case") VALUES (?,?,?,?,?,?)
    """,
        fields,
    )
    conn.commit()
    conn.close()


# Load the text file
text_file_path = "E:/cc_v3.txt"
prefix = "cc"
fields = extract_fields_from_txt(text_file_path, prefix)

# Create the database and insert the data
create_db(fields)
