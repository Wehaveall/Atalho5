from bs4 import BeautifulSoup
import re


def modify_legal_document(input_file_path, output_file_path):
    # Read the input file
    with open(input_file_path, "r", encoding="ISO-8859-1") as file:
        content = file.read()

    # Replace all instances of "" with "-"
    content = content.replace("", "-")

    # Replace any number immediately followed by "o" or "O" with the number followed by "º", considering other characters after "o" or "O"
    content = re.sub(r"(\d)[oO](?=[A-Za-z])", r"\1º", content)

    # Parse the HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Get the body of the document
    body = soup.body

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

    # Add symbols before each type of element
    for element in body.descendants:
        if element.name in [
            "p",
            "li",
        ]:  # These are the tags likely to contain the text we're interested in
            text = element.get_text(strip=True)
            if text.startswith(article_start):
                element.string = "*" + element.get_text()
            elif any(
                text.lower().startswith(start.lower()) for start in paragraph_start
            ):  # We made the comparison case insensitive
                if text.lower().startswith("parágrafo único"):
                    element.string = "#" + element.get_text()
                else:
                    element.string = "%" + element.get_text()
            elif item_pattern.match(text):
                element.string = "$" + element.get_text()
            elif subitem_pattern.match(text):
                element.string = "@" + element.get_text()

    # Save the modified content to the output file
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(str(soup))


# Test the function with the original file and a new output file
modify_legal_document("E:/cf.html", "E:/cf_v2.html")

# "/mnt/data/modified_DEL2848compilado_function_v2.html"  # Return the path of the new file for the user to download


# Agora eu gostaria que fosse criada uma função que criasse um um arquivo .db (sqlite) com os campos
# 1. atalho 2. expansão. Os atalhos iriam começar com "art", começando do 1, onde se encontra o primeiro"*"
# e incrementando de um a um até o ~ultimo "*". Caso haja parágrafos , dentro do artigo, o atalho passaria
# a ser "art(número do artigo) + p(número do parágrafo", por exemplo, "art6p3" Se houver apenas o parágrafo
# único seria acrescida a expressão "pu", como ex: "art5pu". Caso haja incisos dentro dos parágrafos,
# o atalho passaria a ser  "art(número do artigo) + p(número do parágrafo + i(número do inciso"),
# ex: art6p4i2. Caso haja alíneas dentro dos incisos, o atalho seria
# "art(número do artigo) + p(número do parágrafo + i(número do inciso) + a(letra da alínea), como por exemplo "art23p3i7aa".
# parágrafos, incisos são incrementados de 1 em 1 até o fim do artigo e alineas  seguem ordem alfabética até o fim do artigo
