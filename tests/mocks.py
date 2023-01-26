from src.domain.menu.exceptions.menu import MenuNotExists


class MenuRepoMock:
    test_data = {
        'menu_1': {'title': 'title', 'description': 'description'}
    }

    new_value: dict[str, str] | None = None

    async def get_by_id(self, menu_id: str):
        data = self.test_data.get(menu_id)
        if data:
            return menu_id

        raise MenuNotExists

    async def get_by_id_all(self, menu_id: str, load_mock: bool) -> str:
        data = self.test_data.get(menu_id)
        if data:
            return data

        raise MenuNotExists

    async def get_all(self) -> list[str]:
        return [*self.test_data.values()]

    def model(self, title: str, description: str):
        data = {'menu_2': {'title': title, 'description': description}}
        self.new_value = data
        return data['menu_2']

    async def save(self, mock_value: str) -> None:
        self.test_data.update(self.new_value)

    async def refresh(self, mock_value: str):
        return

    async def delete(self, menu_id: str):
        del self.test_data[menu_id]

    async def update_obj(self, menu_id: str, **kwargs):
        self.test_data[menu_id] = dict(kwargs)


class SubMenuRepoMock(MenuRepoMock):
    pass


class DishRepoMock(MenuRepoMock):
    pass


class MenuHolderMock:

    def __init__(self):
        self.menu_repo = MenuRepoMock()
        self.submenu_repo = SubMenuRepoMock()
        self.dish_repo = DishRepoMock()


class UoWMock:
    def __init__(self):
        self.menu_holder = MenuHolderMock()

    async def commit(self):
        return
