class ComfyAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_image(self, prompt: str) -> str:
        return "Image generated"