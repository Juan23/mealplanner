# cli.py
from difflib import get_close_matches
from logger import logger

import os
import sys
import math  # Added for pagination calculations


def osclear():
    """sole job is to clear"""
    os.system("cls" if os.name == "nt" else "clear")


import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_data(file_path):
    """Load JSON data from the given file path."""
    file_path = BASE_DIR / file_path
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(file_path, data):
    """Save JSON data to the given file path."""
    file_path = BASE_DIR / file_path
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def main():
    while True:
        osclear()
        print("Welcome to Recipe App!")
        print("What do you want to do?")
        print("1 - Create meal plan")
        print("2 - Generate shopping list")
        print("3 - Recipes")
        print("q - Exit")

        choice = input("").lower()
        osclear()
        if choice == "1":
            print("Meal plan")
        elif choice == "2":
            print("test")
        elif choice == "3":
            recipes_front_page()
        elif choice == "q":
            # TODO
            sys.exit()
        else:
            input_invalid()


def input_invalid():
    """tell user input is invalid"""
    print("Please enter a valid choice.")
    input("Press Enter to continue...")


# Home > 2
def view_all_recipes():
    pass


# Home > 3
def recipes_front_page():
    """landing page for recipes"""
    while True:
        osclear()
        print("Recipes")
        print("What do you want to do")
        print("1 - View recipes")
        print("2 - Add new recipe")
        print("b - Back")

        choice = input().lower().strip()
        osclear()

        if choice == "1":  # View recipes
            search_recipes()
        elif choice == "2":  # Add new recipe
            get_recipe_name()
        elif choice == "b":
            return
        else:
            input_invalid()


# Home > 3 > 1
def search_recipes():
    """Search which recipe user wants to view
    Show all recipes available, allow option to search by string
    """
    data = load_data("recipes.json")
    all_recipes = sorted(list(data.keys()))
    total_recipes = len(all_recipes)
    page_size = 10
    total_pages = math.ceil(total_recipes / page_size)
    current_page = 1

    while True:
        osclear()
        print(f"All Recipes (Page {current_page}/{total_pages})")
        print("-" * 30)

        # Calculate slice for current page
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        current_batch = all_recipes[start_idx:end_idx]

        # Display numbered list 1-10
        for i, name in enumerate(current_batch, 1):
            print(f"{i}. {name.title()}")

        print("-" * 30)
        print("Options:")
        if current_page > 1:
            print("p - Previous page")
        if current_page < total_pages:
            print("n - Next page")
        print("s - Search by name")
        print("h - Return to home")

        choice = input("> ").lower().strip()

        # Navigation Logic
        if choice == "n" and current_page < total_pages:
            current_page += 1
        elif choice == "p" and current_page > 1:
            current_page -= 1
        elif choice == "s":
            search_recipe_by_name()
        elif choice == "h":
            return
        elif choice.isdigit():
            # Convert user input (1-based) to index (0-based)
            idx = int(choice) - 1
            if 0 <= idx < len(current_batch):
                view_recipe(current_batch[idx])
            else:
                input_invalid()
        else:
            input_invalid()


def search_recipe_by_name():
    """Finds recipes by name using fuzzy matching"""
    data = load_data("recipes.json")
    all_recipes = list(data.keys())

    while True:
        osclear()
        print("Search Recipe")
        print("-" * 30)
        query = input("Enter recipe name (or 'b' to back): ").strip().lower()

        if query == "b":
            return

        # Get 10 closest matches
        matches = get_close_matches(query, all_recipes, n=10, cutoff=0.4)

        if not matches:
            print(f"No matches found for '{query}'.")
            input("Press Enter to search again...")
            continue

        osclear()
        print(f"Matches for '{query}':")
        print("-" * 30)
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match.title()}")
        print("-" * 30)
        print("Select a number to view, or 's' to search again.")

        choice = input("> ").lower().strip()

        if choice == "s":
            continue
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                view_recipe(matches[idx])
                # Return to search results loop after viewing
            else:
                input_invalid()
        elif choice == "b":
            return
        else:
            input_invalid()


# Home > 3 > 2
def get_recipe_name():
    while True:
        print("Add recipe name (or 'b' to back):")
        new_recipe_name = input().lower().strip()
        osclear()

        if new_recipe_name == "b":
            return

        # if name contains special characters, retry
        if not all(c.isalpha() or c.isspace() for c in new_recipe_name):
            print("Invalid input. Please use letters and spaces only.\n")
            continue

        if (similar_recipes := recipe_is_unique(new_recipe_name)) is True:
            logger.debug("recipe name is unique, getting ingredients from user")
            # Step 1: Get Ingredients
            ingredients = get_ingredients_from_user(new_recipe_name)

            # If ingredients is None, user discarded the recipe
            if ingredients is None:
                return

            # Step 2: Get Instructions
            get_instructions_from_user(new_recipe_name, ingredients)

            # Return to menu after finishing (save or discard)
            return
        else:
            logger.debug("matches found")
            show_existing_recipes(similar_recipes, new_recipe_name)
            return


