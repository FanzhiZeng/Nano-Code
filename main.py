import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

if os.getenv("ANTHROPIC_BASE_URL"):
    api_key = os.getenv("ANTHROPIC_API_KEY")

if os.getenv("MODEL_ID"):
    MODEL_ID = os.environ["MODEL_ID"]
else:
    print("Model not found!")
    exit(0)

print(f"Use model {MODEL_ID}")

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"), api_key=api_key)


SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."



def agent_loop(messages: list):
    pass

def main():
    history = []
    while True:
        query = input()
        history.append({
            "role": "user",
            "content": query,
        })

        response  = client.messages.create(
            system=SYSTEM,
            messages=history,
            model=MODEL_ID,
            max_tokens=40,
        )

        content  = response.content[-1].text
        print(content)

        history.append({
            "role": "assistant",
            "content": content
        })

if __name__ == "__main__":
    main()
