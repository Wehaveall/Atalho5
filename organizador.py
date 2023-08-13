from bs4 import BeautifulSoup
import re


def process_element(element):
    # Inicializa o texto vazio
    text = ""

    # Itera sobre os elementos filhos, incluindo texto e elementos HTML
    for child in element.children:
        if isinstance(child, str):  # Se for um texto, apenas o adiciona
            text += child.strip() + " "
        else:  # Se for um elemento HTML, processa-o recursivamente
            text += process_element(child) + " "

    # Substituir ocorrências de "1o", "2 o", etc., por "1º", "2º", etc.
    text = re.sub(r"(\d+)\s*o", r"\1º", text)

    # Remove qualquer sequência de espaços em branco (incluindo tabulações e novas linhas)
    text = re.sub(r"\s+", " ", text)

    return text.strip()  # Remove espaços em branco extras


def modify_legal_document(input_file_path, output_file_path):
    with open(input_file_path, "r", encoding="ISO-8859-1") as file:
        content = file.read()

    soup = BeautifulSoup(content, "html.parser")
    article_start = "Art."
    paragraph_start = ("§", "Parágrafo único")
    item_pattern = re.compile(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}) ?-")
    subitem_pattern = re.compile(r"^[a-z]\)")

    modified_lines = []
    inside_centered_text = False
    skip_next_asterisk = False
    found_first_article = False

    for element in soup.find_all(True, recursive=True):
        if element.name == "p" or (
            element.name == "font" and "Artart" in element.get("class", [])
        ):
            text = process_element(element)

            if text.startswith(article_start) and not found_first_article:
                found_first_article = True

            if not found_first_article:
                continue

            is_centered = element.attrs.get("align") == "center" or text.isupper()

            if is_centered and not inside_centered_text:
                inside_centered_text = True
                text = "*" + text
            elif inside_centered_text and not is_centered:
                inside_centered_text = False
                skip_next_asterisk = True

            if text.startswith(article_start):
                if skip_next_asterisk:
                    skip_next_asterisk = False
                else:
                    text = "*" + text

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

    # Find the index of the first "*" and remove everything before it
    first_star_index = next(
        idx for idx, line in enumerate(modified_lines) if line.startswith("*")
    )
    modified_lines = modified_lines[first_star_index:]

    # Find the index of the last "*"
    last_star_index = max(
        idx for idx, line in enumerate(modified_lines) if line.startswith("*")
    )

    # Find the text following "Brasília" after the last "*"
    for i in range(last_star_index, len(modified_lines)):
        line = modified_lines[i]
        if re.search(r"Bras[ií]lia", line, re.IGNORECASE):
            modified_lines = modified_lines[: i + 1]
            break

    # Join the modified lines into a single text
    modified_text = "\n".join(modified_lines)

    # Save the modified text content to the output file
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(modified_text)


# Test the function with the original file and a new output file
modify_legal_document("E:/cpc.html", "E:/cpc_v2.txt")
