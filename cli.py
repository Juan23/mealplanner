# cli.py
from difflib import get_close_matches
from logger import logger

import os
import sys
import math  # Added for pagination calculations
from datetime import date, timedelta


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
        print("1 - Create/View meal plan")
        print("2 - Generate shopping list")
        print("3 - Recipes")
        print("4 - User Settings")
        print("q - Exit")

        choice = input("").lower()
        osclear()
        if choice == "1":
            view_meal_plan()
        elif choice == "2":
            generate_shopping_list()
        elif choice == "3":
            recipes_front_page()
        elif choice == "4":
            user_settings()
        elif choice == "q":
            # TODO
            sys.exit()
        else:
            input_invalid()


def input_invalid():
    """tell user input is invalid"""
    print("Please enter a valid choice.")
    input("Press Enter to continue...")


def generate_shopping_list():
    osclear()
    print("--- Generate Shopping List ---")
    print("Generating list for the next 7 days...")

    try:
        meal_plan = load_data("meal_plan.json")
    except FileNotFoundError:
        print("No meal plan found.")
        input("Press Enter...")
        return

    try:
        recipes_data = load_data("recipes.json")
    except FileNotFoundError:
        print("No recipes found.")
        input("Press Enter...")
        return

    start_date = date.today()
    shopping_list = {}

    for i in range(7):
        d = start_date + timedelta(days=i)
        d_str = d.isoformat()

        if d_str in meal_plan:
            day_plan = meal_plan[d_str]
            for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
                if meal_type in day_plan:
                    for recipe_name in day_plan[meal_type]:
                        if recipe_name in recipes_data:
                            ing_list = recipes_data[recipe_name].get("ingredients", [])
                            for ing in ing_list:
                                name = ing["item"].lower()
                                try:
                                    qty = float(ing["quantity"])
                                except (ValueError, TypeError):
                                    qty = 0.0
                                unit = ing["unit"].lower()

                                if name not in shopping_list:
                                    shopping_list[name] = {}

                                if unit not in shopping_list[name]:
                                    shopping_list[name][unit] = 0.0

                                shopping_list[name][unit] += qty

    osclear()
    print(f"Shopping List ({start_date} - {start_date + timedelta(days=6)})")
    print("-" * 40)

    sorted_items = sorted(shopping_list.keys())
    for item in sorted_items:
        units_dict = shopping_list[item]
        parts = []
        for unit, qty in units_dict.items():
            # Format to remove trailing zeros if integer
            qty_str = f"{qty:.2f}".rstrip("0").rstrip(".")
            parts.append(f"{qty_str} {unit}")
        print(f"[ ] {item.title()}: {', '.join(parts)}")

    print("-" * 40)
    input("Press Enter to return...")


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
    current_page = 1

    while True:
        data = load_data("recipes.json")
        all_recipes = sorted(list(data.keys()))
        total_recipes = len(all_recipes)
        page_size = 10
        total_pages = math.ceil(total_recipes / page_size)

        if current_page > total_pages and total_pages > 0:
            current_page = total_pages

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
    while True:
        data = load_data("recipes.json")
        all_recipes = list(data.keys())

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
        data = load_data("recipes.json")
        if recipe_name not in data:
            print("Recipe not found (it may have been deleted).")
            input("Press Enter to return...")
            return

        recipe = data[recipe_name]
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
        print("3 - Delete recipe")

        choice = input("> ").strip()

        if choice == "1":
            return
        elif choice == "2":
            print("Feature coming soon.")
            input("Press Enter...")
        elif choice == "3":
            confirm = input(
                f"Are you sure you want to delete '{recipe_name}'? (y/n): "
            ).lower()
            if confirm == "y":
                del data[recipe_name]
                save_data("recipes.json", data)
                print("Recipe deleted.")
                return
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


def view_meal_plan():
    current_date = date.today()

    try:
        settings = load_data("settings.json")
        days_to_show = settings.get("days_to_view", 7)
    except FileNotFoundError:
        days_to_show = 7

    while True:
        try:
            meal_plan = load_data("meal_plan.json")
        except FileNotFoundError:
            meal_plan = {}

        osclear()
        print(
            f"Meal Plan ({current_date} - {current_date + timedelta(days=days_to_show-1)})"
        )
        print("-" * 50)

        week_dates = []
        for i in range(days_to_show):
            d = current_date + timedelta(days=i)
            d_str = d.isoformat()
            week_dates.append(d)

            day_plan = meal_plan.get(d_str, {})
            print(f"{i+1}. {d.strftime('%a %d/%m')}:")

            meals_found = False
            for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
                items = day_plan.get(meal_type, [])
                if items:
                    items_str = ", ".join([x.title() for x in items])
                    print(f"   {meal_type.title()}: {items_str}")
                    meals_found = True

            if not meals_found:
                print("   (Empty)")
            print("")

        print("-" * 50)
        print("n - Next Page")
        print("p - Previous Page")
        print("t - Jump to Today")
        print("b - Back")
        print(f"Select a day number (1-{days_to_show}) to edit.")

        choice = input("> ").lower().strip()

        if choice == "n":
            current_date += timedelta(days=days_to_show)
        elif choice == "p":
            current_date -= timedelta(days=days_to_show)
        elif choice == "t":
            current_date = date.today()
        elif choice == "b":
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < days_to_show:
                edit_day(week_dates[idx])
            else:
                input_invalid()
        else:
            input_invalid()


