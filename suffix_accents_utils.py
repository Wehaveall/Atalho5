import json


# Global variable to hold the current state of suffix_patterns
current_suffix_patterns = {}


def load_suffix_data():
    # Load the suffix data from suffix.json
    with open('suffix.json', 'r', encoding='utf-8') as f:
        suffix_data = json.load(f)

    # Initialize an empty dictionary to store suffix patterns
    suffix_patterns = {}

    # Loop through all languages in the JSON data
    for lang in suffix_data:
        for entry in suffix_data[lang]:
            pattern = entry.get("pattern")
            replace_value = entry.get("replace")

            if replace_value:
                replacement, status = replace_value.split(", ")

            # Only add the pattern if its status is "enabled"
            if status == "enabled":
                suffix_patterns[pattern] = replacement

    return suffix_patterns





def update_suffix_json(lang, pattern, is_enabled):
    # Read the existing JSON data from the file
    with open('suffix.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find the pattern for the given language and update its status
    for entry in data.get(lang, []):
        if entry['pattern'] == pattern:
            replacement, _ = entry['replace'].split(", ")
            entry['replace'] = f"{replacement}, {'enabled' if is_enabled else 'disabled'}"
            break

    # Write the updated JSON data back to the file
    with open('suffix.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_current_suffix_patterns():
      return load_suffix_data()