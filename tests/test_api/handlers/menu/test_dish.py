import json
import uuid

import pytest


class TestDishHandlers:

    @pytest.mark.asyncio
    @pytest.mark.parametrize('menu_id, submenu_id, expected_result, status_code', [
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            '5f740121-65d6-490b-984c-1cb28a4b43fa',
            [],
            200
        ),
        (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            # {
            [],  # 'detail': 'submenu not found'
            # },
            200  # 404
        )
    ])
    async def test_dishes_get(
            self,
            client,
            menu_id,
            submenu_id,
            expected_result,
            status_code,
            menu_data,
            create_menu_in_database,
            submenu_data,
            create_submenu_in_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        response = await client.get(
            f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes'
        )

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_get_dishes_after_create(
            self,
            client,
            submenu_data,
            create_submenu_in_database,
            menu_data,
            create_menu_in_database,
            dish_data,
            create_dish_in_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)
        response = await client.get(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}/dishes'
        )

        assert len(response.json()) == 1
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_submenu(
            self,
            client,
            menu_data,
            create_menu_in_database,
            submenu_data,
            create_submenu_in_database,
            get_dish_from_database,
            get_cache
    ):
        test_data = {
            'title': 'some_title',
            'description': 'some_description',
            'price': '12.497'
        }

        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        response = await client.post(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}/dishes',
            json=test_data
        )
        data = response.json()

        assert data['title'] == test_data['title']
        assert data['description'] == test_data['description']

        dish_from_db = await get_dish_from_database(data['id'])

        assert data['title'] == dish_from_db.title
        assert data['description'] == dish_from_db.description
        assert data['price'] == dish_from_db.price

        dish_from_cache = json.loads(await get_cache.get(data['id']))

        assert data['title'] == dish_from_cache['title']
        assert data['description'] == dish_from_cache['description']
        assert data['price'] == dish_from_cache['price']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('menu_id, submenu_id, test_data, expected_result, status_code', [
        (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            {
                'title': 'title',
                'description': 'description',
                'price': '12.49'
            },
            {
                'detail': 'submenu not found'
            },
            404
        ),
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            '5f740121-65d6-490b-984c-1cb28a4b43fa',
            {
                'price': '12.50'
            },
            {
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
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            '5f740121-65d6-490b-984c-1cb28a4b43fa',
            {
                'title': 'title',
                'description': 'description'
            },
            {
                'detail': [
                    {
                        'loc': [
                            'body',
                            'price'
                        ],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    },
                ]
            },
            422
        ),
        (
            'b61ec7b4-5b25-41de-9d41-f00331b04885',
            '5f740121-65d6-490b-984c-1cb28a4b43fa',
            {
                'title': 'title',
                'description': 'description',
                'price': 'string'
            },
            {
                'detail': 'The price of the dish must be a floating point number'
            },
            422
        ),
    ])
    async def test_invalid_create_dish(
            self,
            client,
            menu_id,
            submenu_id,
            expected_result,
            status_code,
            test_data,
            menu_data,
            create_menu_in_database,
            submenu_data,
            create_submenu_in_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        response = await client.post(
            f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
            json=test_data
        )

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_get_dish(
            self,
            client,
            menu_data,
            submenu_data,
            dish_data,
            create_submenu_in_database,
            create_menu_in_database,
            create_dish_in_database,
            get_cache
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)

        response = await client.get(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}/dishes/{dish_data["dish_id"]}'
        )
        data = response.json()

        assert data['id'] == dish_data['dish_id']
        assert data['title'] == dish_data['title']
        assert data['description'] == dish_data['description']
        assert data['price'] == dish_data['price']
        assert response.status_code == 200

        dish_from_cache = json.loads(await get_cache.get(data['id']))

        assert data['id'] == dish_from_cache['id']
        assert data['title'] == dish_from_cache['title']
        assert data['description'] == dish_from_cache['description']
        assert data['price'] == dish_from_cache['price']

    @pytest.mark.asyncio
    async def test_get_dish_404(self, client):
        response = await client.get(
            f'api/v1/menus/{str(uuid.uuid4())}/submenus/{str(uuid.uuid4())}/dishes/{str(uuid.uuid4())}'
        )

        assert response.status_code == 404
        assert response.json() == {'detail': 'dish not found'}

    @pytest.mark.asyncio
    @pytest.mark.parametrize('dish_id, test_data, expected_result, status_code', [
        (
            '911577a1-fbf5-4931-b075-e7641c84121a',
            {
                'title': 'new_title',
                'description': 'new_description',
                'price': '13.50'
            },
            {
                'id': '911577a1-fbf5-4931-b075-e7641c84121a',
                'title': 'new_title',
                'description': 'new_description',
                'price': '13.50'
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
                'detail': 'dish not found'
            },
            404
        ),
        (
            '911577a1-fbf5-4931-b075-e7641c84121a',
            {},
            {
                'detail': 'dish_data request body empty'
            },
            400
        ),
        (
            '911577a1-fbf5-4931-b075-e7641c84121a',
            {
                'description': 'new_description2',
                'price': '13.50'
            },
            {
                'id': '911577a1-fbf5-4931-b075-e7641c84121a',
                'title': 'some_title',
                'description': 'new_description2',
                'price': '13.50'
            },
            200
        ),
        (
            '911577a1-fbf5-4931-b075-e7641c84121a',
            {
                'title': 'new_title2'
            },
            {
                'id': '911577a1-fbf5-4931-b075-e7641c84121a',
                'title': 'new_title2',
                'description': 'some_description',
                'price': '14.50'
            },
            200
        ),
        (
            '911577a1-fbf5-4931-b075-e7641c84121a',
            {},
            {
                'detail': 'dish_data request body empty'
            },
            400
        ),
        (
            '911577a1-fbf5-4931-b075-e7641c84121a',
            {
                'price': 'string'
            },
            {
                'detail': 'The price of the dish must be a floating point number'
            },
            422
        )
    ])
    async def test_patch_dish(
            self,
            client,
            dish_id,
            test_data,
            expected_result,
            status_code,
            menu_data,
            submenu_data,
            dish_data,
            create_menu_in_database,
            create_submenu_in_database,
            create_dish_in_database,
            get_dish_from_database,
            get_cache

    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)
        response = await client.patch(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}/dishes/{dish_id}',
            json=test_data
        )
        data = response.json()

        assert data == expected_result
        assert response.status_code == status_code

        if data.get('id'):
            dish_from_db = await get_dish_from_database(data['id'])

            assert data['title'] == dish_from_db.title
            assert data['description'] == dish_from_db.description
            assert data['price'] == dish_from_db.price

            dish_from_cache = json.loads(await get_cache.get(data['id']))

            assert data['title'] == dish_from_cache['title']
            assert data['description'] == dish_from_cache['description']
            assert data['price'] == dish_from_cache['price']

    @pytest.mark.asyncio
    async def test_delete_dish(
            self,
            client,
            menu_data,
            submenu_data,
            dish_data,
            create_menu_in_database,
            create_submenu_in_database,
            create_dish_in_database,
            get_dish_from_database
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        await create_dish_in_database(**dish_data)
        response = await client.delete(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}/dishes/{dish_data["dish_id"]}'
        )

        assert response.json() == {
            'status': True,
            'message': 'The dish has been deleted'
        }
        assert response.status_code == 200

        dish_from_db = await get_dish_from_database(dish_data['dish_id'])

        assert dish_from_db is None

    @pytest.mark.asyncio
    async def test_delete_dish_404(self, client):
        response = await client.delete(
            f'api/v1/menus/{str(uuid.uuid4())}/submenus/{str(uuid.uuid4())}/dishes/{str(uuid.uuid4())}'
        )

        assert response.json() == {'detail': 'dish not found'}
        assert response.status_code == 404
