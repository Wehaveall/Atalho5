import ctypes
from comtypes import CoInitializeEx, CoUninitialize, COINIT_MULTITHREADED
from comtypes.client import CreateObject
from ctypes.wintypes import POINT
from comtypes.gen.UIAutomationClient import (
    IUIAutomation,
    CUIAutomation,  # Changed from CUIAutomation8 for compatibility
    IUIAutomationTextPattern2,
    UIA_TextPattern2Id,
    TextPatternRangeEndpoint_Start
)

def main():
    try:
        # Initialize COM for multi-threaded use
        CoInitializeEx(COINIT_MULTITHREADED)
    except OSError as e:
        if e.winerror != -2147417850:  # Check the specific error code
            raise  # Re-raise the exception if it's not the threading error

    try:
        # Create the CUIAutomation instance
        automation = CreateObject(CUIAutomation, interface=IUIAutomation)
        if not automation:
            print("Could not create UI Automation instance")
            return False

        # Get the current mouse position
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))

        # Get the UI Automation element under the cursor
        element = automation.ElementFromPoint(pt)
        if element:
            name = element.CurrentName
            print(f"Watched element {name}")

            # Get the TextPattern2 interface from the element
            text_pattern = element.GetCurrentPattern(UIA_TextPattern2Id)
            text = text_pattern.QueryInterface(IUIAutomationTextPattern2) if text_pattern else None

            if text:
                # Get the document range
                document_range = text.DocumentRange

                # Get the caret range
                active = ctypes.c_bool()
                caret_range = text.GetCaretRange(active)
                if caret_range:
                    # Compare caret start with document start
                    caret_pos = caret_range.CompareEndpoints(
                        TextPatternRangeEndpoint_Start,
                        document_range,
                        TextPatternRangeEndpoint_Start
                    )
                    print(f"Caret is at {caret_pos}")

    finally:
        # Uninitialize COM
        CoUninitialize()

if __name__ == '__main__':
    main()
