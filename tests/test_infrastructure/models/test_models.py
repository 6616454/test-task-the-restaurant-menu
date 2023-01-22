import pytest


class TestCascadeDelete:

    @pytest.mark.asyncio
    async def test_cascade_delete_dishes_submenus_from_menu(
            self,
            menu_data,
            submenu_data,
            dish_data,
            create_menu_in_database,
            create_submenu_in_database,
            create_dish_in_database,
            get_submenu_from_database,
            get_dish_from_database,
            delete_menu_from_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)

        await delete_menu_from_database(menu_data['menu_id'])

        submenu_from_db = await get_submenu_from_database(submenu_data['submenu_id'])
        dish_from_db = await get_dish_from_database(dish_data['dish_id'])

        assert submenu_from_db is None
        assert dish_from_db is None

    @pytest.mark.asyncio
    async def test_cascade_delete_dishes_from_submenu(
            self,
            menu_data,
            submenu_data,
            dish_data,
            create_menu_in_database,
            create_submenu_in_database,
            create_dish_in_database,
            get_dish_from_database,
            delete_submenu_from_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)

        await delete_submenu_from_database(submenu_data['submenu_id'])

        dish_from_db = await get_dish_from_database(dish_data['dish_id'])

        assert dish_from_db is None
