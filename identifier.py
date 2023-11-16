import time
from comtypes import CoInitializeEx, CoUninitialize
from comtypes.client import GetModule, CreateObject

# Load the UI Automation module
GetModule("UIAutomationCore.dll")

# Import the generated UI Automation interfaces
from comtypes.gen.UIAutomationClient import (
    IUIAutomation,
    CUIAutomation,
    IUIAutomationTextPattern,
    UIA_TextPatternId,
    TreeScope_Children,
    UIA_ProcessIdPropertyId,
    UIA_NamePropertyId,
    TextUnit_Word,
    TextPatternRangeEndpoint_Start,
    TextPatternRangeEndpoint_End,
    UIA_ValuePatternId,
    IUIAutomationValuePattern,
    TextUnit_Character,  # Add this to your imports
)


def get_app_name_from_element(element, uiautomation_client):
    process_id = element.GetCurrentPropertyValue(UIA_ProcessIdPropertyId)
    condition = uiautomation_client.CreatePropertyCondition(
        UIA_ProcessIdPropertyId, process_id
    )
    root_element = uiautomation_client.GetRootElement()
    app_window = root_element.FindFirst(TreeScope_Children, condition)
    return (
        app_window.GetCurrentPropertyValue(UIA_NamePropertyId)
        if app_window
        else "Unknown"
    )


def get_word_at_caret(textPattern):
    selection = textPattern.GetSelection()
    if selection.length > 0:
        range = selection.GetElement(0).clone()
        # Collapse the range to a degenerate (empty) range at the start
        range.MoveEndpointByRange(
            TextPatternRangeEndpoint_End, range, TextPatternRangeEndpoint_Start
        )
        # Move the start of the range backward by one word
        range.MoveEndpointByUnit(TextPatternRangeEndpoint_Start, TextUnit_Word, -1)
        # Move the end of the range forward by one word
        range.MoveEndpointByUnit(TextPatternRangeEndpoint_End, TextUnit_Word, 1)
        # Get the text of the range, which should now be just the word at the caret
        word = range.GetText(-1).strip()
        # If the word contains spaces, it might be more than one word,
        # so we take the first part that is likely the word at the caret
        word_parts = word.split()
        return word_parts[0] if word_parts else ""
    return ""


def get_full_text(element, textPattern):
    # First attempt to use the TextPattern's DocumentRange to get the full text
    documentRange = textPattern.DocumentRange
    if documentRange:
        full_text = documentRange.GetText(-1)
        if full_text:
            return full_text.strip()

    # If the TextPattern doesn't provide the full text, use the ValuePattern
    valuePattern = element.GetCurrentPattern(UIA_ValuePatternId)
    if valuePattern:
        valuePattern = valuePattern.QueryInterface(IUIAutomationValuePattern)
        return valuePattern.CurrentValue.strip()

    return ""


def get_focused_info():
    CoInitializeEx()
    uiautomation_client = CreateObject(CUIAutomation, interface=IUIAutomation)
    if not uiautomation_client:
        print("Could not create UI Automation instance")
        CoUninitialize()
        return {}

    try:
        focusedElement = uiautomation_client.GetFocusedElement()
        if not focusedElement:
            print("No focused element.")
            return {}

        app_name = get_app_name_from_element(focusedElement, uiautomation_client)
        info = {
            "app_name": app_name,
            "element_name": focusedElement.CurrentName,
            "word_at_caret": "",
            "full_text": "",
        }

        textPattern = focusedElement.GetCurrentPattern(UIA_TextPatternId)
        if textPattern:
            textPattern = textPattern.QueryInterface(IUIAutomationTextPattern)
            info["word_at_caret"] = get_word_at_caret(textPattern)
            info["full_text"] = get_full_text(focusedElement, textPattern)

        return info

    except Exception as e:
        print(f"An exception occurred: {e}")
        return {}
    finally:
        CoUninitialize()


if __name__ == "__main__":
    info = get_focused_info()
    print("Information:", info)
