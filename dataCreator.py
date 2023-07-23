###------------------------------------------------BASE


import re
import sqlite3
from bs4 import BeautifulSoup


# Function to extract fields from the text
# Function to extract fields from the text
# Function to extract fields from the text
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
# Function to extract fields from the text
# Function to extract fields from the text
# Function to extract fields from the text
def extract_fields(html, prefix):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    pattern = re.compile(r"\*")
    articles = pattern.split(text)
    fields = []


# Function to extract fields from the text
def extract_fields(html, prefix):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    pattern = re.compile(r"\*")
    articles = pattern.split(text)
    fields = []

    for i in range(1, len(articles)):
        article = articles[i].strip()
        shortcut_match = re.search(r"(\d+)(-\s*[a-zA-Z])?", article)
        if shortcut_match:
            # Extract and clean up the shortcut, converting letter to lowercase
            shortcut = shortcut_match.group().replace("-", "").replace(" ", "").lower()
            expansion = "*" + article
            fields.append((prefix, shortcut, expansion))

            # Split the article into incisos at the '$' delimiter
            incisos = re.split(r"\$", expansion)

            for k, inciso in enumerate(
                incisos, start=0
            ):  # We start the enumeration at 0
                if k == 0:  # Skip the first inciso because it's already added
                    continue

                # The 'expansion' of the new row should be the text of the inciso
                new_expansion = "*" + inciso.strip()

                # Extract the Roman numeral after the '$' delimiter and convert it to a decimal number
                roman_numeral = re.search(r"[IVXLCDM]+", inciso)
                if roman_numeral:
                    decimal_number = roman_to_decimal(roman_numeral.group())

                    # Create a new shortcut for the inciso with 'i' suffix and the inciso number
                    new_shortcut_inciso = shortcut + "i" + str(decimal_number)

                    fields.append((prefix, new_shortcut_inciso, new_expansion))

            # Check if '#' delimiter is present in the 'expansion'
            if "#" in expansion:
                # Split the 'expansion' into two parts at the '#' delimiter
                before_delimiter, after_delimiter = expansion.split("#", 1)

                # Create a new shortcut for the article with 'pu' suffix
                new_shortcut = shortcut + "pu"

                # The 'expansion' of the new row should be the text after the '#' delimiter
                new_expansion = "*" + after_delimiter.strip()

                fields.append((prefix, new_shortcut, new_expansion))

                # Split the expansion into incisos at the '$' delimiter
                incisos = re.split(r"\$", new_expansion)

                for k, inciso in enumerate(
                    incisos, start=0
                ):  # We start the enumeration at 0
                    if k == 0:  # Skip the first inciso because it's already added
                        continue

                    # The 'expansion' of the new row should be the text of the inciso
                    new_expansion = "*" + inciso.strip()

                    # Extract the Roman numeral after the '$' delimiter and convert it to a decimal number
                    roman_numeral = re.search(r"[IVXLCDM]+", inciso)
                    if roman_numeral:
                        decimal_number = roman_to_decimal(roman_numeral.group())

                        # Create a new shortcut for the inciso with 'i' suffix and the inciso number
                        new_shortcut_inciso = new_shortcut + "i" + str(decimal_number)

                        fields.append((prefix, new_shortcut_inciso, new_expansion))

            # Split the article into paragraphs at the '%' delimiter
            paragraphs = re.split(r"%", article)

            for j, paragraph in enumerate(paragraphs, start=0):
                if j == 0:  # Skip the first paragraph because it's already added
                    continue

                # The 'expansion' of the new row should be the text of the paragraph
                new_expansion = "*" + paragraph.strip()

                # Create a new shortcut for the paragraph with 'p' suffix and the paragraph number
                new_shortcut = shortcut + "p" + str(j)

                fields.append((prefix, new_shortcut, new_expansion))

                # Split the paragraph into incisos at the '$' delimiter
                incisos = re.split(r"\$", new_expansion)

                for k, inciso in enumerate(
                    incisos, start=0
                ):  # We start the enumeration at 0
                    if k == 0:  # Skip the first inciso because it's already added
                        continue

                    # The 'expansion' of the new row should be the text of the inciso
                    new_expansion = "*" + inciso.strip()

                    # Extract the Roman numeral after the '$' delimiter and convert it to a decimal number
                    roman_numeral = re.search(r"[IVXLCDM]+", inciso)
                    if roman_numeral:
                        decimal_number = roman_to_decimal(roman_numeral.group())

                        # Create a new shortcut for the inciso with 'i' suffix and the inciso number
                        new_shortcut_inciso = new_shortcut + "i" + str(decimal_number)

                        fields.append((prefix, new_shortcut_inciso, new_expansion))

    return fields


# Function to create the database and insert the data
def create_db(fields, db_name="E:/legal.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE Articles
        (prefix text, shortcut text, expansion text)
    """
    )
    c.executemany(
        """
        INSERT INTO Articles VALUES (?,?,?)
    """,
        fields,
    )
    conn.commit()
    conn.close()


# Load the HTML file
with open("E:/cf_v2.html", "r", encoding="utf-8") as file:
    html = file.read()

# Extract the fields from the HTML
prefix = "cf"
fields = extract_fields(html, prefix)

# Create the database and insert the data
create_db(fields)
##----------------------------------------------------------------


# import re
# import sqlite3
# from bs4 import BeautifulSoup


# # Function to extract fields from the text
# def extract_fields(html, prefix):
#     soup = BeautifulSoup(html, "html.parser")
#     text = soup.get_text("\n")
#     pattern = re.compile(r"\*")
#     articles = pattern.split(text)
#     fields = []

#     for i in range(1, len(articles)):
#         article = articles[i].strip()
#         shortcut_match = re.search(r"(\d+)(-\s*[a-zA-Z])?", article)
#         if shortcut_match:
#             # Extract and clean up the shortcut, converting letter to lowercase
#             shortcut = shortcut_match.group().replace("-", "").replace(" ", "").lower()
#             expansion = "*" + article
#             fields.append((prefix, shortcut, expansion))

#     return fields


# # Function to create the database and insert the data
# def create_db(fields, db_name="E:/legal.db"):
#     conn = sqlite3.connect(db_name)
#     c = conn.cursor()
#     c.execute(
#         """
#         CREATE TABLE Articles
#         (prefix text, shortcut text, expansion text)
#     """
#     )
#     c.executemany(
#         """
#         INSERT INTO Articles VALUES (?,?,?)
#     """,
#         fields,
#     )
#     conn.commit()
#     conn.close()


# # Load the HTML file
# with open("E:/ce_v2.html", "r", encoding="utf-8") as file:
#     html = file.read()

# # Extract the fields from the HTML
# prefix = "ce"
# fields = extract_fields(html, prefix)

# # Create the database and insert the data
# create_db(fields)
###------------------