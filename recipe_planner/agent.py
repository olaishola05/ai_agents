import json
import os
import ssl
import urllib.parse
import urllib.request

from dotenv import load_dotenv
from smolagents import (
    REMOVE_PARAMETER,
    CodeAgent,
    DuckDuckGoSearchTool,
    OpenAIServerModel,
    tool,
)

from utils.utils import extract_cuisines, format_cooking_plan, pick_cuisine

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
themealdb_endpoint = os.getenv("MEALDB_ENDPOINT")
grok_api_key = os.getenv("GROK_API_KEY")


@tool
def search_recipe(cuisine: str) -> str:
    """
    Searches for a recipe based on a cuisine type.

    Args:
        cuisine: The desired cuisine type (e.g. Italian, Mexican, Japanese).

    Returns:
        A recipe name and step-by-step cooking instructions.
    """
    query = urllib.parse.quote(cuisine)
    url = f"{themealdb_endpoint}/search.php?s={query}"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    if not data["meals"]:
        return f"No {cuisine} recipe found. Try a different cuisine."

    meal = data["meals"][0]
    name = meal["strMeal"]
    instructions = meal["strInstructions"][:1500]

    return f"Recipe: {name}\n\nInstructions:\n{instructions}"


ingredients = input("Enter ingredients you have (comma-separated): ").strip()

if not ingredients:
    print("⚠️  No ingredients entered. Exiting.")
    exit()

print("\n🔍 Searching for cuisine suggestions based on your ingredients...\n")


model = OpenAIServerModel(
    model_id="llama-3.3-70b-versatile",
    api_base="https://api.groq.com/openai/v1",
    api_key=grok_api_key,
    stop=REMOVE_PARAMETER,
)

suggestion_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=5,
    verbosity_level=5,
)

raw_suggestions = suggestion_agent.run(
    f"Based on these ingredients: {ingredients}, "
    f"suggest exactly 5 cuisine types I could cook. "
    f"Return ONLY a numbered list of cuisine names with no extra explanation."
)

cuisines = extract_cuisines(raw_suggestions)

if not cuisines:
    print("⚠️  Could not parse cuisine suggestions. Please try again.")
    exit()


chosen_cuisine = pick_cuisine(cuisines)
print(f"\n✅  Great choice! Searching for a {chosen_cuisine} recipe...\n")

recipe_agent = CodeAgent(
    tools=[search_recipe],
    model=model,
    max_steps=5,
    verbosity_level=0,
)

result = recipe_agent.run(
    f"I have these ingredients: {ingredients}. "
    f"I want to cook {chosen_cuisine} food. "
    f"Search for a suitable recipe and present a clear, "
    f"formatted step-by-step cooking plan with sections for "
    f"Ingredients and Steps."
)

format_cooking_plan(result)
