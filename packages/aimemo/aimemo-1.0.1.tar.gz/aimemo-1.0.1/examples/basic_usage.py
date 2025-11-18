"""
Basic AIMemo Usage Example
"""

from aimemo import AIMemo
from openai import OpenAI

# Initialize AIMemo
aimemo = AIMemo()
aimemo.enable()

# Create OpenAI client
client = OpenAI()

# First conversation - establish context
print("=== First Conversation ===")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "I'm working on a FastAPI project with PostgreSQL"}
    ]
)
print(response.choices[0].message.content)

print("\n" + "="*50 + "\n")

# Second conversation - AIMemo automatically provides context
print("=== Second Conversation (with memory) ===")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "How do I add JWT authentication to it?"}
    ]
)
print(response.choices[0].message.content)
# Notice: The model knows about your FastAPI + PostgreSQL project!

# Cleanup
aimemo.disable()

