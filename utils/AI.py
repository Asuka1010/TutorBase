import json
from openai import OpenAI
from django.conf import settings


class AI:
    """
    A class for interacting with OpenAI's ChatGPT API to assist with Korean language learning.

    This class sends prompts to the ChatGPT API and processes the responses,
    optionally parsing JSON-formatted output.

    Methods:
        ask_chatgpt(prompt, is_json=True): Sends a prompt to ChatGPT and returns the response.
    """

    def ask(self, prompt, is_json=True):
        """
        Sends a prompt to ChatGPT and retrieves the response.

        Args:
            prompt (str): The input text to be sent to ChatGPT.
            is_json (bool): Whether to parse the response as JSON.

        Returns:
            dict or str: Parsed JSON response if `is_json=True`, otherwise the raw text response.

        Raises:
            json.JSONDecodeError: If the response cannot be parsed as JSON.
            KeyError: If the expected format is not found in the response.
        """
        print("chatgpt")
        client = OpenAI(
            api_key=settings.OPENROUTER_API,
            base_url="https://openrouter.ai/api/v1",
        )  # Initialize OpenAI client

        # print(prompt)  # Debug: Print the input prompt

        # Make the API call
        completion = client.chat.completions.create(
            #model="gpt-4o-mini",  # Adjust model if needed
            messages=[
                {"role": "system", "content": "You are a helpful assistant for helping tutors generate lesson plans."},
                {"role": "user", "content": prompt}
            ],
            model="deepseek/deepseek-chat-v3-0324:free",
            stream=False
        )

        # Extract the response message content
        response = completion.choices[0].message.content
        # print(response[0:7])  # Debug: Print first few characters of response

        print(response)  # Debug: Print the processed response
        return response
