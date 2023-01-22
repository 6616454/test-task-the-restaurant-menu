import pytest

from src.domain.menu.dto.menu import CreateMenu
from src.domain.menu.exceptions.menu import MenuNotExists
from src.domain.menu.usecases.menu import GetMenu, GetMenus, AddMenu, DeleteMenu, PatchMenu
from tests.mocks import UoWMock


class TestMenuUseCases:
    def setup_method(self):
        self.uow_mock = UoWMock()

    @pytest.mark.asyncio
    async def test_get_usecase(self):
        menu = await GetMenu(self.uow_mock)('menu_1', load=True)

        assert menu == self.uow_mock.menu_holder.menu_repo.test_data['menu_1']

    @pytest.mark.asyncio
    async def test_raises_get_usecase(self):
        with pytest.raises(MenuNotExists):
            await GetMenu(self.uow_mock)('menu_2', load=True)

    @pytest.mark.asyncio
    async def test_get_all_usecase(self):
        menus = await GetMenus(self.uow_mock)()

        assert menus == [self.uow_mock.menu_holder.menu_repo.test_data['menu_1']]
        assert isinstance(menus, list) is True

    @pytest.mark.asyncio
    async def test_add_usecase(self):
        new_menu = await AddMenu(self.uow_mock)(CreateMenu(
            title='t2',
            description='d2'
        ))

        assert len(self.uow_mock.menu_holder.menu_repo.test_data) == 2
        assert self.uow_mock.menu_holder.menu_repo.test_data['menu_2'] == new_menu

    @pytest.mark.asyncio
    async def test_delete_usecase(self):
        await DeleteMenu(self.uow_mock)('menu_2')

        assert len(self.uow_mock.menu_holder.menu_repo.test_data) == 1

    @pytest.mark.asyncio
    async def test_raise_delete_usecase(self):
        with pytest.raises(MenuNotExists):
            await DeleteMenu(self.uow_mock)('menu_3')

    @pytest.mark.asyncio
    async def test_patch_usecase(self):
        test_data = {'title': 't', 'description': 'd'}
        await PatchMenu(self.uow_mock)('menu_1', test_data)
        assert self.uow_mock.menu_holder.menu_repo.test_data['menu_1'] == test_data

