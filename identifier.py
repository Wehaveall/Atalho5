import time
from comtypes import CoInitializeEx, CoUninitialize
from comtypes.client import GetModule, CreateObject

# Load the UI Automation module
GetModule("UIAutomationCore.dll")

# Import the generated UI Automation interfaces
from comtypes.gen.UIAutomationClient import (
    IUIAutomation,
    CUIAutomation,
    IUIAutomationValuePattern,
    UIA_ValuePatternId,
    IUIAutomationTextPattern,
    UIA_TextPatternId,
    TreeScope_Ancestors,
    TreeScope_Children,
    UIA_ProcessIdPropertyId,
    UIA_NamePropertyId,
    TextPatternRangeEndpoint_Start,
    TextPatternRangeEndpoint_End,
    TextUnit_Character,
    TextUnit_Word
)

def get_app_name_from_element(element, uiautomation_client):
    # First, get the process ID of the focused element
    process_id = element.GetCurrentPropertyValue(UIA_ProcessIdPropertyId)
    # With the process ID, find the top-level window
    condition = uiautomation_client.CreatePropertyCondition(UIA_ProcessIdPropertyId, process_id)
    root_element = uiautomation_client.GetRootElement()
    app_window = root_element.FindFirst(TreeScope_Children, condition)
    if app_window:
        # Get the name of the application window
        return app_window.GetCurrentPropertyValue(UIA_NamePropertyId)
    return "Unknown"

def get_focused_info():
    # Initialize COM for the calling thread
    CoInitializeEx()

    # Create UI Automation instance
    uiautomation_client = CreateObject(CUIAutomation, interface=IUIAutomation)
    if not uiautomation_client:
        print("Could not create UI Automation instance")
        CoUninitialize()
        return {}

    try:
        # Get the element that currently has focus
        focusedElement = uiautomation_client.GetFocusedElement()
        if not focusedElement:
            print("No focused element.")
            return {}

        # Initialize the dictionary to store information
        info = {
            'app_name': get_app_name_from_element(focusedElement, uiautomation_client),
            'element_name': focusedElement.CurrentName,
            'full_text': '',
            'word_at_caret': ''
        }

        # Check if the focused element supports the ValuePattern and retrieve the value for the full text
        valuePattern = focusedElement.GetCurrentPattern(UIA_ValuePatternId)
        if valuePattern:
            valuePattern = valuePattern.QueryInterface(IUIAutomationValuePattern)
            info['full_text'] = valuePattern.CurrentValue

        textPattern = focusedElement.GetCurrentPattern(UIA_TextPatternId)
        if textPattern:
            textPattern = textPattern.QueryInterface(IUIAutomationTextPattern)
            
            # Get the degenerate range where the caret is
            range = textPattern.GetSelection().GetElement(0)
            if range:
                # Clone the range for checking the character before the caret
                charBeforeCaretRange = range.Clone()
                # Move the start of the range to the previous character
                charBeforeCaretRange.MoveEndpointByUnit(TextPatternRangeEndpoint_Start, TextUnit_Character, -1)
                # Get the character before the caret
                charBeforeCaret = charBeforeCaretRange.GetText(-1)

                # Check if the character before the caret is a space or if there is no character (beginning of text)
                if charBeforeCaret.isspace() or charBeforeCaret == '':
                    info['word_at_caret'] = ''
                else:
                    # Move the start of the range to the beginning of the word
                    range.MoveEndpointByUnit(TextPatternRangeEndpoint_Start, TextUnit_Word, -1)
                    # Move the end of the range to the end of the word
                    range.MoveEndpointByUnit(TextPatternRangeEndpoint_End, TextUnit_Word, 1)
                    # Get the text of the word at the caret
                    info['word_at_caret'] = range.GetText(-1).strip()

        # Return the gathered information
        return info

    except Exception as e:
        print(f"An exception occurred: {e}")
        return {}
    finally:
        # Uninitialize COM for the calling thread
        CoUninitialize()

if __name__ == '__main__':
    info = get_focused_info()
    print("Information:", info)
