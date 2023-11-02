import time
from comtypes import CoInitializeEx, CoUninitialize
from comtypes.client import GetModule, CreateObject

# Load the UI Automation module
GetModule("UIAutomationCore.dll")

# Import the generated UI Automation interfaces
from comtypes.gen.UIAutomationClient import IUIAutomation, CUIAutomation, IUIAutomationValuePattern, UIA_ValuePatternId

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
        pattern = focusedElement.GetCurrentPattern(UIA_ValuePatternId)
        valuePattern = pattern.QueryInterface(IUIAutomationValuePattern)
        
        if valuePattern:
            value = valuePattern.CurrentValue
            print(f"The text inside the focused control is: {value}")
        else:
            print("Focused control does not support ValuePattern.")

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
