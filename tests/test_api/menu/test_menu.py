import uuid

import pytest


class TestResultSaver:
    menu_id: str = ''
    submenu_id: str = ''

    def set_menu(self, value: str):
        self.menu_id = value

    def set_submenu(self, value):
        self.submenu_id = value


test_result = TestResultSaver()


class TestMenuScenario:
    @pytest.mark.asyncio
    async def test_menus_get(self, client):
        response = client.get('/api/v1/menus')

        assert response.json() == []
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_menu(self, client):
        test_data = {
            'title': 'test_title',
            'description': 'test_description'
        }
        response = client.post('api/v1/menus', json=test_data)
        data = response.json()

        test_result.set_menu(str(data['id']))

        assert response.status_code == 201
        assert data['title'] == test_data['title']
        assert data['description'] == test_data['description']
        assert data['submenus_count'] == 0
        assert data['dishes_count'] == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize('data, expected_result, status_code', [
        (
                {}, {
                    "detail": [
                        {
                            "loc": [
                                "body",
                                "title"
                            ],
                            "msg": "field required",
                            "type": "value_error.missing"
                        },
                        {
                            "loc": [
                                "body",
                                "description"
                            ],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                },
                422
        ),
        (
                {'title': 'title'},
                {
                    "detail": [
                        {
                            "loc": [
                                "body",
                                "description"
                            ],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                },
                422,
        ),
        (
                {'description': 'desc'}, {
                    "detail": [
                        {
                            "loc": [
                                "body",
                                "title"
                            ],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                },
                422
        )
    ])
    async def test_invalid_create_menu(self, client, data, expected_result, status_code):
        response = client.post('api/v1/menus', json=data)

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_menus_get_after_create(self, client):
        response = client.get('/api/v1/menus')
        assert len(response.json()) == 1
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize('data, expected_result, status_code', [
        (
                test_result.menu_id,
                [
                    {
                        'id': '1',
                        'title': 'test_title',
                        'description': 'test_description',
                        'submenus_count': 0,
                        'dishes_count': 0
                    }
                ],
                200
        ),
        (
                str(uuid.uuid4()),
                {
                    'detail': 'menu not found'
                },
                404
        )
    ])
    async def test_get_menu(self, client, data, expected_result, status_code):
        response = client.get(f'api/v1/menus/{data}')
        if isinstance(expected_result, list):
            expected_result[0]['id'] = test_result.menu_id
        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    @pytest.mark.parametrize('id_, test_data, expected_result, status_code', [
        (
                test_result.menu_id,
                {
                    'title': 'new_title',
                    'description': 'new_description'
                },
                {
                    'id': '1',
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
                test_result.menu_id,
                {},
                {
                    'detail': 'menu_data request body empty'
                },
                200
        ),
        (
                test_result.menu_id,
                {
                    'description': 'new_description2'
                },
                {
                    'id': '1',
                    'title': 'new_title',
                    'description': 'new_description2',
                    'submenus_count': 0,
                    'dishes_count': 0
                },
                200
        ),
    ])
    async def test_patch_menu(self, client, id_, test_data, expected_result, status_code):
        if id_:
            response = client.patch(f'api/v1/menus/{id_}', json=test_data)
        else:
            response = client.patch(f'api/v1/menus/{test_result.menu_id}', json=test_data)

        if expected_result.get('id'):
            expected_result['id'] = test_result.menu_id

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    @pytest.mark.parametrize('menu_id, expected_result, status_code', [
        (
                str(uuid.uuid4()),
                {
                    'detail': 'menu not found'
                },
                404
        ),
        (
                test_result.menu_id,
                [],
                200
        )
    ])
    async def test_get_submenus(self, client, menu_id, expected_result, status_code):
        if menu_id:
            response = client.get(f'api/v1/menus/{menu_id}/submenus')
        else:
            response = client.get(f'api/v1/menus/{test_result.menu_id}/submenus')

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_create_submenu(self, client):
        test_data = {
            'title': 'test_title',
            'description': 'description'
        }

        response = client.post(f'api/v1/menus/{test_result.menu_id}/submenus', json=test_data)
        data = response.json()

        test_result.set_submenu(str(data['id']))

        assert response.status_code == 201
        assert data['title'] == test_data['title']
        assert data['description'] == test_data['description']
        assert data['dishes_count'] == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize('menu_id, test_data, expected_result, status_code', [
        (
            str(uuid.uuid4()),
            {
                'title': 'title',
                'description': 'description'
            },
            {
                'detail': 'menu not found'
            },
            404
        ),
        (
            test_result.menu_id,
            {
                'title': 'title'
            },
            {
                "detail": [
                    {
                        "loc": [
                            "body",
                            "description"
                        ],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            },
            422
        ),
        (
            test_result.menu_id,
            {
                'description': 'description'
            },
            {
                "detail": [
                    {
                        "loc": [
                            "body",
                            "title"
                        ],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            },
            422
        ),
        (
            test_result.menu_id,
            {},
            {
                "detail": [
                    {
                        "loc": [
                            "body",
                            "title"
                        ],
                        "msg": "field required",
                        "type": "value_error.missing"
                    },
                    {
                        "loc": [
                            "body",
                            "description"
                        ],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            },
            422
        )
    ])
    async def test_invalid_create_submenu(self, client, menu_id, test_data, expected_result, status_code):
        if menu_id:
            response = client.post(f'api/v1/menus/{menu_id}/submenus', json=test_data)
        else:
            response = client.post(f'api/v1/menus/{test_result.menu_id}/submenus', json=test_data)

        assert response.json() == expected_result
        assert response.status_code == status_code
