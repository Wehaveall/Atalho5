from docx import Document
import re


def modify_word_document(input_file_path, output_file_path):
    # Read the input file
    doc = Document(input_file_path)

    # Define the start of each type of element
    article_start = "Art."
    paragraph_start = ("§", "Parágrafo único")

    # Define regular expressions for items and subitems
    item_pattern = re.compile(
        r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}) ?-"
    )  # Matches Roman numerals up to 99
    subitem_pattern = re.compile(
        r"^[a-z]\)"
    )  # Matches letters followed by a parenthesis

    # Variables for creating the shortcut
    article_number = 0
    paragraph_number = 0
    item_number = 0
    subitem_letter = ""

    # Add symbols before each type of element
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if text.startswith(article_start):
            article_number += 1
            paragraph_number = 0
            item_number = 0
            subitem_letter = ""
            paragraph.text = "*" + text

        elif any(
            text.lower().startswith(start.lower()) for start in paragraph_start
        ):  # We made the comparison case insensitive
            paragraph_number += 1
            item_number = 0
            subitem_letter = ""
            if text.lower().startswith("parágrafo único"):
                paragraph.text = "#" + text
            else:
                paragraph.text = "%" + text

        elif item_pattern.match(text):
            item_number += 1
            subitem_letter = ""
            paragraph.text = "$" + text

        elif subitem_pattern.match(text):
            subitem_letter = text[0]
            paragraph.text = "@" + text

    # Save the modified content to the output file
    doc.save(output_file_path)


# Test the function with the original file and a new output file
modify_word_document("E:/cf88.docx", "E:/cf88_v2.docx")
