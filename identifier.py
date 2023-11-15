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
    TextPatternRangeEndpoint_Start,
    TextPatternRangeEndpoint_End,
    TextUnit_Character,
    TextUnit_Word,
    TextUnit_Document,
)


def get_app_name_from_element(element, uiautomation_client):
    # Get process ID and find the top-level window
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

        info = {
            "app_name": get_app_name_from_element(focusedElement, uiautomation_client),
            "element_name": focusedElement.CurrentName,
            "full_text": "",
            "word_at_caret": "",
        }

        textPattern = focusedElement.GetCurrentPattern(UIA_TextPatternId)
        if textPattern:
            textPattern = textPattern.QueryInterface(IUIAutomationTextPattern)
            range = textPattern.GetSelection().GetElement(0)
            if range:
                range.ExpandToEnclosingUnit(TextUnit_Word)
                word_at_caret = range.GetText(-1).strip()
                info["word_at_caret"] = "".join(filter(str.isalnum, word_at_caret))

        textPattern = focusedElement.GetCurrentPattern(UIA_TextPatternId)
        if textPattern:
            textPattern = textPattern.QueryInterface(IUIAutomationTextPattern)
            documentRange = textPattern.DocumentRange
            if documentRange:
                info["full_text"] = documentRange.GetText(-1)

        return info

    except Exception as e:
        print(f"An exception occurred: {e}")
        return {}
    finally:
        CoUninitialize()


if __name__ == "__main__":
    info = get_focused_info()
    print("Information:", info)
