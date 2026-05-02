"""
Example 3: API Design with Dynamic Reasoning

Demonstrates Think Anywhere on a design problem with multiple valid approaches.
Shows reasoning about RESTful conventions, naming, and HTTP verbs.
"""

from think_anywhere import ThinkingAgent


def main():
    print("=" * 70)
    print("Think Anywhere Example: API Design")
    print("=" * 70)
    print()
    
    agent = ThinkingAgent(
        model="gpt-4",
        entropy_threshold=0.6  # Lower threshold for design problems
    )
    
    prompt = """
    Design a RESTful API for a todo list application using FastAPI.
    Include endpoints for:
    - Creating tasks
    - Listing all tasks
    - Getting a specific task
    - Updating a task
    - Deleting a task
    
    Follow REST conventions and best practices.
    """
    
    result = agent.generate(prompt)
    
    print("GENERATED API DESIGN:")
    print("-" * 70)
    print(result.output)
    print()
    
    print("DESIGN DECISIONS (Reasoning):")
    print("-" * 70)
    for i, thought in enumerate(result.thoughts, 1):
        print(f"\n{i}. Decision Point:")
        print("   " + "\n   ".join(thought.split("\n")))
    print()
    
    print("UNCERTAINTY POINTS:")
    print("-" * 70)
    for point in result.entropy_points:
        print(f"• At token '{point.token}': {point.reason}")
    print()


if __name__ == "__main__":
    main()
