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
    IUIAutomationLegacyIAccessiblePattern,
    UIA_LegacyIAccessiblePatternId,
    TextPatternRangeEndpoint_Start,
    TextPatternRangeEndpoint_End,
    TextUnit_Character,
    TextUnit_Word,
    TextUnit_Document
)

def main():
    # Initialize COM for the calling thread
    CoInitializeEx()

    # Create UI Automation instance
    pClientUIA = CreateObject(CUIAutomation, interface=IUIAutomation)
    if not pClientUIA:
        print("Could not create UI Automation instance")
        CoUninitialize()
        return False

    try:
        # Get the element that currently has focus
        focusedElement = pClientUIA.GetFocusedElement()
        if not focusedElement:
            print("No focused element.")
            return False

        # Get the name property of the focused element
        name = focusedElement.CurrentName
        print(f"The focused element is: {name}")

        # First, attempt to use ValuePattern to get the full text if it's a single-line edit control.
        valuePattern = focusedElement.GetCurrentPattern(UIA_ValuePatternId)
        if valuePattern:
            valuePattern = valuePattern.QueryInterface(IUIAutomationValuePattern)
            full_text = valuePattern.CurrentValue
            print(f"The full text inside the focused control is: '{full_text}'")
        else:
            # If ValuePattern is not supported, attempt to use TextPattern to get the full text.
            textPattern = focusedElement.GetCurrentPattern(UIA_TextPatternId)
            if textPattern:
                textPattern = textPattern.QueryInterface(IUIAutomationTextPattern)
                documentRange = textPattern.DocumentRange
                full_text = documentRange.GetText(-1)
                print(f"The full text inside the focused control is: '{full_text}'")

                # Get the degenerate range where the caret is
                range = textPattern.GetSelection().GetElement(0)
                # Check if we got a range (the caret is within a text pattern)
                if range:
                    # Move the start of the range to the beginning of the word
                    range.MoveEndpointByUnit(TextPatternRangeEndpoint_Start, TextUnit_Word, -1)
                    # Move the end of the range to the end of the word
                    range.MoveEndpointByUnit(TextPatternRangeEndpoint_End, TextUnit_Word, 1)
                    # Get the text of the word at the caret
                    word_at_caret = range.GetText(-1).strip()
                    print(f"The word at the caret position is: '{word_at_caret}'")
                else:
                    print("Could not get text range from caret position.")
            else:
                print("Focused control does not support ValuePattern or TextPattern.")

        # Assuming success if we get this far
        return True

    except Exception as e:
        print(f"An exception occurred: {e}")
        return False
    finally:
        # Uninitialize COM for the calling thread
        CoUninitialize()

if __name__ == '__main__':
    result = main()
    print("Result:", result)
