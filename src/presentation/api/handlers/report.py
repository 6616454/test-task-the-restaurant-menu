from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from src.domain.report.usecases.report import ReportService
from src.presentation.api.di import get_report_service

router = APIRouter(prefix="/api/v1/report", tags=["report"])


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create excel task",
    description="Create background task for generate excel file with Menu.",
)
async def create_report(
    report_service: ReportService = Depends(get_report_service),
) -> str:
    return await report_service.collect_menu_data()


@router.get(
    "/{task_id}",
    summary="Get info by task id",
    description="Get info about background task by task id",
)
async def get_info_about_task(
    task_id: str, report_service: ReportService = Depends(get_report_service)
):
    return await report_service.get_info_about_task(task_id)


@router.get(
    "/download/{file_name}",
    summary="Download file",
    description="Endpoint for download Excel file with menu",
)
async def download_report_file(file_name: str) -> FileResponse:
    return FileResponse(
        path=f"data/{file_name}",
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
