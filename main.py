import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
import json
from call_function import call_function, available_functions
import sys

def main():
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise RuntimeError("OPENROUTER_API_KEY was not found")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="Prompt >>> ")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    # Now we can access `args.user_prompt`

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    def generate_content(client: OpenAI, messages: list) -> bool:
        response = client.chat.completions.create( 
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
        )
        message = response.choices[0].message
        messages.append(message)
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, verbose=args.verbose)
                messages.append(result_message)
                if not result_message["content"]:
                    raise Exception(f"Tool call failed: {result_message}")
                if args.verbose is True:
                    print(f"-> {result_message['content']}")
            if (response.usage != None):
                if (args.verbose is True):
                    print(f"User prompt: {args.user_prompt}")
                    print(f"Prompt tokens: {response.usage.prompt_tokens}")
                    print(f"Response tokens: {response.usage.completion_tokens}")
            else:
                raise RuntimeError("Sowwy something is wrong with the API")
            return False
        else:
            print(f"Response: {message.content}")
            return True
    for i in range(20):
        done = generate_content(client, messages)
        if done is True:
            break
    else: 
        print("Ran out of iterations. Please try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
