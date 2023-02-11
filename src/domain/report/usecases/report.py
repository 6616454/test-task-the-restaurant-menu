from src.domain.report.dto.report import (
    ReportDish,
    ReportMenu,
    ReportStatusTask,
    ReportSubMenu,
)
from src.domain.report.exceptions.report import ReportDataEmpty
from src.domain.report.interfaces.tasks_sender import IReportTasksSender
from src.domain.report.interfaces.uow import IReportUoW
from src.domain.report.interfaces.usecases import ReportUseCase


class GetReportData(ReportUseCase):
    async def __call__(self) -> list[dict]:
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


class ReportService:
    def __init__(self, tasks_sender: IReportTasksSender, uow: IReportUoW):
        self.tasks_sender = tasks_sender
        self.uow = uow

    async def get_info_about_task(self, task_id: str) -> ReportStatusTask:
        task = self.tasks_sender.get_info_by_task_id(task_id)

        return ReportStatusTask(status=task.status, link=task.result)

    async def collect_menu_data(self) -> str:
        report_menus = await GetReportData(self.uow)()

        if report_menus:
            task_id = self.tasks_sender.collect_menu_data(report_menus)

            return task_id

        raise ReportDataEmpty
