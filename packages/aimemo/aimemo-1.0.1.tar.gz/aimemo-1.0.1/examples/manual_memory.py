"""
Manual Memory Management Example
"""

from aimemo import AIMemo

# Initialize
aimemo = AIMemo(namespace="user_123")

# Manually add memories
print("Adding memories...")
aimemo.add_memory(
    content="User prefers Python over JavaScript",
    tags=["preference", "programming"]
)

aimemo.add_memory(
    content="User is building an e-commerce platform",
    tags=["project", "context"]
)

aimemo.add_memory(
    content="User's favorite framework is FastAPI",
    tags=["preference", "framework"]
)

# Search memories
print("\nSearching for 'Python programming'...")
results = aimemo.search("Python programming", limit=3)

for result in results:
    print(f"- {result['content']}")
    print(f"  Tags: {result['tags']}")
    print()

# Get formatted context
print("\nGetting context for 'web framework'...")
context = aimemo.get_context("web framework")
print(context)

# Clear memories
print("\nClearing memories...")
aimemo.clear()
print("Memories cleared!")

