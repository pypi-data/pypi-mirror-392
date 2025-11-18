"""
Minimal Claude (Anthropic) Integration Example
Shows basic integration of Memory Mori with Claude's API
"""

import sys
sys.path.append('..')

from anthropic import Anthropic
from api import MemoryMori
from config import MemoryConfig

# Initialize Anthropic client
client = Anthropic(api_key="your-api-key-here")

# Initialize Memory Mori
config = MemoryConfig(
    collection_name="claude_example",
    persist_directory="./claude_example_data"
)
mm = MemoryMori(config)


def chat(user_message: str, model: str = "claude-3-5-sonnet-20241022") -> str:
    """
    Chat with Claude using Memory Mori for context.

    Args:
        user_message: User's question
        model: Claude model to use

    Returns:
        Assistant's response
    """
    # Get relevant context from memory
    context = mm.get_context(user_message, max_items=3)

    # Build the prompt
    if context:
        system_prompt = f"""You are a helpful assistant with access to conversation history.

Here is relevant context from previous conversations:
{context}

Use this context to provide more personalized and informed responses."""
    else:
        system_prompt = "You are a helpful assistant."

    # Call Claude
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    assistant_message = response.content[0].text

    # Store conversation in memory
    mm.store(f"User: {user_message}\nAssistant: {assistant_message}")

    return assistant_message


if __name__ == "__main__":
    print("Claude + Memory Mori - Interactive Mode")
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
        print(f"\nClaude: {response}\n")
