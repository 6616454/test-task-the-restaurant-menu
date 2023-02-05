from fastapi import APIRouter, Depends, status

from src.domain.report.usecases.report import ReportService
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.presentation.api.di import uow_provider
from src.presentation.api.di.providers.services import report_service_stub

router = APIRouter(prefix="/api/v1/report", tags=["report"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_report(
    uow: SQLAlchemyUoW = Depends(uow_provider),
    report_service: ReportService = Depends(report_service_stub),
) -> str:
    return await report_service.collect_menu_data(uow)


@router.get("/{task_id}")
async def get_info_about_task(
    task_id: str, report_service: ReportService = Depends(report_service_stub)
):
    return await report_service.get_info_about_task(task_id)
