from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse

from src.domain.report.exceptions.report import ReportDataEmpty
from src.domain.report.usecases.report import ReportService
from src.presentation.api.di import get_report_service
from src.presentation.api.handlers.responses.exceptions.report import (
    ReportDataEmptyError,
    ReportFileNotFoundError,
)
from src.presentation.api.handlers.responses.report import (
    ReportTaskResponse,
    ReportTaskStatusResponse,
)

router = APIRouter(prefix="/api/v1/report", tags=["report"])


@router.post(
    "/",
    responses={status.HTTP_404_NOT_FOUND: {"model": ReportDataEmptyError}},
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create excel task",
    description="Create background task for generate excel file with Menu.",
)
async def create_report(
    response: Response,
    report_service: ReportService = Depends(get_report_service),
) -> ReportTaskResponse | ReportDataEmptyError:
    try:
        return ReportTaskResponse(task_id=await report_service.collect_menu_data())
    except ReportDataEmpty:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ReportDataEmptyError()


@router.get(
    "/{task_id}",
    summary="Get info by task id",
    description="Get info about background task by task id",
)
async def get_info_about_task(
    task_id: str, report_service: ReportService = Depends(get_report_service)
) -> ReportTaskStatusResponse:
    return ReportTaskStatusResponse(
        task=await report_service.get_info_about_task(task_id)
    )


@router.get(
    "/download/{file_name}",
    responses={status.HTTP_404_NOT_FOUND: {"model": ReportFileNotFoundError}},
    summary="Download report file",
    description="Endpoint for download Excel file with menu",
)
async def download_report_file(
    response: Response, file_name: str
) -> ReportFileNotFoundError:
    try:
        return FileResponse(
            path=f"data/{file_name}",
            filename=file_name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except FileNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ReportFileNotFoundError()