# Home > 3 > 2 > existing recipe found
def show_existing_recipes(matches, recipe_name):
    logger.debug("running show_existing_recipes")

    while True:
        print("Existing recipes found.")
        for i, match in enumerate(matches, start=1):
            print(f"{i} - {match}")
        print("c - Create new recipe.")
        print("b - Back")

        choice = input("\nSelect an option: ").lower().strip()
        osclear()

        if choice == "b":
            return

        if choice == "c":
            ingredients = get_ingredients_from_user(recipe_name)
            if ingredients is not None:
                get_instructions_from_user(recipe_name, ingredients)
            return

        if not choice.isdigit():
            pass
        else:
            index = int(choice) - 1
            if 0 <= index < len(matches):
                view_recipe(matches[index])
                return

        print("Please enter a valid option.")
        input("Press any key to continue...")


def view_recipe(recipe_name):
    """Shows recipe_name"""
    osclear()
    while True:
        recipe = load_data("recipes.json")[recipe_name]
        ingredients = recipe["ingredients"]
        instructions = recipe["instructions"]

        print(f"--- {recipe_name.title()} ---")
        print("\nIngredients")
        for ingredient in ingredients:
            print(
                f"> {ingredient['quantity']} {ingredient['unit']} {ingredient['item']}"
            )

        print("\nInstructions")
        for i, instruction in enumerate(instructions):
            print(f"{i+1}. {instruction}")

        print("\nWhat do you want to do?")
        print("1 - Return")
        print("2 - Add this recipe to calendar")

        choice = input("> ").strip()

        if choice == "1":
            return
        elif choice == "2":
            print("Feature coming soon.")
            input("Press Enter...")
        else:
            pass


# Home > 3 > 2 > create new recipe (Step 1)
def get_ingredients_from_user(recipe_name, ingredients=None):
    if ingredients is None:
        ingredients = []

    available_ingredients = load_data("ingredients.json")

    while True:
        osclear()
        print(f"--- Creating: {recipe_name.title()} (Ingredients) ---")
        print("\nCurrent Ingredients:")
        if not ingredients:
            print(" (None)")
        else:
            for ing in ingredients:
                print(f" - {ing['item']}: {ing['quantity']} {ing['unit']}")

        print("\nCommands:")
        print("- Type an ingredient name to search/add")
        if ingredients:
            print("- Type 'edit' to modify/delete ingredients")
            print("- Type 'next' or 'done' to proceed to instructions")
        print("- Type 'back' or 'quit' to discard changes")

        user_input = input("\n> ").lower().strip()

        if not user_input:
            continue

        # Navigation / Commands
        if user_input in ["quit", "q", "back", "b"]:
            if input("Discard recipe? (y/n): ").lower() == "y":
                return None
            continue

        if user_input in ["next", "n", "done"] and ingredients:
            return ingredients

        if user_input == "edit" and ingredients:
            while True:
                osclear()
                print("--- Edit Ingredients ---")
                for i, ing in enumerate(ingredients, 1):
                    print(f"{i}. {ing['item']}: {ing['quantity']} {ing['unit']}")
                print("\nEnter number to edit/delete (or Enter to go back):")

                sel = input("> ").strip()
                if not sel:
                    break  # Go back to main loop

                if sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(ingredients):
                        ing = ingredients[idx]
                        print(f"\nSelected: {ing['item']}")
                        action = input("(e)dit or (d)elete? ").lower().strip()

                        if action == "d":
                            ingredients.pop(idx)
                            break
                        elif action == "e":
                            new_unit = input(f"Unit ({ing['unit']}): ").strip()
                            if not new_unit:
                                new_unit = ing["unit"]

                            new_qty = input(f"Quantity ({ing['quantity']}): ").strip()
                            if not new_qty:
                                new_qty = ing["quantity"]

                            ingredients[idx]["unit"] = new_unit
                            ingredients[idx]["quantity"] = new_qty
                            break
                    else:
                        print("Invalid number.")
                        input("Press Enter...")
            continue

        # Search Logic (previously inside 'a' option)
        search_query = user_input
        selected_ingredient = None

        # Exact match check
        if search_query in available_ingredients:
            selected_ingredient = search_query
        else:
            # Fuzzy match
            matches = get_close_matches(
                search_query, available_ingredients, n=5, cutoff=0.6
            )

            if matches:
                print(f"\n'{search_query}' not found. Did you mean:")
                for i, m in enumerate(matches, 1):
                    print(f"{i}. {m}")
                print("c - Create new ingredient")
                print("s - Search again")

                valid_selection = False
                while not valid_selection:
                    sub_choice = input("Select: ").lower().strip()

                    if sub_choice.isdigit():
                        idx = int(sub_choice) - 1
                        if 0 <= idx < len(matches):
                            selected_ingredient = matches[idx]
                            valid_selection = True
                        else:
                            print("Invalid number.")
                    elif sub_choice == "c":
                        selected_ingredient = create_new_ingredient()
                        valid_selection = True
                    elif sub_choice == "s":
                        valid_selection = True  # selected_ingredient stays None
                    else:
                        print("Invalid choice. Enter a number, 'c', or 's'.")

            else:
                # No matches
                print(f"\nNo matches for '{search_query}'.")
                print("c. Create new ingredient")
                print("s. Search again")

                valid_selection = False
                while not valid_selection:
                    sub_choice = input("Select: ").lower().strip()
                    if sub_choice == "c":
                        selected_ingredient = create_new_ingredient()
                        valid_selection = True
                    elif sub_choice == "s":
                        valid_selection = True
                    else:
                        print("Invalid choice. Enter 'c' or 's'.")

        if not selected_ingredient:
            continue

        # 2. Get Details (Unit/Qty)
        print(f"\nSelected: {selected_ingredient.title()}")
        unit = input("Unit (g, tbsp, tsp, ml, pcs): ").strip()
        qty = input("Quantity: ").strip()

        # 3. Add to list (No confirmation)
        ingredients.append({"item": selected_ingredient, "quantity": qty, "unit": unit})


