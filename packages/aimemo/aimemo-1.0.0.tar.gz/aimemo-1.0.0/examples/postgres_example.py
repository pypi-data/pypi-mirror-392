"""
PostgreSQL Storage Example
"""

from aimemo import AIMemo, PostgresStore
from openai import OpenAI

# Initialize with PostgreSQL
store = PostgresStore("postgresql://user:password@localhost/aimemo")
aimemo = AIMemo(store=store)
aimemo.enable()

# Use normally
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Remember that I'm a data scientist"}
    ]
)
print(response.choices[0].message.content)

# Later conversations will have this context
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What tools should I learn?"}
    ]
)
print(response.choices[0].message.content)

aimemo.disable()

