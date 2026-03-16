import re

from smolagents.utils import Any


def format_cooking_plan(result: Any) -> None:
    """Prints the final cooking plan with clean formatting."""
    print("\n" + "=" * 40)
    print("        🍽️  YOUR COOKING PLAN")
    print("=" * 40 + "\n")

    # Bold section headers if they exist (Step 1, Ingredients, etc.)
    lines = result.strip().split("\n")
    for line in lines:
        if re.match(
            r"^(step\s*\d+|ingredients|instructions|note)", line, re.IGNORECASE
        ):
            print(f"\n--- {line.upper()} ---")
        else:
            print(line)

    print("\n" + "=" * 40)


def pick_cuisine(cuisines: list[str]) -> str:
    """
    Displays cuisine options and validates user input.
    Retries until a valid choice is made.
    """
    while True:
        print("\n=== SUGGESTED CUISINES ===\n")
        for i, cuisine in enumerate(cuisines, 1):
            print(f"  {i}. {cuisine}")

        choice = input(
            f"\nPick a cuisine (enter a number 1-{len(cuisines)}, "
            f"or type a cuisine name): "
        ).strip()

        # Check if user entered a number
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(cuisines):
                return cuisines[index]
            else:
                print(f"  ⚠️  Please enter a number between 1 and {len(cuisines)}.")

        # Check if user typed a name matching the list (case-insensitive)
        elif choice.lower() in [c.lower() for c in cuisines]:
            return choice.capitalize()

        # Allow any custom cuisine with confirmation
        else:
            confirm = (
                input(f"  '{choice}' isn't in the list. Use it anyway? (y/n): ")
                .strip()
                .lower()
            )
            if confirm == "y":
                return choice.capitalize()
            else:
                print("  Let's try again.\n")


def extract_cuisines(suggestions: Any) -> list[str]:
    """
    Parses the agent's numbered list response into a clean Python list.
    Handles formats like: '1. Italian', '1) Italian', '- Italian'
    """
    # print(suggestions, "My suggestions")
    # lines = suggestions.strip().split("\n")
    cuisines = []
    for line in suggestions:
        # Strip numbering, bullets, dashes
        cleaned = re.sub(r"^[\d\.\)\-\*\s]+", "", line).strip()
        # Take only the cuisine name (before any dash or colon explanation)
        cleaned = re.split(r"[-–:]", cleaned)[0].strip()
        if cleaned:
            cuisines.append(cleaned)
    return cuisines
