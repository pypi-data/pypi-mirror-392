"""
Minimal Ollama Integration Example
Shows basic integration of Memory Mori with local Ollama models
"""

import sys
sys.path.append('..')

import requests
from api import MemoryMori
from config import MemoryConfig

# Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api/chat"

# Initialize Memory Mori
config = MemoryConfig(
    collection_name="ollama_example",
    persist_directory="./ollama_example_data"
)
mm = MemoryMori(config)


def chat(user_message: str, model: str = "llama3.2") -> str:
    """
    Chat with Ollama using Memory Mori for context.

    Args:
        user_message: User's question
        model: Ollama model to use (e.g., "llama3.2", "mistral", "phi3")

    Returns:
        Assistant's response
    """
    # Get relevant context from memory
    context = mm.get_context(user_message, max_items=3)

    # Build messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to conversation history."
        }
    ]

    # Add context if available
    if context:
        messages.append({
            "role": "system",
            "content": f"Context from previous conversations:\n{context}"
        })

    # Add user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Call Ollama
    response = requests.post(
        OLLAMA_API,
        json={
            "model": model,
            "messages": messages,
            "stream": False
        }
    )

    if response.status_code == 200:
        assistant_message = response.json()["message"]["content"]
    else:
        raise Exception(f"Ollama API error: {response.status_code}")

    # Store conversation in memory
    mm.store(f"User: {user_message}\nAssistant: {assistant_message}")

    return assistant_message


if __name__ == "__main__":
    print("Ollama + Memory Mori - Interactive Mode")
    print("=" * 60)
    print("Note: Make sure Ollama is running (ollama serve)")
    print("Type 'quit' or 'exit' to end the conversation\n")

    while True:
        try:
            user_message = input("You: ").strip()

            if user_message.lower() in ['quit', 'exit']:
                print("\nGoodbye!")
                break

            if not user_message:
                continue

            response = chat(user_message)
            print(f"\nAssistant: {response}\n")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure:")
            print("  1. Ollama is installed: https://ollama.ai")
            print("  2. Ollama is running: ollama serve")
            print("  3. Model is downloaded: ollama pull llama3.2\n")
