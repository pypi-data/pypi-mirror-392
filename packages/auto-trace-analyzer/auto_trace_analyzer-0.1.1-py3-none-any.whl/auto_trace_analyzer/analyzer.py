import os
from typing import Optional
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_error(error_text: str, code_snippet: Optional[str] = None) -> str:

    if not os.getenv("OPENAI_API_KEY"):
        return (
            "The OPENAI_API_KEY environment variable was not detected, and the OpenAI interface could not be called.\n"
            "Please configure the terminal first:\n"
            "export OPENAI_API_KEY='your API Key'\n"
        )

    system_prompt = (
        "You are a Python debugging assistant."
        "The user will provide you with an error traceback (which may also include a small piece of code).\n"
        "Please answer in English. The output format should consist of three parts:\n"
        "1. Error Overview: Briefly describe the error in 1-2 sentences.\n"
        "2. Possible causes: Provide 1 to 3 possible causes, and try to combine them with key information from the traceback.\n"
        "3. Suggested modifications: Provide clear and actionable suggestions for modification (including which line should be changed and what it should be changed to).\n"
    )

    user_content = f"Below is the complete error message:\n\n{error_text}\n"
    if code_snippet:
        user_content += f"\nBelow is a relevant code snippet (you can ignore it if there are any errors):\n\n{code_snippet}\n"

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
        )

        return response.output_text

    except Exception as e:
        return f"Failed to call OpenAI API:{e}"
