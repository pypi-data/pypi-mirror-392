"""
Minimal OpenAI Integration Example
Shows basic integration of Memory Mori with OpenAI's API
"""

import sys
sys.path.append('..')

from typing import List
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from api import MemoryMori
from config import MemoryConfig

# Initialize OpenAI client
client = OpenAI(api_key="your-api-key-here")

# Initialize Memory Mori
config = MemoryConfig(
    collection_name="openai_example",
    persist_directory="./openai_example_data"
)
mm = MemoryMori(config)


def chat(user_message: str, model: str = "gpt-4o-mini") -> str:
    """
    Chat with OpenAI using Memory Mori for context.

    Args:
        user_message: User's question
        model: OpenAI model to use

    Returns:
        Assistant's response
    """
    # Get relevant context from memory
    context = mm.get_context(user_message, max_items=3)

    # Build messages
    messages: List[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to conversation history."
        }
    ]

    # Add context if available
    if context:
        messages.append({
            "role": "system",
            "content": f"Context:\n{context}"
        })

    # Add user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Call OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    assistant_message = response.choices[0].message.content or ""

    # Store conversation in memory
    mm.store(f"User: {user_message}\nAssistant: {assistant_message}")

    return assistant_message


if __name__ == "__main__":
    print("OpenAI + Memory Mori - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation\n")

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break

        if not user_message:
            continue

        response = chat(user_message)
        print(f"\nAssistant: {response}\n")
