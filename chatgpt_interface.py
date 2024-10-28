"""
Application Builder File Summary
chatgpt_interface.py

This file serves as a critical component of the Python Application Builder, facilitating the integration with the ChatGPT API to automate the generation of documentation and enhance code readability. Its primary purpose is to streamline the documentation process by generating README files and inserting meaningful comments into Python code, ultimately improving developer productivity and collaboration.

Key Components:
1. **ChatGPTClient Class**: Provides an interface to interact with the ChatGPT model, enabling tasks like documentation creation and comment generation.
2. **__init__ Method**: Initializes the ChatGPT client with an optional API key for authenticating requests, allowing for flexible integration with the OpenAI API.
3. **fetch_chatgpt_response Method**: Sends prompts to the ChatGPT model and retrieves relevant answers, supporting various documentation and commenting needs.

Overall, this file empowers developers to focus on writing high-quality code while ensuring thorough documentation and clarity within their projects.

"""


import os
from openai import OpenAI

class ChatGPTClient:
    def __init__(self, api_key=None):
        """Initialize the ChatGPT client with the provided API key."""
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("❌ [DEBUG] Missing API key for OpenAI.")
        print("[DEBUG] ChatGPT client initialized.")

    def fetch_chatgpt_response(self, prompt, context='none'):
        """Fetch response from ChatGPT based on the provided prompt and context."""
        print(f"[DEBUG] Sending prompt to ChatGPT: {prompt}")

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"Context: {context}"},
                    {"role": "user", "content": prompt}
                ],
            )
            result = response.choices[0].message.content
            print(f"[DEBUG] ChatGPT response received: {result}")
            return result
        except Exception as e:
            print(f"❌ [DEBUG] Error fetching response from ChatGPT: {e}")
            return None
