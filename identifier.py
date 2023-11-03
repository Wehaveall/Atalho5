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
    TextPatternRangeEndpoint_Start,
    TextPatternRangeEndpoint_End,
    TextUnit_Character,
    TextUnit_Word
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

        # Check if the focused element supports the ValuePattern and retrieve the value
        valuePattern = focusedElement.GetCurrentPattern(UIA_ValuePatternId)
        if valuePattern:
            valuePattern = valuePattern.QueryInterface(IUIAutomationValuePattern)
            value = valuePattern.CurrentValue
            print(f"The full text inside the focused control is: {value}")
        else:
            print("Focused control does not support ValuePattern.")

        # Check if the focused element supports the TextPattern and retrieve it
        pattern = focusedElement.GetCurrentPattern(UIA_TextPatternId)
        if pattern:
            textPattern = pattern.QueryInterface(IUIAutomationTextPattern)
            # Get the degenerate range where the caret is
            range = textPattern.GetSelection().GetElement(0)

            # Check if we got a range (the caret is within a text pattern)
            if range:
                # Expand the range to get the full word at the caret
                word_range = range.Clone()
                word_range.ExpandToEnclosingUnit(TextUnit_Word)
                word_at_caret = word_range.GetText(-1)
                print(f"The word at the caret position is: '{word_at_caret}'")
            else:
                print("Could not get text range from caret position.")
        else:
            print("Focused control does not support TextPattern.")

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
