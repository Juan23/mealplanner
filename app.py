import flet as ft
import cli
from datetime import date, timedelta


def main(page: ft.Page):
    page.title = "Meal Planner"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800

    # --- Helper to refresh views ---
    def refresh_all():
        # Update the content of each tab
        meal_plan_tab.content = build_meal_plan_view()
        recipes_tab.content = build_recipes_view()
        shopping_list_tab.content = build_shopping_list_view()
        page.update()

    # --- Meal Plan View ---
    def build_meal_plan_view():
        plan_data = cli.get_meal_plan()

        days_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

        # Show next 7 days
        start_date = date.today()
        for i in range(7):
            d = start_date + timedelta(days=i)
            d_str = d.isoformat()
            day_plan = plan_data.get(d_str, {})

            # Build rows for each meal type
            meal_rows = []
            for m_type in ["Breakfast", "Lunch", "Dinner", "Snack"]:
                items = day_plan.get(m_type.lower(), [])
                meal_rows.append(build_meal_row(d_str, m_type, items))

            day_card = ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        [
                            ft.Text(
                                d.strftime("%A, %Y-%m-%d"),
                                weight=ft.FontWeight.BOLD,
                                size=16,
                            ),
                            ft.Divider(),
                            *meal_rows,
                        ]
                    ),
                )
            )
            days_column.controls.append(day_card)

        return ft.Container(content=days_column, padding=10)

    def build_meal_row(date_str, meal_type, items):
        # items is a list of recipe names
        chips = []
        for idx, item in enumerate(items):
            chips.append(
                ft.Chip(
                    label=ft.Text(item.title()),
                    on_delete=lambda e, d=date_str, m=meal_type, i=idx: delete_meal(
                        d, m, i
                    ),
                )
            )

        # Add button
        add_btn = ft.IconButton(
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            tooltip=f"Add {meal_type}",
            on_click=lambda e: open_recipe_selector(date_str, meal_type),
        )

        return ft.Column(
            [
                ft.Row(
                    [ft.Text(meal_type, weight=ft.FontWeight.W_500), add_btn],
                    alignment=ft.MainAxisAlignment.START,
                ),
                (
                    ft.Row(chips, wrap=True)
                    if chips
                    else ft.Text("(None)", italic=True, size=12, color=ft.colors.GREY)
                ),
                ft.Divider(height=1, color=ft.colors.TRANSPARENT),  # Spacer
            ],
            spacing=2,
        )

    def delete_meal(date_str, meal_type, index):
        cli.remove_from_meal_plan(date_str, meal_type.lower(), index)
        refresh_all()

    def open_recipe_selector(date_str, meal_type):
        def close_dlg(e):
            dlg.open = False
            page.update()

        def select_recipe(e):
            recipe_name = e.control.data
            cli.update_meal_plan(date_str, meal_type.lower(), recipe_name)
            dlg.open = False
            refresh_all()

        recipes = cli.get_all_recipes()
        recipe_list = ft.ListView(expand=1, spacing=5, padding=10)

        for r_name in sorted(recipes.keys()):
            recipe_list.controls.append(
                ft.ListTile(
                    title=ft.Text(r_name.title()), on_click=select_recipe, data=r_name
                )
            )

        dlg = ft.AlertDialog(
            title=ft.Text(f"Select for {meal_type}"),
            content=ft.Container(
                content=recipe_list,
                width=400,
                height=400,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
            ),
            actions=[ft.TextButton("Cancel", on_click=close_dlg)],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- Recipes View ---
    def build_recipes_view():
        recipes = cli.get_all_recipes()

        lv = ft.ListView(expand=True, spacing=5)

        for name in sorted(recipes.keys()):
            lv.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.RESTAURANT),
                    title=ft.Text(name.title()),
                    trailing=ft.IconButton(
                        ft.icons.DELETE_OUTLINE,
                        icon_color=ft.colors.RED_400,
                        on_click=lambda e, n=name: delete_recipe_click(n),
                    ),
                    on_click=lambda e, n=name: view_recipe_details(n),
                )
            )

        return ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Recipes", size=24, weight=ft.FontWeight.BOLD),
                            ft.FloatingActionButton(
                                icon=ft.icons.ADD,
                                on_click=lambda e: open_add_recipe_dialog(),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    lv,
                ],
                expand=True,
            ),
        )

    def delete_recipe_click(name):
        def confirm_delete(e):
            cli.delete_recipe(name)
            confirm_dlg.open = False
            refresh_all()

        def cancel_delete(e):
            confirm_dlg.open = False
            page.update()

        confirm_dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete '{name}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.TextButton(
                    "Delete",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ft.colors.RED),
                ),
            ],
        )
        page.dialog = confirm_dlg
        confirm_dlg.open = True
        page.update()

    def view_recipe_details(name):
        recipes = cli.get_all_recipes()
        recipe = recipes.get(name)
        if not recipe:
            return

        ingredients_controls = [
            ft.Text(f"• {i['quantity']} {i['unit']} {i['item']}")
            for i in recipe["ingredients"]
        ]
        instructions_controls = [
            ft.Text(f"{idx+1}. {step}")
            for idx, step in enumerate(recipe["instructions"])
        ]

        dlg = ft.AlertDialog(
            title=ft.Text(name.title(), size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=500,
                height=400,
                content=ft.Column(
                    [
                        ft.Text("Ingredients", weight=ft.FontWeight.BOLD, size=16),
                        ft.Column(ingredients_controls, spacing=2),
                        ft.Divider(),
                        ft.Text("Instructions", weight=ft.FontWeight.BOLD, size=16),
                        ft.Column(instructions_controls, spacing=5),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda e: setattr(dlg, "open", False) or page.update(),
                )
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def open_add_recipe_dialog():
        name_tf = ft.TextField(label="Recipe Name", autofocus=True)

        # Lists to hold UI controls and data
        ing_column = ft.Column()
        inst_column = ft.Column()

        added_ingredients = []
        added_instructions = []

        def refresh_dialog_lists():
            ing_column.controls.clear()
            for ing in added_ingredients:
                ing_column.controls.append(
                    ft.Text(f"• {ing['quantity']} {ing['unit']} {ing['item']}")
                )

            inst_column.controls.clear()
            for idx, step in enumerate(added_instructions, 1):
                inst_column.controls.append(ft.Text(f"{idx}. {step}"))
            page.update()

        def add_ing_click(e):
            i_item = ft.TextField(label="Item", expand=2)
            i_qty = ft.TextField(label="Qty", expand=1)
            i_unit = ft.TextField(label="Unit", expand=1)

            def save_ing(e):
                if i_item.value:
                    ing = {
                        "item": i_item.value,
                        "quantity": i_qty.value,
                        "unit": i_unit.value,
                    }
                    added_ingredients.append(ing)
                    refresh_dialog_lists()
                    ing_dlg.open = False
                    page.update()

            ing_dlg = ft.AlertDialog(
                title=ft.Text("Add Ingredient"),
                content=ft.Row([i_item, i_qty, i_unit]),
                actions=[ft.TextButton("Add", on_click=save_ing)],
            )
            page.dialog = ing_dlg
            ing_dlg.open = True
            page.update()

        def add_inst_click(e):
            i_step = ft.TextField(label="Step Description", multiline=True)

            def save_inst(e):
                if i_step.value:
                    added_instructions.append(i_step.value)
                    refresh_dialog_lists()
                    inst_dlg.open = False
                    page.update()

            inst_dlg = ft.AlertDialog(
                title=ft.Text("Add Instruction"),
                content=i_step,
                actions=[ft.TextButton("Add", on_click=save_inst)],
            )
            page.dialog = inst_dlg
            inst_dlg.open = True
            page.update()

        def save_recipe(e):
            if name_tf.value:
                cli.add_recipe(
                    name_tf.value.lower(), added_ingredients, added_instructions
                )
                main_dlg.open = False
                refresh_all()

        main_dlg = ft.AlertDialog(
            title=ft.Text("New Recipe"),
            content=ft.Container(
                width=600,
                height=500,
                content=ft.Column(
                    [
                        name_tf,
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Text("Ingredients", weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.icons.ADD, on_click=add_ing_click),
                            ]
                        ),
                        ing_column,
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Text("Instructions", weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.icons.ADD, on_click=add_inst_click),
                            ]
                        ),
                        inst_column,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: setattr(main_dlg, "open", False)
                    or page.update(),
                ),
                ft.ElevatedButton("Save Recipe", on_click=save_recipe),
            ],
        )
        page.dialog = main_dlg
        main_dlg.open = True
        page.update()

    # --- Shopping List View ---
    def build_shopping_list_view():
        s_list = cli.generate_shopping_list_data(date.today(), 7)

        lv = ft.ListView(expand=True, spacing=5)
        sorted_items = sorted(s_list.keys())

        if not sorted_items:
            lv.controls.append(
                ft.Text("No items needed for the next 7 days.", italic=True)
            )

        for item in sorted_items:
            units_dict = s_list[item]
            parts = []
            for unit, qty in units_dict.items():
                qty_str = f"{qty:.2f}".rstrip("0").rstrip(".")
                parts.append(f"{qty_str} {unit}")

            lv.controls.append(
                ft.ListTile(
                    leading=ft.Checkbox(),
                    title=ft.Text(item.title()),
                    subtitle=ft.Text(", ".join(parts)),
                )
            )

        return ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Text(
                        "Shopping List (Next 7 Days)",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    lv,
                ],
                expand=True,
            ),
        )

    # --- Initialization ---
    meal_plan_tab = ft.Tab(
        text="Meal Plan", icon=ft.icons.DATE_RANGE, content=build_meal_plan_view()
    )
    recipes_tab = ft.Tab(
        text="Recipes", icon=ft.icons.RESTAURANT_MENU, content=build_recipes_view()
    )
    shopping_list_tab = ft.Tab(
        text="Shopping List",
        icon=ft.icons.SHOPPING_CART,
        content=build_shopping_list_view(),
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[meal_plan_tab, recipes_tab, shopping_list_tab],
        expand=1,
    )

    page.add(tabs)


if __name__ == "__main__":
    ft.app(target=main)
