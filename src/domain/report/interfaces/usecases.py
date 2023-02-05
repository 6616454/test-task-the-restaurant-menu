from abc import ABC

from src.domain.report.interfaces.uow import IReportUoW


class ReportUseCase(ABC):
    def __init__(self, uow: IReportUoW):
        self.uow = uow