def edit_day(day_date):
    d_str = day_date.isoformat()

    while True:
        try:
            meal_plan = load_data("meal_plan.json")
        except FileNotFoundError:
            meal_plan = {}

        day_plan = meal_plan.get(d_str, {})

        osclear()
        print(f"Editing Plan for {day_date.strftime('%A, %Y-%m-%d')}")
        print("-" * 30)

        meal_types = ["breakfast", "lunch", "dinner", "snack"]

        for m in meal_types:
            items = day_plan.get(m, [])
            print(
                f"{m.title()}: {', '.join([i.title() for i in items]) if items else '(None)'}"
            )

        print("-" * 30)
        print("1 - Add Breakfast")
        print("2 - Add Lunch")
        print("3 - Add Dinner")
        print("4 - Add Snack")
        print("5 - Clear Day")
        print("6 - Clear Specific Meal")
        print("b - Back")

        choice = input("> ").lower().strip()

        if choice == "b":
            return

        if choice in ["1", "2", "3", "4"]:
            m_type = meal_types[int(choice) - 1]
            recipe = select_recipe()
            if recipe:
                if d_str not in meal_plan:
                    meal_plan[d_str] = {}
                if m_type not in meal_plan[d_str]:
                    meal_plan[d_str][m_type] = []

                meal_plan[d_str][m_type].append(recipe)
                save_data("meal_plan.json", meal_plan)
        elif choice == "5":
            if d_str in meal_plan:
                del meal_plan[d_str]
                save_data("meal_plan.json", meal_plan)
                print("Cleared day.")
        elif choice == "6":
            print("\nSelect meal to clear:")
            print("1 - Breakfast")
            print("2 - Lunch")
            print("3 - Dinner")
            print("4 - Snack")
            sub = input("> ").strip()
            if sub in ["1", "2", "3", "4"]:
                m_type = meal_types[int(sub) - 1]
                if d_str in meal_plan and m_type in meal_plan[d_str]:
                    del meal_plan[d_str][m_type]
                    if not meal_plan[d_str]:  # Clean up empty day
                        del meal_plan[d_str]
                    save_data("meal_plan.json", meal_plan)
                    print(f"Cleared {m_type}.")
                else:
                    print("Nothing to clear.")
            input("Press Enter...")
        else:
            input_invalid()


def select_recipe():
    """Select a recipe to return its name"""
    current_page = 1

    while True:
        data = load_data("recipes.json")
        all_recipes = sorted(list(data.keys()))
        total_recipes = len(all_recipes)
        page_size = 10
        total_pages = math.ceil(total_recipes / page_size)

        if current_page > total_pages and total_pages > 0:
            current_page = total_pages

        osclear()
        print(f"Select Recipe (Page {current_page}/{total_pages})")
        print("-" * 30)

        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        current_batch = all_recipes[start_idx:end_idx]

        for i, name in enumerate(current_batch, 1):
            print(f"{i}. {name.title()}")

        print("-" * 30)
        print("n - Next page")
        print("p - Previous page")
        print("b - Cancel")
        print("(Type recipe name to search directly)")

        choice = input("> ").lower().strip()

        if not choice:
            continue

        if choice == "n" and current_page < total_pages:
            current_page += 1
        elif choice == "p" and current_page > 1:
            current_page -= 1
        elif choice == "b":
            return None
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(current_batch):
                return current_batch[idx]
            else:
                input_invalid()
        else:
            res = select_recipe_by_name(choice)
            if res:
                return res


def select_recipe_by_name(initial_query=None):
    """Fuzzy search for selection"""
    while True:
        data = load_data("recipes.json")
        all_recipes = list(data.keys())

        if initial_query:
            query = initial_query
            initial_query = None
        else:
            osclear()
            print("Search Recipe to Select")
            print("-" * 30)
            query = input("Enter recipe name (or 'b' to back): ").strip().lower()

        if query == "b":
            return None

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
        print("Select a number to pick, 's' to search again, or 'b' to back.")
        choice = input("> ").lower().strip()

        if choice == "s":
            continue
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                return matches[idx]
            else:
                input_invalid()
        elif choice == "b":
            return None
        else:
            input_invalid()


def user_settings():
    """
    Allow user to:
        - select default number of days view for view meal plan
    """
    while True:
        osclear()
        print("--- User Settings ---")
        try:
            settings = load_data("settings.json")
        except FileNotFoundError:
            settings = {}

        current_days = settings.get("days_to_view", 7)
        print(f"1 - Set Meal Plan View Days (Current: {current_days})")
        print("b - Back")

        choice = input("> ").strip().lower()

        if choice == "b":
            return
        elif choice == "1":
            try:
                val = int(input("Enter number of days (1-14): "))
                if 1 <= val <= 14:
                    settings["days_to_view"] = val
                    save_data("settings.json", settings)
                    print("Settings saved.")
                    input("Press Enter...")
                else:
                    print("Please enter a value between 1 and 14.")
                    input("Press Enter...")
            except ValueError:
                print("Invalid input.")
                input("Press Enter...")
        else:
            input_invalid()


if __name__ == "__main__":
    osclear()
    main()
