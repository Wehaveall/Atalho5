import webview


class Api:
    def __init__(self):
        pass

    def start_recording(self, params):
        print("Start recording function in Python script has been called!")
        return "Recording started from Python"  # Ensure this method returns a value


if __name__ == "__main__":
    api = Api()  # Create an instance of the Api class
    webview.create_window(
        "Hello world", "https://pywebview.flowrl.com/hello", js_api=api
    )
    webview.start()
