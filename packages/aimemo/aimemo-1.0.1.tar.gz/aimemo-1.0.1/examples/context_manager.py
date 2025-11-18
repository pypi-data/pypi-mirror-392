"""
Context Manager Usage Example
"""

from aimemo import AIMemo
from openai import OpenAI

# Use as context manager
with AIMemo() as aimemo:
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "My name is Alice"}
        ]
    )
    print(response.choices[0].message.content)
    
    # Memory is automatically enabled within the context
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What's my name?"}
        ]
    )
    print(response.choices[0].message.content)

# Memory is automatically disabled when exiting the context

