"""
Main GUI module for the Meal Planner application using NiceGUI.
Handles the layout, navigation, and rendering of different tabs (Meal Plan, Recipes, Shopping List, Settings).
"""

from nicegui import ui
import json
from pathlib import Path
from datetime import date, timedelta
import cli


# --- State ---
# Global state dictionary to hold runtime configuration and current view context.
state = {"current_date": date.today(), "view_days": 7}

# --- Load Initial Settings ---
# Attempts to load user preferences from 'settings.json'.
try:
    settings = cli.load_data("settings.json")
except FileNotFoundError:
    settings = {}

# Apply loaded settings to the global state
state["view_days"] = settings.get("days_to_view", 7)

# --- Logic ---


# --- UI ---


@ui.page("/")
def main_page():
    """
    Renders the main application page layout.
    Includes the header, navigation tabs, and the container for tab panels.
    """
    ui.colors(primary="#5898d4")
    ui.dark_mode().auto()

    # --- Header & Navigation ---
    with ui.header(elevated=True).classes(
        "items-center justify-between flex-wrap gap-2 dark:bg-gray-800"
    ):
        ui.label("Meal Planner").classes("text-2xl font-bold")
        with ui.tabs() as tabs:
            ui.tab("home", label="Home")
            ui.tab("plan", label="Meal Plan")
            ui.tab("recipes", label="Recipes")
            ui.tab("shopping", label="Shopping List")
            ui.tab("settings", label="Settings")

    # --- Main Content Area ---
    with ui.tab_panels(tabs, value="home").classes("w-full p-0"):
        # --- Home Tab ---
        with ui.tab_panel("home"):
            with ui.column().classes("w-full items-center mt-10"):
                ui.label("Welcome to Meal Planner").classes(
                    "text-4xl font-bold text-gray-800 dark:text-gray-100"
                )
                ui.label("Select a tab above to get started.").classes(
                    "text-xl text-gray-600 dark:text-gray-300"
                )

        # --- Meal Plan Tab ---
        with ui.tab_panel("plan"):
            render_meal_plan_tab()

        # --- Recipes Tab ---
        with ui.tab_panel("recipes"):
            render_recipes_tab()

        # --- Shopping List Tab ---
        with ui.tab_panel("shopping"):
            render_shopping_list_tab()

        # --- Settings Tab ---
        with ui.tab_panel("settings"):
            render_settings_tab()


def render_meal_plan_tab():
    """
    Renders the 'Meal Plan' tab.
    Displays the daily meal schedule based on 'state["view_days"]'.
    """
    with ui.column().classes("w-full"):
        # --- Date Navigation Controls ---
        with ui.row().classes("items-center justify-center mb-4"):
            ui.button(
                icon="chevron_left", on_click=lambda: change_date(-state["view_days"])
            )
            ui.button("Today", on_click=lambda: reset_date())
            ui.button(
                icon="chevron_right", on_click=lambda: change_date(state["view_days"])
            )
            ui.label().bind_text_from(
                state,
                "current_date",
                backward=lambda d: f"Starting: {d.strftime('%Y-%m-%d')}",
            ).classes("text-gray-800 dark:text-gray-100")

        # Container for the daily cards
        meal_plan_container = ui.row().classes(
            "w-full flex-wrap gap-4 items-start justify-center"
        )

        def refresh_plan():
            """Fetches meal plan data and rebuilds the UI cards."""
            meal_plan_container.clear()
            plan_data = cli.get_meal_plan()
            with meal_plan_container:
                for i in range(state["view_days"]):
                    d = state["current_date"] + timedelta(days=i)
                    d_str = d.isoformat()
                    day_data = plan_data.get(d_str, {})

                    # --- Day Card ---
                    with ui.card().classes(
                        "w-full sm:w-[280px] bg-gray-50 dark:bg-gray-900 p-2"
                    ):
                        ui.label(d.strftime("%A, %b %d")).classes(
                            "text-lg font-bold text-primary"
                        )

                        # Render sections for each meal type
                        for m_type in ["breakfast", "lunch", "dinner", "snack"]:
                            with ui.column().classes(
                                "w-full mt-2 p-1 bg-gray-100 dark:bg-gray-800 rounded shadow-sm"
                            ):
                                with ui.row().classes(
                                    "w-full justify-between items-center"
                                ):
                                    ui.label(m_type.title()).classes(
                                        "font-semibold text-sm text-gray-600 dark:text-gray-300"
                                    )
                                    ui.button(
                                        icon="add",
                                        on_click=lambda d=d_str, m=m_type: open_add_meal_dialog(
                                            d, m, refresh_plan
                                        ),
                                    ).props("round flat dense size=sm").classes(
                                        "text-gray-600 dark:text-gray-300"
                                    )

                                items = day_data.get(m_type, [])
                                if items:
                                    for idx, item in enumerate(items):
                                        with ui.row().classes(
                                            "w-full justify-between items-center"
                                        ):
                                            ui.label(item).classes(
                                                "text-sm dark:text-gray-200"
                                            )
                                            ui.button(
                                                icon="close",
                                                on_click=lambda d=d_str, m=m_type, i=idx: [
                                                    cli.remove_from_meal_plan(d, m, i),
                                                    refresh_plan(),
                                                ],
                                            ).props(
                                                "round flat dense size=xs color=red"
                                            )
                                else:
                                    ui.label("-").classes("text-xs text-gray-300")

        refresh_plan()

        def change_date(delta):
            state["current_date"] += timedelta(days=delta)
            refresh_plan()

        def reset_date():
            state["current_date"] = date.today()
            refresh_plan()


