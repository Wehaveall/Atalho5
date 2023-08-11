from bs4 import BeautifulSoup
import re


def modify_legal_document(input_file_path, output_file_path):
    # Read the input file
    with open(input_file_path, "r", encoding="ISO-8859-1") as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Define the start of each type of element
    article_start = "Art."
    paragraph_start = ("§", "Parágrafo único")

    # Define regular expressions for items and subitems
    item_pattern = re.compile(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}) ?-")
    subitem_pattern = re.compile(r"^[a-z]\)")

    # Initialize variables to handle lines and heading
    modified_lines = []
    insert_star = False
    first_star = True
    last_centered = False

    for element in soup.descendants:
        if element.name == "p" and element.string:
            text = element.string.strip()

            # Check if the text is centered or uppercase
            if element.attrs.get("align") == "center" or text.isupper():
                if not first_star and not last_centered:
                    text = "*" + text
                    last_centered = True
                else:
                    last_centered = False
                    text = text.lstrip(
                        "*"
                    )  # Remove any asterisks from consecutive centered uppercase lines

                insert_star = True

            if text.startswith(article_start):
                if first_star or not insert_star:
                    text = "*" + text
                first_star = False
                insert_star = False

            if text.startswith(article_start):
                modified_lines.append(text)
            elif any(
                text.lower().startswith(start.lower()) for start in paragraph_start
            ):
                modified_lines.append(
                    "#" + text
                    if text.lower().startswith("parágrafo único")
                    else "%" + text
                )
            elif item_pattern.match(text):
                modified_lines.append("$" + text)
            elif subitem_pattern.match(text):
                modified_lines.append("@" + text)
            else:
                modified_lines.append(text)

    # Join the modified lines into a single text
    modified_text = "\n".join(modified_lines)

    # Save the modified text content to the output file
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(modified_text)


# Test the function with the original file and a new output file
modify_legal_document("E:/ce.html", "E:/ce_v2.txt")
