import uuid

import pytest


class TestMenuHandlers:
    @pytest.mark.asyncio
    async def test_menus_get(self, client):
        response = await client.get('api/v1/menus/')

        assert response.json() == []
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menus_get_after_create(self, client, create_menu_in_database, menu_data):
        await create_menu_in_database(**menu_data)
        response = await client.get('api/v1/menus/')

        assert len(response.json()) == 1
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_menu(self, client, get_menu_from_database):
        test_data = {
            'title': 'test_title',
            'description': 'test_description'
        }
        response = await client.post('api/v1/menus/', json=test_data)
        data = response.json()

        assert response.status_code == 201
        assert data['title'] == test_data['title']
        assert data['description'] == test_data['description']
        assert data['submenus_count'] == 0
        assert data['dishes_count'] == 0

        menu_from_db = await get_menu_from_database(data['id'])

        assert data['title'] == menu_from_db.title
        assert data['description'] == menu_from_db.description

    @pytest.mark.asyncio
    @pytest.mark.parametrize('data, expected_result, status_code', [
        (
            {}, {
                'detail': [
                    {
                        'loc': [
                            'body',
                            'title'
                        ],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    },
                    {
                        'loc': [
                            'body',
                            'description'
                        ],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            422
        ),
        (
            {'title': 'title'},
            {
                'detail': [
                    {
                        'loc': [
                            'body',
                            'description'
                        ],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            422,
        ),
        (
            {'description': 'desc'}, {
                'detail': [
                    {
                        'loc': [
                            'body',
                            'title'
                        ],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            422
        )
    ])
    async def test_invalid_create_menu(self, client, data, expected_result, status_code):
        response = await client.post('api/v1/menus/', json=data)

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_get_menu(self, client, create_menu_in_database, menu_data):
        await create_menu_in_database(**menu_data)
        response = await client.get(f'api/v1/menus/{menu_data["menu_id"]}')
        data = response.json()

        assert data['id'] == menu_data['menu_id']
        assert data['title'] == menu_data['title']
        assert data['description'] == menu_data['description']
        assert data['submenus_count'] == 0
        assert data['dishes_count'] == 0

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_menu_404(self, client):
        response = await client.get(f'api/v1/menus/{str(uuid.uuid4())}')

        assert response.json() == {'detail': 'menu not found'}
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.parametrize('menu_id, test_data, expected_result, status_code', [
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            {
                'title': 'new_title',
                'description': 'new_description'
            },
            {
                'id': 'b61ec7b4-5b25-41de-9d41-f00331b04885',
                'title': 'new_title',
                'description': 'new_description',
                'submenus_count': 0,
                'dishes_count': 0
            },
            200
        ),
        (
            str(uuid.uuid4()),
            {
                'title': 'new_title',
                'description': 'new_description'
            },
            {
                'detail': 'menu not found'
            },
            404
        ),
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            {},
            {
                'detail': 'menu_data request body empty'
            },
            400
        ),
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            {
                'description': 'new_description2'
            },
            {
                'id': 'b61ec7b4-5b25-41de-9d41-f00331b04885',
                'title': 'some_title',
                'description': 'new_description2',
                'submenus_count': 0,
                'dishes_count': 0
            },
            200
        ),
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            {
                'title': 'new_title2'
            },
            {
                'id': 'b61ec7b4-5b25-41de-9d41-f00331b04885',
                'title': 'new_title2',
                'description': 'some_description',
                'submenus_count': 0,
                'dishes_count': 0
            },
            200
        )
    ])
    async def test_patch_menu(
            self,
            client,
            menu_id,
            test_data,
            expected_result,
            status_code,
            menu_data,
            create_menu_in_database,
            get_menu_from_database
    ):
        await create_menu_in_database(**menu_data)
        response = await client.patch(f'api/v1/menus/{menu_id}', json=test_data)
        data = response.json()

        assert data == expected_result
        assert response.status_code == status_code

        if data.get('id'):
            menu_from_db = await get_menu_from_database(data['id'])

            assert data['title'] == menu_from_db.title
            assert data['description'] == menu_from_db.description

    @pytest.mark.asyncio
    async def test_delete_menu(self, client, menu_data, create_menu_in_database, get_menu_from_database):
        await create_menu_in_database(**menu_data)

        response = await client.delete(f'api/v1/menus/{menu_data["menu_id"]}')

        assert response.json() == {
            'status': True,
            'message': 'The menu has been deleted'
        }
        assert response.status_code == 200

        menu_from_db = await get_menu_from_database(menu_data['menu_id'])

        assert menu_from_db is None

    @pytest.mark.asyncio
    async def test_delete_menu_404(self, client):
        response = await client.get(f'api/v1/menus/{str(uuid.uuid4())}')

        assert response.json() == {'detail': 'menu not found'}
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_counter_menu(
            self,
            client,
            menu_data,
            submenu_data,
            dish_data,
            create_menu_in_database,
            create_submenu_in_database,
            create_dish_in_database,
            delete_submenu_from_database,
            delete_dish_from_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)

        temp = dish_data['dish_id']
        dish_data['dish_id'] = str(uuid.uuid4())
        dish_data['title'] = 'new_title_dish'

        await create_dish_in_database(**dish_data)

        first_response = await client.get(f'api/v1/menus/{menu_data["menu_id"]}')
        first_data = first_response.json()

        await delete_dish_from_database(dish_data['dish_id'])
        await delete_dish_from_database(temp)
        await delete_submenu_from_database(submenu_data['submenu_id'])

        second_response = await client.get(f'api/v1/menus/{menu_data["menu_id"]}')
        second_data = second_response.json()

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert first_data['submenus_count'] == 1
        assert first_data['dishes_count'] == 2
        assert second_data['submenus_count'] == 0
        assert second_data['dishes_count'] == 0
