from dataclasses import dataclass

from src.domain.report.interfaces.tasks_sender import IReportTasksSender
from src.domain.report.interfaces.uow import IReportUoW
from src.domain.report.interfaces.usecases import ReportUseCase


class GetData(ReportUseCase):
    async def __call__(self):
        menus = await self.uow.menu_holder.menu_repo.get_all()
        return menus[0].to_dto()


@dataclass
class ReportService:
    tasks_sender: IReportTasksSender

    async def collect_menu_data(self, uow: IReportUoW):
        menu = await GetData(uow)()

        my_id = self.tasks_sender.collect_menu_data(menu)
        return my_id
