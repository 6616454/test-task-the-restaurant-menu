import json
import uuid

import pytest


class TestSubMenuHandlers:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "menu_id, expected_result, status_code",
        [
            ("b61ec7b4-5b25-41de-9d41-f00331b04885", [], 200),
            (str(uuid.uuid4()), {"detail": "menu not found"}, 404),
        ],
    )
    async def test_get_submenus(
        self,
        client,
        menu_id,
        expected_result,
        status_code,
        menu_data,
        create_menu_in_database,
    ):
        await create_menu_in_database(**menu_data)
        response = await client.get(f"api/v1/menus/{menu_id}/submenus")

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_get_submenus_after_create(
        self,
        client,
        submenu_data,
        create_submenu_in_database,
        menu_data,
        create_menu_in_database,
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        response = await client.get(f'api/v1/menus/{menu_data["menu_id"]}/submenus')

        assert len(response.json()) == 1
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_submenu(
        self,
        client,
        menu_data,
        create_menu_in_database,
        get_submenu_from_database,
        get_cache,
    ):
        test_data = {"title": "some_title", "description": "some_description"}

        await create_menu_in_database(**menu_data)
        response = await client.post(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus', json=test_data
        )
        data = response.json()

        assert data["title"] == test_data["title"]
        assert data["description"] == test_data["description"]
        assert data["dishes_count"] == 0

        submenu_from_db = await get_submenu_from_database(data["id"])

        assert data["title"] == submenu_from_db.title
        assert data["description"] == submenu_from_db.description

        submenu_from_cache = json.loads(await get_cache.get(data["id"]))

        assert data["title"] == submenu_from_cache["title"]
        assert data["description"] == submenu_from_cache["description"]
        assert data["dishes_count"] == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "menu_id, test_data, expected_result, status_code",
        [
            (
                str(uuid.uuid4()),
                {"title": "title", "description": "description"},
                {"detail": "menu not found"},
                404,
            ),
            (
                "b61ec7b4-5b25-41de-9d41-f00331b04885",
                {"title": "title"},
                {
                    "detail": [
                        {
                            "loc": ["body", "description"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                },
                422,
            ),
            (
                "b61ec7b4-5b25-41de-9d41-f00331b04885",
                {"description": "description"},
                {
                    "detail": [
                        {
                            "loc": ["body", "title"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                },
                422,
            ),
            (
                "b61ec7b4-5b25-41de-9d41-f00331b04885",
                {},
                {
                    "detail": [
                        {
                            "loc": ["body", "title"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        },
                        {
                            "loc": ["body", "description"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        },
                    ]
                },
                422,
            ),
        ],
    )
    async def test_invalid_create_submenu(
        self,
        client,
        menu_id,
        test_data,
        menu_data,
        create_menu_in_database,
        expected_result,
        status_code,
    ):
        await create_menu_in_database(**menu_data)
        response = await client.post(f"api/v1/menus/{menu_id}/submenus", json=test_data)

        assert response.json() == expected_result
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_get_submenu(
        self,
        client,
        menu_data,
        submenu_data,
        create_submenu_in_database,
        create_menu_in_database,
        get_cache,
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)

        response = await client.get(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}'
        )
        data = response.json()

        assert data["id"] == submenu_data["submenu_id"]
        assert data["title"] == submenu_data["title"]
        assert data["description"] == submenu_data["description"]
        assert data["dishes_count"] == 0
        assert response.status_code == 200

        submenu_from_cache = json.loads(await get_cache.get(submenu_data["submenu_id"]))
        assert data["id"] == submenu_from_cache["id"]
        assert data["title"] == submenu_from_cache["title"]
        assert data["description"] == submenu_from_cache["description"]
        assert submenu_from_cache["dishes_count"] == 0

    @pytest.mark.asyncio
    async def test_get_submenu_404(self, client):
        response = await client.get(
            f"api/v1/menus/{str(uuid.uuid4())}/submenus/{str(uuid.uuid4())}"
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "submenu not found"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "submenu_id, test_data, expected_result, status_code",
        [
            (
                "5f740121-65d6-490b-984c-1cb28a4b43fa",
                {"title": "new_title", "description": "new_description"},
                {
                    "id": "5f740121-65d6-490b-984c-1cb28a4b43fa",
                    "title": "new_title",
                    "description": "new_description",
                    "dishes_count": 0,
                },
                200,
            ),
            (
                str(uuid.uuid4()),
                {"title": "new_title", "description": "new_description"},
                {"detail": "submenu not found"},
                404,
            ),
            (
                "5f740121-65d6-490b-984c-1cb28a4b43fa",
                {},
                {"detail": "submenu_data request body empty"},
                400,
            ),
            (
                "5f740121-65d6-490b-984c-1cb28a4b43fa",
                {"description": "new_description2"},
                {
                    "id": "5f740121-65d6-490b-984c-1cb28a4b43fa",
                    "title": "some_title",
                    "description": "new_description2",
                    "dishes_count": 0,
                },
                200,
            ),
            (
                "5f740121-65d6-490b-984c-1cb28a4b43fa",
                {"title": "new_title2"},
                {
                    "id": "5f740121-65d6-490b-984c-1cb28a4b43fa",
                    "title": "new_title2",
                    "description": "some_description",
                    "dishes_count": 0,
                },
                200,
            ),
        ],
    )
    async def test_patch_submenu(
        self,
        client,
        submenu_id,
        test_data,
        expected_result,
        status_code,
        menu_data,
        submenu_data,
        create_menu_in_database,
        create_submenu_in_database,
        get_submenu_from_database,
        get_cache,
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        response = await client.patch(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_id}', json=test_data
        )
        data = response.json()

        assert data == expected_result
        assert response.status_code == status_code

        if data.get("id"):
            submenu_from_db = await get_submenu_from_database(data["id"])

            assert data["title"] == submenu_from_db.title
            assert data["description"] == submenu_from_db.description

            submenu_from_cache = json.loads(await get_cache.get(data["id"]))

            assert data["title"] == submenu_from_cache["title"]
            assert data["description"] == submenu_from_cache["description"]

    @pytest.mark.asyncio
    async def test_delete_submenu(
        self,
        client,
        menu_data,
        submenu_data,
        create_menu_in_database,
        create_submenu_in_database,
        get_submenu_from_database,
        get_cache,
    ):
        await create_menu_in_database(**menu_data)
        await create_submenu_in_database(**submenu_data)
        response = await client.delete(
            f'api/v1/menus/{menu_data["menu_id"]}/submenus/{submenu_data["submenu_id"]}'
        )

        assert response.json() == {
            "status": True,
            "message": "The submenu has been deleted",
        }
        assert response.status_code == 200

        submenu_from_db = await get_submenu_from_database(submenu_data["submenu_id"])

        assert submenu_from_db is None

    @pytest.mark.asyncio
    async def test_delete_submenu_404(self, client):
        response = await client.get(
            f"api/v1/menus/{str(uuid.uuid4())}/submenus/{str(uuid.uuid4())}"
        )

        assert response.json() == {"detail": "submenu not found"}
        assert response.status_code == 404
