import pytest


class TestReportHandlers:
    @pytest.mark.asyncio
    async def test_report_data_empty_error(self, client):
        response = await client.post("api/v1/report/")

        assert response.json() == {
            "detail": "Report data for create Excel-file with menu was empty"
        }
        assert response.status_code == 404
