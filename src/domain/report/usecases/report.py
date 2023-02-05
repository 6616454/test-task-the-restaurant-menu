from dataclasses import dataclass

from celery.result import AsyncResult
from fastapi.responses import JSONResponse

from src.domain.report.dto.report import ReportDish, ReportMenu, ReportSubMenu
from src.domain.report.interfaces.tasks_sender import IReportTasksSender
from src.domain.report.interfaces.uow import IReportUoW
from src.domain.report.interfaces.usecases import ReportUseCase


class GetReportData(ReportUseCase):
    async def __call__(self):
        result = []

        menus = await self.uow.menu_holder.menu_repo.get_all()

        for menu in menus:
            result.append(
                ReportMenu(
                    title=menu.title,
                    description=menu.description,
                    submenus=[
                        ReportSubMenu(
                            title=submenu.title,
                            description=submenu.description,
                            dishes=[
                                ReportDish(
                                    title=dish.title,
                                    description=dish.description,
                                    price=dish.price,
                                )
                                for dish in submenu.dishes
                            ],
                        )
                        for submenu in menu.submenus
                    ],
                ).dict()
            )

        return result


@dataclass
class ReportService:
    tasks_sender: IReportTasksSender

    @staticmethod
    async def get_info_about_task(task_id: str) -> JSONResponse:
        task = AsyncResult(task_id)

        return JSONResponse(
            content={
                "status": task.status,
                "detail": "Wait when status of task will be SUCCESS.",
                "link": f"Link for download Excel-file with Menu - {task.result}",
            }
        )

    async def collect_menu_data(self, uow: IReportUoW) -> JSONResponse:
        report_menus = await GetReportData(uow)()

        task_id = self.tasks_sender.collect_menu_data(report_menus)

        return JSONResponse(
            content={
                "task_id": task_id,
                "detail": "Task for get Excel-file with Menu started...",
            }
        )
