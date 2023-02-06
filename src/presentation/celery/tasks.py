from datetime import datetime

from openpyxl.workbook import Workbook


def collect_menu_data(report_menus: list[dict]) -> str:
    filename = f"{str(datetime.now())}_menu.xlsx"

    book = Workbook()
    sheet = book.active
    menu_row, menu_column, menu_counter = 1, 1, 1
    for menu in report_menus:
        sheet.cell(menu_row, menu_column).value = menu_counter
        sheet.cell(menu_row, menu_column + 1).value = menu["title"]
        sheet.cell(menu_row, menu_column + 2).value = menu["description"]
        menu_counter += 1
        submenu_row = menu_row + 1
        submenu_column = menu_column + 1
        submenu_counter = 1
        for submenu in menu["submenus"]:
            sheet.cell(submenu_row, submenu_column).value = submenu_counter
            sheet.cell(submenu_row, submenu_column + 1).value = submenu["title"]
            sheet.cell(submenu_row, submenu_column + 2).value = submenu["description"]
            submenu_counter += 1
            dish_row = submenu_row + 1
            dish_column = submenu_column + 1
            dish_counter = 1
            for dish in submenu["dishes"]:
                sheet.cell(dish_row, dish_column).value = dish_counter
                sheet.cell(dish_row, dish_column + 1).value = dish["title"]
                sheet.cell(dish_row, dish_column + 2).value = dish["description"]
                sheet.cell(dish_row, dish_column + 3).value = dish["price"]
                dish_counter += 1
                dish_row += 1
            submenu_row = dish_row
        menu_row = submenu_row

    book.save(f"data/{filename}")

    return f"http://127.0.0.1:8000/api/v1/report/download/{filename}"