# Home > 3 > 2 > create new recipe (Step 2)
def get_instructions_from_user(recipe_name, ingredients):
    instructions = []
    while True:
        osclear()
        print(f"--- Creating: {recipe_name.title()} (Instructions) ---")

        if instructions:
            print("\nCurrent Instructions:")
            for i, step in enumerate(instructions, 1):
                print(f"{i}. {step}")
        else:
            print("\n(No instructions yet)")

        print("\nCommands:")
        print("- Type an instruction step to add it immediately")
        if instructions:
            print("- Type 'edit' to modify/delete steps")
            print("- Type 'save' or 'done' to finish recipe")
        print("- Type 'quit' to discard changes")

        user_input = input("\n> ").strip()

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ["quit", "q"]:
            if input("Discard recipe? (y/n): ").lower() == "y":
                return

        elif cmd in ["save", "done", "s"] and instructions:
            save_new_recipe_to_file(recipe_name, ingredients, instructions)
            return

        elif cmd == "edit" and instructions:
            # Edit/Delete Logic
            while True:
                osclear()
                print("--- Edit Instructions ---")
                for i, step in enumerate(instructions, 1):
                    print(f"{i}. {step}")
                print("\nEnter number to edit/delete (or Enter to go back):")

                sel = input("> ").strip()
                if not sel:
                    break  # Go back to main loop

                if sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(instructions):
                        print(f"\nSelected: {instructions[idx]}")
                        action = input("(e)dit or (d)elete? ").lower().strip()

                        if action == "d":
                            instructions.pop(idx)
                            break

                        elif action == "e":
                            new_text = input("New text: ").strip()
                            if new_text:
                                instructions[idx] = new_text
                            break
                    else:
                        print("Invalid number.")
                        input("Press Enter...")

        else:
            # Treat input as a new instruction step automatically
            instructions.append(user_input)


def create_new_ingredient():
    """Creates a new ingredient and adds it to ingredients.json"""
    while True:
        osclear()
        print("--- Create New Ingredient ---")
        name = input("Enter ingredient name (or 'b' to back): ").lower().strip()

        if not name:
            continue

        if name == "b":
            return None

        # Check if it actually exists now (in case they typed it wrong before)
        data = load_data("ingredients.json")
        if name in data:
            print(f"'{name}' already exists!")
            input("Press Enter...")
            return name

        if input(f"Save '{name}' to database? (y/n): ").lower() == "y":
            data.append(name)
            data.sort()
            save_data("ingredients.json", data)
            print("Ingredient saved.")
            return name

        if input("Try again? (y/n): ").lower() != "y":
            return None


def save_new_recipe_to_file(name, ingredients, instructions):
    """Helper to save the final recipe"""
    recipes = load_data("recipes.json")

    recipes[name] = {"ingredients": ingredients, "instructions": instructions}

    save_data("recipes.json", recipes)
    print(f"\nRecipe '{name}' saved successfully!")
    input("Press Enter to continue...")


def recipe_is_unique(recipe_name: str):
    """
    Checks if a recipe name is unique.

    Returns:
        True if no similar recipe exists.
        List[str] of similar recipe names if duplicates found.
    """
    data = load_data("recipes.json")  # dict: {recipe_name: {...}}

    # normalize input once
    recipe_name = recipe_name.lower().strip()

    existing_recipes = list(data.keys())

    matches = get_close_matches(recipe_name, existing_recipes, n=3, cutoff=0.6)

    if matches:
        logger.info(f"found these matches: {matches}")
        return matches  # list[str]

    logger.info("recipe is unique")
    return True


if __name__ == "__main__":
    osclear()
    main()