def open_add_meal_dialog(date_str, meal_type, callback):
    """
    Opens a dialog to add a recipe to a specific meal slot.

    Args:
        date_str (str): ISO formatted date string.
        meal_type (str): 'breakfast', 'lunch', 'dinner', or 'snack'.
        callback (callable): Function to run after adding (usually to refresh UI).
    """
    recipes = cli.get_all_recipes()
    options = sorted(list(recipes.keys()))

    with ui.dialog() as dialog, ui.card().classes("bg-white dark:bg-gray-900"):
        ui.label(f"Add to {meal_type.title()}").classes(
            "text-xl font-bold dark:text-gray-100"
        )

        select = ui.select(options, label="Search Recipe", with_input=True).classes(
            "w-64"
        )

        def save():
            if select.value:
                cli.update_meal_plan(date_str, meal_type, select.value)
                callback()
                dialog.close()

        with ui.row().classes("w-full justify-end"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Add", on_click=save)

    dialog.open()


def render_recipes_tab():
    """
    Renders the 'Recipes' tab.
    Lists existing recipes and provides a button to create new ones.
    """
    with ui.column().classes("w-full"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Recipes").classes("text-2xl dark:text-gray-100")
            ui.button(
                "New Recipe",
                icon="add",
                on_click=lambda: open_recipe_editor(None, refresh_list),
            )

        recipe_list = ui.column().classes("w-full gap-2")

        def refresh_list():
            """Reloads the list of recipes from storage."""
            recipe_list.clear()
            recipes = cli.get_all_recipes()
            with recipe_list:
                for name in sorted(recipes.keys()):
                    with ui.expansion(name.title()).classes(
                        "w-full bg-gray-50 dark:bg-gray-900"
                    ):
                        data = recipes[name]
                        with ui.column().classes("p-4"):
                            ui.label("Ingredients:").classes(
                                "font-bold dark:text-gray-100"
                            )
                            for ing in data.get("ingredients", []):
                                ui.label(
                                    f"• {ing['quantity']} {ing['unit']} {ing['item']}"
                                ).classes("dark:text-gray-200")

                            ui.label("Instructions:").classes(
                                "font-bold mt-2 dark:text-gray-100"
                            )
                            for i, step in enumerate(data.get("instructions", []), 1):
                                ui.label(f"{i}. {step}").classes("dark:text-gray-200")

                            with ui.row().classes("mt-4"):
                                ui.button(
                                    "Delete",
                                    color="red",
                                    icon="delete",
                                    on_click=lambda n=name: [
                                        cli.delete_recipe(n),
                                        refresh_list(),
                                    ],
                                ).props("flat")

        refresh_list()


def open_recipe_editor(existing_name, callback):
    """
    Opens a dialog to create a new recipe or edit an existing one.

    Args:
        existing_name (str or None): Name of the recipe if editing, else None.
        callback (callable): Function to run after saving.
    """
    ingredients_list = []
    instructions_list = []

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-[600px] bg-white dark:bg-gray-900"
    ):
        ui.label("New Recipe").classes("text-xl font-bold dark:text-gray-100")

        name_input = ui.input("Recipe Name").classes("w-full")

        ui.label("Ingredients").classes("font-bold mt-2 dark:text-gray-100")
        ing_container = ui.column().classes("w-full")

        def refresh_ings():
            """Refreshes the ingredients list UI inside the dialog."""
            ing_container.clear()
            with ing_container:
                for i, ing in enumerate(ingredients_list):
                    with ui.row().classes("items-center w-full"):
                        ui.label(
                            f"{ing['quantity']} {ing['unit']} {ing['item']}"
                        ).classes("flex-grow dark:text-gray-200")
                        ui.button(
                            icon="delete",
                            on_click=lambda idx=i: [
                                ingredients_list.pop(idx),
                                refresh_ings(),
                            ],
                        ).props("flat dense color=red")

        refresh_ings()

        # --- Add Ingredient Inputs ---
        with ui.row().classes("w-full items-end gap-2"):
            i_name = ui.input("Item").classes("flex-grow")
            i_qty = ui.input("Qty").classes("w-16")
            i_unit = ui.input("Unit").classes("w-16")

            def add_ing():
                if i_name.value and i_qty.value:
                    ingredients_list.append(
                        {
                            "item": i_name.value,
                            "quantity": i_qty.value,
                            "unit": i_unit.value,
                        }
                    )
                    i_name.value = ""
                    i_qty.value = ""
                    i_unit.value = ""
                    refresh_ings()

            ui.button(icon="add", on_click=add_ing).props("round dense")

        ui.label("Instructions").classes("font-bold mt-2 dark:text-gray-100")
        inst_container = ui.column().classes("w-full")

        def refresh_inst():
            """Refreshes the instructions list UI inside the dialog."""
            inst_container.clear()
            with inst_container:
                for i, step in enumerate(instructions_list):
                    with ui.row().classes("items-center w-full"):
                        ui.label(f"{i+1}. {step}").classes(
                            "flex-grow dark:text-gray-200"
                        )
                        ui.button(
                            icon="delete",
                            on_click=lambda idx=i: [
                                instructions_list.pop(idx),
                                refresh_inst(),
                            ],
                        ).props("flat dense color=red")

        refresh_inst()

        # --- Add Instruction Input ---
        with ui.row().classes("w-full items-end gap-2"):
            inst_input = ui.input("Step").classes("flex-grow")

            def add_inst():
                if inst_input.value:
                    instructions_list.append(inst_input.value)
                    inst_input.value = ""
                    refresh_inst()

            ui.button(icon="add", on_click=add_inst).props("round dense")

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def save():
                if name_input.value:
                    cli.add_recipe(
                        name_input.value.lower(), ingredients_list, instructions_list
                    )
                    callback()
                    dialog.close()

            ui.button("Save", on_click=save)

    dialog.open()


def render_shopping_list_tab():
    """
    Renders the 'Shopping List' tab.
    Allows generating a consolidated shopping list for a date range.
    """
    with ui.column().classes("w-full"):
        ui.label("Shopping List").classes("text-2xl mb-4 dark:text-gray-100")

        with ui.row().classes("items-center gap-4 mb-4"):
            days_input = ui.number("Days", value=7, min=1, max=30).classes("w-20")
            ui.button("Generate", on_click=lambda: generate(days_input.value))

        result_area = ui.column().classes("w-full")

        def generate(days):
            """Generates the shopping list data and renders checkboxes."""
            result_area.clear()
            data = cli.generate_shopping_list_data(date.today(), int(days))
            sorted_items = sorted(data.keys())

            with result_area:
                if not sorted_items:
                    ui.label("No items found for the selected period.")
                    return

                for item in sorted_items:
                    units_dict = data[item]
                    parts = []
                    for unit, qty in units_dict.items():
                        qty_str = f"{qty:.2f}".rstrip("0").rstrip(".")
                        parts.append(f"{qty_str} {unit}")

                    with ui.row().classes("items-center"):
                        ui.checkbox(f"{item.title()}: {', '.join(parts)}").classes(
                            "dark:text-gray-200"
                        )


def render_settings_tab():
    """
    Renders the 'Settings' tab.
    Provides UI to modify application settings (e.g., view_days).
    """
    with ui.column().classes("w-full"):
        ui.label("Settings").classes("text-2xl mb-4 dark:text-gray-100")

        # Setting: Number of days to display in the Meal Plan view
        days = ui.number(
            "Days to View in Meal Plan", value=state["view_days"], min=1, max=14
        ).classes("w-64")

        def save():
            state["view_days"] = int(days.value)
            cli.save_data("settings.json", {"days_to_view": int(days.value)})
            ui.notify("Settings saved")

        ui.button("Save", on_click=save).classes("mt-4")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Meal Planner", host="0.0.0.0", port=8080)
